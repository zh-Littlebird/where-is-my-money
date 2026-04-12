# 交易搜索与管理

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

## 批量更新交易

通过 Python API 调用 `client.bulk_update_transactions(data)` 批量更新交易记录。
