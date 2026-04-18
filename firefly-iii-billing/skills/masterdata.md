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

# 可用预算
scripts/firefly_client.py available-budgets <TOKEN> [START] [END]
scripts/firefly_client.py available-budget-get <TOKEN> <AVAILABLE_BUDGET_ID>

# 预算额度明细
scripts/firefly_client.py budget-limit-list <TOKEN> <BUDGET_ID> [START] [END]
scripts/firefly_client.py budget-limit-get <TOKEN> <BUDGET_ID> <LIMIT_ID>
scripts/firefly_client.py budget-limit-create <TOKEN> <BUDGET_ID> '<JSON_DATA>'
scripts/firefly_client.py budget-limit-update <TOKEN> <BUDGET_ID> <LIMIT_ID> '<JSON_DATA>'
scripts/firefly_client.py budget-limit-delete <TOKEN> <BUDGET_ID> <LIMIT_ID>
```

说明：
- `budgets` 带日期时会返回该时间段已花金额
- `budget-get` / `budget-update` / `budget-delete` 面向预算定义本身
- `available-budgets` 面向 Firefly III 计算出的可用预算金额
- `budget-limits` 是跨预算、按日期范围的额度总表
- `budget-limit-list/get/create/update/delete` 面向某个预算下面的额度分段明细
- 关闭预算的自动月预算时，不要把 `auto_budget_type` / `auto_budget_period` / `auto_budget_amount` 直接传 `null` 或把金额设为 `0`，Firefly III 常会返回 `422`
- 实测可用写法：`budget-update` 时传 `auto_budget_type: "none"`，同时保留一个大于 `0` 的 `auto_budget_amount` 与原 `auto_budget_period`；接口会在保存后把这三个字段清成 `null`，从而真正关闭自动预算
- 若是新建预算额度 `budget-limit-create`，`currency_id` 应传整数而不是字符串；字符串在部分 Firefly III 版本会触发 `500`

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
