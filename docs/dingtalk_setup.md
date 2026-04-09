# 钉钉应用配置指南

## 1. 创建钉钉内部应用

1. 登录 [钉钉开放平台](https://open.dingtalk.com/)
2. 进入「应用开发」→「企业内部应用」→「创建应用」
3. 记录 `AppKey` 和 `AppSecret`，填入 `.env`

**需要开通的权限点：**
- 通讯录只读权限
- 企业会话消息推送
- AI 表格读写权限（`apaas:aitable:*`）

---

## 2. 配置机器人 Webhook

1. 在目标钉钉群 → 「群设置」→「智能群助手」→「添加机器人」
2. 选择「自定义」，安全设置选「加签」
3. 复制 Webhook URL 和 Secret，填入 `.env`

---

## 3. 创建 AI 表格

按照 `scripts/init_tables.py` 输出的字段清单，在钉钉 AI 表格中依次创建：

| 表名 | 用途 |
|------|------|
| 项目合同表 | 项目全生命周期管理 |
| 收付款流水表 | 应收应付账款追踪 |
| CRM 客户表 | 市场部客户跟进 |

创建完成后，从表格 URL 中提取 `base_id` 和 `table_id`，填入 `.env`。

---

## 4. 配置定时任务

**macOS / Linux（crontab）：**

```bash
# 每天早上 9 点检查质保金
0 9 * * * /path/to/.venv/bin/python /path/to/src/automation/warranty_reminder.py

# 每月 1 日早上 8:30 推送月报
30 8 1 * * /path/to/.venv/bin/python /path/to/src/automation/monthly_report.py
```

**钉钉自动化流程（推荐，无需服务器）：**
- 在 AI 表格中配置「自动化」→「定时触发」
- 调用 Webhook 触发本地脚本或云函数
