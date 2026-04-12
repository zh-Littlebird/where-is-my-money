import sys
import json
import os
import urllib.request
import urllib.parse
from datetime import date, datetime
from calendar import monthrange
from collections import defaultdict
from urllib.error import URLError, HTTPError
from concurrent.futures import ThreadPoolExecutor, as_completed


class FireflyClient:
    def __init__(self, base_url, token):
        self.base_url = base_url.rstrip('/') + '/api/v1'
        self.token = token

    @classmethod
    def from_config(cls, config_path=None):
        if config_path is None:
            config_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'config.json')
        with open(config_path, 'r') as f:
            config = json.load(f)
        return cls(config['FIREFLY_III_BASE_URL'], config['FIREFLY_III_ACCESS_TOKEN'])

    # ── Core request helpers ──

    def _request(self, method, endpoint, data=None, params=None):
        url = f"{self.base_url}/{endpoint}"
        if params:
            url = f"{url}?{urllib.parse.urlencode(params)}"
        headers = {
            "Authorization": f"Bearer {self.token}",
            "Accept": "application/json",
            "Content-Type": "application/json"
        }
        req_data = json.dumps(data).encode('utf-8') if data else None
        req = urllib.request.Request(url, data=req_data, headers=headers, method=method)
        try:
            with urllib.request.urlopen(req) as resp:
                body = resp.read().decode('utf-8')
                return json.loads(body) if body else {"success": True}
        except HTTPError as e:
            err_body = e.read().decode('utf-8')
            print(f"HTTP Error: {e.code} - {e.reason}", file=sys.stderr)
            print(f"Response: {err_body}", file=sys.stderr)
            try:
                return {"error": True, "code": e.code, "detail": json.loads(err_body)}
            except json.JSONDecodeError:
                return {"error": True, "code": e.code, "message": err_body}
        except URLError as e:
            print(f"URL Error: {e.reason}", file=sys.stderr)
            return {"error": True, "message": str(e.reason)}

    def _request_binary(self, method, endpoint, file_path, content_type="application/octet-stream"):
        url = f"{self.base_url}/{endpoint}"
        with open(file_path, 'rb') as f:
            file_data = f.read()
        req = urllib.request.Request(url, data=file_data, method=method)
        req.add_header("Authorization", f"Bearer {self.token}")
        req.add_header("Content-Type", content_type)
        req.add_header("Accept", "application/json")
        try:
            with urllib.request.urlopen(req) as resp:
                body = resp.read().decode('utf-8')
                return json.loads(body) if body else {"success": True}
        except HTTPError as e:
            err_body = e.read().decode('utf-8')
            return {"error": True, "code": e.code, "message": err_body}
        except URLError as e:
            return {"error": True, "message": str(e.reason)}

    def _get_all_pages(self, endpoint, params=None):
        all_data = []
        page = 1
        while True:
            p = dict(params or {})
            p['page'] = page
            result = self._request("GET", endpoint, params=p)
            if result.get('error'):
                return result
            all_data.extend(result.get('data', []))
            total_pages = result.get('meta', {}).get('pagination', {}).get('total_pages', 1)
            if page >= total_pages:
                break
            page += 1
        return all_data

    def _parse_payload(self, data_str_or_file):
        if os.path.isfile(data_str_or_file):
            with open(data_str_or_file, 'r') as f:
                return json.load(f)
        return json.loads(data_str_or_file)

    # ── Metadata ──

    def list_metadata(self):
        endpoints = {
            "accounts": "accounts",
            "categories": "categories",
            "tags": "tags",
            "budgets": "budgets"
        }
        results = {}
        with ThreadPoolExecutor(max_workers=4) as executor:
            futures = {
                executor.submit(self._get_all_pages, ep): name
                for name, ep in endpoints.items()
            }
            for future in as_completed(futures):
                name = futures[future]
                try:
                    data = future.result()
                    results[name] = data if not isinstance(data, dict) or not data.get('error') else []
                except Exception:
                    results[name] = []
        return results

    # ── Transactions ──

    def post_transactions(self, data_str_or_file):
        payload = self._parse_payload(data_str_or_file)
        if isinstance(payload, dict):
            payload = [payload]
        return self._request("POST", "transactions", data={
            "error_if_duplicate_hash": False,
            "apply_rules": True,
            "fire_webhooks": True,
            "group_title": "Imported via Clawdbot",
            "transactions": payload
        })

    def get_transaction(self, transaction_id):
        return self._request("GET", f"transactions/{transaction_id}")

    def update_transaction(self, transaction_id, data_str_or_file):
        payload = self._parse_payload(data_str_or_file)
        if isinstance(payload, dict):
            payload = [payload]
        return self._request("PUT", f"transactions/{transaction_id}", data={
            "transactions": payload
        })

    def delete_transaction(self, transaction_id):
        return self._request("DELETE", f"transactions/{transaction_id}")

    def search_transactions(self, query, page=1, limit=50):
        return self._request("GET", "search/transactions", params={
            "query": query, "page": page, "limit": limit
        })

    def bulk_update_transactions(self, data_str_or_file):
        payload = self._parse_payload(data_str_or_file)
        return self._request("POST", "data/bulk/transactions", data=payload)

    # ── Tags ──

    def get_tags(self):
        return self._get_all_pages("tags")

    def get_tag(self, tag_id):
        return self._request("GET", f"tags/{tag_id}")

    def update_tag(self, tag_id, data):
        return self._request("PUT", f"tags/{tag_id}", data=data)

    def update_tag_description(self, tag_id, description):
        tag = self._request("GET", f"tags/{tag_id}")
        if isinstance(tag, dict) and tag.get('error'):
            return tag
        attrs = tag['data']['attributes'].copy()
        attrs['description'] = description
        return self._request("PUT", f"tags/{tag_id}", data=attrs)

    # ── Autocomplete ──

    def autocomplete(self, resource_type, query, limit=10):
        return self._request("GET", f"autocomplete/{resource_type}", params={
            "query": query, "limit": limit
        })

    # ── Bills ──

    def list_bills(self):
        return self._get_all_pages("bills")

    def get_bill(self, bill_id):
        return self._request("GET", f"bills/{bill_id}")

    def create_bill(self, data_str_or_file):
        payload = self._parse_payload(data_str_or_file)
        return self._request("POST", "bills", data=payload)

    def update_bill(self, bill_id, data_str_or_file):
        payload = self._parse_payload(data_str_or_file)
        return self._request("PUT", f"bills/{bill_id}", data=payload)

    def delete_bill(self, bill_id):
        return self._request("DELETE", f"bills/{bill_id}")

    # ── Piggy Banks ──

    def list_piggy_banks(self):
        return self._get_all_pages("piggy-banks")

    def get_piggy_bank(self, piggy_id):
        return self._request("GET", f"piggy-banks/{piggy_id}")

    def create_piggy_bank(self, data_str_or_file):
        payload = self._parse_payload(data_str_or_file)
        return self._request("POST", "piggy-banks", data=payload)

    def update_piggy_bank(self, piggy_id, data_str_or_file):
        payload = self._parse_payload(data_str_or_file)
        return self._request("PUT", f"piggy-banks/{piggy_id}", data=payload)

    def delete_piggy_bank(self, piggy_id):
        return self._request("DELETE", f"piggy-banks/{piggy_id}")

    # ── Attachments ──

    def create_attachment(self, attachable_type, attachable_id, filename, title=None):
        return self._request("POST", "attachments", data={
            "filename": filename,
            "attachable_type": attachable_type,
            "attachable_id": str(attachable_id),
            "title": title or filename
        })

    def upload_attachment(self, attachment_id, file_path):
        return self._request_binary("POST", f"attachments/{attachment_id}/upload", file_path)

    # ── Transactions listing (date-range) ──

    def list_transactions(self, start=None, end=None, tx_type="all"):
        """Fetch all transactions in a date range (paginated)."""
        params = {"type": tx_type}
        if start:
            params["start"] = start
        if end:
            params["end"] = end
        return self._get_all_pages("transactions", params=params)

    # ── Monthly Report ──

    def monthly_report(self, year=None, month=None):
        """Generate a monthly financial summary.

        Returns a dict with:
          - period: "YYYY-MM"
          - income / expense / transfer totals
          - net: income - expense
          - by_category: {name: amount}  (expenses)
          - by_budget: {name: amount}    (expenses)
          - by_tag: {name: amount}       (expenses)
          - by_source_account: {name: amount}  (expenses, which asset paid)
          - transaction_count: {withdrawal, deposit, transfer}
        """
        today = date.today()
        year = year or today.year
        month = month or today.month
        _, last_day = monthrange(year, month)
        start = f"{year}-{month:02d}-01"
        end = f"{year}-{month:02d}-{last_day:02d}"

        raw = self.list_transactions(start=start, end=end)
        if isinstance(raw, dict) and raw.get("error"):
            return raw

        income_total = 0.0
        expense_total = 0.0
        transfer_total = 0.0
        by_category = defaultdict(float)
        by_budget = defaultdict(float)
        by_tag = defaultdict(float)
        by_source = defaultdict(float)
        counts = {"withdrawal": 0, "deposit": 0, "transfer": 0}

        for group in raw:
            for tx in group.get("attributes", {}).get("transactions", []):
                amount = float(tx.get("amount", 0))
                tx_type = tx.get("type", "")
                category = tx.get("category_name") or "未分类"
                budget = tx.get("budget_name") or "无预算"
                src = tx.get("source_name", "")
                tags = tx.get("tags", [])

                if tx_type == "withdrawal":
                    expense_total += amount
                    counts["withdrawal"] += 1
                    by_category[category] += amount
                    by_budget[budget] += amount
                    by_source[src] += amount
                    for tag in tags:
                        tag_name = tag if isinstance(tag, str) else tag.get("tag", "")
                        if tag_name:
                            by_tag[tag_name] += amount
                elif tx_type == "deposit":
                    income_total += amount
                    counts["deposit"] += 1
                elif tx_type == "transfer":
                    transfer_total += amount
                    counts["transfer"] += 1

        return {
            "period": f"{year}-{month:02d}",
            "start": start,
            "end": end,
            "income": round(income_total, 2),
            "expense": round(expense_total, 2),
            "transfer": round(transfer_total, 2),
            "net": round(income_total - expense_total, 2),
            "by_category": dict(sorted(by_category.items(), key=lambda x: x[1], reverse=True)),
            "by_budget": dict(sorted(by_budget.items(), key=lambda x: x[1], reverse=True)),
            "by_tag": dict(sorted(by_tag.items(), key=lambda x: x[1], reverse=True)),
            "by_source_account": dict(sorted(by_source.items(), key=lambda x: x[1], reverse=True)),
            "transaction_count": counts,
        }

    # ── Trend Report ──

    # Account types that are "internal" (affect net worth)
    _ASSET_TYPES = {"asset", "Asset account", "Default asset account", "Cash account",
                    "Shared asset account", "cash"}
    _LIABILITY_TYPES = {"liability", "Loan", "Debt", "Mortgage", "liabilities",
                        "Credit card", "creditcard"}
    # Account types that are "external" (revenue / expense)
    _REVENUE_TYPES = {"revenue", "Revenue account"}
    _EXPENSE_TYPES = {"expense", "Expense account"}

    @classmethod
    def _net_worth_impact(cls, tx):
        """Determine how a transaction affects net worth.

        Returns (income, expense) tuple:
          - income: amount flowing in from external (revenue) sources
          - expense: amount flowing out to external (expense) sinks
          - transfers between asset/liability accounts = (0, 0)
        """
        amount = float(tx.get("amount", 0))
        src_type = tx.get("source_type", "")
        dst_type = tx.get("destination_type", "")

        # Real income: revenue → asset/liability
        is_income = (src_type in cls._REVENUE_TYPES and
                     (dst_type in cls._ASSET_TYPES or dst_type in cls._LIABILITY_TYPES))
        # Real expense: asset/liability → expense
        is_expense = ((src_type in cls._ASSET_TYPES or src_type in cls._LIABILITY_TYPES) and
                      dst_type in cls._EXPENSE_TYPES)

        if is_income:
            return (amount, 0.0)
        elif is_expense:
            return (0.0, amount)
        else:
            return (0.0, 0.0)

    @staticmethod
    def _generate_periods(granularity, count, ref_date=None):
        """Generate a list of (label, start_date, end_date) tuples going backwards from ref_date."""
        ref = ref_date or date.today()
        periods = []
        if granularity == "monthly":
            for i in range(count):
                y = ref.year
                m = ref.month - i
                while m <= 0:
                    m += 12
                    y -= 1
                _, last = monthrange(y, m)
                periods.append((f"{y}-{m:02d}", f"{y}-{m:02d}-01", f"{y}-{m:02d}-{last:02d}"))
        elif granularity == "quarterly":
            # Current quarter first, then go backwards
            q_month = (ref.month - 1) // 3 * 3 + 1  # first month of current quarter
            q_year = ref.year
            for i in range(count):
                m = q_month - i * 3
                y = q_year
                while m <= 0:
                    m += 12
                    y -= 1
                end_m = m + 2
                end_y = y
                if end_m > 12:
                    end_m -= 12
                    end_y += 1
                _, last = monthrange(end_y, end_m)
                q_num = (m - 1) // 3 + 1
                periods.append((f"{y}-Q{q_num}", f"{y}-{m:02d}-01", f"{end_y}-{end_m:02d}-{last:02d}"))
        elif granularity == "yearly":
            for i in range(count):
                y = ref.year - i
                periods.append((str(y), f"{y}-01-01", f"{y}-12-31"))
        else:
            raise ValueError(f"Unknown granularity: {granularity}")
        periods.reverse()
        return periods

    def trend_report(self, granularity="monthly", count=6):
        """Generate a multi-period net-growth trend.

        Args:
            granularity: "monthly", "quarterly", or "yearly"
            count: number of periods to include (going backwards from today)

        Returns a dict with:
            - granularity, count
            - periods: list of {label, start, end, income, expense, net}
            - totals: {income, expense, net} across all periods
        """
        period_defs = self._generate_periods(granularity, count)
        periods = []

        # Fetch all periods concurrently
        def fetch_one(label, start, end):
            raw = self.list_transactions(start=start, end=end)
            if isinstance(raw, dict) and raw.get("error"):
                return {"label": label, "start": start, "end": end,
                        "income": 0, "expense": 0, "net": 0, "error": True}
            income = 0.0
            expense = 0.0
            for group in raw:
                for tx in group.get("attributes", {}).get("transactions", []):
                    inc, exp = self._net_worth_impact(tx)
                    income += inc
                    expense += exp
            net = round(income - expense, 2)
            return {"label": label, "start": start, "end": end,
                    "income": round(income, 2), "expense": round(expense, 2), "net": net}

        with ThreadPoolExecutor(max_workers=min(count, 6)) as executor:
            futures = {
                executor.submit(fetch_one, label, s, e): idx
                for idx, (label, s, e) in enumerate(period_defs)
            }
            results = [None] * len(period_defs)
            for future in as_completed(futures):
                idx = futures[future]
                results[idx] = future.result()

        total_income = sum(p["income"] for p in results)
        total_expense = sum(p["expense"] for p in results)

        return {
            "granularity": granularity,
            "count": count,
            "periods": results,
            "totals": {
                "income": round(total_income, 2),
                "expense": round(total_expense, 2),
                "net": round(total_income - total_expense, 2),
            }
        }


# ── CLI ──

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python3 firefly_client.py <action> <token> [data]")
        sys.exit(1)

    action = sys.argv[1]
    token = sys.argv[2]

    config_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'config.json')
    try:
        with open(config_path, 'r') as f:
            cfg = json.load(f)
        base_url = cfg['FIREFLY_III_BASE_URL']
    except (FileNotFoundError, KeyError):
        print("Error: config.json not found or missing FIREFLY_III_BASE_URL. See config.example.json.", file=sys.stderr)
        sys.exit(1)

    client = FireflyClient(base_url, token)

    if action == "list":
        print(json.dumps(client.list_metadata()))
    elif action == "post" and len(sys.argv) >= 4:
        print(json.dumps(client.post_transactions(sys.argv[3])))
    elif action == "search" and len(sys.argv) >= 4:
        print(json.dumps(client.search_transactions(sys.argv[3])))
    elif action == "get" and len(sys.argv) >= 4:
        print(json.dumps(client.get_transaction(sys.argv[3])))
    elif action == "update" and len(sys.argv) >= 5:
        print(json.dumps(client.update_transaction(sys.argv[3], sys.argv[4])))
    elif action == "delete" and len(sys.argv) >= 4:
        print(json.dumps(client.delete_transaction(sys.argv[3])))
    elif action == "autocomplete" and len(sys.argv) >= 5:
        print(json.dumps(client.autocomplete(sys.argv[3], sys.argv[4])))
    elif action == "bills":
        print(json.dumps(client.list_bills()))
    elif action == "piggybanks":
        print(json.dumps(client.list_piggy_banks()))
    elif action == "report":
        # Usage: report <token> [YYYY-MM]
        year, month = None, None
        if len(sys.argv) >= 4:
            parts = sys.argv[3].split("-")
            year = int(parts[0])
            month = int(parts[1])
        print(json.dumps(client.monthly_report(year, month)))
    elif action == "trend":
        # Usage: trend <token> [granularity] [count]
        # granularity: monthly (default), quarterly, yearly
        # count: number of periods (default 6)
        granularity = sys.argv[3] if len(sys.argv) >= 4 else "monthly"
        count = int(sys.argv[4]) if len(sys.argv) >= 5 else 6
        print(json.dumps(client.trend_report(granularity, count)))
    else:
        print(json.dumps({"error": True, "message": "Invalid action or missing arguments"}))
        sys.exit(1)
