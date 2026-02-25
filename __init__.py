import os

current_dir = os.path.dirname(os.path.abspath(__file__))

# 1. 讀取函式 (自動在最上面加入「無」)
def load_items(file_name):
    file_path = os.path.join(current_dir, file_name)
    items = ["無"] 
    
    if os.path.exists(file_path):
        with open(file_path, "r", encoding="utf-8") as f:
            for line in f:
                item = line.strip()
                if item and item != "無":
                    items.append(item)
                    
    if len(items) == 1: 
        items.append(f"(找不到 {file_name})")
        
    return items

NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}

# ==========================================
# 2. 獨立顏色選擇器
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
        final_color = "" if selected_color == "無" or "(找不到" in selected_color else selected_color
        return (final_color, index)

NODE_CLASS_MAPPINGS["MyColorSelector"] = ColorSelector
NODE_DISPLAY_NAME_MAPPINGS["MyColorSelector"] = "🎨 顏色選擇器 (Color)"


# ==========================================
# 3. 角色服裝總控大節點 (加入連線覆寫機制)
# ==========================================
class MasterOutfitSelector:
    @classmethod
    def INPUT_TYPES(s):
        color_list = load_items("color.txt")
        
        return {
            "required": {
                "base_prompt": ("STRING", {"multiline": True, "default": "1girl, masterpiece, best quality"}),
                
                # 下拉選單區
                "hair": (load_items("hair.txt"), ),
                "hair_color_main": (color_list, ),
                "hair_color_sub": (color_list, ),
                
                "tops": (load_items("tops.txt"), ),
                "tops_color": (color_list, ),
                
                "bottoms": (load_items("bottoms.txt"), ),
                "bottoms_color": (color_list, ),
                
                "shoes": (load_items("shoes.txt"), ),
                "shoes_color": (color_list, ),
                
                "accessories": (load_items("accessories.txt"), ),
                "accessories_color": (color_list, ),
                
                "bags": (load_items("bags.txt"), ),
                "bags_color": (color_list, ),
                
                "neckwear": (load_items("neckwear.txt"), ),
                "neckwear_color": (color_list, ),
                
                "wrist": (load_items("wrist.txt"), ),
                "wrist_color": (color_list, ),
            },
            "optional": {
                # 左側連線區 (供 ColorSelector 直接插線覆寫)
                "hair_color_main_link": ("STRING", {"forceInput": True}),
                "hair_color_sub_link": ("STRING", {"forceInput": True}),
                "tops_color_link": ("STRING", {"forceInput": True}),
                "bottoms_color_link": ("STRING", {"forceInput": True}),
                "shoes_color_link": ("STRING", {"forceInput": True}),
                "accessories_color_link": ("STRING", {"forceInput": True}),
                "bags_color_link": ("STRING", {"forceInput": True}),
                "neckwear_color_link": ("STRING", {"forceInput": True}),
                "wrist_color_link": ("STRING", {"forceInput": True}),
            }
        }
    
    RETURN_TYPES = ("STRING", "STRING", "STRING", "STRING", "STRING", "STRING", "STRING", "STRING", "STRING")
    RETURN_NAMES = (
        "髮型 Prompt", "上著 Prompt", "下著 Prompt", "鞋子 Prompt", 
        "飾品 Prompt", "包包 Prompt", "頸部 Prompt", "腕部 Prompt", 
        "🌟 最終總組合 Prompt"
    )
    FUNCTION = "build_prompt"
    CATEGORY = "MyCustomNodes/Character_Outfit"

    def build_prompt(self, base_prompt, 
                     hair, hair_color_main, hair_color_sub,
                     tops, tops_color, bottoms, bottoms_color,
                     shoes, shoes_color, accessories, accessories_color,
                     bags, bags_color, neckwear, neckwear_color,
                     wrist, wrist_color,
                     # 接收連線傳來的參數 (預設為 None)
                     hair_color_main_link=None, hair_color_sub_link=None,
                     tops_color_link=None, bottoms_color_link=None,
                     shoes_color_link=None, accessories_color_link=None,
                     bags_color_link=None, neckwear_color_link=None,
                     wrist_color_link=None):
        
        # 覆寫判定大師：如果有連線且字串不為空，就採用連線的顏色，否則用下拉選單
        def resolve_color(dropdown_color, linked_color):
            if linked_color is not None and isinstance(linked_color, str) and linked_color.strip() != "":
                return linked_color
            return dropdown_color

        # 算出最終決定採用的顏色
        c_hair_main = resolve_color(hair_color_main, hair_color_main_link)
        c_hair_sub = resolve_color(hair_color_sub, hair_color_sub_link)
        c_tops = resolve_color(tops_color, tops_color_link)
        c_bottoms = resolve_color(bottoms_color, bottoms_color_link)
        c_shoes = resolve_color(shoes_color, shoes_color_link)
        c_acc = resolve_color(accessories_color, accessories_color_link)
        c_bags = resolve_color(bags_color, bags_color_link)
        c_neck = resolve_color(neckwear_color, neckwear_color_link)
        c_wrist = resolve_color(wrist_color, wrist_color_link)

        # 輔助函式：判斷是否為「無」，並自動組合
        def format_part(item, color, prefix):
            if item == "無" or "(找不到" in item: 
                return ""
            if color == "無": 
                return f"{prefix}{item}"
            return f"{prefix}{color}的{item}"

        # 髮型組合邏輯
        p_hair = ""
        if hair != "無" and "(找不到" not in hair:
            if c_hair_main != "無" and c_hair_sub != "無":
                p_hair = f"留著主色{c_hair_main}與副色{c_hair_sub}的{hair}"
            elif c_hair_main != "無":
                p_hair = f"留著{c_hair_main}的{hair}"
            else:
                p_hair = f"留著{hair}"

        # 其他部位組合邏輯 (全部套用剛才算好的最終顏色)
        p_tops = format_part(tops, c_tops, "上半身穿著")
        p_bottoms = format_part(bottoms, c_bottoms, "下半身穿著")
        p_shoes = format_part(shoes, c_shoes, "腳上穿著")
        p_acc = format_part(accessories, c_acc, "配戴著")
        p_bags = format_part(bags, c_bags, "背著")
        p_neck = format_part(neckwear, c_neck, "脖子上圍著")
        p_wrist = format_part(wrist, c_wrist, "手腕上配戴著")

        # 收集所有「非空白」的字串
        all_parts = [base_prompt.strip()] if base_prompt.strip() else []
        for p in [p_hair, p_tops, p_bottoms, p_shoes, p_acc, p_bags, p_neck, p_wrist]:
            if p:
                all_parts.append(p)
        
        # 用逗號串接
        final_prompt = ", ".join(all_parts)
        
        return (p_hair, p_tops, p_bottoms, p_shoes, p_acc, p_bags, p_neck, p_wrist, final_prompt)

NODE_CLASS_MAPPINGS["MasterOutfitSelector"] = MasterOutfitSelector
NODE_DISPLAY_NAME_MAPPINGS["MasterOutfitSelector"] = "👑 角色服裝總控中心 (Master Outfit)"

__all__ = ['NODE_CLASS_MAPPINGS', 'NODE_DISPLAY_NAME_MAPPINGS']