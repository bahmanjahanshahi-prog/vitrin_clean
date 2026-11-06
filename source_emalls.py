import requests
from bs4 import BeautifulSoup
import re

def persian_to_english(text):
    persian_digits = "۰۱۲۳۴۵۶۷۸۹"
    english_digits = "0123456789"
    translation_table = str.maketrans(persian_digits, english_digits)
    return text.translate(translation_table)

def get_prices():
    url = "https://emalls.ir/%D9%84%DB%8C%D8%B3%D8%AA-%D9%82%DB%8C%D9%85%D8%AA~skey~%D9%84%D9%88%D9%84%D8%A7"
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()
    except Exception as e:
        print(f"خطا در اتصال به ایمالز: {e}")
        return []

    soup = BeautifulSoup(response.text, 'html.parser')
    results = []
    
    # پیدا کردن همه کارت‌های محصول
    products = soup.find_all('div', class_='product-block')
    
    for product in products:
        try:
            # اسم محصول
            title_tag = product.find('a', class_='prd-name')
            if not title_tag:
                continue
            title = title_tag.text.strip()
            
            # قیمت
            price_tag = product.find('div', class_='prd-price')
            if not price_tag:
                continue
                
            price_span = price_tag.find('span')
            if not price_span:
                continue
                
            price_text = price_span.text.strip()
            # تبدیل اعداد فارسی به انگلیسی
            price_text = persian_to_english(price_text)
            # حذف کاما و فاصله
            price_clean = price_text.replace(',', '').replace('٬', '').replace(' ', '').strip()
            
            if price_clean.isdigit():
                price_num = int(price_clean)
                if price_num > 0:
                    results.append({
                        "brand": title,
                        "price": price_num
                    })
        except:
            continue
            
    return results

if __name__ == "__main__":
    prices = get_prices()
    print(f"تعداد {len(prices)} محصول پیدا شد.")
    for p in prices[:10]:
        print(p)