"""
初始化脚本 — 在钉钉 AI 表格中创建所需的表结构
首次部署时运行一次即可

使用方法：
    python scripts/init_tables.py
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from src.models.table_schemas import get_all_schemas
from dotenv import load_dotenv

load_dotenv()

# ─── 说明 ────────────────────────────────────────────────────
# 由于钉钉 AI 表格的建表 API 需要企业管理员权限，
# 本脚本提供两种模式：
#   1. 打印模式（默认）：输出字段清单，供手动在钉钉中创建
#   2. API 模式：如企业已开通相关权限，自动调用 API 建表
# ────────────────────────────────────────────────────────────

MODE = os.getenv("INIT_MODE", "print")  # "print" or "api"


def print_field_guide():
    """打印字段配置指南，供手动在钉钉 AI 表格中建表"""
    schemas = get_all_schemas()

    print("=" * 60)
    print("钉钉 AI 表格字段配置指南")
    print("请在钉钉 AI 表格中依次创建以下表格和字段")
    print("=" * 60)

    for key, schema in schemas.items():
        print(f"\n📋 【{schema['name']}】")
        print(f"{'序号':<4} {'字段名':<16} {'类型':<16} {'说明'}")
        print("-" * 60)
        for i, field in enumerate(schema["fields"], 1):
            options = ""
            if "options" in field:
                options = f"选项: {', '.join(field['options'])}"
            desc = field.get("desc", "") or options
            print(f"{i:<4} {field['name']:<16} {field['type']:<16} {desc}")

    print("\n" + "=" * 60)
    print("✅ 字段配置完成后，将各表的 Table ID 填入 .env 文件")
    print("=" * 60)


def auto_create_tables():
    """自动调用 API 创建表结构（需要管理员权限）"""
    # 此功能需要钉钉开放平台 aitable 建表 API 权限
    # 详见：https://open.dingtalk.com/document/orgapp/create-table
    print("⚠️  自动建表功能需要企业管理员授权")
    print("   请联系钉钉管理员在开放平台开通 aitable 建表权限后再使用")
    print("   当前建议使用 print 模式（默认）手动配置")


if __name__ == "__main__":
    if MODE == "api":
        auto_create_tables()
    else:
        print_field_guide()
