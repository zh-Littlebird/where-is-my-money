---
name: firefly-iii-billing
description: 当用户需要根据文字或图片记账，或查询、修改、分析个人财务数据时使用。支持单笔、多笔和拆分交易录入，匹配账户、预算、分类、标签等元数据，并提供交易管理、自动补全、账单、存钱罐、标签、附件、月度报表和收支趋势分析。
---

# Firefly III 记账技能

## 触发场景

- 用户用文字描述交易：如"刚打车花了20"、"昨天在便利店买了饮料5.6元"
- 用户上传交易图片：收据、发票、支付截图、账单等
- 用户查询或管理已有交易、账单、存钱罐、标签等

## 工具概览

| CLI 命令 | 用途 |
|----------|------|
| `scripts/firefly_client.py list <TOKEN>` | 获取账户/分类/标签/预算元数据 |
| `scripts/firefly_client.py post <TOKEN> '<JSON>'` | 提交交易（支持 JSON 字符串或文件路径） |
| `scripts/firefly_client.py get <TOKEN> <ID>` | 查看交易详情 |
| `scripts/firefly_client.py update <TOKEN> <ID> '<JSON>'` | 更新交易 |
| `scripts/firefly_client.py delete <TOKEN> <ID>` | 删除交易 |
| `scripts/firefly_client.py search <TOKEN> '<QUERY>'` | 搜索交易 |
| `scripts/firefly_client.py autocomplete <TOKEN> <TYPE> '<QUERY>'` | 自动补全（轻量模糊匹配） |
| `scripts/firefly_client.py bills <TOKEN>` | 查看所有账单 |
| `scripts/firefly_client.py piggybanks <TOKEN>` | 查看所有存钱罐 |
| `scripts/firefly_client.py report <TOKEN> [YYYY-MM]` | 月度资金变动报告（默认当月） |
| `scripts/firefly_client.py trend <TOKEN> [粒度] [期数]` | 多期净增长趋势（粒度: monthly/quarterly/yearly，默认 monthly 6 期） |

> **配置来源**：从 `config.json` 中读取 `FIREFLY_III_ACCESS_TOKEN` 及自动新建开关。若未显式配置，账户、分类、标签、预算、存钱罐的自动新建默认均为 `true`。

## 按需加载指引

根据用户意图，使用 Read 工具加载对应的子文件获取详细流程：

| 用户意图 | 加载文件 |
|----------|----------|
| 记账（文字/图片描述交易） | `skills/record.md` |
| 搜索/查看/修改/删除交易 | `skills/manage.md` |
| 账单/存钱罐/标签/附件 | `skills/finance.md` |
| 月度报告/收支趋势 | `skills/report.md` |

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

以上配置默认均为 `true`；设为 `false` 时，`FireflyClient` 会在代码层强制拦截对应新建请求，以及会导致隐式新建的交易提交/更新请求，不能仅靠提示词绕过。

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
