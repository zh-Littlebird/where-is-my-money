# 交易查询与管理

本模块处理“查、搜、改、删、账户列表”这类已存在数据的操作。凡是更新或删除，都先拿到真实交易组 ID，再执行。

## 列出交易

```bash
python3 scripts/firefly_client.py transactions [START] [END] [TYPE]
```

参数规则：
- `START`：可选，开始日期，格式必须是 `YYYY-MM-DD`。
- `END`：可选，结束日期，格式必须是 `YYYY-MM-DD`。
- `TYPE`：可选，默认 `all`。常用值：`all`、`withdrawal`、`deposit`、`transfer`。
- 如果想跳过 `START` 只传 `END`，CLI 中必须用 `-` 占位。

适用场景：
- “列出本月所有交易”
- “查 2026-04-01 到 2026-04-18 的支出”
- 为分析前先拉原始流水

## 列出账户

```bash
python3 scripts/firefly_client.py accounts [TYPE]
```

适用场景：
- 查询当前账户列表
- 获取账户分析和净资产分析底座
- 限制账户类型时可传 `asset`、`liability`、`expense`、`revenue`

## 搜索交易

```bash
python3 scripts/firefly_client.py search '<QUERY>'
```

参数规则：
- `QUERY`：必填，搜索表达式，建议整体用单引号包住。
- CLI 当前固定使用 Firefly 的默认分页参数：`page=1`、`limit=50`；这两个参数没有暴露为命令行参数。

支持高级搜索语法：
- 文本搜索：`groceries`
- 字段搜索：`amount:>100`、`category:food`、`date:2024-01-01`
- 布尔逻辑：空格表示 AND，`OR` 关键字
- 精确匹配：`"monthly rent"`

适用场景：查重、回顾消费记录

## 交易管理

```bash
# 查看交易详情
python3 scripts/firefly_client.py get <TRANSACTION_ID>

# 更新交易
python3 scripts/firefly_client.py update <TRANSACTION_ID> '<JSON_DATA>'

# 删除交易
python3 scripts/firefly_client.py delete <TRANSACTION_ID>
```

参数规则：
- `TRANSACTION_ID`：必填，指交易组 ID，也就是接口返回里的顶层 `data.id`；不是 split 内部的 `transaction_journal_id`。
- `JSON_DATA`：仅 `update` 需要。可以是 JSON 字符串，或一个本地 JSON 文件路径。

`get` 请求规则：
- 只接受 `TRANSACTION_ID`。
- 返回的是整笔交易组，里面包含一个或多个 split，真正可修改的是 `attributes.transactions[]` 里的 split 字段。

`delete` 请求规则：
- 只接受 `TRANSACTION_ID`。
- 删除的是整个交易组，不是单个 split。

`update` 请求规则：
- `JSON_DATA` 传给 CLI 时，顶层必须是“单个 split 对象”或“split 对象数组”。
- 不要把 `JSON_DATA` 再包成 `{"transactions":[...]}`，CLI 会自行包一层；你手工再包一次会形成错误层级。
- 单 split 更新时，可以只传一个对象。
- 多 split 更新时，必须传数组，并且每个 split 都必须带 `transaction_journal_id`；缺任何一个都不要提交。
- 只要是改分类、预算、账户、金额这类核心字段，推荐先 `get` 原交易，再用原 split 拼出完整 payload 回写，不要依赖最小局部更新。

`update` 可写字段规则：
- 预算优先传 `budget_id`。这是最稳定的写法。
- 不要依赖 `budget_name` 改预算。Firefly 的 update schema 中这个字段是只读返回值，常见现象是请求成功但预算不变。
- 分类优先传 `category_id`。
- `category_name` 理论上可写，但稳定性不如 `category_id`；如果同时传 `category_id` 和 `category_name`，以 `category_id` 为准。
- 账户优先传 `source_id` / `destination_id`，不要混用不存在的名称。
- `tags` 必须是字符串数组，不是标签 ID 数组。
- `date` 必须是带时区的 ISO 8601，如 `2026-04-18T09:30:00+08:00`。
- `amount` 必须是字符串金额，如 `"50.00"`，不要传数值类型。
- 如果是为了“只改预算/分类”，也建议一并带上原来的 `type`、`date`、`amount`、`description`、`source_id`、`destination_id`，避免 Firefly 静默忽略字段。

推荐的单 split 更新 payload：

```json
{
  "type": "withdrawal",
  "date": "2026-04-18T09:30:00+08:00",
  "amount": "50.00",
  "description": "示例消费",
  "source_id": "SOURCE_ACCOUNT_ID",
  "destination_id": "DESTINATION_ACCOUNT_ID",
  "category_id": "CATEGORY_ID",
  "budget_id": "BUDGET_ID",
  "tags": ["example-tag"],
  "notes": "Auto-synced by Clawdbot from text"
}
```

## 自动补全

```bash
python3 scripts/firefly_client.py autocomplete <RESOURCE_TYPE> '<QUERY>'
```

参数规则：
- `RESOURCE_TYPE`：必填，可选值：`accounts`、`tags`、`categories`、`budgets`、`bills`、`piggy-banks`、`transactions`、`currencies`。
- `QUERY`：必填，模糊匹配关键字，建议整体用单引号包住。
- CLI 默认 `limit=10`，命令行未暴露自定义 limit。

支持的资源类型：`accounts`、`tags`、`categories`、`budgets`、`bills`、`piggy-banks`、`transactions`、`currencies`

比全量 `list` 更轻量，适合交互式模糊匹配。

> `autocomplete` 主要用于记账交互优化，不属于当前 MVP 核心分析链路。

## 批量更新交易

```bash
python3 scripts/firefly_client.py bulk-update '<JSON_DATA>'
```

参数规则：
- `JSON_DATA`：必填，可以是 JSON 字符串或本地 JSON 文件路径。
- 顶层必须是对象或对象数组，每个对象都必须同时包含 `where` 和 `update`。
- 当前只允许 `where.account_id` 和 `update.account_id`。
- 不支持 `category_id`、`budget_id`、`tags`、`amount` 等字段的批量改动。

适用场景：
- 仅用于把一批交易上的账户 ID 从 A 改到 B
- 导入后集中整理一批历史流水

说明：
- 该端点当前只支持 `where.account_id` / `update.account_id`
- 不支持批量修改分类、预算、标签；这些需求不要走 `bulk-update`
- 创建新交易仍使用 `post`，这里仅用于批量更新已有交易

## 更新拆分交易

- 若一次 `update` 请求里包含多个 split，必须为每个 split 提交 `transaction_journal_id`
- 少任何一个 split 的 `transaction_journal_id` 都不要提交，否则 Firefly III 可能删除原 split 或把修改当成新 split 创建

## 预算相关交易查询

```bash
python3 scripts/firefly_client.py budget-transactions <BUDGET_ID> [START] [END] [TYPE]
python3 scripts/firefly_client.py budget-limit-transactions <BUDGET_ID> <LIMIT_ID>
python3 scripts/firefly_client.py transactions-without-budget [START] [END] [TYPE]
```

参数规则：
- `BUDGET_ID`：必填，预算 ID，不是预算名。
- `LIMIT_ID`：仅 `budget-limit-transactions` 需要，必填，对应预算额度分段 ID。
- `START` / `END`：可选，格式必须是 `YYYY-MM-DD`。
- `TYPE`：可选，常用值 `withdrawal`；不限制时可省略，或在 CLI 中传 `-` 占位。

适用场景：
- 查询某个预算下的全部交易
- 追查某个预算额度分段内为什么超支
- 查找没有挂预算的支出，补齐漏配数据

说明：
- `budget-transactions` 支持按日期和交易类型过滤
- `budget-limit-transactions` 直接对应某条预算额度，不再额外传时间范围
- `transactions-without-budget` 适合和 `insight expense no-budget` 配合：前者看明细，后者看聚合
