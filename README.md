# Firefly III Billing Skill

[Firefly III](https://www.firefly-iii.org/) 记账技能，作为 [Claude Code](https://docs.anthropic.com/en/docs/claude-code) 的 custom skill 使用。支持**文本记账**和**图片记账**两种方式，自动提取交易信息并匹配账户、分类、标签等元数据，实现自然语言快速记账。

## 功能特性

- **文本记账**：用自然语言描述交易，如"刚打车花了 20"、"昨天在便利店买了饮料 5.6 元"
- **图片记账**：上传收据、发票、支付截图，自动识别并提取交易信息
- **交易管理**：查询、更新、删除交易记录
- **高级搜索**：支持多字段、布尔逻辑的搜索语法
- **账单管理**：管理周期性支出（房租、订阅等）
- **存钱罐**：管理储蓄目标
- **标签管理**：标签的增删改查
- **月度报告**：按分类、预算、标签、账户多维度汇总收支
- **趋势分析**：按月/季度/年展示多期收支净增长趋势

## 项目结构

```
firefly-iii-billing/
├── SKILL.md                    # Claude Code skill 定义文件
├── config.example.json         # 配置文件模板
├── config.json                 # 实际配置文件（已 gitignore）
├── scripts/
│   └── firefly_client.py       # Firefly III API 客户端
└── references/
    └── api_reference.md        # Firefly III API 参考文档
```

## 快速开始

### 前置条件

- Python 3.7+（无需额外依赖，仅使用标准库）
- 一个运行中的 [Firefly III](https://www.firefly-iii.org/) 实例
- Firefly III 的 Personal Access Token
- [Claude Code](https://docs.anthropic.com/en/docs/claude-code) CLI

### 安装配置

1. **克隆仓库**

   ```bash
   git clone https://github.com/your-username/firefly-iii-billing.git
   ```

2. **创建配置文件**

   ```bash
   cp config.example.json config.json
   ```

   编辑 `config.json`，填入你的 Firefly III 实例地址和 Access Token：

   ```json
   {
     "FIREFLY_III_BASE_URL": "https://your-firefly-instance.example.com/",
     "FIREFLY_III_ACCESS_TOKEN": "your-token-here"
   }
   ```

3. **在 Claude Code 中注册 skill**

   将 `SKILL.md` 作为 Claude Code custom skill 加载即可使用。

## CLI 用法

`firefly_client.py` 也可以作为独立 CLI 工具使用：

```bash
# 获取账户/分类/标签/预算元数据
python3 scripts/firefly_client.py list <TOKEN>

# 提交交易
python3 scripts/firefly_client.py post <TOKEN> '<JSON_DATA>'

# 查看交易详情
python3 scripts/firefly_client.py get <TOKEN> <TRANSACTION_ID>

# 更新交易
python3 scripts/firefly_client.py update <TOKEN> <TRANSACTION_ID> '<JSON_DATA>'

# 删除交易
python3 scripts/firefly_client.py delete <TOKEN> <TRANSACTION_ID>

# 搜索交易
python3 scripts/firefly_client.py search <TOKEN> '<QUERY>'

# 自动补全
python3 scripts/firefly_client.py autocomplete <TOKEN> <RESOURCE_TYPE> '<QUERY>'

# 查看账单
python3 scripts/firefly_client.py bills <TOKEN>

# 查看存钱罐
python3 scripts/firefly_client.py piggybanks <TOKEN>

# 月度资金变动报告（默认当月）
python3 scripts/firefly_client.py report <TOKEN> [YYYY-MM]

# 多期净增长趋势（默认按月 6 期）
python3 scripts/firefly_client.py trend <TOKEN> [monthly|quarterly|yearly] [期数]
```

## Python API 用法

```python
from scripts.firefly_client import FireflyClient

# 从 config.json 初始化
client = FireflyClient.from_config()

# 获取元数据
metadata = client.list_metadata()

# 提交交易
client.post_transactions('{"type":"withdrawal","amount":"25.50",...}')

# 月度报告
report = client.monthly_report(2026, 3)

# 趋势分析
trend = client.trend_report("monthly", 6)
```

## 安全说明

- `config.json` 包含敏感的 Access Token，已在 `.gitignore` 中排除
- 请勿将 Access Token 硬编码在代码中或提交到版本控制
- 建议定期轮换 Firefly III 的 Personal Access Token

## License

MIT
