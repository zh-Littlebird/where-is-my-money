# 财务管理（Phase 2）

本文件中的能力暂不属于当前 agent MVP 主链路。只有当用户明确要求账单、存钱目标或附件上传时，再加载并使用。

## 账单管理

```bash
scripts/firefly_client.py bills <TOKEN>
```

查看所有账单，支持周期性支出（房租、会员费、保险等）关联。

> Python API 还支持 `create_bill`、`update_bill`、`delete_bill`，可通过 `python3 -c` 调用。

## 存钱罐管理

```bash
scripts/firefly_client.py piggybanks <TOKEN>
```

查看所有存钱罐，支持储蓄目标场景（如"往旅行基金存了500"）。

`FIREFLY_III_AUTO_CREATE_PIGGY_BANKS` 约束的是交易/归属流程里的隐式自动新建，不拦截用户明确要求的显式创建。
若 `FIREFLY_III_AUTO_CREATE_PIGGY_BANKS=false`，在涉及存钱罐归属或选择时，必须先调用 `piggybanks` 或 `autocomplete piggy-banks` 读取已有列表，并从现有存钱罐中选择；无匹配项时向用户展示现有选项，而不是继续隐式创建。

> Python API 还支持 `create_piggy_bank`、`update_piggy_bank`、`delete_piggy_bank`，可通过 `python3 -c` 调用。

## 标签管理

标签已升级为主数据管理能力，优先加载 `skills/masterdata.md`。

如需仅通过 Python API 操作，也可使用：

`FIREFLY_III_AUTO_CREATE_TAGS` 约束的是交易流程里的隐式自动新建。
若 `FIREFLY_III_AUTO_CREATE_TAGS=false`，必须先读取现有标签列表，再从已有标签中选择或让用户指定现有标签；不能在交易 payload 中直接提交新的标签名。

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

## 附件上传

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
