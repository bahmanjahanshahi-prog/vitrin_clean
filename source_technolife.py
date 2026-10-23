import asyncio
import json
import shutil
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


def get_prices(query="لپ تاپ"):
    """جستجوی محصولات در تکنولایف با استفاده از کلاینت رسمی MCP."""
    technolife_cmd = shutil.which("technolife-mcp")
    if not technolife_cmd:
        print("   ⚠️ technolife-mcp پیدا نشد.")
        return []

    async def _fetch():
        server_params = StdioServerParameters(command=technolife_cmd, args=[])
        async with stdio_client(server_params) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()
                result = await session.call_tool("tl_search", arguments={"query": query})
                if result.content:
                    return result.content[0].text
                return None

    try:
        result_json = asyncio.run(_fetch())
        if not result_json:
            print("   -> technolife: پاسخی دریافت نشد.")
            return []

        data = json.loads(result_json)
        products = data.get("products", []) if isinstance(data, dict) else data

        results = []
        for item in products:
            price = item.get("final_price") or item.get("price", 0)
            if price and 1000 < price < 500_000_000:
                title = item.get("name") or item.get("title", "")
                results.append({
                    "name": title,
                    "title": title,
                    "brand": title,
                    "price": price,
                    "url": f"https://www.technolife.com/product/{item.get('code', '')}",
                    "seller": item.get("seller_name", "تکنولایف"),
                    "rating": item.get("rating", 0),
                    "review_count": item.get("review_count", 0),
                    "in_stock": item.get("in_stock", True),
                })

        print(f"   -> technolife: {len(results)} محصول دریافت شد.")
        return results

    except Exception as e:
        print(f"   ⚠️ خطا در اتصال به تکنولایف: {e}")
        return []