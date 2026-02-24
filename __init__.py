import os

current_dir = os.path.dirname(os.path.abspath(__file__))

# 1. 共用的檔案讀取函式
def load_items(file_name):
    file_path = os.path.join(current_dir, file_name)
    items = []
    if os.path.exists(file_path):
        with open(file_path, "r", encoding="utf-8") as f:
            for line in f:
                item = line.strip()
                if item:
                    items.append(item)
    # 防呆：如果檔案不存在或沒內容，顯示提示
    return items if items else [f"(找不到 {file_name} 或為空)"]

NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}

# ==========================================
# 2. 定義你的 8 個檔案清單與專屬的節點名稱
# 格式： "檔案名稱": ("內部類別名稱", "畫面上顯示的名稱")
# ==========================================
FILE_MAPPINGS = {
    "accessories.txt": ("AccessoriesSelector", "💍 飾品選擇器 (Accessories)"),
    "bags.txt":        ("BagsSelector",        "🎒 包包選擇器 (Bags)"),
    "bottoms.txt":     ("BottomsSelector",     "👖 下著選擇器 (Bottoms)"),
    "hair.txt":        ("HairSelector",        "💇‍♀️ 髮型選擇器 (Hair)"),
    "neckwear.txt":    ("NeckwearSelector",    "🧣 頸部配件選擇器 (Neckwear)"),
    "shoes.txt":       ("ShoesSelector",       "👟 鞋子選擇器 (Shoes)"),
    "tops.txt":        ("TopsSelector",        "👕 上著選擇器 (Tops)"),
    "wrist.txt":       ("WristSelector",       "⌚ 腕部配件選擇器 (Wrist)"),
}

# ==========================================
# 3. 節點產生器 (Factory)
# ==========================================
def create_selector_class(file_name):
    class DynamicSelectorNode:
        @classmethod
        def INPUT_TYPES(s):
            # 每個節點只會載入自己對應的那個 txt 檔
            return {"required": {"selected_item": (load_items(file_name), )}}
        
        RETURN_TYPES = ("STRING", "INT")
        RETURN_NAMES = ("物品字串", "物品編號")
        FUNCTION = "get_selection"
        # 將它們統一收納在一個專屬的右鍵選單分類中
        CATEGORY = "MyCustomNodes/Character_Outfit" 

        def get_selection(self, selected_item):
            lst = load_items(file_name)
            index = lst.index(selected_item) if selected_item in lst else 0
            return (selected_item, index)
            
    return DynamicSelectorNode

# ==========================================
# 4. 批次建立並註冊這 8 個節點
# ==========================================
for file_name, (class_name, display_name) in FILE_MAPPINGS.items():
    # 呼叫產生器，為該檔案量身打造一個節點類別
    node_class = create_selector_class(file_name)
    
    # 註冊到 ComfyUI 系統中
    NODE_CLASS_MAPPINGS[class_name] = node_class
    NODE_DISPLAY_NAME_MAPPINGS[class_name] = display_name

# 導出設定
__all__ = ['NODE_CLASS_MAPPINGS', 'NODE_DISPLAY_NAME_MAPPINGS']