# 分析与预算

本文件只描述当前 agent MVP 直接依赖的分析接口。优先使用官方 API 返回的结果，不要先用本地聚合替代。

## 基础汇总

```bash
scripts/firefly_client.py summary <TOKEN> <START> <END> [CURRENCY_CODE]
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
scripts/firefly_client.py chart-account <TOKEN> <START> <END> [PERIOD]
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

## 支出分类洞察

```bash
scripts/firefly_client.py insight-expense-category <TOKEN> <START> <END>
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

## 预算列表

```bash
scripts/firefly_client.py budgets <TOKEN> [START] [END]
```

对应接口：
- `GET /v1/budgets`

适用场景：
- “有哪些预算”
- “这个月每个预算已经花了多少”

使用规则：
- 不带日期时，主要拿预算定义
- 带 `START`、`END` 时，Firefly III 会返回该时间段内的 `spent` 信息

## 预算额度

```bash
scripts/firefly_client.py budget-limits <TOKEN> <START> <END>
```

对应接口：
- `GET /v1/budget-limits`

适用场景：
- “预算上限是多少”
- “还剩多少预算”
- “哪些预算已经超支”

说明：
- 预算分析时，`budgets` 和 `budget-limits` 必须结合看
- `budgets` 解决“花了多少”，`budget-limits` 解决“额度是多少”

## Phase 2 包装能力

这些命令可以保留，但它们是本地包装，不是当前 MVP 的事实源：

```bash
scripts/firefly_client.py networth <TOKEN> [YYYY-MM-DD] [CURRENCY_CODE]
scripts/firefly_client.py report <TOKEN> [YYYY-MM]
scripts/firefly_client.py trend <TOKEN> [monthly|quarterly|yearly] [COUNT]
```

使用规则：
- `networth` 是 `summary/basic` 的便捷包装
- `report` 和 `trend` 是本地聚合结果
- 当用户要求“精确对应 Firefly III 的分析接口”时，优先使用上面的官方接口命令
