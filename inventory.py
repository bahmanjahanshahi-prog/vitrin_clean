import json
import os

DATA_DIR = "D:/MyAIProjects/serch/data"

def ensure_data_dir():
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)

def get_inventory_path(source_name, category_code):
    ensure_data_dir()
    return os.path.join(DATA_DIR, f"inventory_{source_name}_{category_code}.json")

def load_inventory(source_name, category_code):
    path = get_inventory_path(source_name, category_code)
    if not os.path.exists(path):
        return []
    try:
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception:
        return []

def save_to_inventory(source_name, category_code, new_products):
    inventory = load_inventory(source_name, category_code)
    inv_dict = {p['name']: p for p in inventory}
    
    added, updated = 0, 0
    for prod in new_products:
        name = prod.get('name')
        if not name: continue
        
        if name not in inv_dict:
            inv_dict[name] = prod
            added += 1
        else:
            if inv_dict[name].get('price') != prod.get('price'):
                inv_dict[name]['price'] = prod['price']
                updated += 1
    
    final_list = list(inv_dict.values())
    path = get_inventory_path(source_name, category_code)
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(final_list, f, ensure_ascii=False, indent=2)
    
    print(f"   💾 انبار {source_name}/{category_code}: {added} جدید، {updated} آپدیت. (کل: {len(final_list)})")
    return final_list

def load_all_categories(source_name):
    """لیست تمام دسته‌بندی‌های موجود برای یک منبع"""
    ensure_data_dir()
    prefix = f"inventory_{source_name}_"
    categories = []
    for f in os.listdir(DATA_DIR):
        if f.startswith(prefix) and f.endswith(".json"):
            cat = f[len(prefix):-5]  # حذف prefix و .json
            categories.append(cat)
    return categories