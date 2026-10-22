# config.py

# تنظیمات مخصوص هر منبع
SOURCE_CONFIG = {
    # چوب‌رو: مخصوص MDF، هایگلاس، یراق‌آلات
    "choobro": {
        "use_keyword_filter": True,   # کلمات متنی را چک کن
        "use_blacklist": True,        # کلمات مزاحم را حذف کن
    },
    
    # ترب: مقایسه قیمت عمومی
    "torob": {
        "use_keyword_filter": True,
        "use_blacklist": True,
    },
    
    # دیجی‌کالا: کالاهای عمومی
    "digikala": {
        "use_keyword_filter": False,  # دیجی‌کالا سخت‌گیر نباش!
        "use_blacklist": False,
    },
    
    # ایمالز
    "emalls": {
        "use_keyword_filter": True,
        "use_blacklist": True,
    },
    
    # شهر یراق
    "shahreyaragh": {
        "use_keyword_filter": True,
        "use_blacklist": True,
    }
}