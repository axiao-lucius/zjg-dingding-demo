"""
质保金到期提醒
每日运行，检查未来 30 天内到期的质保金项目，推送钉钉群通知
"""
import os
import sys
from datetime import datetime, timedelta

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../.."))
from src.api.dingtalk_client import client
from dotenv import load_dotenv

load_dotenv()

BASE_ID = os.getenv("AITABLE_BASE_ID")
PROJECT_TABLE_ID = os.getenv("PROJECT_TABLE_ID")
WARN_DAYS = 30  # 提前预警天数


def check_warranty_expiry():
    """检查即将到期的质保金项目并推送提醒"""
    today = datetime.today().date()
    warn_date = today + timedelta(days=WARN_DAYS)

    print(f"[{today}] 开始检查质保金到期情况（预警窗口：{WARN_DAYS} 天）")

    # 查询质保期项目
    records = client.aitable_list_records(
        base_id=BASE_ID,
        table_id=PROJECT_TABLE_ID,
        filter_formula='({项目状态}="质保期")',
    )

    expiring = []
    overdue = []

    for rec in records:
        fields = rec.get("fields", {})
        warranty_date_str = fields.get("质保到期日")
        if not warranty_date_str:
            continue

        try:
            warranty_date = datetime.strptime(warranty_date_str[:10], "%Y-%m-%d").date()
        except ValueError:
            continue

        project_name = fields.get("项目名称", "未知项目")
        amount = fields.get("合同金额", 0)
        warranty_amount = amount * fields.get("质保金比例", 0.05)

        if warranty_date < today:
            overdue.append({
                "name": project_name,
                "date": warranty_date_str[:10],
                "amount": warranty_amount,
                "days": (today - warranty_date).days,
            })
        elif warranty_date <= warn_date:
            expiring.append({
                "name": project_name,
                "date": warranty_date_str[:10],
                "amount": warranty_amount,
                "days": (warranty_date - today).days,
            })

    if not expiring and not overdue:
        print("✅ 无即将到期或逾期的质保金项目")
        return

    _send_reminder(expiring, overdue)


def _send_reminder(expiring: list, overdue: list):
    """构建并发送钉钉提醒消息"""
    lines = ["## ⏰ 质保金到期提醒\n"]

    if overdue:
        lines.append(f"### 🔴 已逾期（{len(overdue)} 个项目）\n")
        for p in overdue:
            lines.append(
                f"- **{p['name']}** | 到期日：{p['date']} "
                f"| 已逾期 **{p['days']} 天** | 质保金约 ¥{p['amount']:,.0f}\n"
            )

    if expiring:
        lines.append(f"\n### 🟡 即将到期（{len(expiring)} 个项目，30天内）\n")
        for p in expiring:
            lines.append(
                f"- **{p['name']}** | 到期日：{p['date']} "
                f"| 剩余 **{p['days']} 天** | 质保金约 ¥{p['amount']:,.0f}\n"
            )

    lines.append("\n> 请项目经理及时跟进收款，如有疑问联系财务。")
    content = "".join(lines)

    success = client.send_robot_message(content, msg_type="markdown", title="质保金到期提醒")
    if success:
        print(f"✅ 提醒已发送：逾期 {len(overdue)} 个，即将到期 {len(expiring)} 个")
    else:
        print("❌ 消息发送失败，请检查 Webhook 配置")


if __name__ == "__main__":
    check_warranty_expiry()
