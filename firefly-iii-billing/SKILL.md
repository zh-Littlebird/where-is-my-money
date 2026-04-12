---
name: firefly-iii-billing
description: Firefly III 记账技能。支持文本和图片两种记账方式，自动提取交易信息并匹配账户、分类、标签等元数据，实现快速记账。同时提供交易搜索、账单管理、存钱罐、标签管理和附件上传等完整的财务管理能力。
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

> **Token 来源**：从 `config.json` 中的 `FIREFLY_III_ACCESS_TOKEN` 字段读取。

## 记账流程

### 步骤 1：获取元数据

```bash
scripts/firefly_client.py list <TOKEN>
```

返回并发获取的四类元数据：`accounts`、`categories`、`tags`、`budgets`。

**元数据使用规则**：
- 必须实时获取最新数据，不使用缓存
- **⚠️ 账户、分类、标签、预算必须从 Firefly III 已有数据中选择，严禁自行新建**
- 若确实无法匹配到已有项，必须明确告知用户并征得同意后才能新建
- 当不确定支出账户时需要询问用户

### 步骤 2：解析交易信息

**文字记账**：直接分析文字描述，提取交易详情，支持批量处理多笔交易

**图片记账**：利用多模态视觉能力识别图片内容，每张图片独立处理，严禁合并

**交易信息提取规则**：

1. **交易类型**
   - 支出：日常消费、购物等
   - 收入：工资、奖金、退款等
   - 转账：账户间转移、基金买卖（⚠️ 基金买卖必须记为转账）

2. **金额**
   - 提取数字金额，保留小数点

3. **日期与时间**
   - 日期：提取交易日期，默认为今天
   - 时间：**必须确定具体时间**（格式 `HH:MM:SS`）
     - 明确时间：如"14:35"、"下午3点" → 转换为 `14:35:00`、`15:00:00`
     - 相对时间：如"刚刚"、"5分钟前"、"今天早上" → 基于当前时间换算
     - **严禁使用 `00:00:00` 作为占位符**
     - 无法确定时必须向用户询问

4. **描述**
   - 商户名称或消费项目简述

5. **源账户（Source Account）**
   - **⚠️ 必须从已有账户中匹配，无法匹配时须征得用户同意后才能新建**
   - 支出：资产账户（Asset）或债务账户（Liability）
   - 收入：收入账户（Revenue）
   - 转账：资产账户或债务账户

6. **目标账户（Destination Account）**
   - **⚠️ 必须从已有账户中匹配，无法匹配时须征得用户同意后才能新建**
   - 支出：支出账户（Expense）
   - 收入：资产账户（Asset）或债务账户（Liability）
   - 转账：资产账户或债务账户

7. **预算（Budget）**
   - 仅支出类型需要选择预算
   - **必须从元数据列表中选择**，无匹配项时须询问用户是否新建

8. **分类（Category）**
   - **必须从元数据列表中选择**，无匹配项时须询问用户是否新建

9. **标签（Tags）**
   - **必须从元数据列表中选择**，无匹配项时须询问用户是否新建

10. **备注（Notes）**
    - 固定格式：`Auto-synced by Clawdbot from [text/image]`

### 步骤 3：用户确认

**文字记账**：
- 信息明确（金额、账户、时间都清楚）且为常规消费 → 直接记账
- 信息模糊（账户不确定、需新建账户、时间不明） → 向用户确认

**图片记账**：
- 必须展示识别结果供用户确认

确认格式示例（单笔）：

```
📝 交易确认

| 字段 | 值 |
|------|-----|
| 类型 | 💸 支出 |
| 金额 | ￥XX.XX |
| 日期 | 20XX-XX-XX XX:XX:XX |
| 描述 | 商品描述 |
| 源账户 | 信用卡-XX银行 |
| 目标账户 | XX便利店 |
| 预算 | 预算名称 |
| 分类 | 分类名称 |
| 标签 | 标签名称 |

确认记账？
```

确认格式示例（多笔）：

```
📝 交易确认（共 2 笔，合计 ￥XX.XX）

① 💸 支出 ￥XX.XX · 20XX-XX-XX XX:XX
   商品描述 | 信用卡-XX银行 → XX便利店
   分类: 分类名称 · 预算: 预算名称 · 标签: 标签名称

② 💸 支出 ￥XX.XX · 20XX-XX-XX XX:XX
   打车描述 | XX钱包 → XX出行
   分类: 分类名称 · 预算: 预算名称 · 标签: 标签名称

确认记账？
```

**格式选择规则**：
- 单笔交易：使用表格格式，字段完整清晰
- 多笔交易：使用紧凑行格式，便于快速浏览
- 多笔时在标题显示笔数和合计金额（仅合计同币种同类型）

### 步骤 4：提交交易

```bash
# 单笔或多笔交易（JSON 字符串）
scripts/firefly_client.py post <TOKEN> '<JSON_DATA>'

# 或使用临时文件（数据量大时）
scripts/firefly_client.py post <TOKEN> <FILE_PATH>
```

`firefly_client.py` 的 `post_transactions` 方法自动将单个 dict 包装为列表，并使用以下提交参数：
- `error_if_duplicate_hash`: false
- `apply_rules`: true
- `fire_webhooks`: true
- `group_title`: "Imported via Clawdbot"

### 步骤 5：最终汇报

成功提交后，向用户展示所有交易的详细信息供最终核对。

## 隐私保护规则

⚠️ **严禁将生活类交易记录到项目进展日志**

生活类交易（餐饮、购物、日常消费等）属于个人隐私，严禁调用其他技能写入任何项目报告或日志。此类信息仅保留在 Firefly III 系统内。

## 扩展功能

### 搜索交易

```bash
scripts/firefly_client.py search <TOKEN> '<QUERY>'
```

支持高级搜索语法：
- 文本搜索：`groceries`
- 字段搜索：`amount:>100`、`category:food`、`date:2024-01-01`
- 布尔逻辑：空格表示 AND，`OR` 关键字
- 精确匹配：`"monthly rent"`

适用场景：查重、回顾消费记录

### 交易管理

```bash
# 查看交易详情
scripts/firefly_client.py get <TOKEN> <TRANSACTION_ID>

# 更新交易
scripts/firefly_client.py update <TOKEN> <TRANSACTION_ID> '<JSON_DATA>'

# 删除交易
scripts/firefly_client.py delete <TOKEN> <TRANSACTION_ID>
```

### 自动补全

```bash
scripts/firefly_client.py autocomplete <TOKEN> <RESOURCE_TYPE> '<QUERY>'
```

支持的资源类型：`accounts`、`tags`、`categories`、`budgets`、`bills`、`piggy-banks`、`transactions`、`currencies`

比全量 `list` 更轻量，适合交互式模糊匹配。

### 账单管理

```bash
scripts/firefly_client.py bills <TOKEN>
```

查看所有账单，支持周期性支出（房租、会员费、保险等）关联。

> Python API 还支持 `create_bill`、`update_bill`、`delete_bill`，可通过 `python3 -c` 调用。

### 存钱罐管理

```bash
scripts/firefly_client.py piggybanks <TOKEN>
```

查看所有存钱罐，支持储蓄目标场景（如"往旅行基金存了500"）。

> Python API 还支持 `create_piggy_bank`、`update_piggy_bank`、`delete_piggy_bank`，可通过 `python3 -c` 调用。

### 标签管理

通过 Python API 调用（无 CLI 快捷命令）：

```python
from scripts.firefly_client import FireflyClient
client = FireflyClient.from_config()

# 获取所有标签
client.get_tags()

# 获取单个标签
client.get_tag(tag_id)

# 更新标签
client.update_tag(tag_id, data)

# 仅更新标签描述
client.update_tag_description(tag_id, "new description")
```

### 批量更新交易

通过 Python API 调用 `client.bulk_update_transactions(data)` 批量更新交易记录。

### 附件上传

通过 Python API 将小票/发票原图关联到交易记录：

```python
# 1. 创建附件元数据
attachment = client.create_attachment(
    attachable_type="TransactionJournal",
    attachable_id=journal_id,
    filename="receipt.jpg",
    title="消费小票"
)

# 2. 上传文件
client.upload_attachment(attachment['data']['id'], "/path/to/receipt.jpg")
```

### 月度资金变动报告

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

### 资金净增长趋势

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

## 配置说明

配置文件：`config.json`

```json
{
  "FIREFLY_III_BASE_URL": "https://your-firefly-instance.example.com/",
  "FIREFLY_III_ACCESS_TOKEN": "your-token-here"
}
```

新环境请参考 `config.example.json` 创建配置文件。

## 故障排除

| 问题 | 解决方案 |
|------|---------|
| 图片模糊无法识别 | 请求用户提供清晰图片 |
| 账户/分类/标签不存在 | 严禁自行新建，必须向用户确认是否创建 |
| 交易类型判断困难 | 根据上下文判断（如基金买卖是转账） |
| 时间信息缺失 | 基于当前时间解析相对表达，无法确定时向用户询问 |
| HTTP Error | 检查 Token 是否过期或 Firefly III 服务是否可用 |
| 重复交易 | 使用 `search` 先查重，`error_if_duplicate_hash` 默认关闭 |
