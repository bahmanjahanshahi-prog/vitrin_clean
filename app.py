from flask import Flask, render_template_string, request
import subprocess
import json
import os
import sys
import requests
import time

app = Flask(__name__)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# ================== تنظیمات گیت‌هاب ==================
GITHUB_USERNAME = "bahmanjahanshahi-prog"
GITHUB_REPO = "vitrin_clean"
GITHUB_BRANCH = "main"
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN", "")
# ======================================================

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="fa" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ویترین | بهترین قیمت‌ها</title>
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
        }
        body { 
            font-family: 'Vazirmatn', sans-serif; 
            background-color: var(--bg-color); 
            background-image: linear-gradient(180deg, #0f172a 0%, #1e1b4b 100%);
            color: var(--text-main); 
            margin: 0; 
            padding: 0; 
            min-height: 100vh;
        }
        
        /* Header */
        .header { 
            background: rgba(15, 23, 42, 0.8); 
            backdrop-filter: blur(12px); 
            border-bottom: 1px solid var(--border);
            padding: 20px 40px; 
            display: flex; 
            justify-content: space-between; 
            align-items: center; 
            position: sticky; 
            top: 0; 
            z-index: 100; 
        }
        .logo-area { display: flex; align-items: center; gap: 15px; }
        .logo-text { font-size: 28px; font-weight: 700; color: #fff; margin: 0; letter-spacing: -1px; }
        .slogan-text { font-size: 13px; color: var(--text-sub); font-weight: 300; border-right: 1px solid var(--border); padding-right: 15px; }
        
        /* Search */
        .search-container { width: 100%; max-width: 500px; position: relative; }
        .search-input { 
            width: 100%; 
            padding: 12px 20px; 
            font-size: 14px; 
            border: 1px solid var(--border); 
            border-radius: 30px; 
            box-sizing: border-box; 
            font-family: inherit; 
            outline: none; 
            background: rgba(255,255,255,0.05); 
            color: #fff;
            transition: all 0.3s ease;
        }
        .search-input:focus { border-color: var(--accent); background: rgba(255,255,255,0.1); }
        .search-btn { 
            position: absolute; 
            left: 5px; 
            top: 5px; 
            bottom: 5px; 
            background-color: var(--accent); 
            color: #0f172a; 
            border: none; 
            border-radius: 25px; 
            padding: 0 20px; 
            font-family: inherit; 
            font-weight: bold;
            cursor: pointer; 
            transition: background 0.3s; 
        }
        .search-btn:hover { background-color: var(--accent-hover); }

        /* Hero Section */
        .hero {
            text-align: center;
            padding: 60px 20px;
            background: url('https://images.unsplash.com/photo-1451187580459-43490279c0fa?q=80&w=2072&auto=format&fit=crop') no-repeat center center;
            background-size: cover;
            position: relative;
        }
        .hero::before {
            content: '';
            position: absolute;
            top: 0; left: 0; right: 0; bottom: 0;
            background: rgba(15, 23, 42, 0.8);
        }
        .hero-content { position: relative; z-index: 1; max-width: 800px; margin: 0 auto; }
        .hero h2 { font-size: 36px; margin-bottom: 10px; font-weight: 700; }
        .hero p { font-size: 16px; color: var(--text-sub); margin-bottom: 30px; }

        /* Main Layout */
        .feed-container { max-width: 1300px; margin: 40px auto; padding: 0 20px; }
        
        /* Filter Bar */
        .filter-bar {
            display: flex;
            gap: 15px;
            margin-bottom: 30px;
            overflow-x: auto;
            padding-bottom: 10px;
        }
        .filter-btn {
            background: var(--card-bg);
            border: 1px solid var(--border);
            color: var(--text-main);
            padding: 10px 20px;
            border-radius: 12px;
            cursor: pointer;
            font-family: inherit;
            white-space: nowrap;
            transition: all 0.3s;
        }
        .filter-btn:hover, .filter-btn.active {
            background: var(--accent);
            color: #0f172a;
            border-color: var(--accent);
        }

        /* Grid */
        .grid-layout { 
            display: grid; 
            grid-template-columns: repeat(auto-fill, minmax(280px, 1fr)); 
            gap: 25px; 
        }
        
        /* Card */
        .card { 
            background: var(--card-bg); 
            border: 1px solid var(--border); 
            border-radius: 20px; 
            overflow: hidden; 
            display: flex; 
            flex-direction: column; 
            transition: transform 0.3s, box-shadow 0.3s; 
        }
        .card:hover { 
            transform: translateY(-8px); 
            box-shadow: 0 15px 30px rgba(0,0,0,0.3); 
            border-color: rgba(56, 189, 248, 0.3);
        }
        .card-image { 
            width: 100%; 
            height: 200px; 
            object-fit: contain; 
            background: rgba(0,0,0,0.2); 
            padding: 20px; 
            box-sizing: border-box; 
        }
        .card-content { padding: 20px; display: flex; flex-direction: column; flex-grow: 1; }
        .card-title { font-size: 15px; font-weight: 700; margin-bottom: 15px; color: var(--text-main); line-height: 1.6; height: 48px; overflow: hidden; }
        .card-bottom { margin-top: auto; }
        .price-row { display: flex; justify-content: space-between; align-items: center; margin-bottom: 15px; }
        .card-price { font-size: 18px; font-weight: 700; color: var(--accent); }
        .card-rating { font-size: 12px; color: #fbbf24; font-weight: bold; background: rgba(251, 191, 36, 0.1); padding: 4px 8px; border-radius: 8px; }
        .card-btn { 
            background: linear-gradient(90deg, var(--accent) 0%, #818cf8 100%); 
            color: #fff; 
            padding: 12px 0; 
            border-radius: 12px; 
            text-decoration: none; 
            text-align: center; 
            font-weight: 700; 
            font-size: 14px; 
            transition: 0.3s; 
            width: 100%; 
            display: block; 
            border: none;
        }
        .card-btn:hover { 
            background: linear-gradient(90deg, #818cf8 0%, var(--accent) 100%); 
            box-shadow: 0 0 15px rgba(56, 189, 248, 0.4);
        }
        
        .section-title { 
            font-size: 24px; 
            color: var(--text-main); 
            margin: 0 0 25px 0; 
            display: flex;
            align-items: center;
            gap: 10px;
        }
        .section-title::before {
            content: '';
            display: block;
            width: 6px;
            height: 24px;
            background: var(--accent);
            border-radius: 3px;
        }
        .error-msg { color: #f87171; text-align: center; font-weight: bold; padding: 20px; background: rgba(248, 113, 113, 0.1); border-radius: 12px; margin-bottom: 20px; }
    </style>
</head>
<body>
    <div class="header">
        <div class="logo-area">
            <h1 class="logo-text">ویترین</h1>
            <div class="slogan-text">بهترین قیمت‌ها</div>
        </div>
        <form class="search-container" action="/" method="GET">
            <input type="text" name="q" class="search-input" placeholder="جستجوی محصول در منابع مختلف..." value="{{ query }}">
            <button type="submit" class="search-btn">جستجو</button>
        </form>
    </div>

    {% if not query %}
    <div class="hero">
        <div class="hero-content">
            <h2>به ویترین خوش آمدید</h2>
            <p>بهترین کالاها با بهترین قیمت‌ها از منابع معتبر</p>
        </div>
    </div>
    {% endif %}

    <div class="feed-container">
        {% if query %}
            <div class="section-title">نتایج جستجو برای: {{ query }}</div>
            
            <div class="filter-bar">
                <button class="filter-btn active">همه</button>
                <button class="filter-btn">دیجی‌کالا</button>
                <button class="filter-btn">باسلام</button>
                <button class="filter-btn">تکنولایف</button>
            </div>

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
            <div class="section-title">🔥 پیشنهادهای ویژه امروز</div>
            {% if feed %}
            <div class="grid-layout">
                {% for item in feed %}
                <div class="card">
                    {% if item.image %}<img src="{{ item.image }}" class="card-image" alt="عکس">{% else %}<div class="card-image" style="display:flex; align-items:center; justify-content:center; color:#475569;">بدون عکس</div>{% endif %}
                    <div class="card-content">
                        <div class="card-title">{{ item.title }}</div>
                        <div class="card-bottom">
                            <div class="price-row">
                                <div class="card-price">{{ "{:,}".format(item.price) }} تومان</div>
                                {% if item.rating and item.rating > 0 %}<div class="card-rating">⭐ {{ item.rating }}</div>{% endif %}
                            </div>
                            <a href="{{ item.url if item.url else '#' }}" target="_blank" class="card-btn">مشاهده و خرید</a>
                        </div>
                    </div>
                </div>
                {% endfor %}
            </div>
            {% else %}
            <div class="error-msg">هنوز محصولی به ویترین اضافه نشده است. (فایل main.json خالی است)</div>
            {% endif %}
        {% endif %}
    </div>
</body>
</html>
"""

_cache_data = None
_cache_time = 0
CACHE_DURATION = 300  # 5 minutes

def get_github_json(file_path):
    global _cache_data, _cache_time
    if _cache_data is not None and (time.time() - _cache_time) < CACHE_DURATION:
        return _cache_data, None
    
    url = f"https://api.github.com/repos/{GITHUB_USERNAME}/{GITHUB_REPO}/contents/{file_path}"
    headers = {"Authorization": f"token {GITHUB_TOKEN}", "Accept": "application/vnd.github.v3+json"}
    try:
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code == 200:
            import base64
            content = base64.b64decode(response.json()['content']).decode('utf-8')
            data = json.loads(content)
            _cache_data = data
            _cache_time = time.time()
            return data, None
        else:
            return [], f"Status Code: {response.status_code}"
    except Exception as e:
        return [], str(e)

@app.route('/health')
def health():
    return {"status": "ok"}, 200

@app.route('/')
def index():
    query = request.args.get('q', '')
    results = []
    error = None
    feed = []
    debug_error = None

    if query:
        output_json = "/tmp/web_search_results.json"
        python_script = os.path.join(BASE_DIR, "main.py")
        
        if os.path.exists(output_json): os.remove(output_json)
        try:
            subprocess.run([sys.executable, python_script, query, "digikala,torob,choobro,basalam,technolife,khanoumi", output_json], check=True, timeout=60)
            if os.path.exists(output_json):
                with open(output_json, 'r', encoding='utf-8') as f:
                    results = json.load(f)
                if results and "error" in results[0]:
                    error = results[0]["error"]
                    results = []
        except Exception as e:
            error = f"خطا در جستجو."
    else:
        data, debug_error = get_github_json("showcase_data/main.json")
        for item in data:
            feed.append({
                "title": item.get("note", "نامشخص"),
                "price": item.get("price", 0) or 0,
                "rating": item.get("rating", 0) or 0,
                "url": item.get("url", "#"),
            })

    return render_template_string(HTML_TEMPLATE, query=query, results=results, feed=feed, error=error, debug_error=debug_error)

if __name__ == '__main__':
    app.run(debug=True, use_reloader=False)