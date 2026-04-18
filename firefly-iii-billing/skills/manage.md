# 交易查询与管理

## 列出交易

```bash
scripts/firefly_client.py transactions <TOKEN> [START] [END] [TYPE]
```

说明：
- `START` / `END` 使用 `YYYY-MM-DD`
- `TYPE` 可选，默认 `all`
- 如果想跳过 `START` 只传 `END`，CLI 中用 `-` 占位

适用场景：
- “列出本月所有交易”
- “查 2026-04-01 到 2026-04-18 的支出”
- 为分析前先拉原始流水

## 列出账户

```bash
scripts/firefly_client.py accounts <TOKEN> [TYPE]
```

适用场景：
- 查询当前账户列表
- 获取账户分析和净资产分析底座
- 限制账户类型时可传 `asset`、`liability`、`expense`、`revenue`

## 搜索交易

```bash
scripts/firefly_client.py search <TOKEN> '<QUERY>'
```

支持高级搜索语法：
- 文本搜索：`groceries`
- 字段搜索：`amount:>100`、`category:food`、`date:2024-01-01`
- 布尔逻辑：空格表示 AND，`OR` 关键字
- 精确匹配：`"monthly rent"`

适用场景：查重、回顾消费记录

## 交易管理

```bash
# 查看交易详情
scripts/firefly_client.py get <TOKEN> <TRANSACTION_ID>

# 更新交易
scripts/firefly_client.py update <TOKEN> <TRANSACTION_ID> '<JSON_DATA>'

# 删除交易
scripts/firefly_client.py delete <TOKEN> <TRANSACTION_ID>
```

## 自动补全

```bash
scripts/firefly_client.py autocomplete <TOKEN> <RESOURCE_TYPE> '<QUERY>'
```

支持的资源类型：`accounts`、`tags`、`categories`、`budgets`、`bills`、`piggy-banks`、`transactions`、`currencies`

比全量 `list` 更轻量，适合交互式模糊匹配。

> `autocomplete` 主要用于记账交互优化，不属于当前 MVP 核心分析链路。

## 批量更新交易

```bash
scripts/firefly_client.py bulk-update <TOKEN> '<JSON_DATA>'
```

适用场景：
- 批量修正账户、分类、预算、标签等字段
- 导入后集中整理一批历史流水

说明：
- 提交内容直接透传到 `POST /v1/data/bulk/transactions`
- 创建新交易仍使用 `post`，这里仅用于批量更新已有交易

## 预算相关交易查询

```bash
scripts/firefly_client.py budget-transactions <TOKEN> <BUDGET_ID> [START] [END] [TYPE]
scripts/firefly_client.py budget-limit-transactions <TOKEN> <BUDGET_ID> <LIMIT_ID>
scripts/firefly_client.py transactions-without-budget <TOKEN> [START] [END] [TYPE]
```

适用场景：
- 查询某个预算下的全部交易
- 追查某个预算额度分段内为什么超支
- 查找没有挂预算的支出，补齐漏配数据

说明：
- `budget-transactions` 支持按日期和交易类型过滤
- `budget-limit-transactions` 直接对应某条预算额度，不再额外传时间范围
- `transactions-without-budget` 适合和 `insight expense no-budget` 配合：前者看明细，后者看聚合
