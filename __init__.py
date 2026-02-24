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
# 2. 顏色選擇器
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
# 3. 髮型選擇器 (加入連線覆寫邏輯)
# ==========================================
class HairSelector:
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "selected_hair": (load_items("hair.txt"), ),
                # 這是畫面上的下拉選單
                "color_main_dropdown": (load_items("color.txt"), ), 
                "color_sub_dropdown": (load_items("color.txt"), ),
            },
            "optional": {
                # 這是畫面左側的連線端點 (名字精簡為 color_main / color_sub)
                "color_main": ("STRING", {"forceInput": True}),
                "color_sub": ("STRING", {"forceInput": True}),
            }
        }
    
    RETURN_TYPES = ("STRING", "INT", "STRING", "STRING", "STRING")
    RETURN_NAMES = ("髮型字串", "髮型編號", "最終主色", "最終副色", "最終組合Prompt")
    FUNCTION = "get_selection"
    CATEGORY = "MyCustomNodes/Character_Outfit"

    def get_selection(self, selected_hair, color_main_dropdown, color_sub_dropdown, color_main=None, color_sub=None):
        lst = load_items("hair.txt")
        index = lst.index(selected_hair) if selected_hair in lst else 0
        
        # 覆寫邏輯：如果左側 color_main 有接線，選單直接失效！
        final_main = color_main if (color_main and isinstance(color_main, str) and color_main.strip()) else color_main_dropdown
        final_sub = color_sub if (color_sub and isinstance(color_sub, str) and color_sub.strip()) else color_sub_dropdown

        combined_prompt = f"留著主色{final_main}與副色{final_sub}的{selected_hair}"
        return (selected_hair, index, final_main, final_sub, combined_prompt)

NODE_CLASS_MAPPINGS["MyHairSelector"] = HairSelector
NODE_DISPLAY_NAME_MAPPINGS["MyHairSelector"] = "💇‍♀️ 髮型特化選擇器 (Hair)"


# ==========================================
# 4. 其他部位選擇器 (加入連線覆寫邏輯)
# ==========================================
FILE_MAPPINGS = {
    "accessories.txt": ("AccessoriesSelector", "💍 飾品選擇器 (Accessories)", "配戴著"),
    "bags.txt":        ("BagsSelector",        "🎒 包包選擇器 (Bags)",        "背著"),
    "bottoms.txt":     ("BottomsSelector",     "👖 下著選擇器 (Bottoms)",     "下半身穿著"),
    "neckwear.txt":    ("NeckwearSelector",    "🧣 頸部配件選擇器 (Neckwear)", "脖子上圍著"),
    "shoes.txt":       ("ShoesSelector",       "👟 鞋子選擇器 (Shoes)",       "腳上穿著"),
    "tops.txt":        ("TopsSelector",        "👕 上著選擇器 (Tops)",        "上半身穿著"),
    "wrist.txt":       ("WristSelector",       "⌚ 腕部配件選擇器 (Wrist)",    "手腕上配戴著"),
}

def create_selector_class(file_name, prefix_text):
    class DynamicSelectorNode:
        @classmethod
        def INPUT_TYPES(s):
            return {
                "required": {
                    "selected_item": (load_items(file_name), ),
                    # 下拉選單
                    "color_dropdown": (load_items("color.txt"), ), 
                },
                "optional": {
                    # 左側連線端點，名字精簡為 color
                    "color": ("STRING", {"forceInput": True}),
                }
            }
        
        RETURN_TYPES = ("STRING", "INT", "STRING", "STRING")
        RETURN_NAMES = ("物品字串", "物品編號", "最終採用顏色", "最終組合Prompt")
        FUNCTION = "get_selection"
        CATEGORY = "MyCustomNodes/Character_Outfit"

        def get_selection(self, selected_item, color_dropdown, color=None):
            lst = load_items(file_name)
            index = lst.index(selected_item) if selected_item in lst else 0
            
            # 覆寫邏輯：如果左側 color 有接線，選單直接失效！
            final_color = color if (color and isinstance(color, str) and color.strip()) else color_dropdown
            
            combined_prompt = f"{prefix_text}{final_color}的{selected_item}"
            return (selected_item, index, final_color, combined_prompt)
            
    return DynamicSelectorNode

for file_name, (class_name, display_name, prefix_text) in FILE_MAPPINGS.items():
    node_class = create_selector_class(file_name, prefix_text)
    NODE_CLASS_MAPPINGS[class_name] = node_class
    NODE_DISPLAY_NAME_MAPPINGS[class_name] = display_name


# ==========================================
# 5. 終極服裝 Prompt 融合器
# ==========================================
class OutfitPromptBuilder:
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "base_prompt": ("STRING", {"multiline": True, "default": "1girl, masterpiece, best quality"}),
            },
            "optional": {
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
    CATEGORY = "MyCustomNodes/Final"

    def build_prompt(self, base_prompt, hair="", tops="", bottoms="", shoes="", accessories="", bags="", neckwear="", wrist=""):
        parts = [base_prompt, hair, tops, bottoms, shoes, accessories, bags, neckwear, wrist]
        valid_parts = [p for p in parts if p and isinstance(p, str) and p.strip() != ""]
        final_prompt = ", ".join(valid_parts)
        return (final_prompt,)

NODE_CLASS_MAPPINGS["MyOutfitPromptBuilder"] = OutfitPromptBuilder
NODE_DISPLAY_NAME_MAPPINGS["MyOutfitPromptBuilder"] = "🧩 終極服裝 Prompt 融合器"

# 告訴 ComfyUI 去載入我們寫好的網頁前端 JS 腳本
WEB_DIRECTORY = "./web"
__all__ = ['NODE_CLASS_MAPPINGS', 'NODE_DISPLAY_NAME_MAPPINGS']