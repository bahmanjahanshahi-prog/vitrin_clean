from flask import Flask, render_template_string, request, abort
import subprocess
import json
import os
import sys
import requests
import time
import base64
import random

app = Flask(__name__)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# ================== تنظیمات گیت‌هاب ==================
GITHUB_USERNAME = "bahmanjahanshahi-prog"
GITHUB_REPO = "vitrin_clean"
GITHUB_BRANCH = "main"
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN", "")
# ======================================================

# ---------------------------------------------------------------
# قالب پایه (شامل هدر و فوتر مشترک)
# ---------------------------------------------------------------
BASE_TEMPLATE = """
<!DOCTYPE html>
<html lang="fa" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{% block title %}ویترین | بهترین قیمت‌ها{% endblock %}</title>
    <link href="https://fonts.googleapis.com/css2?family=Vazirmatn:wght@300;400;700&display=swap" rel="stylesheet">
    <style>
        :root {
            --bg-color: #0f172a;
            --card-bg: rgba(30, 41, 59, 0.7);
            --text-main: #f1f5f9;
            --text-sub: #94a3b8;
            --accent: #38bdf8;
            --accent-hover: #0ea5e9;
            --border: rgba(255, 255, 255, 0.1);
            --success: #4ade80;
            --danger: #f87171;
        }
        * { box-sizing: border-box; }
        body { 
            font-family: 'Vazirmatn', sans-serif; 
            background-color: var(--bg-color); 
            background-image: linear-gradient(180deg, #0f172a 0%, #1e1b4b 100%);
            color: var(--text-main); 
            margin: 0; 
            padding: 0; 
            min-height: 100vh;
            display: flex;
            flex-direction: column;
        }
        a { text-decoration: none; color: inherit; }
        
        /* Header */
        .header { 
            background: rgba(15, 23, 42, 0.8); 
            backdrop-filter: blur(12px); 
            border-bottom: 1px solid var(--border);
            padding: 15px 30px; 
            display: flex; 
            justify-content: space-between; 
            align-items: center; 
            position: sticky; 
            top: 0; 
            z-index: 100; 
            flex-wrap: wrap;
            gap: 15px;
        }
        .logo-area { display: flex; align-items: center; gap: 15px; }
        .logo-text { font-size: 26px; font-weight: 700; color: #fff; margin: 0; letter-spacing: -1px; }
        .slogan-text { font-size: 12px; color: var(--text-sub); border-right: 1px solid var(--border); padding-right: 15px; }
        
        /* Navigation */
        .nav-menu { display: flex; gap: 20px; }
        .nav-link { font-size: 14px; color: var(--text-sub); transition: color 0.3s; }
        .nav-link:hover { color: var(--accent); }

        /* Search */
        .search-container { width: 100%; max-width: 400px; position: relative; }
        .search-input { 
            width: 100%; padding: 10px 20px; font-size: 14px; border: 1px solid var(--border); 
            border-radius: 30px; outline: none; background: rgba(255,255,255,0.05); color: #fff; transition: all 0.3s ease;
        }
        .search-input:focus { border-color: var(--accent); background: rgba(255,255,255,0.1); }
        .search-btn { 
            position: absolute; left: 5px; top: 5px; bottom: 5px; background-color: var(--accent); 
            color: #0f172a; border: none; border-radius: 25px; padding: 0 15px; font-weight: bold; cursor: pointer; 
        }

        /* Main Layout */
        .main-content { flex: 1; max-width: 1300px; margin: 30px auto; padding: 0 20px; width: 100%; }
        
        /* Hero Section */
        .hero { text-align: center; padding: 50px 20px; background: rgba(56, 189, 248, 0.1); border-radius: 20px; margin-bottom: 40px; border: 1px solid var(--border); }
        .hero h1 { font-size: 32px; margin-bottom: 10px; font-weight: 700; }
        .hero p { font-size: 16px; color: var(--text-sub); }

        /* Section Title */
        .section-title { 
            font-size: 22px; color: var(--text-main); margin: 40px 0 20px 0; 
            display: flex; align-items: center; gap: 10px;
        }
        .section-title::before { content: ''; display: block; width: 5px; height: 22px; background: var(--accent); border-radius: 3px; }

        /* Grid */
        .grid-layout { display: grid; grid-template-columns: repeat(auto-fill, minmax(260px, 1fr)); gap: 20px; }
        
        /* Card */
        .card { 
            background: var(--card-bg); border: 1px solid var(--border); border-radius: 16px; 
            overflow: hidden; display: flex; flex-direction: column; transition: transform 0.3s, box-shadow 0.3s; 
        }
        .card:hover { transform: translateY(-5px); box-shadow: 0 10px 20px rgba(0,0,0,0.3); border-color: rgba(56, 189, 248, 0.3); }
        .card-image { width: 100%; height: 180px; object-fit: contain; background: rgba(0,0,0,0.2); padding: 15px; }
        .card-content { padding: 15px; display: flex; flex-direction: column; flex-grow: 1; }
        .card-title { font-size: 15px; font-weight: 700; margin-bottom: 10px; color: var(--text-main); line-height: 1.5; height: 45px; overflow: hidden; }
        .card-bottom { margin-top: auto; }
        .price-row { display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px; }
        .card-price { font-size: 16px; font-weight: 700; color: var(--accent); }
        .card-rating { font-size: 11px; color: #fbbf24; font-weight: bold; background: rgba(251, 191, 36, 0.1); padding: 3px 6px; border-radius: 6px; }
        .card-btn { 
            background: var(--accent); color: #0f172a; padding: 10px 0; border-radius: 10px; 
            text-align: center; font-weight: 700; font-size: 13px; transition: 0.3s; width: 100%; display: block; border: none; cursor: pointer;
        }
        .card-btn:hover { background: var(--accent-hover); }

        /* Product Detail */
        .product-detail { display: flex; flex-direction: column; gap: 30px; }
        @media (min-width: 768px) { .product-detail { flex-direction: row; } }
        .product-image-container { flex: 1; max-width: 500px; }
        .product-image-container img { width: 100%; border-radius: 20px; background: rgba(0,0,0,0.2); padding: 20px; }
        .product-info { flex: 1; }
        .product-info h1 { font-size: 24px; margin-bottom: 15px; }
        .product-info .price-tag { font-size: 28px; color: var(--accent); font-weight: 700; margin-bottom: 20px; }
        .product-description { font-size: 15px; color: var(--text-sub); line-height: 1.8; margin-bottom: 20px; }
        .product-description h3 { color: var(--text-main); margin-top: 20px; }
        .buy-btn { background: linear-gradient(90deg, var(--accent) 0%, #818cf8 100%); color: #fff; padding: 15px 30px; border-radius: 12px; font-weight: 700; font-size: 16px; display: inline-block; transition: 0.3s; border: none; cursor: pointer; }
        .buy-btn:hover { box-shadow: 0 0 15px rgba(56, 189, 248, 0.4); }

        /* Footer */
        .footer { background: rgba(15, 23, 42, 0.8); border-top: 1px solid var(--border); padding: 20px; text-align: center; color: var(--text-sub); font-size: 13px; margin-top: auto; }
        .footer a { color: var(--accent); margin: 0 10px; }

        .error-msg { color: var(--danger); text-align: center; padding: 20px; background: rgba(248, 113, 113, 0.1); border-radius: 12px; }
    </style>
</head>
<body>
    <div class="header">
        <div class="logo-area">
            <h1 class="logo-text"><a href="/">ویترین</a></h1>
            <div class="slogan-text">بهترین قیمت‌ها</div>
        </div>
        <div class="nav-menu">
            <a href="/" class="nav-link">خانه</a>
            <a href="/?category=digital" class="nav-link">دیجیتال</a>
            <a href="/?category=building" class="nav-link">ساختمان</a>
        </div>
        <form class="search-container" action="/" method="GET">
            <input type="text" name="q" class="search-input" placeholder="جستجوی محصول..." value="{{ query }}">
            <button type="submit" class="search-btn">جستجو</button>
        </form>
    </div>

    <div class="main-content">
        {% block content %}{% endblock %}
    </div>

    <div class="footer">
        <p>© ۲۰۲۶ ویترین | تمامی حقوق محفوظ است.</p>
        <p><a href="/about">درباره ما</a> | <a href="/contact">تماس با ما</a></p>
    </div>
</body>
</html>
"""

# ---------------------------------------------------------------
# قالب صفحه اصلی (Home)
# ---------------------------------------------------------------
HOME_TEMPLATE = BASE_TEMPLATE.replace("{% block content %}{% endblock %}", """
    {% if query %}
        <div class="section-title">نتایج جستجو برای: {{ query }}</div>
        {% if error %}<div class="error-msg">{{ error }}</div>
        {% elif results %}
            <div class="grid-layout">
                {% for item in results %}
                <div class="card">
                    {% if item.image %}<img src="{{ item.image }}" class="card-image" alt="عکس">{% else %}<div class="card-image" style="display:flex; align-items:center; justify-content:center; color:#475569;">بدون عکس</div>{% endif %}
                    <div class="card-content">
                        <div class="card-title">{{ item.note }}</div>
                        <div class="card-bottom">
                            <div class="price-row">
                                <div class="card-price">{{ "{:,}".format(item.price) }} تومان</div>
                                {% if item.rating and item.rating > 0 %}<div class="card-rating">⭐ {{ item.rating }}</div>{% endif %}
                            </div>
                            <a href="{{ item.url }}" target="_blank" class="card-btn">مشاهده و خرید</a>
                        </div>
                    </div>
                </div>
                {% endfor %}
            </div>
        {% else %}<div class="error-msg">هیچ محصولی با این عبارت پیدا نشد.</div>{% endif %}
    {% else %}
        <div class="hero">
            <h1>به ویترین خوش آمدید</h1>
            <p>بهترین کالاها با بهترین قیمت‌ها از منابع معتبر</p>
        </div>

        {% if main_feed %}
        <div class="section-title">🔥 پیشنهادهای ویژه امروز</div>
        <div class="grid-layout">
            {% for item in main_feed %}
            <div class="card">
                {% if item.image %}<img src="{{ item.image }}" class="card-image" alt="عکس">{% else %}<div class="card-image" style="display:flex; align-items:center; justify-content:center; color:#475569;">بدون عکس</div>{% endif %}
                <div class="card-content">
                    <div class="card-title">{{ item.title }}</div>
                    <div class="card-bottom">
                        <div class="price-row">
                            <div class="card-price">{{ "{:,}".format(item.price) }} تومان</div>
                            {% if item.rating and item.rating > 0 %}<div class="card-rating">⭐ {{ item.rating }}</div>{% endif %}
                        </div>
                        <a href="/product/{{ item.id }}" class="card-btn">مشاهده جزئیات</a>
                    </div>
                </div>
            </div>
            {% endfor %}
        </div>
        {% endif %}

        {% if digital_feed %}
        <div class="section-title">💻 ویترین دیجیتال</div>
        <div class="grid-layout">
            {% for item in digital_feed %}
            <div class="card">
                {% if item.image %}<img src="{{ item.image }}" class="card-image" alt="عکس">{% else %}<div class="card-image" style="display:flex; align-items:center; justify-content:center; color:#475569;">بدون عکس</div>{% endif %}
                <div class="card-content">
                    <div class="card-title">{{ item.title }}</div>
                    <div class="card-bottom">
                        <div class="price-row">
                            <div class="card-price">{{ "{:,}".format(item.price) }} تومان</div>
                            {% if item.rating and item.rating > 0 %}<div class="card-rating">⭐ {{ item.rating }}</div>{% endif %}
                        </div>
                        <a href="/product/{{ item.id }}" class="card-btn">مشاهده جزئیات</a>
                    </div>
                </div>
            </div>
            {% endfor %}
        </div>
        {% endif %}

        {% if building_feed %}
        <div class="section-title">🏗️ ویترین ساختمان</div>
        <div class="grid-layout">
            {% for item in building_feed %}
            <div class="card">
                {% if item.image %}<img src="{{ item.image }}" class="card-image" alt="عکس">{% else %}<div class="card-image" style="display:flex; align-items:center; justify-content:center; color:#475569;">بدون عکس</div>{% endif %}
                <div class="card-content">
                    <div class="card-title">{{ item.title }}</div>
                    <div class="card-bottom">
                        <div class="price-row">
                            <div class="card-price">{{ "{:,}".format(item.price) }} تومان</div>
                            {% if item.rating and item.rating > 0 %}<div class="card-rating">⭐ {{ item.rating }}</div>{% endif %}
                        </div>
                        <a href="/product/{{ item.id }}" class="card-btn">مشاهده جزئیات</a>
                    </div>
                </div>
            </div>
            {% endfor %}
        </div>
        {% endif %}
    {% endif %}
""")

# ---------------------------------------------------------------
# قالب صفحه محصول (Product Detail)
# ---------------------------------------------------------------
PRODUCT_TEMPLATE = BASE_TEMPLATE.replace("{% block content %}{% endblock %}", """
    <div class="product-detail">
        <div class="product-image-container">
            {% if product.image %}
                <img src="{{ product.image }}" alt="{{ product.title }}">
            {% else %}
                <div style="background: rgba(0,0,0,0.2); border-radius: 20px; height: 400px; display: flex; align-items: center; justify-content: center; color:#475569;">بدون عکس</div>
            {% endif %}
        </div>
        <div class="product-info">
            <h1>{{ product.title }}</h1>
            <div class="price-tag">{{ "{:,}".format(product.price) }} تومان</div>
            
            {% if product.description %}
            <div class="product-description">
                <h3>درباره این محصول</h3>
                <p>{{ product.description }}</p>
            </div>
            {% endif %}

            <a href="{{ product.url }}" target="_blank" class="buy-btn">🛒 خرید از {{ product.source if product.source else 'فروشگاه' }}</a>
        </div>
    </div>
""")

# ---------------------------------------------------------------
# توابع دریافت داده از گیت‌هاب
# ---------------------------------------------------------------
_cache = {}
CACHE_DURATION = 300

def get_github_json(file_path):
    now = time.time()
    if file_path in _cache and (now - _cache[file_path]['time']) < CACHE_DURATION:
        return _cache[file_path]['data'], None
    
    url = f"https://api.github.com/repos/{GITHUB_USERNAME}/{GITHUB_REPO}/contents/{file_path}"
    headers = {"Authorization": f"token {GITHUB_TOKEN}", "Accept": "application/vnd.github.v3+json"}
    try:
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code == 200:
            content = base64.b64decode(response.json()['content']).decode('utf-8')
            data = json.loads(content)
            _cache[file_path] = {'data': data, 'time': now}
            return data, None
        else:
            return [], f"Status Code: {response.status_code}"
    except Exception as e:
        return [], str(e)

def format_feed(data):
    feed = []
    if not isinstance(data, list): return feed
    for item in data:
        if isinstance(item, dict):
            # ✅ تولید id از url (بخش دوم) یا یک id تصادفی
            url = item.get("url", "")
            if url and "dkp-" in url:
                product_id = url.split("dkp-")[-1].strip("/")
            elif url and "/p/" in url:
                product_id = url.split("/p/")[-1].strip("/")
            else:
                product_id = str(random.randint(1000, 9999))
            
            feed.append({
                "id": product_id,
                "title": item.get("note", item.get("title", item.get("name", "نامشخص"))),
                "price": item.get("price", 0) or 0,
                "rating": item.get("rating", 0) or 0,
                "url": url if url else "#",
                "image": item.get("image", ""),
                "description": item.get("description", ""),
                "source": item.get("source", "فروشگاه"),
                "images": item.get("images", [])
            })
    return feed

# ---------------------------------------------------------------
# روت‌ها
# ---------------------------------------------------------------
@app.route('/health')
def health():
    return {"status": "ok"}, 200

@app.route('/')
def index():
    query = request.args.get('q', '')
    category = request.args.get('category', '')
    results = []
    error = None
    main_feed, digital_feed, building_feed = [], [], []

    if query:
        output_json = "/tmp/web_search_results.json"
        python_script = os.path.join(BASE_DIR, "main.py")
        
        if os.path.exists(output_json): os.remove(output_json)
        try:
            subprocess.run([sys.executable, python_script, query, "digikala,torob,choobro,basalam,technolife,khanoumi", output_json], check=True, timeout=600)
            if os.path.exists(output_json):
                with open(output_json, 'r', encoding='utf-8') as f:
                    results = json.load(f)
                if results and "error" in results[0]:
                    error = results[0]["error"]
                    results = []
        except Exception as e:
            error = f"خطا در جستجو."
    else:
        main_data, _ = get_github_json("showcase_data/main.json")
        digital_data, _ = get_github_json("showcase_data/digital.json")
        building_data, _ = get_github_json("showcase_data/building.json")

        main_feed = format_feed(main_data)
        digital_feed = format_feed(digital_data)
        building_feed = format_feed(building_data)

        if category == 'digital':
            main_feed, building_feed = [], []
        elif category == 'building':
            main_feed, digital_feed = [], []

    return render_template_string(HOME_TEMPLATE, query=query, results=results, 
                                  main_feed=main_feed, digital_feed=digital_feed, 
                                  building_feed=building_feed, error=error)

@app.route('/product/<product_id>')
def product_detail(product_id):
    all_products = []
    for file in ["main.json", "digital.json", "building.json"]:
        data, _ = get_github_json(f"showcase_data/{file}")
        all_products.extend(format_feed(data))

    product = next((p for p in all_products if p['id'] == product_id), None)
    
    if not product:
        abort(404)
    
    return render_template_string(PRODUCT_TEMPLATE, product=product)

@app.route('/about')
def about():
    return render_template_string(BASE_TEMPLATE.replace("{% block content %}{% endblock %}", """
        <div class="hero">
            <h1>درباره ویترین</h1>
            <p>ویترین یک پلتفرم مقایسه قیمت و راهنمای خرید است که با هدف کمک به کاربران برای پیدا کردن بهترین کالاها با بهترین قیمت‌ها راه‌اندازی شده است.</p>
        </div>
    """))

@app.route('/contact')
def contact():
    return render_template_string(BASE_TEMPLATE.replace("{% block content %}{% endblock %}", """
        <div class="hero">
            <h1>تماس با ما</h1>
            <p>برای ارتباط با ما می‌توانید به کانال تلگرام <strong>best_price_vitrin</strong> مراجعه کنید.</p>
        </div>
    """))

if __name__ == '__main__':
    app.run(debug=True, use_reloader=False)