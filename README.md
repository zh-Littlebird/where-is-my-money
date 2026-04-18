# Firefly III Billing Skill

[Firefly III](https://www.firefly-iii.org/) 记账技能，作为 [Claude Code](https://docs.anthropic.com/en/docs/claude-code) 的 custom skill 使用。支持**文本记账**和**图片记账**两种方式，自动提取交易信息并匹配账户、分类、标签等元数据，实现自然语言快速记账。

## 功能特性

- **文本记账**：用自然语言描述交易，如"刚打车花了 20"、"昨天在便利店买了饮料 5.6 元"
- **图片记账**：上传收据、发票、支付截图，自动识别并提取交易信息
- **交易管理**：查询、更新、删除交易记录
- **主数据管理**：账户、分类、预算、标签的显式增删改查
- **高级搜索**：支持多字段、布尔逻辑的搜索语法
- **账单管理**：管理周期性支出（房租、订阅等）
- **存钱罐**：管理储蓄目标
- **标签管理**：标签的增删改查
- **净资产查询**：查询指定日期的净资产快照
- **月度报告**：按分类、预算、标签、账户多维度汇总收支
- **趋势分析**：按月/季度/年展示多期收支净增长趋势

## 项目结构

```
firefly-iii-billing/
├── SKILL.md                    # Claude Code skill 定义文件
├── config.example.json         # 配置文件模板
├── config.json                 # 实际配置文件（已 gitignore）
├── scripts/
│   └── firefly_client.py       # Firefly III API 客户端
└── references/
    └── api_reference.md        # Firefly III API 参考文档
```

## 快速开始

### 前置条件

- Python 3.7+（无需额外依赖，仅使用标准库）
- 一个运行中的 [Firefly III](https://www.firefly-iii.org/) 实例
- Firefly III 的 Personal Access Token
- [Claude Code](https://docs.anthropic.com/en/docs/claude-code) CLI

### 安装配置

1. **克隆仓库**

   ```bash
   git clone https://github.com/your-username/firefly-iii-billing.git
   ```

2. **创建配置文件**

   ```bash
   cp config.example.json config.json
   ```

   编辑 `config.json`，填入你的 Firefly III 实例地址和 Access Token：

   ```json
   {
     "FIREFLY_III_BASE_URL": "https://your-firefly-instance.example.com/",
     "FIREFLY_III_ACCESS_TOKEN": "your-token-here",
     "FIREFLY_III_AUTO_CREATE_ACCOUNTS": true,
     "FIREFLY_III_AUTO_CREATE_CATEGORIES": true,
     "FIREFLY_III_AUTO_CREATE_TAGS": true,
     "FIREFLY_III_AUTO_CREATE_BUDGETS": true,
     "FIREFLY_III_AUTO_CREATE_PIGGY_BANKS": true
   }
   ```

   以上自动新建开关默认都为 `true`。设为 `false` 后，`FireflyClient` 会在代码层直接拒绝对应创建请求，以及会触发隐式新建的交易提交/更新请求。

3. **在 Claude Code 中注册 skill**

   将 `SKILL.md` 作为 Claude Code custom skill 加载即可使用。

## CLI 用法

`firefly_client.py` 也可以作为独立 CLI 工具使用：

```bash
# 获取记账元数据
python3 scripts/firefly_client.py list <TOKEN>

# 按时间范围列出交易
python3 scripts/firefly_client.py transactions <TOKEN> [START] [END] [TYPE]

# 提交交易
python3 scripts/firefly_client.py post <TOKEN> '<JSON_DATA>'

# 查看交易详情
python3 scripts/firefly_client.py get <TOKEN> <TRANSACTION_ID>

# 更新交易
python3 scripts/firefly_client.py update <TOKEN> <TRANSACTION_ID> '<JSON_DATA>'

# 删除交易
python3 scripts/firefly_client.py delete <TOKEN> <TRANSACTION_ID>

# 搜索交易
python3 scripts/firefly_client.py search <TOKEN> '<QUERY>'

# 列出账户
python3 scripts/firefly_client.py accounts <TOKEN> [TYPE]

# 账户主数据 CRUD
python3 scripts/firefly_client.py account-get <TOKEN> <ACCOUNT_ID>
python3 scripts/firefly_client.py account-create <TOKEN> '<JSON_DATA>'
python3 scripts/firefly_client.py account-update <TOKEN> <ACCOUNT_ID> '<JSON_DATA>'
python3 scripts/firefly_client.py account-delete <TOKEN> <ACCOUNT_ID>

# 分类主数据 CRUD
python3 scripts/firefly_client.py categories <TOKEN>
python3 scripts/firefly_client.py category-get <TOKEN> <CATEGORY_ID>
python3 scripts/firefly_client.py category-create <TOKEN> '<JSON_DATA>'
python3 scripts/firefly_client.py category-update <TOKEN> <CATEGORY_ID> '<JSON_DATA>'
python3 scripts/firefly_client.py category-delete <TOKEN> <CATEGORY_ID>

# 标签主数据 CRUD
python3 scripts/firefly_client.py tags <TOKEN>
python3 scripts/firefly_client.py tag-get <TOKEN> <TAG_OR_ID>
python3 scripts/firefly_client.py tag-create <TOKEN> '<JSON_DATA>'
python3 scripts/firefly_client.py tag-update <TOKEN> <TAG_OR_ID> '<JSON_DATA>'
python3 scripts/firefly_client.py tag-delete <TOKEN> <TAG_OR_ID>

# 基础汇总
python3 scripts/firefly_client.py summary <TOKEN> <START> <END> [CURRENCY_CODE]

# 列出预算及已花金额
python3 scripts/firefly_client.py budgets <TOKEN> [START] [END]

# 预算主数据 CRUD
python3 scripts/firefly_client.py budget-get <TOKEN> <BUDGET_ID>
python3 scripts/firefly_client.py budget-create <TOKEN> '<JSON_DATA>'
python3 scripts/firefly_client.py budget-update <TOKEN> <BUDGET_ID> '<JSON_DATA>'
python3 scripts/firefly_client.py budget-delete <TOKEN> <BUDGET_ID>

# 列出预算额度
python3 scripts/firefly_client.py budget-limits <TOKEN> <START> <END>

# 账户余额趋势
python3 scripts/firefly_client.py chart-account <TOKEN> <START> <END> [PERIOD]

# 支出分类洞察
python3 scripts/firefly_client.py insight-expense-category <TOKEN> <START> <END>

# 自动补全（Phase 2）
python3 scripts/firefly_client.py autocomplete <TOKEN> <RESOURCE_TYPE> '<QUERY>'

# 查看账单（Phase 2）
python3 scripts/firefly_client.py bills <TOKEN>

# 查看存钱罐（Phase 2）
python3 scripts/firefly_client.py piggybanks <TOKEN>

# 查询净资产便捷包装（Phase 2）
python3 scripts/firefly_client.py networth <TOKEN> [YYYY-MM-DD] [CURRENCY_CODE]

# 月度资金变动报告，本地聚合（Phase 2）
python3 scripts/firefly_client.py report <TOKEN> [YYYY-MM]

# 多期净增长趋势，本地聚合（Phase 2）
python3 scripts/firefly_client.py trend <TOKEN> [monthly|quarterly|yearly] [期数]
```

## Python API 用法

```python
from scripts.firefly_client import FireflyClient

# 从 config.json 初始化
client = FireflyClient.from_config()

# 读取自动新建配置
settings = FireflyClient.get_auto_create_settings()

# 获取元数据
metadata = client.list_metadata()

# 列出账户
accounts = client.list_accounts(account_type="asset")

# 账户 CRUD
account = client.get_account("123")
client.create_account('{"name":"Wallet","type":"asset"}')
client.update_account("123", '{"name":"Wallet 2"}')
client.delete_account("123")

# 分类 CRUD
categories = client.list_categories()
client.create_category('{"name":"Pets"}')
client.update_category("123", '{"name":"Pet Care"}')
client.delete_category("123")

# 读取基础汇总
summary = client.get_basic_summary("2026-04-01", "2026-04-18", "CNY")

# 读取账户趋势
chart = client.get_account_chart_overview("2026-01-01", "2026-04-18", period="1M")

# 标签 CRUD
tags = client.get_tags()
client.create_tag('{"tag":"coffee"}')
client.update_tag_payload("coffee", '{"tag":"coffee","description":"Cafe expenses"}')
client.delete_tag("coffee")

# 读取支出分类洞察
expense_by_category = client.get_expense_category_insight("2026-04-01", "2026-04-18")

# 提交交易
client.post_transactions('{"type":"withdrawal","amount":"25.50",...}')

# 预算与预算额度
budgets = client.list_budgets("2026-04-01", "2026-04-30")
budget = client.get_budget("123")
client.create_budget('{"name":"Food"}')
client.update_budget("123", '{"name":"Food 2026"}')
client.delete_budget("123")
budget_limits = client.list_budget_limits("2026-04-01", "2026-04-30")
```

## 安全说明

- `config.json` 包含敏感的 Access Token，已在 `.gitignore` 中排除
- 请勿将 Access Token 硬编码在代码中或提交到版本控制
- 建议定期轮换 Firefly III 的 Personal Access Token

## License

MIT
