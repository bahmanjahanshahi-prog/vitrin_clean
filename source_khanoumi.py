import asyncio
import json
import shutil
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


def get_prices(query="کرم"):
    """جستجوی محصولات در خانومی با استفاده از کلاینت رسمی MCP."""
    khanoumi_cmd = shutil.which("khanoumi-mcp")
    if not khanoumi_cmd:
        print("   ⚠️ khanoumi-mcp پیدا نشد.")
        return []

    async def _fetch():
        server_params = StdioServerParameters(command=khanoumi_cmd, args=[])
        async with stdio_client(server_params) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()
                # استفاده از ابزار kh_search برای جستجو
                result = await session.call_tool("kh_search", arguments={"query": query})
                if result.content:
                    return result.content[0].text
                return None

    try:
        result_json = asyncio.run(_fetch())
        if not result_json:
            print("   -> khanoumi: پاسخی دریافت نشد.")
            return []

        data = json.loads(result_json)
        products = data.get("products", []) if isinstance(data, dict) else data

        results = []
        for item in products:
            price = item.get("final_price") or item.get("price", 0)
            if price and 1000 < price < 50_000_000:
                title = item.get("name") or item.get("title", "")
                results.append({
                    "name": title,
                    "title": title,
                    "brand": title,
                    "price": price,
                    "url": f"https://www.khanoumi.com/product/{item.get('id', '')}",
                    "seller": item.get("brand", "خانومی"),
                    "rating": item.get("rating", 0),
                    "review_count": item.get("review_count", 0),
                    "in_stock": item.get("in_stock", True),
                })

        print(f"   -> khanoumi: {len(results)} محصول دریافت شد.")
        return results

    except Exception as e:
        print(f"   ⚠️ خطا در اتصال به خانومی: {e}")
        return []