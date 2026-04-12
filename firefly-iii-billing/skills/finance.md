# 财务管理（账单、存钱罐、标签、附件）

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

> Python API 还支持 `create_piggy_bank`、`update_piggy_bank`、`delete_piggy_bank`，可通过 `python3 -c` 调用。

## 标签管理

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
