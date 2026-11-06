"""
filters.py — مغز فیلترهای اتاق فرمان ویترین
هیچ وابستگی به GUI نداره. فقط منطق خالص.
"""

import json
import os


def filter_products(
    products,
    min_rating=0,
    min_price=0,
    max_price=999999999,
    numbers_in_query=None,
    sellers=None,
    only_deals=False,
    min_reviews=0,
    custom_fields=None,
):
    """
    لیست محصولات رو با پارامترهای داده‌شده فیلتر می‌کنه.
    """
    if numbers_in_query is None:
        numbers_in_query = []
    if custom_fields is None:
        custom_fields = []

    filtered = []
    for item in products:
        price = item.get('price', 0) or 0
        rating = item.get('rating', 0) or 0
        name = (item.get('note') or '').lower()
        seller = (item.get('seller') or '').lower()
        review_count = item.get('review_count', 0) or 0

        # فیلتر امتیاز
        if rating < min_rating:
            continue

        # فیلتر قیمت
        if price < min_price or price > max_price:
            continue

        # فیلتر تعداد نظرات
        if review_count < min_reviews:
            continue

        # فیلتر فروشنده
        if sellers:
            sellers_lower = [s.lower() for s in sellers]
            if seller not in sellers_lower:
                continue

        # فیلتر تخفیف‌دار (حالا discount_pct هم چک میشه)
        if only_deals:
            has_discount = (
                item.get('discount') or
                item.get('old_price') or
                item.get('discount_percent') or
                item.get('discount_pct')
            )
            if not has_discount:
                continue

        # فیلتر اعداد (ضخامت/ابعاد)
        if numbers_in_query:
            has_number = any(num in name for num in numbers_in_query)
            if not has_number:
                continue

        # فیلتر فیلدهای سفارشی (داینامیک)
        if custom_fields:
            match_all = True
            for field in custom_fields:
                f_name = field.get('name', '').strip().lower()
                f_value = field.get('value', '').strip().lower()
                if not f_name and not f_value:
                    continue
                if f_name and f_name not in name:
                    match_all = False
                    break
                if f_value and f_value not in name:
                    match_all = False
                    break
            if not match_all:
                continue

        filtered.append(item)

    return filtered


def calculate_smart_scores(products):
    """
    به هر محصول یک امتیاز هوشمند (smart_score) اضافه می‌کنه.
    ترکیبی از قیمت (وزن 0.5)، امتیاز (وزن 0.3)، تعداد نظرات (وزن 0.2).
    """
    import math

    if not products:
        return []

    prices = [(i.get('price') or 0) for i in products if (i.get('price') or 0) > 0]
    if not prices:
        return list(products)
    min_p, max_p = min(prices), max(prices)

    result = []
    for item in products:
        item_copy = dict(item)
        price = item_copy.get('price', 0) or 0
        rating = item_copy.get('rating', 0) or 0
        review_count = item_copy.get('review_count', 0) or 0

        price_score = 1.0 - ((price - min_p) / (max_p - min_p + 1)) if max_p > min_p else 1.0
        rating_score = rating / 5.0
        review_score = min(1.0, math.log10(review_count + 1) / 4.0) if review_count > 0 else 0

        item_copy['smart_score'] = (price_score * 0.5) + (rating_score * 0.3) + (review_score * 0.2)
        result.append(item_copy)

    result.sort(key=lambda x: x.get('smart_score', 0), reverse=True)
    return result


def get_all_sellers(products):
    """لیست یکتای فروشنده‌ها رو از محصولات استخراج می‌کنه."""
    sellers = set()
    for item in products:
        s = item.get('seller')
        if s:
            sellers.add(s)
    return sorted(sellers)


# ---------------------------------------------------------------
# مدیریت PRESETS (الگوهای فیلتر)
# ---------------------------------------------------------------

DEFAULT_PRESETS = {
    "همه (بدون فیلتر)": {
        "min_rating": 0,
        "min_price": 0,
        "max_price": 999999999,
        "sellers": [],
        "only_deals": False,
        "min_reviews": 0,
    },
    "ارزان و باکیفیت": {
        "min_rating": 4.0,
        "min_price": 0,
        "max_price": 10000000,
        "sellers": [],
        "only_deals": True,
        "min_reviews": 20,
    },
    "فقط تخفیف‌دارها": {
        "min_rating": 0,
        "min_price": 0,
        "max_price": 999999999,
        "sellers": [],
        "only_deals": True,
        "min_reviews": 0,
    },
    "محبوب‌ها (نظرات بالا)": {
        "min_rating": 4.0,
        "min_price": 0,
        "max_price": 999999999,
        "sellers": [],
        "only_deals": False,
        "min_reviews": 100,
    },
    "فقط دیجی‌کالا": {
        "min_rating": 0,
        "min_price": 0,
        "max_price": 999999999,
        "sellers": ["دیجی‌کالا"],
        "only_deals": False,
        "min_reviews": 0,
    },
}


def load_presets(presets_file):
    """PRESETS رو از فایل JSON می‌خونه. اگه نبود، پیش‌فرض‌ها رو برمی‌گردونه."""
    if not os.path.exists(presets_file):
        return dict(DEFAULT_PRESETS)
    try:
        with open(presets_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        if not isinstance(data, dict):
            return dict(DEFAULT_PRESETS)
        for key, val in DEFAULT_PRESETS.items():
            data.setdefault(key, val)
        return data
    except Exception:
        return dict(DEFAULT_PRESETS)


def save_presets(presets_file, presets):
    """PRESETS رو توی فایل JSON ذخیره می‌کنه."""
    try:
        with open(presets_file, 'w', encoding='utf-8') as f:
            json.dump(presets, f, ensure_ascii=False, indent=2)
        return True
    except Exception:
        return False