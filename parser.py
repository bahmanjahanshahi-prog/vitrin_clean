import re

def parse_search_query(query):
    """
    این تابع یک جمله جستجو (مثل 'MDF سفید 16 183*366') رو می‌گیره
    و اون رو به بخش‌های مختلف (اسم، نوع، ضخامت، ابعاد) تقسیم می‌کنه.
    """
    query = query.strip().lower()
    if not query:
        return {"name": None, "type_brand": None, "thickness": None, "dimensions": None}

    # ۱. پیدا کردن ابعاد (الگوی عدد*عدد)
    dimensions = None
    dim_match = re.search(r'(\d+)\s*[*x×]\s*(\d+)', query)
    if dim_match:
        dimensions = f"{dim_match.group(1)}*{dim_match.group(2)}"
        query = query.replace(dim_match.group(0), '') # حذف ابعاد از جمله

    # ۲. پیدا کردن ضخامت (عددی که قبلش کلمه میل/مم/میلی‌متر یا خودش عدد تنها باشه)
    thickness = None
    # الگوهای رایج: 16, 16mm, 16میل, ۱۶
    thick_match = re.search(r'\b(\d{1,2})\s*(?:mm|میل|میلی|میلی‌متر)?\b', query)
    if thick_match:
        thickness = thick_match.group(1)
        query = query.replace(thick_match.group(0), '') # حذف ضخامت از جمله

    # ۳. پیدا کردن اسم کالا (کلمات کلیدی شناخته شده)
    name = None
    known_names = ['mdf', 'ورق', 'تخته', 'لولا', 'ریل', 'لبه', 'پیچ', 'دستگیره']
    for n in known_names:
        if n in query:
            name = n
            query = query.replace(n, '')
            break

    # ۴. هر چیزی که باقی موند، به عنوان نوع/برند در نظر می‌گیریم (مثل سفید، رنگی، هایگلاس)
    type_brand = query.strip()
    if not type_brand:
        type_brand = None

    return {
        "name": name,
        "type_brand": type_brand,
        "thickness": thickness,
        "dimensions": dimensions
    }

# تست دستی
if __name__ == "__main__":
    tests = [
        "MDF سفید 16 183*366",
        "لولا گازور",
        "MDF هایگلاس",
        "16 میل سفید",
        "MDF 18 122*280"
    ]
    for t in tests:
        print(f"'{t}' -> {parse_search_query(t)}")