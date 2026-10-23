from flask import Flask, render_template_string, request
import subprocess
import json
import os
import sys
import requests

app = Flask(__name__)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# ================== تنظیمات گیت‌هاب ==================
GITHUB_USERNAME = "bahmanjahanshahi-prog"
GITHUB_REPO = "vitrin_clean"
GITHUB_BRANCH = "main"
GITHUB_TOKEN = "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"
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
        body { font-family: 'Vazirmatn', sans-serif; background-color: #f7fafc; color: #333; margin: 0; padding: 0; }
        .header { background: rgba(255, 255, 255, 0.95); backdrop-filter: blur(10px); box-shadow: 0 2px 10px rgba(0,0,0,0.05); padding: 15px 30px; display: flex; justify-content: space-between; align-items: center; position: sticky; top: 0; z-index: 100; }
        .logo-area { display: flex; align-items: center; gap: 15px; }
        .logo-text { font-size: 28px; font-weight: 700; color: #1a365d; margin: 0; letter-spacing: -1px; }
        .slogan-text { font-size: 13px; color: #718096; font-weight: 300; border-right: 1px solid #e2e8f0; padding-right: 15px; }
        .search-container { width: 100%; max-width: 400px; position: relative; }
        .search-input { width: 100%; padding: 10px 15px; font-size: 14px; border: 2px solid #e2e8f0; border-radius: 20px; box-sizing: border-box; font-family: inherit; transition: all 0.3s ease; outline: none; background: #f7fafc; }
        .search-input:focus { border-color: #3182ce; background: #fff; }
        .search-btn { position: absolute; left: 5px; top: 5px; bottom: 5px; background-color: #3182ce; color: white; border: none; border-radius: 15px; padding: 0 15px; font-family: inherit; font-size: 13px; cursor: pointer; transition: background 0.3s; }
        .search-btn:hover { background-color: #2b6cb0; }
        .feed-container { max-width: 1200px; margin: 30px auto; padding: 0 20px; }
        .card { background: #fff; border: 1px solid #e2e8f0; border-radius: 16px; overflow: hidden; display: flex; flex-direction: column; box-shadow: 0 4px 6px rgba(0,0,0,0.02); transition: transform 0.3s, box-shadow 0.3s; margin-bottom: 20px; }
        .card:hover { transform: translateY(-5px); box-shadow: 0 10px 25px rgba(0,0,0,0.1); }
        .grid-layout { display: grid; grid-template-columns: repeat(auto-fill, minmax(280px, 1fr)); gap: 20px; }
        .card-image { width: 100%; height: 220px; object-fit: contain; background: #f7fafc; padding: 20px; box-sizing: border-box; }
        .card-content { padding: 15px; display: flex; flex-direction: column; flex-grow: 1; }
        .card-title { font-size: 14px; font-weight: 700; margin-bottom: 10px; color: #2d3748; line-height: 1.6; height: 44px; overflow: hidden; }
        .card-bottom { margin-top: auto; }
        .price-row { display: flex; justify-content: space-between; align-items: center; margin-bottom: 15px; }
        .card-price { font-size: 18px; font-weight: 700; color: #d32f2f; }
        .card-rating { font-size: 13px; color: #ff9800; font-weight: bold; background: #fffaf0; padding: 4px 8px; border-radius: 8px; }
        .card-btn { background: #3182ce; color: white; padding: 12px 0; border-radius: 10px; text-decoration: none; text-align: center; font-weight: 700; font-size: 14px; transition: 0.3s; width: 100%; display: block; }
        .card-btn:hover { background: #2b6cb0; }
        .section-title { font-size: 22px; color: #2d3748; margin: 30px 0 20px; border-right: 4px solid #3182ce; padding-right: 10px; font-weight: 700; }
        .error-msg { color: #e53e3e; text-align: center; font-weight: bold; padding: 20px; background: #fff5f5; border-radius: 8px; margin-bottom: 20px; word-break: break-all; }
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

    <div class="feed-container">
        {% if query %}
            <div class="section-title">نتایج جستجو برای: {{ query }}</div>
            {% if error %}<div class="error-msg">{{ error }}</div>
            {% elif results %}
                <div class="grid-layout">
                    {% for item in results %}
                    <div class="card">
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
            
            {% if debug_error %}
                <div class="error-msg">خطا در خواندن از گیت‌هاب: {{ debug_error }}</div>
            {% elif feed %}
            <div class="grid-layout">
                {% for item in feed %}
                <div class="card">
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

def get_github_json(file_path):
    """فایل JSON رو از لینک خام گیت‌هاب با احراز هویت می‌خونه."""
    url = f"https://raw.githubusercontent.com/{GITHUB_USERNAME}/{GITHUB_REPO}/{GITHUB_BRANCH}/{file_path}"
    headers = {
        "Authorization": f"Bearer {GITHUB_TOKEN}",
        "User-Agent": "Vitrin-App"
    }
    try:
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code == 200:
            return response.json(), None
        else:
            return [], f"Status Code: {response.status_code} - {response.text[:100]}"
    except Exception as e:
        return [], str(e)

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