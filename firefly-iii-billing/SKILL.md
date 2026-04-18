---
name: firefly-iii-billing
description: 当用户需要根据文字或图片记账，或查询、修改、分析个人财务数据时使用。支持交易录入、交易查询、主数据管理（账户/分类/预算/标签）、预算闭环分析（额度、余额、明细、漏记）、账户与预算分析、支出分类洞察；账单、存钱罐、标签、附件等扩展能力归入第二阶段。
---

# Firefly III 记账技能

## 触发场景

- 用户用文字描述交易：如"刚打车花了20"、"昨天在便利店买了饮料5.6元"
- 用户上传交易图片：收据、发票、支付截图、账单等
- 用户查询或管理已有交易、账户、预算、分类分析数据

## MVP 工具概览

| CLI 命令 | 用途 |
|----------|------|
| `scripts/firefly_client.py list <TOKEN>` | 获取记账所需元数据：账户/分类/标签/预算 |
| `scripts/firefly_client.py transactions <TOKEN> [START] [END] [TYPE]` | 按时间范围列出交易 |
| `scripts/firefly_client.py post <TOKEN> '<JSON>'` | 提交交易（支持 JSON 字符串或文件路径） |
| `scripts/firefly_client.py get <TOKEN> <ID>` | 查看交易详情 |
| `scripts/firefly_client.py update <TOKEN> <ID> '<JSON>'` | 更新交易 |
| `scripts/firefly_client.py delete <TOKEN> <ID>` | 删除交易 |
| `scripts/firefly_client.py search <TOKEN> '<QUERY>'` | 搜索交易 |
| `scripts/firefly_client.py accounts <TOKEN> [TYPE]` | 列出账户，作为净资产和账户分析底座 |
| `scripts/firefly_client.py account-get/create/update/delete ...` | 账户主数据 CRUD |
| `scripts/firefly_client.py categories <TOKEN>` | 列出分类 |
| `scripts/firefly_client.py category-get/create/update/delete ...` | 分类主数据 CRUD |
| `scripts/firefly_client.py tags <TOKEN>` | 列出标签 |
| `scripts/firefly_client.py tag-get/create/update/delete ...` | 标签主数据 CRUD |
| `scripts/firefly_client.py summary <TOKEN> <START> <END> [CURRENCY_CODE]` | 获取基础汇总，直接对应 `summary/basic` |
| `scripts/firefly_client.py budgets <TOKEN> [START] [END]` | 列出预算及预算区间内已花金额 |
| `scripts/firefly_client.py budget-get/create/update/delete ...` | 预算主数据 CRUD |
| `scripts/firefly_client.py available-budgets <TOKEN> [START] [END]` | 列出可用预算余额及对应周期 |
| `scripts/firefly_client.py available-budget-get <TOKEN> <ID>` | 查看单个可用预算 |
| `scripts/firefly_client.py budget-limits <TOKEN> <START> <END>` | 按时间范围列出预算额度明细 |
| `scripts/firefly_client.py budget-limit-list/get/create/update/delete ...` | 某预算下的额度明细 CRUD |
| `scripts/firefly_client.py budget-transactions <TOKEN> <BUDGET_ID> ...` | 查看某预算下交易明细 |
| `scripts/firefly_client.py budget-limit-transactions <TOKEN> <BUDGET_ID> <LIMIT_ID>` | 查看某预算区间下交易，定位超支原因 |
| `scripts/firefly_client.py transactions-without-budget <TOKEN> ...` | 查看未挂预算的交易，定位漏记 |
| `scripts/firefly_client.py chart-account <TOKEN> <START> <END> [PERIOD]` | 获取账户余额趋势图数据 |
| `scripts/firefly_client.py insight <TOKEN> <SCOPE> <GROUP> <START> <END> [FILTER_IDS] [ACCOUNT_IDS]` | 获取完整官方洞察矩阵：支出/收入/转账，支持按分类/预算/标签/账单/账户/总额聚合 |
| `scripts/firefly_client.py insight-expense-category <TOKEN> <START> <END> [CATEGORY_IDS] [ACCOUNT_IDS]` | 支出分类洞察兼容快捷命令 |

## Phase 2 工具

这些能力保留，但不属于当前 agent MVP 主链路：

| CLI 命令 | 用途 |
|----------|------|
| `scripts/firefly_client.py autocomplete <TOKEN> <TYPE> '<QUERY>'` | 自动补全（交互优化，不是核心分析接口） |
| `scripts/firefly_client.py bills <TOKEN>` | 查看所有账单 |
| `scripts/firefly_client.py bill-get/create/update/delete ...` | 账单主数据 CRUD |
| `scripts/firefly_client.py piggybanks <TOKEN>` | 查看所有存钱罐 |
| `scripts/firefly_client.py piggybank-get/create/update/delete ...` | 存钱罐主数据 CRUD |
| `scripts/firefly_client.py attachment-create/upload ...` | 创建附件并上传交易凭证 |
| `scripts/firefly_client.py bulk-update <TOKEN> '<JSON>'` | 批量更新交易 |
| `scripts/firefly_client.py networth <TOKEN> [YYYY-MM-DD] [CURRENCY_CODE]` | 净资产便捷包装，底层仍是 `summary/basic` |
| `scripts/firefly_client.py report <TOKEN> [YYYY-MM]` | 本地聚合月报 |
| `scripts/firefly_client.py trend <TOKEN> [粒度] [期数]` | 本地聚合趋势分析 |

> **配置来源**：从 `config.json` 中读取 `FIREFLY_III_ACCESS_TOKEN` 及自动新建开关。若未显式配置，账户、分类、标签、预算、存钱罐的自动新建默认均为 `true`。

## 按需加载指引

根据用户意图，使用 Read 工具加载对应的子文件获取详细流程：

| 用户意图 | 加载文件 |
|----------|----------|
| 记账（文字/图片描述交易） | `skills/record.md` |
| 交易查询、编辑、账户列表 | `skills/manage.md` |
| 主数据管理（账户/分类/预算/标签） | `skills/masterdata.md` |
| 汇总、预算、分类洞察、账户趋势 | `skills/report.md` |
| 账单、存钱罐、标签、附件（第二阶段） | `skills/finance.md` |

> **⚠️ 重要**：识别用户意图后，**必须先加载对应子文件**再执行操作。子文件包含完整的流程步骤、格式模板和业务规则。

## 隐私保护规则

⚠️ **严禁将生活类交易记录到项目进展日志**

生活类交易（餐饮、购物、日常消费等）属于个人隐私，严禁调用其他技能写入任何项目报告或日志。此类信息仅保留在 Firefly III 系统内。

## 配置说明

配置文件：`config.json`

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

新环境请参考 `config.example.json` 创建配置文件。

自动新建开关说明：

- `FIREFLY_III_AUTO_CREATE_ACCOUNTS`：找不到匹配账户时是否允许自动新建
- `FIREFLY_III_AUTO_CREATE_CATEGORIES`：找不到匹配分类时是否允许自动新建
- `FIREFLY_III_AUTO_CREATE_TAGS`：找不到匹配标签时是否允许自动新建
- `FIREFLY_III_AUTO_CREATE_BUDGETS`：找不到匹配预算时是否允许自动新建
- `FIREFLY_III_AUTO_CREATE_PIGGY_BANKS`：找不到匹配存钱罐时是否允许自动新建

以上配置默认均为 `true`；设为 `false` 时，`FireflyClient` 会在代码层强制拦截交易提交/更新中会触发隐式新建的引用，不能仅靠提示词绕过。

这些开关约束的是“自动新建”行为，不是用户明确要求的主数据维护动作。若用户明确要求新建账户、分类、标签、预算或存钱罐，可走对应显式创建命令。

执行规则：

- 任一自动新建开关为 `false` 时，模型必须先读取对应已有列表，再从列表中选择，不能直接使用新的账户、分类、标签、预算或存钱罐名称
- 账户/分类/标签/预算优先使用 `list`，候选过多时使用 `autocomplete`
- 存钱罐优先使用 `piggybanks`，候选过多时使用 `autocomplete piggy-banks`
- 若现有列表中没有合适项，先向用户展示可选项并请其改选或调整配置，不要继续提交会失败的请求

## 故障排除

| 问题 | 解决方案 |
|------|---------|
| 图片模糊无法识别 | 请求用户提供清晰图片 |
| 账户/分类/标签/预算/存钱罐不存在 | 根据自动新建开关处理；开关为 `false` 时必须先向用户确认 |
| 交易类型判断困难 | 根据上下文判断（如基金买卖是转账） |
| 时间信息缺失 | 基于当前时间解析相对表达，无法确定时向用户询问 |
| HTTP Error | 检查 Token 是否过期或 Firefly III 服务是否可用 |
| 重复交易 | 使用 `search` 先查重，`error_if_duplicate_hash` 默认关闭 |
