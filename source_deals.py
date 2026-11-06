import asyncio
import json
import shutil
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

# ایمپورت کردن دیجی‌کالا (از قبل نصب شده)
try:
    from digikala_mcp import catalog
    DIGIKALA_AVAILABLE = True
except ImportError:
    DIGIKALA_AVAILABLE = False

# ایمپورت کردن ترب
try:
    from torob_mcp import catalog as torob_catalog
    TOROB_AVAILABLE = True
except ImportError:
    TOROB_AVAILABLE = False


def get_deals():
    """جمع‌آوری تخفیف‌های واقعی از منابع مختلف."""
    results = []
    
    # ۱. دیجی‌کالا
    if DIGIKALA_AVAILABLE:
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            deals = loop.run_until_complete(catalog.dk_deals())
            loop.close()
            if deals and isinstance(deals, dict) and 'products' in deals:
                for item in deals['products']:
                    results.append({
                        "name": item.get('title', 'نامشخص'),
                        "price": item.get('price', 0) or 0,
                        "url": item.get('url', ''),
                        "seller": "دیجی‌کالا",
                        "source": "digikala",
                        "discount": item.get('discount', 0) or 0,
                    })
            print(f"   -> digikala: {len(deals.get('products', []))} تخفیف دریافت شد.")
        except Exception as e:
            print(f"   ⚠️ خطا در دیجی‌کالا: {e}")
    
    # ۲. ترب
    if TOROB_AVAILABLE:
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            deals = loop.run_until_complete(torob_catalog.tr_deals())
            loop.close()
            if deals and isinstance(deals, dict) and 'products' in deals:
                for item in deals['products']:
                    results.append({
                        "name": item.get('title', 'نامشخص'),
                        "price": item.get('price', 0) or 0,
                        "url": item.get('url', ''),
                        "seller": "ترب",
                        "source": "torob",
                        "discount": item.get('discount', 0) or 0,
                    })
            print(f"   -> torob: {len(deals.get('products', []))} تخفیف دریافت شد.")
        except Exception as e:
            print(f"   ⚠️ خطا در ترب: {e}")
    
    # ۳. باسلام (فقط محصولاتی که discount_pct دارن)
    basalam_cmd = shutil.which("basalam-mcp")
    if basalam_cmd:
        try:
            async def _fetch_basalam():
                server_params = StdioServerParameters(command=basalam_cmd, args=[])
                async with stdio_client(server_params) as (read, write):
                    async with ClientSession(read, write) as session:
                        await session.initialize()
                        # جستجوی کلمه "تخفیف" در باسلام
                        result = await session.call_tool("bs_search", arguments={"query": "تخفیف"})
                        if result.content:
                            return result.content[0].text
                        return None
            
            result_json = asyncio.run(_fetch_basalam())
            if result_json:
                data = json.loads(result_json)
                products = data.get("products", [])
                basalam_count = 0
                for item in products:
                    if item.get("discount_pct", 0) > 0:  # فقط محصولاتی که تخفیف دارن
                        results.append({
                            "name": item.get('name', 'نامشخص'),
                            "price": item.get('price', 0) or 0,
                            "url": f"https://basalam.com/p/{item.get('id', '')}",
                            "seller": item.get('shop', 'باسلام'),
                            "source": "basalam",
                            "discount": item.get('discount_pct', 0),
                        })
                        basalam_count += 1
                print(f"   -> basalam: {basalam_count} تخفیف دریافت شد.")
        except Exception as e:
            print(f"   ⚠️ خطا در باسلام: {e}")
    
    # مرتب‌سازی بر اساس درصد تخفیف (نزولی)
    results.sort(key=lambda x: x.get('discount', 0), reverse=True)
    
    if not results:
        return {"error": "هیچ تخفیفی از منابع دریافت نشد."}
    
    return {"products": results, "total": len(results)}


if __name__ == "__main__":
    res = get_deals()
    print(f"\nجمع کل: {res.get('total', 0)} تخفیف")
    for item in res.get('products', [])[:5]:
        print(f"  - {item['name'][:50]} | {item['price']:,} تومان | تخفیف: {item['discount']}% | {item['source']}")