import json
import os

DICT_FILE = "D:/MyAIProjects/serch/data/dictionary.json"

# دسته‌بندی‌های پیش‌فرض
DEFAULT_CATEGORIES = {
    "mdf_kham": ["خام", "raw"],
    "mdf_sefid": ["سفید", "صابونی", "white"],
    "mdf_rangi": ["رنگی", "ملامینه", "طرح چوب", "طرح بتن"],
    "highgloss": ["هایگلاس", "براق", "پلی گلاس", "highgloss"],
    "neopan": ["نئوپان", "neopan", "chipboard"],
    "pvc": ["پی وی سی", "نوار لبه", "pvc", "edge"],
    "corian": ["کورین", "corian"],
    "hdf": ["اچ دی اف", "hdf"],
    "lola": ["لولا", "hinge"],
    "rail": ["ریل", "کشو", "ریل کشو", "slide"],
    "paye": ["پایه", "پایه کابینت"],
    "sabad": ["سبد", "سبد آبچکون", "آبچکون"],
    "sink": ["سینک", "سینک ظرفشویی"],
    "safe_kabinet": ["صفحه کابینت", "صفحه کابینت"]
}

def ensure_data_dir():
    if not os.path.exists("D:/MyAIProjects/serch/data"):
        os.makedirs("D:/MyAIProjects/serch/data")

def load_dictionary():
    ensure_data_dir()
    if not os.path.exists(DICT_FILE):
        save_dictionary(DEFAULT_CATEGORIES)
        return DEFAULT_CATEGORIES
    try:
        with open(DICT_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception:
        return DEFAULT_CATEGORIES

def save_dictionary(dict_data):
    ensure_data_dir()
    with open(DICT_FILE, 'w', encoding='utf-8') as f:
        json.dump(dict_data, f, ensure_ascii=False, indent=2)

def detect_category(query):
    """تشخیص دسته‌بندی بر اساس کلمات کلیدی"""
    dictionary = load_dictionary()
    query_lower = query.lower()
    
    for cat_code, keywords in dictionary.items():
        for kw in keywords:
            if kw in query_lower:
                return cat_code
    return None

def add_new_category(category_code, keywords):
    """اضافه کردن دسته‌بندی جدید (پویا)"""
    dictionary = load_dictionary()
    if category_code not in dictionary:
        dictionary[category_code] = keywords
        save_dictionary(dictionary)
        print(f"   🆕 دسته‌بندی جدید ساخته شد: {category_code}")
    return category_code

def expand_keywords(query):
    """گسترش کلمات برای جستجوی بهتر"""
    words = query.lower().split()
    expanded = set(words)
    dictionary = load_dictionary()
    
    for cat_code, keywords in dictionary.items():
        for kw in keywords:
            if kw in words or any(w in kw for w in words):
                expanded.update(keywords)
                expanded.add(cat_code)
    return list(expanded)