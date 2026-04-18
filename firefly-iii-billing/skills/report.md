# 报表与趋势

## 净资产查询

```bash
# 查询今天的净资产
scripts/firefly_client.py networth <TOKEN>

# 查询指定日期的净资产
scripts/firefly_client.py networth <TOKEN> 2026-04-18

# 查询指定日期、指定币种的净资产
scripts/firefly_client.py networth <TOKEN> 2026-04-18 CNY
```

**触发场景**：
- 用户问"我现在净资产多少"、"查下我的总资产"、"截至今天净值是多少"等
- 用户明确给出某个日期，想看该日的净资产快照
- 用户需要按币种查看净资产时，可追加 `CURRENCY_CODE`

**实现说明**：
- 底层使用 `GET /v1/summary/basic`
- Firefly III 要求 `start < end`，CLI 会自动将查询起点设为目标日期前一天
- `as_of` 表示你真正想查看的净资产日期，`end` 与它相同

**返回数据**：
- `as_of`：净资产快照日期
- `entry`：仅当结果只有一个币种时提供，便于直接读取
- `entries`：净资产条目列表；每项包含 `monetary_value`、`value_parsed`、`currency_code`、`currency_symbol`

**展示格式**：

```
净资产（截至 2026-04-18）

- CNY: ¥123,214.79
```

**展示规则**：
- 优先展示 `value_parsed`
- 多币种时逐行列出，不自行换汇合并
- 若用户只问“当前净资产”，默认查询今天
- 若用户指定币种，则优先返回该币种的单项结果

## 月度资金变动报告

```bash
# 当前月报告
scripts/firefly_client.py report <TOKEN>

# 指定月份
scripts/firefly_client.py report <TOKEN> 20XX-XX
```

**触发场景**：
- 用户问"这个月花了多少"、"上个月收支情况"、"3月资金变动"等
- 默认为当前月，用户指定月份时使用 `YYYY-MM` 格式

**返回数据**：
- `income` / `expense` / `transfer`：收入、支出、转账总额
- `net`：净现金流（收入 − 支出）
- `by_category`：按分类汇总支出
- `by_budget`：按预算汇总支出
- `by_tag`：按标签汇总支出
- `by_source_account`：按源账户（哪张卡/钱包付的）汇总支出
- `transaction_count`：各类型交易笔数

**报告展示格式**：

```
📊 20XX年X月 资金变动报告

💰 总览
| 项目 | 金额 |
|------|------|
| 收入 | ￥XX,XXX.XX |
| 支出 | ￥X,XXX.XX |
| 转账 | ￥X,XXX.XX |
| 净现金流 | +￥X,XXX.XX |
| 交易笔数 | 收入 X · 支出 XX · 转账 X |

📂 支出分类
| 分类 | 金额 | 占比 |
|------|------|------|
| 分类A | ￥X,XXX.XX | XX.X% |
| 分类B | ￥X,XXX.XX | XX.X% |
| 分类C | ￥XXX.XX | XX.X% |
| 分类D | ￥XXX.XX | XX.X% |

📋 预算执行
| 预算 | 金额 | 占比 |
|------|------|------|
| 预算A | ￥X,XXX.XX | XX.X% |
| 预算B | ￥X,XXX.XX | XX.X% |
| 预算C | ￥XXX.XX | XX.X% |

🏷️ 标签分布
| 标签 | 金额 | 占比 |
|------|------|------|
| 标签A | ￥X,XXX.XX | XX.X% |
| 标签B | ￥X,XXX.XX | XX.X% |
| 标签C | ￥XXX.XX | XX.X% |

💳 支出账户分布
| 账户 | 金额 |
|------|------|
| 信用卡-XX银行 | ￥X,XXX.XX |
| XX钱包 | ￥X,XXX.XX |
```

**展示规则**：
- 各维度按金额降序排列，支出为 0 的项省略
- 分类/预算/标签均显示占比百分比
- 净现金流为正用 `+` 前缀，为负用 `-` 前缀
- 金额使用千位分隔符格式化

## 资金净增长趋势

```bash
# 最近 6 个月（默认）
scripts/firefly_client.py trend <TOKEN>

# 最近 4 个季度
scripts/firefly_client.py trend <TOKEN> quarterly 4

# 最近 3 年
scripts/firefly_client.py trend <TOKEN> yearly 3

# 最近 12 个月
scripts/firefly_client.py trend <TOKEN> monthly 12
```

**触发场景**：
- 用户问"最近半年收支趋势"、"每个季度赚了多少"、"今年和去年比怎么样"等
- 默认按月展示最近 6 期

**粒度选项**：

| 粒度 | 参数 | 示例标签 |
|------|------|----------|
| 按月 | `monthly` | 2026-01, 2026-02, ... |
| 按季度 | `quarterly` | 2025-Q4, 2026-Q1, ... |
| 按年 | `yearly` | 2024, 2025, 2026 |

**返回数据**：
- `periods`：每期的 `label`、`income`、`expense`、`net`（收入 − 支出）
- `totals`：所有期汇总的 `income`、`expense`、`net`

**报告展示格式**：

```
📈 资金净增长趋势（按月，最近 6 期）

| 月份 | 收入 | 支出 | 净增长 |
|------|------|------|--------|
| 20XX-XX | ￥XX,XXX.XX | ￥X,XXX.XX | +￥X,XXX.XX |
| 20XX-XX | ￥XX,XXX.XX | ￥X,XXX.XX | +￥X,XXX.XX |
| 20XX-XX | ￥XX,XXX.XX | ￥X,XXX.XX | +￥X,XXX.XX |
| 20XX-XX | ￥XX,XXX.XX | ￥X,XXX.XX | +￥X,XXX.XX |
| 20XX-XX | ￥XX,XXX.XX | ￥X,XXX.XX | +￥X,XXX.XX |
| 20XX-XX | ￥0.00 | ￥XXX.XX | -￥XXX.XX |
| **合计** | **￥XX,XXX.XX** | **￥XX,XXX.XX** | **+￥XX,XXX.XX** |

📊 趋势图
20XX-XX ██████████████░░░░░░ +￥X,XXX
20XX-XX ███████████░░░░░░░░░ +￥X,XXX
20XX-XX ████████████████░░░░ +￥X,XXX
20XX-XX █████████████████████████████████ +￥X,XXX
20XX-XX ████████████░░░░░░░░ +￥X,XXX
20XX-XX ▓▓▓▓                -￥XXX
```

**展示规则**：
- 表格 + 文本柱状图，直观呈现趋势变化
- 正增长用 `█`，负增长用 `▓`，柱长按最大绝对值等比缩放
- 最后一行显示合计
- 净增长正值用 `+` 前缀，负值用 `-` 前缀
