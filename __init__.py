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
    return items if items else [f"(找不到 {file_name} 或為空)"]

NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}

# ==========================================
# 2. 顏色選擇器 (獨立放到 Color 分類)
# ==========================================
class ColorSelector:
    @classmethod
    def INPUT_TYPES(s):
        return {"required": {"selected_color": (load_items("color.txt"), )}}
    
    RETURN_TYPES = ("STRING", "INT")
    RETURN_NAMES = ("顏色字串", "顏色編號")
    FUNCTION = "get_selection"
    CATEGORY = "MyCustomNodes/Color"

    def get_selection(self, selected_color):
        lst = load_items("color.txt")
        index = lst.index(selected_color) if selected_color in lst else 0
        return (selected_color, index)

NODE_CLASS_MAPPINGS["MyColorSelector"] = ColorSelector
NODE_DISPLAY_NAME_MAPPINGS["MyColorSelector"] = "🎨 顏色選擇器 (Color)"


# ==========================================
# 3. 髮型選擇器 (強制顏色變為連線輸入端點)
# ==========================================
class HairSelector:
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                # 髮型本身保留下拉選單
                "selected_hair": (load_items("hair.txt"), ),
                
                # 顏色部分改為 STRING 型態，並加上 "forceInput": True 強制變成連線端點
                "hair_color_main": ("STRING", {"forceInput": True}), 
                "hair_color_sub": ("STRING", {"forceInput": True}),
            }
        }
    
    RETURN_TYPES = ("STRING", "INT", "STRING", "STRING", "STRING")
    RETURN_NAMES = ("髮型字串", "髮型編號", "主色", "副色", "最終組合Prompt")
    FUNCTION = "get_selection"
    CATEGORY = "MyCustomNodes/Character_Outfit"

    def get_selection(self, selected_hair, hair_color_main, hair_color_sub):
        lst = load_items("hair.txt")
        index = lst.index(selected_hair) if selected_hair in lst else 0
        
        combined_prompt = f"主色{hair_color_main}與副色{hair_color_sub}的{selected_hair}"
        
        return (selected_hair, index, hair_color_main, hair_color_sub, combined_prompt)

NODE_CLASS_MAPPINGS["MyHairSelector"] = HairSelector
NODE_DISPLAY_NAME_MAPPINGS["MyHairSelector"] = "💇‍♀️ 髮型特化選擇器 (Hair)"


# ==========================================
# 4. 其他部位選擇器 (批次建立)
# ==========================================
FILE_MAPPINGS = {
    "accessories.txt": ("AccessoriesSelector", "💍 飾品選擇器 (Accessories)"),
    "bags.txt":        ("BagsSelector",        "🎒 包包選擇器 (Bags)"),
    "bottoms.txt":     ("BottomsSelector",     "👖 下著選擇器 (Bottoms)"),
    "neckwear.txt":    ("NeckwearSelector",    "🧣 頸部配件選擇器 (Neckwear)"),
    "shoes.txt":       ("ShoesSelector",       "👟 鞋子選擇器 (Shoes)"),
    "tops.txt":        ("TopsSelector",        "👕 上著選擇器 (Tops)"),
    "wrist.txt":       ("WristSelector",       "⌚ 腕部配件選擇器 (Wrist)"),
}

def create_selector_class(file_name):
    class DynamicSelectorNode:
        @classmethod
        def INPUT_TYPES(s):
            return {"required": {"selected_item": (load_items(file_name), )}}
        
        RETURN_TYPES = ("STRING", "INT")
        RETURN_NAMES = ("物品字串", "物品編號")
        FUNCTION = "get_selection"
        CATEGORY = "MyCustomNodes/Character_Outfit"

        def get_selection(self, selected_item):
            lst = load_items(file_name)
            index = lst.index(selected_item) if selected_item in lst else 0
            return (selected_item, index)
            
    return DynamicSelectorNode

for file_name, (class_name, display_name) in FILE_MAPPINGS.items():
    node_class = create_selector_class(file_name)
    NODE_CLASS_MAPPINGS[class_name] = node_class
    NODE_DISPLAY_NAME_MAPPINGS[class_name] = display_name

__all__ = ['NODE_CLASS_MAPPINGS', 'NODE_DISPLAY_NAME_MAPPINGS']