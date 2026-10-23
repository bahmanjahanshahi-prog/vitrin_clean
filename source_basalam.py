import asyncio
import json
import shutil
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


def get_prices(query="لولا"):
    """جستجوی محصولات در باسلام با استفاده از کلاینت رسمی MCP."""
    basalam_cmd = shutil.which("basalam-mcp")
    if not basalam_cmd:
        print("   ⚠️ basalam-mcp پیدا نشد.")
        return []

    async def _fetch():
        server_params = StdioServerParameters(command=basalam_cmd, args=[])
        async with stdio_client(server_params) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()
                result = await session.call_tool("bs_search", arguments={"query": query})
                if result.content:
                    return result.content[0].text
                return None

    try:
        result_json = asyncio.run(_fetch())
        if not result_json:
            print("   -> basalam: پاسخی دریافت نشد.")
            return []

        data = json.loads(result_json)
        products = data.get("products", []) if isinstance(data, dict) else data

        results = []
        for item in products:
            price = item.get("price", 0)
            if price and 1000 < price < 200_000_000:
                # باسلام از کلید name استفاده می‌کنه
                title = item.get("name", "")
                results.append({
                    "name": title,
                    "title": title,
                    "brand": title,
                    "price": price,
                    "url": f"https://basalam.com/p/{item.get('id', '')}",
                    "seller": item.get("shop", "باسلام"),
                    "rating": item.get("rating", 0),
                    "review_count": item.get("rating_count", 0),
                    "in_stock": item.get("in_stock", True),
                })

        print(f"   -> basalam: {len(results)} محصول دریافت شد.")
        return results

    except Exception as e:
        print(f"   ⚠️ خطا در اتصال به باسلام: {e}")
        return []