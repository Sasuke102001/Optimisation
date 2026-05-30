import os
import httpx

class SupabaseTable:
    def __init__(self, table_name: str, url: str, key: str):
        self.table_name = table_name
        self.url = url
        self.key = key
        self.headers = {
            "apikey": key,
            "Authorization": f"Bearer {key}",
            "Content-Type": "application/json",
        }

    def insert(self, data: dict):
        class InsertBuilder:
            def __init__(self, parent):
                self.parent = parent
                self.data = data

            async def execute(self):
                async with httpx.AsyncClient() as client:
                    resp = await client.post(
                        f"{self.parent.url}/rest/v1/{self.parent.table_name}",
                        json=self.data,
                        headers={**self.parent.headers, "Prefer": "return=representation"},
                        timeout=10.0
                    )
                    resp.raise_for_status()
                    class Result:
                        def __init__(self, json_data):
                            self.data = json_data
                    return Result(resp.json())
        return InsertBuilder(self)

    def update(self, data: dict):
        class UpdateBuilder:
            def __init__(self, parent):
                self.parent = parent
                self.data = data
                self.filters = {}

            def eq(self, column: str, value):
                self.filters[column] = value
                return self

            async def execute(self):
                query_parts = []
                for col, val in self.filters.items():
                    query_parts.append(f"{col}=eq.{val}")
                query_str = "?" + "&".join(query_parts) if query_parts else ""

                async with httpx.AsyncClient() as client:
                    resp = await client.patch(
                        f"{self.parent.url}/rest/v1/{self.parent.table_name}{query_str}",
                        json=self.data,
                        headers=self.parent.headers,
                        timeout=10.0
                    )
                    resp.raise_for_status()
                    class Result:
                        def __init__(self):
                            self.data = None
                    return Result()
        return UpdateBuilder(self)


class PostgrestSupabaseClient:
    def __init__(self, url: str, key: str):
        self.url = url.rstrip("/")
        self.key = key

    def table(self, name: str) -> SupabaseTable:
        return SupabaseTable(name, self.url, self.key)


_client: PostgrestSupabaseClient | None = None

def get_supabase() -> PostgrestSupabaseClient | None:
    global _client
    if _client is not None:
        return _client
    url = os.environ.get("SUPABASE_URL")
    key = os.environ.get("SUPABASE_SERVICE_KEY")
    if not url or not key:
        print("WARNING: SUPABASE_URL or SUPABASE_SERVICE_KEY not set — Council logging disabled.")
        return None
    _client = PostgrestSupabaseClient(url, key)
    return _client
