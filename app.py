from flask import Flask, render_template_string, request
import subprocess
import json
import os
import sys

app = Flask(__name__)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="fa" dir="rtl">
<head>
    <meta charset="UTF-8">
    <title>ویترین | بهترین قیمت‌ها</title>
    <link href="https://fonts.googleapis.com/css2?family=Vazirmatn:wght@300;400;700&display=swap" rel="stylesheet">
    <style>
        body { font-family: 'Vazirmatn', sans-serif; background-color: #f7fafc; color: #333; margin: 0; padding: 0; }
        .header { background: #fff; box-shadow: 0 2px 10px rgba(0,0,0,0.05); padding: 15px 30px; display: flex; justify-content: space-between; align-items: center; }
        .logo-area { display: flex; align-items: center; gap: 15px; }
        .logo-text { font-size: 28px; font-weight: 700; color: #1a365d; margin: 0; }
        .search-container { width: 100%; max-width: 400px; position: relative; }
        .search-input { width: 100%; padding: 10px 15px; font-size: 14px; border: 2px solid #e2e8f0; border-radius: 20px; box-sizing: border-box; outline: none; }
        .search-btn { position: absolute; left: 5px; top: 5px; bottom: 5px; background-color: #3182ce; color: white; border: none; border-radius: 15px; padding: 0 15px; cursor: pointer; }
        .feed-container { max-width: 1200px; margin: 30px auto; padding: 0 20px; }
        .card { background: #fff; border: 1px solid #e2e8f0; border-radius: 16px; padding: 15px; display: flex; flex-direction: column; margin-bottom: 20px; }
        .grid-layout { display: grid; grid-template-columns: repeat(auto-fill, minmax(280px, 1fr)); gap: 20px; }
        .card-title { font-size: 14px; font-weight: 700; margin-bottom: 10px; height: 44px; overflow: hidden; }
        .card-price { font-size: 18px; font-weight: 700; color: #d32f2f; }
        .card-btn { background: #3182ce; color: white; padding: 12px 0; border-radius: 10px; text-decoration: none; text-align: center; margin-top: 10px; display: block; }
        .section-title { font-size: 22px; color: #2d3748; margin: 30px 0 20px; border-right: 4px solid #3182ce; padding-right: 10px; }
        .error-msg { color: #e53e3e; text-align: center; font-weight: bold; padding: 20px; background: #fff5f5; border-radius: 8px; }
    </style>
</head>
<body>
    <div class="header">
        <div class="logo-area">
            <h1 class="logo-text">ویترین</h1>
        </div>
        <form class="search-container" action="/" method="GET">
            <input type="text" name="q" class="search-input" placeholder="جستجوی محصول..." value="{{ query }}">
            <button type="submit" class="search-btn">جستجو</button>
        </form>
    </div>

    <div class="feed-container">
        {% if query %}
            <div class="section-title">نتایج جستجو برای: {{ query }}</div>
            {% if error %}
                <div class="error-msg">{{ error }}</div>
            {% elif results %}
                <div class="grid-layout">
                    {% for item in results %}
                    <div class="card">
                        <div class="card-title">{{ item.note }}</div>
                        <div class="card-price">{{ "{:,}".format(item.price) }} تومان</div>
                        <a href="{{ item.url }}" target="_blank" class="card-btn">مشاهده و خرید</a>
                    </div>
                    {% endfor %}
                </div>
            {% else %}
                <div class="error-msg">محصولی یافت نشد.</div>
            {% endif %}
        {% else %}
            <div class="section-title">👋 به ویترین خوش آمدید</div>
            <p style="text-align:center; color:#718096;">برای شروع، نام محصول مورد نظر خود را جستجو کنید.</p>
        {% endif %}
    </div>
</body>
</html>
"""

@app.route('/')
def index():
    query = request.args.get('q', '')
    results = []
    error = None

    if query:
        output_json = "/tmp/web_search_results.json"
        python_script = os.path.join(BASE_DIR, "main.py")
        
        if os.path.exists(output_json): os.remove(output_json)
        try:
            # اجرای main.py با مسیر نسبی و پایتون سرور
            subprocess.run([sys.executable, python_script, query, "digikala,torob,choobro", output_json], check=True, timeout=60)
            if os.path.exists(output_json):
                with open(output_json, 'r', encoding='utf-8') as f:
                    results = json.load(f)
                if results and "error" in results[0]:
                    error = results[0]["error"]
                    results = []
        except Exception as e:
            error = f"خطا در جستجو: {str(e)}"

    return render_template_string(HTML_TEMPLATE, query=query, results=results, error=error)

if __name__ == '__main__':
    app.run(debug=True)
