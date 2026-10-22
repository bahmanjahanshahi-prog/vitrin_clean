import requests
from bs4 import BeautifulSoup
import re

def get_prices(query=""):
    url = "https://choobro.ir/price-list-mdf/"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()
    except Exception as e:
        print(f"خطا در اتصال به چوبرو: {e}")
        return []

    soup = BeautifulSoup(response.text, 'html.parser')
    results = [] 
    
    tables = soup.find_all('table')
    query_words = query.lower().split() if query else []
    
    for table in tables:
        rows = table.find_all('tr')
        for row in rows:
            cols = row.find_all(['td', 'th'])
            
            # طبق ساختار جدید، هر سطر ۳ ستون داره
            if len(cols) >= 2:
                name_text = cols[0].text.strip()
                price_text = cols[1].text.strip()
                
                # اگر سطر مربوط به هدر جدول بود، رد کن
                if "نام" in name_text and "قیمت" in price_text:
                    continue
                
                # تمیز کردن قیمت (حذف کاما و تبدیل به عدد)
                price_clean = price_text.replace(',', '').replace('٬', '').replace(' ', '')
                
                if price_clean.isdigit():
                    price_num = int(price_clean)
                    
                    # تبدیل ریال به تومان (اگر عدد خیلی بزرگ بود)
                    if price_num > 100_000_000:
                        price_toman = price_num // 10
                    else:
                        price_toman = price_num
                        
                    # فیلتر قیمت منطقی
                    if 50_000 < price_toman < 100_000_000:
                        
                        # فیلتر کلمه جستجو (اگر کاربر چیزی سرچ کرده بود)
                        if query_words:
                            full_text = f"{name_text} {price_text}".lower()
                            if not all(word in full_text for word in query_words):
                                continue
                                
                        # استخراج سایز و ضخامت از اسم
                        dimensions = ""
                        thickness = ""
                        # پیدا کردن ابعاد مثل 183*366
                        dim_match = re.search(r'(\d+\s*[*xX×]\s*\d+)', name_text)
                        if dim_match:
                            dimensions = dim_match.group(1)
                        # پیدا کردن ضخامت مثل 16میل
                        thick_match = re.search(r'(\d+\s*میل)', name_text)
                        if thick_match:
                            thickness = thick_match.group(1)
                            
                        results.append({
                            "name": name_text.replace('\n', ' '),
                            "brand": name_text.replace('\n', ' '),
                            "dimensions": dimensions,
                            "thickness": thickness,
                            "price": price_toman,
                            "url": url,
                            "source": "choobro",
                            "rating": 0,
                            "review_count": 0,
                            "seller": "چوب‌رو",
                            "seller_stars": 0,
                            "in_stock": True
                        })
    return results

if __name__ == "__main__":
    prices = get_prices("") # تست بدون فیلتر (همه رو بگیر)
    print(f"تعداد کل محصولات پیدا شده: {len(prices)}")
    for p in prices[:5]:
        print(f"- {p['name']} | قیمت: {p['price']} | ضخامت: {p['thickness']}")