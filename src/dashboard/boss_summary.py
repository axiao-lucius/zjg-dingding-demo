"""
老板驾驶舱 — 实时数据汇总
按需触发或每日定时推送，一条消息掌握公司全貌
"""
import os
import sys
from datetime import datetime, date

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../.."))
from src.api.dingtalk_client import client
from dotenv import load_dotenv

load_dotenv()

BASE_ID = os.getenv("AITABLE_BASE_ID")
PROJECT_TABLE_ID = os.getenv("PROJECT_TABLE_ID")
FINANCE_TABLE_ID = os.getenv("FINANCE_TABLE_ID")
CRM_TABLE_ID = os.getenv("CRM_TABLE_ID")
BOSS_USER_ID = os.getenv("BOSS_USER_ID")


def build_dashboard():
    """汇总关键指标，推送老板驾驶舱"""
    today = date.today()
    today_str = today.strftime("%Y-%m-%d")
    month_start = today.strftime("%Y-%m-01")

    # ── 项目数据 ──────────────────────────────────────────
    projects = client.aitable_list_records(BASE_ID, PROJECT_TABLE_ID)
    active = [p for p in projects if p["fields"].get("项目状态") in ("施工中", "质保期")]
    pending_start = [p for p in projects if p["fields"].get("项目状态") == "待开工"]
    overdue_warranty = [
        p for p in projects
        if p["fields"].get("项目状态") == "质保期"
        and (p["fields"].get("质保到期日") or "9999")[:10] < today_str
    ]

    # ── 财务数据 ──────────────────────────────────────────
    finances = client.aitable_list_records(BASE_ID, FINANCE_TABLE_ID)

    month_income = sum(
        r["fields"].get("金额", 0) for r in finances
        if r["fields"].get("收/付") == "收款"
        and r["fields"].get("状态") == "已到账"
        and (r["fields"].get("实际到账日") or "")[:7] == today_str[:7]
    )
    total_receivable = sum(
        r["fields"].get("金额", 0) for r in finances
        if r["fields"].get("收/付") == "收款"
        and r["fields"].get("状态") == "待收/付"
    )
    pending_warranty_amt = sum(
        r["fields"].get("金额", 0) for r in finances
        if r["fields"].get("款项类型") == "质保金"
        and r["fields"].get("状态") == "待收/付"
    )
    overdue_finance = [r for r in finances if r["fields"].get("状态") == "逾期"]

    # ── CRM 数据 ──────────────────────────────────────────
    crm = client.aitable_list_records(BASE_ID, CRM_TABLE_ID)
    active_leads = [c for c in crm if c["fields"].get("跟进状态") in ("需求确认", "报价中", "合同谈判")]

    # ── 构建消息 ──────────────────────────────────────────
    warn_lines = []
    if overdue_warranty:
        warn_lines.append(f"🔴 质保金逾期未收：**{len(overdue_warranty)} 个项目**")
    if overdue_finance:
        warn_lines.append(f"🟠 逾期款项：**{len(overdue_finance)} 笔**，请财务跟进")

    warn_block = "\n".join(warn_lines) if warn_lines else "✅ 无异常预警"

    dashboard = f"""## 📊 紫金港达美 · 实时驾驶舱
**更新时间：** {datetime.now().strftime('%Y-%m-%d %H:%M')}

---

### 🏗️ 项目概况
- 在建项目：**{len(active)} 个**
- 待开工：{len(pending_start)} 个
- 商机跟进中（CRM）：{len(active_leads)} 个

### 💰 财务概况
- 本月已收款：**¥{month_income:,.0f}**
- 应收账款合计：¥{total_receivable:,.0f}
- 待收质保金：¥{pending_warranty_amt:,.0f}

### ⚠️ 预警事项
{warn_block}

---
> 数据来源：钉钉 AI 表格 · 实时同步
"""

    # 推送老板工作通知
    if BOSS_USER_ID:
        client.send_work_notification(BOSS_USER_ID, "实时驾驶舱", dashboard)

    # 推送群
    client.send_robot_message(dashboard, msg_type="markdown", title="老板驾驶舱")
    print("✅ 驾驶舱数据已推送")


if __name__ == "__main__":
    build_dashboard()
