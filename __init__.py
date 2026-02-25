import os

current_dir = os.path.dirname(os.path.abspath(__file__))

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
# 2. 獨立顏色選擇器 (輸出 STRING)
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
# 3. 角色服裝總控大節點 
# ==========================================
class MasterOutfitSelector:
    @classmethod
    def INPUT_TYPES(s):
        color_list = load_items("color.txt")
        
        return {
            "required": {
                "base_prompt": ("STRING", {"multiline": True, "default": "1girl, masterpiece, best quality"}),
                
                # 面板下拉選單 (COMBO 型態)
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
                # 供外部連線專用的 STRING 端點，這才是 ColorSelector 認得的洞！
                "in_hair_main_color": ("STRING", {"forceInput": True}),
                "in_hair_sub_color": ("STRING", {"forceInput": True}),
                "in_tops_color": ("STRING", {"forceInput": True}),
                "in_bottoms_color": ("STRING", {"forceInput": True}),
                "in_shoes_color": ("STRING", {"forceInput": True}),
                "in_accessories_color": ("STRING", {"forceInput": True}),
                "in_bags_color": ("STRING", {"forceInput": True}),
                "in_neckwear_color": ("STRING", {"forceInput": True}),
                "in_wrist_color": ("STRING", {"forceInput": True}),
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
                     in_hair_main_color=None, in_hair_sub_color=None,
                     in_tops_color=None, in_bottoms_color=None,
                     in_shoes_color=None, in_accessories_color=None,
                     in_bags_color=None, in_neckwear_color=None,
                     in_wrist_color=None):
        
        # 決定顏色：如果有連線進來的字串就用連線的，否則用下拉選單的
        def resolve_color(dropdown, linked):
            if linked is not None and isinstance(linked, str) and linked.strip() != "":
                return linked
            return dropdown

        c_hair_main = resolve_color(hair_color_main, in_hair_main_color)
        c_hair_sub = resolve_color(hair_color_sub, in_hair_sub_color)
        c_tops = resolve_color(tops_color, in_tops_color)
        c_bottoms = resolve_color(bottoms_color, in_bottoms_color)
        c_shoes = resolve_color(shoes_color, in_shoes_color)
        c_acc = resolve_color(accessories_color, in_accessories_color)
        c_bags = resolve_color(bags_color, in_bags_color)
        c_neck = resolve_color(neckwear_color, in_neckwear_color)
        c_wrist = resolve_color(wrist_color, in_wrist_color)

        def format_part(item, color, prefix):
            if item == "無" or "(找不到" in item: return ""
            if color == "無": return f"{prefix}{item}"
            return f"{prefix}{color}的{item}"

        p_hair = ""
        if hair != "無" and "(找不到" not in hair:
            if c_hair_main != "無" and c_hair_sub != "無":
                p_hair = f"留著主色{c_hair_main}與副色{c_hair_sub}的{hair}"
            elif c_hair_main != "無":
                p_hair = f"留著{c_hair_main}的{hair}"
            else:
                p_hair = f"留著{hair}"

        p_tops = format_part(tops, c_tops, "上半身穿著")
        p_bottoms = format_part(bottoms, c_bottoms, "下半身穿著")
        p_shoes = format_part(shoes, c_shoes, "腳上穿著")
        p_acc = format_part(accessories, c_acc, "配戴著")
        p_bags = format_part(bags, c_bags, "背著")
        p_neck = format_part(neckwear, c_neck, "脖子上圍著")
        p_wrist = format_part(wrist, c_wrist, "手腕上配戴著")

        all_parts = [base_prompt.strip()] if base_prompt.strip() else []
        for p in [p_hair, p_tops, p_bottoms, p_shoes, p_acc, p_bags, p_neck, p_wrist]:
            if p:
                all_parts.append(p)
        
        final_prompt = ", ".join(all_parts)
        
        return (p_hair, p_tops, p_bottoms, p_shoes, p_acc, p_bags, p_neck, p_wrist, final_prompt)

NODE_CLASS_MAPPINGS["MasterOutfitSelector"] = MasterOutfitSelector
NODE_DISPLAY_NAME_MAPPINGS["MasterOutfitSelector"] = "👑 角色服裝總控中心 (Master Outfit)"

__all__ = ['NODE_CLASS_MAPPINGS', 'NODE_DISPLAY_NAME_MAPPINGS']