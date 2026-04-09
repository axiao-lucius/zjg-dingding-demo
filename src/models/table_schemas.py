"""
AI 表格字段定义
对应钉钉 AI 表格中各张表的字段结构
"""

# ─── 项目合同表 ────────────────────────────────────────────────
PROJECT_TABLE_FIELDS = [
    {"name": "项目编号",       "type": "Text",       "desc": "自动生成，格式 ZJG-2026-001"},
    {"name": "项目名称",       "type": "Text",       "desc": "例：瑞幸咖啡深业上城店装修"},
    {"name": "客户名称",       "type": "Text",       "desc": "关联 CRM 客户表"},
    {"name": "合同金额",       "type": "Currency",   "desc": "含税总价，单位元"},
    {"name": "合同签订日期",   "type": "Date",       "desc": ""},
    {"name": "预计开工日期",   "type": "Date",       "desc": ""},
    {"name": "预计竣工日期",   "type": "Date",       "desc": ""},
    {"name": "实际竣工日期",   "type": "Date",       "desc": ""},
    {"name": "项目状态",       "type": "SingleSelect",
     "options": ["待开工", "施工中", "已竣工", "质保期", "已结案"],
     "desc": ""},
    {"name": "项目经理",       "type": "Member",     "desc": "负责人钉钉账号"},
    {"name": "质保金比例",     "type": "Percent",    "desc": "通常 5%"},
    {"name": "质保到期日",     "type": "Date",       "desc": "竣工日 + 质保期（月）"},
    {"name": "备注",           "type": "LongText",   "desc": ""},
]

# ─── 收付款流水表 ──────────────────────────────────────────────
FINANCE_TABLE_FIELDS = [
    {"name": "流水编号",   "type": "Text",         "desc": "自动生成"},
    {"name": "关联项目",   "type": "Text",         "desc": "关联项目编号"},
    {"name": "款项类型",   "type": "SingleSelect",
     "options": ["预付款", "进度款", "尾款", "质保金", "材料付款", "分包付款"],
     "desc": ""},
    {"name": "收/付",      "type": "SingleSelect", "options": ["收款", "付款"], "desc": ""},
    {"name": "金额",       "type": "Currency",     "desc": ""},
    {"name": "计划日期",   "type": "Date",         "desc": ""},
    {"name": "实际到账日", "type": "Date",         "desc": ""},
    {"name": "状态",       "type": "SingleSelect",
     "options": ["待收/付", "已到账", "逾期", "已开票"],
     "desc": ""},
    {"name": "发票号",     "type": "Text",         "desc": ""},
    {"name": "备注",       "type": "LongText",     "desc": ""},
]

# ─── CRM 客户表 ────────────────────────────────────────────────
CRM_TABLE_FIELDS = [
    {"name": "客户名称",     "type": "Text",         "desc": "如：瑞幸咖啡（华南区）"},
    {"name": "客户类型",     "type": "SingleSelect",
     "options": ["餐饮连锁", "商业综合体", "其他"],
     "desc": ""},
    {"name": "关键联系人",   "type": "Text",         "desc": "姓名+职位"},
    {"name": "联系方式",     "type": "Text",         "desc": "手机/企业微信"},
    {"name": "跟进状态",     "type": "SingleSelect",
     "options": ["初步接触", "需求确认", "报价中", "合同谈判", "已签约", "暂停"],
     "desc": ""},
    {"name": "最近跟进日期", "type": "Date",         "desc": ""},
    {"name": "跟进记录",     "type": "LongText",     "desc": "每次沟通追加记录"},
    {"name": "负责BD",       "type": "Member",       "desc": "市场部负责人"},
]


def get_all_schemas() -> dict:
    """返回所有表结构定义"""
    return {
        "project": {"name": "项目合同表", "fields": PROJECT_TABLE_FIELDS},
        "finance": {"name": "收付款流水表", "fields": FINANCE_TABLE_FIELDS},
        "crm":     {"name": "CRM客户表",   "fields": CRM_TABLE_FIELDS},
    }
