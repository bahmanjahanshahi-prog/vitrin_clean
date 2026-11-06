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

# ✅ کلماتی که نباید به عنوان فیلتر متنی در نظر گرفته شوند
STOP_WORDS = ["پرفروش", "بهترین", "ارزان‌ترین", "ارزانترین", "جدید", "ترند", "محبوب", "تخفیف", "حراج"]

# ✅ تمام منابع اتاق فرمان
ALL_SOURCES = {
    "choobro": "source_choobro",
    "torob": "source_torob",
    "shahreyaragh": "source_shahreyaragh",
    "emalls": "source_emalls",
    "digikala": "source_digikala",
    "basalam": "source_basalam",
    "technolife": "source_technolife",
    "khanoumi": "source_khanoumi"
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
    # ✅ اصلاح مشکل حروف عربی و فارسی (ي -> ی و ك -> ک)
    query = query.replace('ي', 'ی').replace('ك', 'ک')
    
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
            if word not in ["mdf", "ام", "دی", "اف"]:
                text_words.append(word)
            
    print(f"   کلمات متنی: {text_words}")
    print(f"   اعداد (ضخامت/سایز): {number_words}")
    
    # ✅ حذف کلمات دستوری (مثل پرفروش) از جستجو
    effective_words = [w for w in text_words if w not in STOP_WORDS]
    
    search_term = " ".join(effective_words)
    if not search_term:
        search_term = " ".join(text_words)  # اگر همه کلمات دستوری بودند، از خود query استفاده کن
    if not search_term:
        search_term = query
        
    all_data = []
    # ✅ تایمر ۶۰۰ ثانیه برای جلوگیری از خطای Timeout
    with concurrent.futures.ThreadPoolExecutor() as executor:
        future_to_source = {executor.submit(fetch_from_source, key, search_term): key for key in source_keys}
        for future in concurrent.futures.as_completed(future_to_source, timeout=600):
            try:
                data = future.result(timeout=590)
                all_data.extend(data)
            except Exception as e:
                print(f"   ⚠️ یک منبع طول کشید یا خطا داد: {e}")
    
    if not all_data:
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump([{"error": "هیچ داده‌ای از منابع دریافت نشد."}], f, ensure_ascii=False)
        print("❌ هیچ داده‌ای از منابع دریافت نشد.")
        return

    # ✅ بلاک‌لیست بسیار کوتاه
    blacklist = ["کارتن", "بسته", "عمده", "پالت", "تیراژ", "ارتباط با", "تماس با", "کارشناس"]
    
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
        
        # ✅ فیلتر دسته‌بندی بازتر
        is_relevant = True 
        if main_category_word == "mdf":
            mdf_keywords = ["mdf", "ام دی اف", "تخته", "ورق", "هایگلاس", "ملامینه", "چوب", "رنگی", "سفید", "خام", "صابونی", "یکرو", "دورو", "پرینتی", "نئوپان"]
            is_relevant = any(kw in product_name for kw in mdf_keywords)
        elif main_category_word == "hardware":
            hw_keywords = ["لولا", "ریل", "دستگیره", "یراق", "آرام بند", "گازور", "قفل", "پیچ"]
            is_relevant = any(kw in product_name for kw in hw_keywords)
        elif main_category_word == "mobile":
            mob_keywords = ["گوشی", "phone", "mobile", "samsung", "apple", "xiaomi"]
            is_relevant = any(kw in product_name for kw in mob_keywords)
        else:
            # ✅ فیلتر متنی هوشمند (اصلاح شده - منطق any)
            # کلماتی که باید نادیده گرفته شوند (کلمات دستوری مثل پرفروش)
            effective_filter_words = [w for w in text_words if w not in STOP_WORDS]
            
            if effective_filter_words:
                # چک کردن اینکه حداقل یکی از کلمات کلیدی در اسم محصول هست
                is_relevant = False
                for kw in effective_filter_words:
                    synonyms = expand_keywords(kw)
                    if kw in ENG_TRANSLATIONS:
                        synonyms.extend(ENG_TRANSLATIONS[kw])
                    
                    if any(syn.lower() in product_name for syn in synonyms):
                        is_relevant = True
                        break
                
                if not is_relevant:
                    continue

        if source_name in ["digikala", "torob"]:
            is_relevant = True

        if not is_relevant:
            continue
            
        # فیلتر اعداد (ضخامت، سایز و...)
        full_info = product_name
        if item.get('thickness'):
            full_info += " " + str(item['thickness']).lower()
        if item.get('dimensions'):
            full_info += " " + str(item['dimensions']).lower()
            
        match_numbers = True
        for num in number_words:
            if num not in full_info:
                match_numbers = False
                break
                
        if not match_numbers:
            continue
            
        # ✅ فیلتر متنی فقط اگه کلمات کلیدی متمایز وجود داشته باشن
        if source_rules.get("use_keyword_filter", True):
            # کلماتی که واقعاً معنادار هستند (نه کلمات دستوری)
            effective_filter_words = [w for w in text_words if w not in STOP_WORDS]
            
            if effective_filter_words:
                match_text = False
                for tw in effective_filter_words:
                    synonyms = expand_keywords(tw)
                    if tw in ENG_TRANSLATIONS:
                        synonyms.extend(ENG_TRANSLATIONS[tw])
                    
                    if any(syn.lower() in product_name for syn in synonyms):
                        match_text = True
                        break
                
                # اگه هیچ کلمه متمایزکننده‌ای پیدا نشد، رد کن (به جز MDF)
                if not match_text and not any(w in product_name for w in ["mdf", "ام دی اف", "تخته", "ورق"]):
                    continue
        
        # فیلتر بلاک‌لیست
        if source_rules.get("use_blacklist", True):
            if any(word in product_name for word in blacklist):
                continue
            
        filtered_results.append(item)
            
    results = []
    if filtered_results:
        filtered_results.sort(key=lambda x: x['price'])
        
        for item in filtered_results:
            # ✅ بازه قیمت بازتر
            if 10_000 < item['price'] < 1_000_000_000:
                results.append({
                    "source_id": "python_engine",
                    "source_name": "موتور جستجو",
                    "url": item.get('url', ''),
                    "image": item.get('image', ''),  # ✅ فیلد عکس
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