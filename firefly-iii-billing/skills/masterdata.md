# 主数据管理

本文件覆盖交易依赖的核心主数据：账户、分类、预算、标签。目标是补足显式 CRUD 能力，不改变原有记账、查询、分析链路。

## 使用原则

- 保持原有交易命令和分析命令不变
- 自动新建开关约束的是交易流程里的隐式新建，不拦截用户明确要求的主数据创建
- 更新和删除属于显式维护操作，执行前应向用户确认对象和影响范围

## 账户

```bash
# 列表
scripts/firefly_client.py accounts <TOKEN> [TYPE]

# 详情
scripts/firefly_client.py account-get <TOKEN> <ACCOUNT_ID>

# 创建
scripts/firefly_client.py account-create <TOKEN> '<JSON_DATA>'

# 更新
scripts/firefly_client.py account-update <TOKEN> <ACCOUNT_ID> '<JSON_DATA>'

# 删除
scripts/firefly_client.py account-delete <TOKEN> <ACCOUNT_ID>
```

适用场景：
- “新建一个招商银行储蓄卡账户”
- “把这个信用卡账户改名”
- “删除废弃账户”

## 分类

```bash
# 列表
scripts/firefly_client.py categories <TOKEN>

# 详情
scripts/firefly_client.py category-get <TOKEN> <CATEGORY_ID>

# 创建
scripts/firefly_client.py category-create <TOKEN> '<JSON_DATA>'

# 更新
scripts/firefly_client.py category-update <TOKEN> <CATEGORY_ID> '<JSON_DATA>'

# 删除
scripts/firefly_client.py category-delete <TOKEN> <CATEGORY_ID>
```

适用场景：
- “新增一个宠物分类”
- “把旧分类合并前先改名”
- “清理不再使用的分类”

## 预算

```bash
# 列表
scripts/firefly_client.py budgets <TOKEN> [START] [END]

# 详情
scripts/firefly_client.py budget-get <TOKEN> <BUDGET_ID>

# 创建
scripts/firefly_client.py budget-create <TOKEN> '<JSON_DATA>'

# 更新
scripts/firefly_client.py budget-update <TOKEN> <BUDGET_ID> '<JSON_DATA>'

# 删除
scripts/firefly_client.py budget-delete <TOKEN> <BUDGET_ID>
```

说明：
- `budgets` 带日期时会返回该时间段已花金额
- `budget-get` / `budget-update` / `budget-delete` 面向预算定义本身
- 预算额度仍使用 `budget-limits`

## 标签

```bash
# 列表
scripts/firefly_client.py tags <TOKEN>

# 详情
scripts/firefly_client.py tag-get <TOKEN> <TAG_OR_ID>

# 创建
scripts/firefly_client.py tag-create <TOKEN> '<JSON_DATA>'

# 更新
scripts/firefly_client.py tag-update <TOKEN> <TAG_OR_ID> '<JSON_DATA>'

# 删除
scripts/firefly_client.py tag-delete <TOKEN> <TAG_OR_ID>
```

说明：
- Firefly III 标签接口支持传标签名或标签 ID
- 传标签名时若包含非 ASCII 字符，优先改用 ID，避免编码问题

## JSON 提交约定

- 创建和更新命令均支持 JSON 字符串或 JSON 文件路径
- 具体字段以 Firefly III `v1` API 为准
- 对象不确定时，先调用列表或详情命令，不要盲改盲删
