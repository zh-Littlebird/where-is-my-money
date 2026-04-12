# Firefly III API Reference

## Authentication
All API calls require Bearer token authentication:
```
Authorization: Bearer {access_token}
```

## Pagination
Most list endpoints return paginated results. Response includes:
```json
{
  "data": [...],
  "meta": {
    "pagination": {
      "total": 150,
      "count": 50,
      "per_page": 50,
      "current_page": 1,
      "total_pages": 3
    }
  }
}
```
Use `?page=N` to fetch subsequent pages. The `FireflyClient._get_all_pages()` method handles this automatically.

## Accounts Endpoint
`GET /api/v1/accounts[?type={type}]`

### Account Types
- `asset`: Asset accounts (checking, savings)
- `expense`: Expense accounts (creditors)
- `revenue`: Revenue accounts (income sources)
- `liability`: Liability accounts (loans, credit cards)

### Response Format
```json
{
  "data": [
    {
      "id": "1",
      "type": "accounts",
      "attributes": {
        "name": "Checking Account",
        "active": true,
        "type": "asset",
        "account_type_name": "Asset account",
        "account_role": "defaultAsset",
        "currency_code": "CNY",
        "current_balance": "1000.00",
        "include_net_worth": true,
        "iban": null,
        "account_number": null,
        "notes": null,
        "liability_type": null,
        "liability_direction": null,
        "interest": null,
        "interest_period": null
      }
    }
  ]
}
```

### Key Fields
- `include_net_worth` (boolean, default `true`): Whether this account's balance counts toward the user's net worth. Accounts with `include_net_worth: false` (e.g., provident fund, reimbursement accounts) are excluded from net-worth trend calculations.
- `account_role` (string, nullable): Sub-role for asset accounts. Values: `defaultAsset`, `sharedAsset`, `savingAsset`, `ccAsset` (credit card), `cashWalletAsset`. NULL for non-asset accounts.
- `liability_type` (string, nullable): Only for liability accounts. Values: `loan`, `debt`, `mortgage`.
- `liability_direction` (string, nullable): Only for liability accounts. `"credit"` = somebody owes you (receivable); `"debit"` = you owe this debt (payable).
- `current_balance` (string): Current balance in the account's currency. For assets: positive = you have funds. For liabilities: sign depends on `liability_direction` and transactions.
- `active` (boolean, default `true`): Whether the account is active.

> **Full OpenAPI spec**: See `references/firefly-iii-6.5.5-v1.yaml` for the complete API specification (25k+ lines).

## Categories Endpoint
`GET /api/v1/categories`

### Response Format
```json
{
  "data": [
    {
      "id": "1",
      "type": "categories",
      "attributes": {
        "name": "Food & Dining",
        "notes": "Expenses related to food and dining"
      }
    }
  ]
}
```

## Tags Endpoint
- `GET /api/v1/tags` — List all tags (paginated)
- `GET /api/v1/tags/{id}` — Get single tag
- `PUT /api/v1/tags/{id}` — Update tag

### Response Format
```json
{
  "data": [
    {
      "id": "1",
      "type": "tags",
      "attributes": {
        "tag": "Food",
        "date": null,
        "description": null,
        "latitude": null,
        "longitude": null,
        "zoom_level": null
      }
    }
  ]
}
```

## Budgets Endpoint
`GET /api/v1/budgets`

### Response Format
```json
{
  "data": [
    {
      "id": "1",
      "type": "budgets",
      "attributes": {
        "name": "Food Budget",
        "active": true,
        "created_at": "2024-01-01T00:00:00Z",
        "updated_at": "2024-01-01T00:00:00Z"
      }
    }
  ]
}
```

## Transactions Endpoint

### Create Transaction
`POST /api/v1/transactions`

```json
{
  "transactions": [
    {
      "type": "withdrawal",
      "date": "2024-01-01T10:00:00+08:00",
      "amount": "50.00",
      "description": "Transaction description",
      "source_id": "1",
      "destination_id": "2",
      "category_name": "Food & Dining",
      "budget_id": "1",
      "tags": ["Food", "Dining"]
    }
  ]
}
```

### Get Transaction
`GET /api/v1/transactions/{id}`

### Update Transaction
`PUT /api/v1/transactions/{id}`

Request body same structure as create.

### Delete Transaction
`DELETE /api/v1/transactions/{id}`

Returns 204 No Content on success.

### Date Format Requirements
- Must be in ISO 8601 format with timezone
- Examples: `"2024-01-01T10:00:00+08:00"`, `"2024-01-01T10:00:00Z"`

### Transaction Types
- `withdrawal`: Spending money (expense)
- `deposit`: Receiving money (income)
- `transfer`: Moving money between accounts

### Tags Format
- Array of tag name strings, not IDs
- Example: `["Food", "Dining", "Takeaway"]`

## Search Endpoint
`GET /api/v1/search/transactions?query={query}`

Supports rich query syntax:
- Text: `groceries`
- Field filters: `amount:>100`, `category:food`, `date:2024-01-01`
- Boolean: spaces = AND, `OR` keyword
- Exact match: `"monthly rent"`

Parameters: `query` (required), `page`, `limit`

## Search Accounts
`GET /api/v1/search/accounts?query={query}&type={type}&field={field}`

## Autocomplete Endpoints
Lightweight fuzzy-match endpoints, faster than full list.

- `GET /api/v1/autocomplete/accounts?query={query}&limit={limit}`
- `GET /api/v1/autocomplete/categories?query={query}&limit={limit}`
- `GET /api/v1/autocomplete/tags?query={query}&limit={limit}`
- `GET /api/v1/autocomplete/budgets?query={query}&limit={limit}`
- `GET /api/v1/autocomplete/bills?query={query}&limit={limit}`
- `GET /api/v1/autocomplete/piggy-banks?query={query}&limit={limit}`
- `GET /api/v1/autocomplete/transactions?query={query}&limit={limit}`
- `GET /api/v1/autocomplete/currencies?query={query}&limit={limit}`

Returns flat array of `{id, name, ...}` objects (no pagination wrapper).

## Bills Endpoint
- `GET /api/v1/bills` — List all bills (paginated)
- `GET /api/v1/bills/{id}` — Get single bill
- `POST /api/v1/bills` — Create bill
- `PUT /api/v1/bills/{id}` — Update bill
- `DELETE /api/v1/bills/{id}` — Delete bill

## Piggy Banks Endpoint
- `GET /api/v1/piggy-banks` — List all piggy banks (paginated)
- `GET /api/v1/piggy-banks/{id}` — Get single piggy bank
- `POST /api/v1/piggy-banks` — Create piggy bank
- `PUT /api/v1/piggy-banks/{id}` — Update piggy bank
- `DELETE /api/v1/piggy-banks/{id}` — Delete piggy bank

## Attachments Endpoint
Two-step process to attach files (e.g. receipts) to transactions:

### Step 1: Create attachment metadata
`POST /api/v1/attachments`
```json
{
  "filename": "receipt.jpg",
  "attachable_type": "TransactionJournal",
  "attachable_id": "123",
  "title": "Receipt for lunch"
}
```

### Step 2: Upload file content
`POST /api/v1/attachments/{id}/upload`

Content-Type: `application/octet-stream`
Body: raw file bytes

## Bulk Operations
`POST /api/v1/data/bulk/transactions`

Bulk update transactions (e.g. move between accounts).

## Error Responses
Standard error format:
```json
{
  "message": "Error message",
  "errors": {
    "field_name": ["error description"]
  }
}
```
