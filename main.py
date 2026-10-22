import sys
import importlib
import json
import concurrent.futures
import re

sys.stdout.reconfigure(encoding='utf-8')
from dictionary import expand_keywords
from config import SOURCE_CONFIG

ENG_TRANSLATIONS = {
    "گوشی": ["phone", "mobile", "smartphone"],
    "سامسونگ": ["samsung"],
    "اپل": ["apple", "iphone"],
    "شیائومی": ["xiaomi"],
    "لپ‌تاپ": ["laptop", "notebook"],
    "هدفون": ["headphone", "earphone", "airpods"],
}

CATEGORIES = {
    "mdf": ["mdf", "ام دی اف", "ورق", "تخته", "هایگلاس", "ملامینه", "سفید", "رنگی", "ضخامت", "میل"],
    "hardware": ["لولا", "ریل", "دستگیره", "یراق", "پیچ", "آرام بند"],
    "mobile": ["گوشی", "phone", "mobile", "samsung", "apple", "xiaomi"],
}

ALL_SOURCES = {
    "choobro": "source_choobro",
    "torob": "source_torob",
    "shahreyaragh": "source_shahreyaragh",
    "emalls": "source_emalls",
    "digikala": "source_digikala"
}

def fetch_from_source(key, query):
    if key not in ALL_SOURCES: return []
    module_name = ALL_SOURCES[key]
    try:
        module = importlib.import_module(module_name)
        import inspect
        sig = inspect.signature(module.get_prices)
        if len(sig.parameters) > 0:
            data = module.get_prices(query)
        else:
            data = module.get_prices()
        print(f"   -> {module_name}: {len(data)} محصول دریافت شد.")
        return data
    except Exception as e:
        print(f"   ⚠️ خطا در {module_name}: {e}")
        return []

def smart_search(query, source_keys, output_path):
    print(f"⏳ جستجوی هوشمند برای: '{query}'")
    
    words = query.lower().split()
    text_words = []
    number_words = []
    
    for word in words:
        if re.search(r'\d', word):
            clean_numbers = re.sub(r'[^\d]', '', word)
            if clean_numbers:
                number_words.append(clean_numbers)
        else:
            if word != "mdf":
                text_words.append(word)
            
    print(f"   کلمات متنی: {text_words}")
    print(f"   اعداد (ضخامت/سایز): {number_words}")
    
    search_term = " ".join(text_words)
    if not search_term:
        search_term = query
        
    all_data = []
    with concurrent.futures.ThreadPoolExecutor() as executor:
        future_to_source = {executor.submit(fetch_from_source, key, search_term): key for key in source_keys}
        for future in concurrent.futures.as_completed(future_to_source, timeout=30):
            try:
                data = future.result(timeout=25)
                all_data.extend(data)
            except:
                pass
    
    if not all_data:
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump([{"error": "هیچ داده‌ای از منابع دریافت نشد."}], f, ensure_ascii=False)
        print("❌ هیچ داده‌ای از منابع دریافت نشد.")
        return

    blacklist = ["درب", "کابینت", "کمد", "پیوت", "کفش", "کارتن", "بسته", "عمده", "پالت", "تیراژ"]
    
    main_category_word = ""
    for cat, keywords in CATEGORIES.items():
        if any(k in query.lower() for k in keywords):
            main_category_word = cat
            break

    filtered_results = []
    for item in all_data:
        product_name = item.get('name', '').lower()
        if not product_name:
            product_name = item.get('brand', '').lower()
            
        source_name = item.get('source', '')
        source_rules = SOURCE_CONFIG.get(source_name, {"use_keyword_filter": True, "use_blacklist": True})
        
        # --- ۱. فیلتر دسته‌بندی ---
        is_relevant = False
        if main_category_word == "mdf":
            mdf_keywords = ["mdf", "ام دی اف", "تخته", "ورق", "هایگلاس", "ملامینه", "چوب"]
            is_relevant = any(kw in product_name for kw in mdf_keywords)
        elif main_category_word == "hardware":
            hw_keywords = ["لولا", "ریل", "دستگیره", "یراق", "آرام بند"]
            is_relevant = any(kw in product_name for kw in hw_keywords)
        elif main_category_word == "mobile":
            mob_keywords = ["گوشی", "phone", "mobile", "samsung", "apple", "xiaomi"]
            is_relevant = any(kw in product_name for kw in mob_keywords)
        else:
            is_relevant = any(kw.lower() in product_name for kw in query.split())

        if source_name == "digikala":
            is_relevant = True

        if not is_relevant:
            continue
            
        # --- ۲. فیلتر اعداد (ضخامت، سایز و...) ---
        # ساخت یک متن کامل برای جستجوی اعداد
        full_info = product_name
        if item.get('thickness'):
            full_info += " " + str(item['thickness']).lower()
        if item.get('dimensions'):
            full_info += " " + str(item['dimensions']).lower()
            
        match_numbers = True
        for num in number_words:
            # اگر عددی که کاربر خواسته در متن نبود، ردش کن
            if num not in full_info:
                match_numbers = False
                break
                
        if not match_numbers:
            continue
            
        # --- ۳. فیلتر متنی ---
        if source_rules.get("use_keyword_filter", True):
            match_text = True
            for tw in text_words:
                synonyms = expand_keywords(tw)
                if tw in ENG_TRANSLATIONS:
                    synonyms.extend(ENG_TRANSLATIONS[tw])
                
                if not any(syn.lower() in product_name for syn in synonyms):
                    match_text = False
                    break
            if not match_text:
                continue
        
        # --- ۴. بلاک‌لیست ---
        if source_rules.get("use_blacklist", True):
            if any(word in product_name for word in blacklist):
                continue
            
        filtered_results.append(item)
            
    results = []
    if filtered_results:
        filtered_results.sort(key=lambda x: x['price'])
        
        for item in filtered_results:
            if 10_000 < item['price'] < 100_000_000:
                results.append({
                    "source_id": "python_engine",
                    "source_name": "موتور جستجو",
                    "url": item.get('url', ''),
                    "price": item['price'],
                    "unit": "عدد",
                    "date": "",
                    "status": "valid",
                    "confidence": 100,
                    "note": item.get('name', ''),
                    "rating": item.get('rating', 0),
                    "review_count": item.get('review_count', 0),
                    "seller": item.get('seller', ''),
                    "seller_stars": item.get('seller_stars', 0),
                    "in_stock": item.get('in_stock', True),
                    "candidates": []
                })
    
    if not results:
        results.append({"error": f"هیچ محصولی با '{query}' پیدا نشد."})
        print(f"❌ هیچ محصولی پیدا نشد.")
    else:
        print(f"✅ {len(results)} محصول پیدا شد.")
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False)

if __name__ == "__main__":
    if len(sys.argv) >= 3:
        query = sys.argv[1]
        sources_str = sys.argv[2] if len(sys.argv) > 2 else "choobro"
        output_file = sys.argv[3] if len(sys.argv) > 3 else "C:/temp/analyzer_prices.json"
        
        source_keys = sources_str.split(',')
        smart_search(query, source_keys, output_file)
    else:
        smart_search("MDF", ["choobro"], "C:/temp/analyzer_prices.json")