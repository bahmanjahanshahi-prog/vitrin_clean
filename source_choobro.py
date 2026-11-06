import sys
import requests
from bs4 import BeautifulSoup
import re
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

sys.stdout.reconfigure(encoding='utf-8')

_session = requests.Session()
_session.headers.update({
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
})

def extract_from_page(url):
    products = []
    try:
        r = _session.get(url, timeout=15)
        if r.status_code != 200:
            return []
        soup = BeautifulSoup(r.text, 'html.parser')
        
        for table in soup.find_all('table'):
            for row in table.find_all('tr'):
                cells = row.find_all(['td', 'th'])
                if len(cells) >= 2:
                    name_text = cells[0].get_text(separator=' ', strip=True)
                    price_text = cells[1].get_text(strip=True)
                    
                    if not name_text or 'قیمت' in name_text or 'نام' in name_text:
                        continue
                    
                    thickness = ""
                    dimensions = ""
                    
                    thick_match = re.search(r'(\d+)\s*میل', name_text)
                    if thick_match:
                        thickness = thick_match.group(1) + "میل"
                        
                    dim_match = re.search(r'(\d+\s*[*xX×]\s*\d+)', name_text)
                    if dim_match:
                        dimensions = dim_match.group(1).replace(' ', '')
                    
                    name_text = re.sub(r'(\d+)\s*میل', r'\1میل', name_text)
                    
                    price_text = price_text.replace('.', '').replace(',', '').replace('٬', '')
                    nums = re.findall(r'\d+', price_text)
                    
                    if nums:
                        price = int(max(nums, key=len))
                        if price > 100_000_000:
                            price = price // 10
                        if 1_000_000 < price < 500_000_000:
                            products.append({
                                "name": name_text, 
                                "price": price, 
                                "url": url, 
                                "seller": "چوب‌رو",
                                "source": "choobro",
                                "thickness": thickness,
                                "dimensions": dimensions
                            })
    except Exception:
        pass
    return products

def get_prices(query="MDF"):
    print(f"   🤖 ربات چوب‌رو در حال اسکن موازی '{query}'...")
    
    # ✅ لیست صفحات پایه (شامل صفحه اصلی MDF که مرجع جامع است و صفحات تخصصی)
    base_urls = [
        "https://choobro.ir/price-list-mdf/",          # مرجع جامع MDF
        "https://choobro.ir/price-list-mdf-rangi/",    # رنگی
        "https://choobro.ir/price-list-mdf-sefid/",    # سفید
        "https://choobro.ir/price-list-mdf-kham/",     # خام
        "https://choobro.ir/price-list-highgloss/",    # هایگلاس
        "https://choobro.ir/price-list-neopan/",       # نئوپان
        "https://choobro.ir/price-list-pvc/",          # PVC
        "https://choobro.ir/price-list-corian/",       # کورین
        "https://choobro.ir/price-list-hdf/"           # HDF
    ]
    
    all_urls_to_scan = []
    
    # مرحله ۱: ساخت لیست URLها (برای هر صفحه پایه، ۵ صفحه اول کافی است)
    print(f"   🔎 در حال آماده‌سازی لیست صفحات...")
    for base_url in base_urls:
        for page in range(1, 6):  # فقط ۵ صفحه اول (چون سایت بیشتر ندارد)
            if page == 1:
                all_urls_to_scan.append(base_url)
            else:
                all_urls_to_scan.append(f"{base_url.rstrip('/')}/page/{page}/")
    
    print(f"   🚀 شروع اسکن {len(all_urls_to_scan)} صفحه به صورت موازی (۱۵ درخواست همزمان)...")
    
    all_products = []
    
    def process_url(url):
        # تاخیر بسیار کم برای جلوگیری از بلاک
        time.sleep(0.02)
        return extract_from_page(url)

    # مرحله ۲: اسکن موازی با ۱۵ کارگر (سرعت بیشتر)
    with ThreadPoolExecutor(max_workers=15) as executor:
        futures = {executor.submit(process_url, url): url for url in all_urls_to_scan}
        for i, future in enumerate(as_completed(futures)):
            url = futures[future]
            products = future.result()
            if products:
                all_products.extend(products)
                print(f"      ✅ {len(products)} محصول از: {url.split('/')[-2] if '/page/' in url else url.split('/')[-1]}")
            if (i + 1) % 10 == 0:
                print(f"      {i + 1} از {len(all_urls_to_scan)} صفحه اسکن شد...")

    # ✅ مرحله ۳: حذف تکراری‌ها با استفاده از set (بر اساس نام و قیمت)
    print(f"   🧹 حذف تکراری‌ها...")
    seen = set()
    unique_products = []
    for p in all_products:
        key = (p['name'], p['price'])
        if key not in seen:
            seen.add(key)
            unique_products.append(p)
    
    all_products = unique_products
    print(f"   📥 {len(all_products)} محصول یکتا از کل سایت جمع‌آوری شد.")
    
    # ✅ مرحله ۴: فیلتر هوشمند (اگر query عمومی بود، همه را نگه دار)
    query_lower = query.lower().strip()
    query_words = [w for w in query_lower.split() if len(w) > 1]
    
    # کلمات عمومی که نباید فیلتر شوند
    GENERIC_WORDS = {"mdf", "ام", "دی", "اف", "ام دی اف", "میل", "ميل", "mm", "میلیمتر", "و", "با", "بدون", "طرح"}
    distinctive_words = [w for w in query_words if w not in GENERIC_WORDS]
    
    if distinctive_words:
        # اگر کلمه خاصی وجود داشت (مثل رنگی، سفید)، فیلتر کن
        SYNONYMS = {
            "رنگی": ["رنگی", "ملامینه", "طرح بتن", "طرح چوب", "گروه استون", "متالیک", "فانتزی", "سوپرمات", "سوپرمتالیک", "گلکسی", "سینکرونایز", "رنگ های جدید", "رنگ پایه", "رنگ فانتزی", "پایتون", "ماتوپلاس"],
            "سفید": ["سفید", "صابونی", "یکرو", "دورو", "پرینتی"],
            "خام": ["خام", "raw"],
            "هایگلاس": ["هایگلاس", "براق", "پلی گلاس"]
        }
        expanded_words = set()
        for w in distinctive_words:
            if w in SYNONYMS:
                expanded_words.update(SYNONYMS[w])
                print(f"   🔄 گسترش '{w}' به {len(SYNONYMS[w])} مترادف.")
            else:
                expanded_words.add(w)
        expanded_words = list(expanded_words)
        
        filtered = [p for p in all_products if any(w in p['name'].lower() for w in expanded_words)]
        print(f"   🔎 فیلتر با {len(expanded_words)} کلمه: {len(filtered)} محصول مرتبط.")
        all_products = filtered
    else:
        # اگر فقط کلمه عمومی بود (مثل MDF)، همه را نگه دار
        print(f"   ℹ️ فقط کلمات عمومی بودن ({query_words}) — همه‌ی {len(all_products)} محصول نگه داشته شد.")
    
    print(f"   -> choobro: {len(all_products)} محصول نهایی.")
    return all_products