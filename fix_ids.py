import json
import os

DATA_DIR = "showcase_data"
MAIN_FILE = os.path.join(DATA_DIR, "main.json")

def fix_ids():
    if not os.path.exists(MAIN_FILE):
        print("فایل main.json پیدا نشد!")
        return

    with open(MAIN_FILE, 'r', encoding='utf-8') as f:
        products = json.load(f)

    for item in products:
        url = item.get('url', '')
        if 'dkp-' in url:
            item['id'] = url.split('dkp-')[-1].strip('/')
        elif '/p/' in url:
            item['id'] = url.split('/p/')[-1].strip('/')
        else:
            item['id'] = str(abs(hash(item.get('note', ''))))[:8]

    with open(MAIN_FILE, 'w', encoding='utf-8') as f:
        json.dump(products, f, ensure_ascii=False, indent=2)

    print(f"✅ {len(products)} محصول آپدیت شد و id بهشون اضافه شد.")

if __name__ == "__main__":
    fix_ids()