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
# 2. 顏色選擇器 (維持不變)
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
# 3. 髮型選擇器 (加入專屬前綴)
# ==========================================
class HairSelector:
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "selected_hair": (load_items("hair.txt"), ),
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
        
        # 加上「留著」作為前綴
        combined_prompt = f"留著主色{hair_color_main}與副色{hair_color_sub}的{selected_hair}"
        
        return (selected_hair, index, hair_color_main, hair_color_sub, combined_prompt)

NODE_CLASS_MAPPINGS["MyHairSelector"] = HairSelector
NODE_DISPLAY_NAME_MAPPINGS["MyHairSelector"] = "💇‍♀️ 髮型特化選擇器 (Hair)"


# ==========================================
# 4. 其他部位選擇器 (配置升級：綁定專屬前綴詞)
# ==========================================
# 格式改為： "檔案名稱": ("類別名稱", "顯示名稱", "專屬前綴詞")
FILE_MAPPINGS = {
    "accessories.txt": ("AccessoriesSelector", "💍 飾品選擇器 (Accessories)", "配戴著"),
    "bags.txt":        ("BagsSelector",        "🎒 包包選擇器 (Bags)",        "背著"),
    "bottoms.txt":     ("BottomsSelector",     "👖 下著選擇器 (Bottoms)",     "下半身穿著"),
    "neckwear.txt":    ("NeckwearSelector",    "🧣 頸部配件選擇器 (Neckwear)", "脖子上圍著"),
    "shoes.txt":       ("ShoesSelector",       "👟 鞋子選擇器 (Shoes)",       "腳上穿著"),
    "tops.txt":        ("TopsSelector",        "👕 上著選擇器 (Tops)",        "上半身穿著"),
    "wrist.txt":       ("WristSelector",       "⌚ 腕部配件選擇器 (Wrist)",    "手腕上配戴著"),
}

# 讓產生器接收第三個參數 prefix_text
def create_selector_class(file_name, prefix_text):
    class DynamicSelectorNode:
        @classmethod
        def INPUT_TYPES(s):
            return {
                "required": {
                    "selected_item": (load_items(file_name), ),
                    "color": ("STRING", {"forceInput": True}), 
                }
            }
        
        RETURN_TYPES = ("STRING", "INT", "STRING", "STRING")
        RETURN_NAMES = ("物品字串", "物品編號", "顏色字串", "最終組合Prompt")
        FUNCTION = "get_selection"
        CATEGORY = "MyCustomNodes/Character_Outfit"

        def get_selection(self, selected_item, color):
            lst = load_items(file_name)
            index = lst.index(selected_item) if selected_item in lst else 0
            
            # 魔法在這裡！自動組合：前綴詞 + 顏色 + 的 + 物品
            # 例如："上半身穿著" + "紅色" + "的" + "襯衫"
            combined_prompt = f"{prefix_text}{color}的{selected_item}"
            
            return (selected_item, index, color, combined_prompt)
            
    return DynamicSelectorNode

for file_name, (class_name, display_name, prefix_text) in FILE_MAPPINGS.items():
    # 將前綴詞一併送進產生器
    node_class = create_selector_class(file_name, prefix_text)
    NODE_CLASS_MAPPINGS[class_name] = node_class
    NODE_DISPLAY_NAME_MAPPINGS[class_name] = display_name

# ==========================================
# 5. 終極服裝 Prompt 融合器 (支援選填 Optional)
# ==========================================
class OutfitPromptBuilder:
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                # 基礎咒語（例如：1girl, masterpiece, highly detailed）
                "base_prompt": ("STRING", {"multiline": True, "default": "1girl, masterpiece, best quality"}),
            },
            "optional": {
                # 所有部位都設為選填 (Optional)，沒拉線也不會當機！
                "hair": ("STRING", {"forceInput": True}),
                "tops": ("STRING", {"forceInput": True}),
                "bottoms": ("STRING", {"forceInput": True}),
                "shoes": ("STRING", {"forceInput": True}),
                "accessories": ("STRING", {"forceInput": True}),
                "bags": ("STRING", {"forceInput": True}),
                "neckwear": ("STRING", {"forceInput": True}),
                "wrist": ("STRING", {"forceInput": True}),
            }
        }

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("最終完整 Prompt",)
    FUNCTION = "build_prompt"
    CATEGORY = "MyCustomNodes/Character_Outfit"

    # 沒接線的參數預設會傳入 None 或空字串
    def build_prompt(self, base_prompt, hair="", tops="", bottoms="", shoes="", accessories="", bags="", neckwear="", wrist=""):
        
        # 1. 把所有收到的字串裝進一個列表
        parts = [base_prompt, hair, tops, bottoms, shoes, accessories, bags, neckwear, wrist]
        
        # 2. 過濾掉空的、沒拉線的、或者是 None 的項目
        valid_parts = [p for p in parts if p and isinstance(p, str) and p.strip() != ""]
        
        # 3. 用逗號和一個半形空白 ", " 把所有字串完美拼接起來
        final_prompt = ", ".join(valid_parts)
        
        return (final_prompt,)

# 記得把新節點註冊進去
NODE_CLASS_MAPPINGS["MyOutfitPromptBuilder"] = OutfitPromptBuilder
NODE_DISPLAY_NAME_MAPPINGS["MyOutfitPromptBuilder"] = "🧩 終極服裝 Prompt 融合器"

__all__ = ['NODE_CLASS_MAPPINGS', 'NODE_DISPLAY_NAME_MAPPINGS']