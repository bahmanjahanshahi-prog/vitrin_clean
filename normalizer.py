import re

def normalize_text(text):
    if not text:
        return ""
    
    text = str(text)
    
    # 1. تبدیل اعداد فارسی و عربی به انگلیسی
    persian_digits = '۰۱۲۳۴۵۶۷۸۹'
    arabic_digits = '٠١٢٣٤٥٦٧٨٩'
    english_digits = '0123456789'
    translation_table = str.maketrans(persian_digits + arabic_digits, english_digits + english_digits)
    text = text.translate(translation_table)
    
    # 2. یکسان‌سازی حروف عربی/فارسی (ي -> ی , ك -> ک)
    text = text.replace('ي', 'ی').replace('ك', 'ک')
    
    # 3. حذف فاصله‌های اضافی
    text = re.sub(r'\s+', ' ', text).strip()
    
    # 4. تبدیل به حروف کوچک برای اینکه MDF با mdf فرقی نداشته باشه
    # (البته برای نمایش فارسی مشکلی ایجاد نمی‌کنه، فقط برای تطبیق در انگلیسی)
    text = text.lower()
    
    return text

def normalize_product(item):
    """یک محصول رو می‌گیره و فیلدهاش رو تمیز می‌کنه"""
    if not isinstance(item, dict):
        return item
        
    normalized = item.copy()
    
    # تمیز کردن اسم و مشخصات
    if 'name' in normalized:
        normalized['name'] = normalize_text(normalized['name'])
    if 'thickness' in normalized:
        normalized['thickness'] = normalize_text(normalized['thickness'])
    if 'dimensions' in normalized:
        normalized['dimensions'] = normalize_text(normalized['dimensions'])
    if 'seller' in normalized:
        normalized['seller'] = normalize_text(normalized['seller'])
        
    return normalized