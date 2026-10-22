import asyncio
import json
import re
from torob_mcp import search

def get_prices(query="لولا"):
    results = []
    
    try:
        # اجرای تابع async tb_search
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        # فراخوانی تابع جستجو (tb_search)
        # این تابع احتمالاً نام پارامترش q یا query است
        raw_result = loop.run_until_complete(search.tb_search(query=query))
        loop.close()
        
        # تبدیل خروجی به دیکشنری اگر به صورت رشته است
        if isinstance(raw_result, str):
            data = json.loads(raw_result)
        else:
            data = raw_result
            
        # استخراج لیست محصولات (بسته به ساختار خروجی)
        products = data.get('products', []) if isinstance(data, dict) else (data if isinstance(data, list) else [])
        
        for item in products:
            try:
                name = item.get('name', '') or item.get('title', '') or item.get('brand', '')
                price = item.get('price', 0)
                
                # اگر قیمت رشته بود، به عدد تبدیل کن
                if isinstance(price, str):
                    price = int(re.sub(r'[^\d]', '', price))
                
                if not price or price <= 0:
                    continue
                if not (10_000 < price < 100_000_000):
                    continue
                
                # لینک محصول (اگر وجود داشت)
                url = item.get('url', '') or item.get('link', '')
                if not url:
                    url = f"https://torob.com/search/?query={query}"
                
                results.append({
                    "name": name,
                    "brand": name,
                    "price": int(price),
                    "url": url,
                    "rating": 0,
                    "review_count": 0,
                    "seller": "ترب",
                    "seller_stars": 0,
                    "in_stock": True,
                    "source": "torob",
                })
            except Exception:
                continue
                
    except Exception as e:
        print(f"خطا در جستجوی '{query}' در ترب: {e}")
        return []
        
    return results

if __name__ == "__main__":
    prices = get_prices("لولا")
    print(f"تعداد {len(prices)} محصول پیدا شد.")
    for p in prices[:3]:
        print(p)