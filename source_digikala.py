import asyncio
import json
import re
from digikala_mcp import catalog

def get_prices(query="MDF"):
    """
    این تابع از پکیج digikala-mcp برای جستجو استفاده می‌کند.
    خروجی را به فرمت استاندارد پروژه تبدیل می‌کند.
    """
    try:
        # اجرای تابع async در یک حلقه
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        # فراخوانی تابع جستجو (طبق تستی که کردیم، این تابع در catalog است)
        # نکته: تابع ممکن است نامش dk_search باشد (بر اساس تست قبلی)
        result = loop.run_until_complete(catalog.dk_search(query=query))
        loop.close()
        
        # اگر خروجی به صورت رشته (JSON) است، آن را به دیکشنری تبدیل می‌کنیم
        if isinstance(result, str):
            data = json.loads(result)
        else:
            data = result
            
        products = data.get('products', []) if isinstance(data, dict) else []
        
        results = []
        for item in products:
            try:
                # استخراج فیلدها
                name = item.get('title', 'نامشخص')
                price = item.get('price', 0)
                url = item.get('url', '')
                seller = item.get('seller', 'نامشخص')
                rating = item.get('rating', 0)        # 0-5
                rating_count = item.get('rating_count', 0)
                in_stock = item.get('in_stock', True)
                
                if not price or price <= 0:
                    continue
                if not (10_000 < price < 100_000_000):
                    continue
                
                results.append({
                    "name": name,
                    "brand": name,
                    "price": price,
                    "url": url,
                    "rating": rating,             # 0-5 (این پکیج مستقیم از 5 میده)
                    "review_count": rating_count,
                    "seller": seller,
                    "seller_stars": 0,
                    "in_stock": in_stock,
                    "source": "digikala",
                })
            except Exception:
                continue
                
        return results
        
    except Exception as e:
        print(f"خطا در جستجوی '{query}' در دیجی‌کالا (mcp): {e}")
        return []

if __name__ == "__main__":
    prices = get_prices("گوشی سامسونگ")
    print(f"تعداد {len(prices)} محصول پیدا شد.")
    for p in prices[:3]:
        print(p)