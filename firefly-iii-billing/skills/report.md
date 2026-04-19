# 分析与预算

本文件只描述当前 agent MVP 直接依赖的分析接口。优先使用官方 API 返回的结果，不要先用本地聚合替代。

分析类请求先判断用户要的是“总览数字”“分组洞察”“预算额度/余额”“异常明细回查”中的哪一种，再选命令，不要上来就拉全量交易。

## 基础汇总

```bash
python3 scripts/firefly_client.py summary <START> <END> [CURRENCY_CODE]
```

对应接口：
- `GET /v1/summary/basic`

适用场景：
- “这个月总共花了多少 / 赚了多少”
- “这段时间净资产、收入、支出概览”
- 为首页总览卡片提供基础数据

使用规则：
- `START` 和 `END` 必须是 `YYYY-MM-DD`
- Firefly III 要求 `start < end`
- 如果用户指定币种，追加 `CURRENCY_CODE`

## 账户余额趋势

```bash
python3 scripts/firefly_client.py chart-account <START> <END> [PERIOD]
```

对应接口：
- `GET /v1/chart/account/overview`

适用场景：
- “最近半年净资产趋势”
- “账户余额变化曲线”
- 仪表盘折线图

使用规则：
- `PERIOD` 可选，常见值：`1D`、`1W`、`1M`、`3M`、`6M`、`1Y`
- 这是官方图表数据，不要再用 `trend` 冒充账户趋势

## 洞察矩阵

```bash
python3 scripts/firefly_client.py insight <SCOPE> <GROUP> <START> <END> [FILTER_IDS] [ACCOUNT_IDS]
```

对应接口：
- `GET /v1/insight/expense/*`
- `GET /v1/insight/income/*`
- `GET /v1/insight/transfer/*`

参数说明：
- `SCOPE`：`expense`、`income`、`transfer`
- `GROUP`：
  - `expense` 支持：`expense`、`asset`、`bill`、`no-bill`、`budget`、`no-budget`、`category`、`no-category`、`tag`、`no-tag`、`total`
  - `income` 支持：`revenue`、`asset`、`category`、`no-category`、`tag`、`no-tag`、`total`
  - `transfer` 支持：`asset`、`category`、`no-category`、`tag`、`no-tag`、`total`
- `FILTER_IDS`：可选，逗号分隔 ID 列表，仅以下分组可用：
  - `bill` → 账单 ID
  - `budget` → 预算 ID
  - `category` → 分类 ID
  - `tag` → 标签 ID
- `ACCOUNT_IDS`：可选，逗号分隔账户 ID 列表，用于限定资产/负债账户范围
- 不需要某个可选参数时可省略，或传 `-`

适用场景：
- “这个月各分类花了多少”
- “哪些支出没有预算 / 没有关联账单 / 没打标签”
- “这段时间收入按来源账户怎么分布”
- “最近几个月转账按标签或账户怎么看”

使用规则：
- 优先使用官方 insight 接口，不要先拉全量交易再本地分组
- `no-*` 分组用于查漏配数据，适合做记账质量检查
- `total` 用于直接拿官方总额，不要自己二次汇总

示例：

```bash
# 支出按预算聚合
python3 scripts/firefly_client.py insight expense budget 2026-04-01 2026-04-18

# 查询没有预算的支出
python3 scripts/firefly_client.py insight expense no-budget 2026-04-01 2026-04-18

# 收入按标签聚合，只看指定账户
python3 scripts/firefly_client.py insight income tag 2026-04-01 2026-04-18 - 1,2

# 转账总额
python3 scripts/firefly_client.py insight transfer total 2026-04-01 2026-04-18
```

## 支出分类洞察

```bash
python3 scripts/firefly_client.py insight-expense-category <START> <END> [CATEGORY_IDS] [ACCOUNT_IDS]
```

对应接口：
- `GET /v1/insight/expense/category`

适用场景：
- “钱花去哪了”
- “这月餐饮/交通/购物分别花了多少”
- 首页分类占比和分类排行榜

使用规则：
- 优先使用这个接口，而不是先拉全量交易再本地按分类汇总
- 如需补充解释，再回查 `transactions`
- 新场景优先使用通用 `insight` 命令；这里保留是为了兼容已有调用方式

## 预算列表

```bash
python3 scripts/firefly_client.py budgets [START] [END]
```

对应接口：
- `GET /v1/budgets`

适用场景：
- “有哪些预算”
- “这个月每个预算已经花了多少”

使用规则：
- 不带日期时，主要拿预算定义
- 带 `START`、`END` 时，Firefly III 会返回该时间段内的 `spent` 信息

## 可用预算

```bash
python3 scripts/firefly_client.py available-budgets [START] [END]
python3 scripts/firefly_client.py available-budget-get <AVAILABLE_BUDGET_ID>
```

对应接口：
- `GET /v1/available-budgets`
- `GET /v1/available-budgets/{id}`

适用场景：
- “这段时间预算池里实际可分配的钱还有多少”
- “预算额度是怎么分期落下来的”

说明：
- 这不是单个预算的已花/限额，而是 Firefly III 计算出的可用预算金额及其周期
- 和 `budgets` / `budget-limits` 一起看，能区分“预算设了多少”和“本期真正可用多少”

## 预算额度

```bash
python3 scripts/firefly_client.py budget-limits <START> <END>
python3 scripts/firefly_client.py budget-limit-list <BUDGET_ID> [START] [END]
python3 scripts/firefly_client.py budget-limit-get <BUDGET_ID> <LIMIT_ID>
python3 scripts/firefly_client.py budget-limit-create <BUDGET_ID> '<JSON_DATA>'
python3 scripts/firefly_client.py budget-limit-update <BUDGET_ID> <LIMIT_ID> '<JSON_DATA>'
python3 scripts/firefly_client.py budget-limit-delete <BUDGET_ID> <LIMIT_ID>
```

对应接口：
- `GET /v1/budget-limits`
- `GET /v1/budgets/{id}/limits`
- `GET /v1/budgets/{id}/limits/{limitId}`
- `POST /v1/budgets/{id}/limits`
- `PUT /v1/budgets/{id}/limits/{limitId}`
- `DELETE /v1/budgets/{id}/limits/{limitId}`

适用场景：
- “预算上限是多少”
- “还剩多少预算”
- “哪些预算已经超支”
- “给某个预算补一条新月份额度”
- “修正某条预算额度备注/金额/时间范围”

说明：
- 预算分析时，`budgets` 和 `budget-limits` 必须结合看
- `budgets` 解决“花了多少”，`budget-limits` 解决“额度是多少”
- `budget-limit-list` / `budget-limit-get` 解决“这个预算具体有哪些额度分段”
- `budget-limit-create/update/delete` 用于显式维护预算额度，不要再绕回主预算对象

## 预算交易闭环

```bash
python3 scripts/firefly_client.py budget-transactions <BUDGET_ID> [START] [END] [TYPE]
python3 scripts/firefly_client.py budget-limit-transactions <BUDGET_ID> <LIMIT_ID>
python3 scripts/firefly_client.py transactions-without-budget [START] [END] [TYPE]
```

对应接口：
- `GET /v1/budgets/{id}/transactions`
- `GET /v1/budgets/{id}/limits/{limitId}/transactions`
- `GET /v1/budgets/transactions-without-budget`

适用场景：
- “这个预算为什么超了”
- “超的是哪几笔”
- “有哪些支出没挂预算，钱漏记到哪了”

使用规则：
- 先用 `budgets` / `budget-limits` 找到异常预算，再回查 `budget-transactions` 或 `budget-limit-transactions`
- `budget-limit-transactions` 的时间范围由预算额度本身决定，最适合解释某个额度分段为何超支
- `transactions-without-budget` 用于查漏配，定位应该归到预算但当前没挂上的交易
- 需要限制交易类型时，`budget-transactions` 和 `transactions-without-budget` 可追加 `TYPE`，例如 `withdrawal`

## Phase 2 包装能力

这些命令可以保留，但它们是本地包装，不是当前 MVP 的事实源：

```bash
python3 scripts/firefly_client.py networth [YYYY-MM-DD] [CURRENCY_CODE]
python3 scripts/firefly_client.py report [YYYY-MM]
python3 scripts/firefly_client.py trend [monthly|quarterly|yearly] [COUNT]
```

使用规则：
- `networth` 是 `summary/basic` 的便捷包装
- `report` 和 `trend` 是本地聚合结果
- 当用户要求“精确对应 Firefly III 的分析接口”时，优先使用上面的官方接口命令
