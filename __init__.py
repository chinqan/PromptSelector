import os
from .textmodeswitch import TextModeSwitch

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
# 2. 獨立顏色選擇器
# ==========================================
class ColorSelector:
    @classmethod
    def INPUT_TYPES(s):
        # 加上調色盤圖示
        return {"required": {"🎨 選擇顏色 (color)": (load_items("color.txt"), )}}
    
    RETURN_TYPES = ("STRING", "INT")
    RETURN_NAMES = ("顏色字串", "顏色編號")
    FUNCTION = "get_selection"
    CATEGORY = "MyCustomNodes/Color"

    # 使用 **kwargs 繞過 Python 變數命名限制
    def get_selection(self, **kwargs):
        selected_color = kwargs.get("🎨 選擇顏色 (color)", "無")
        lst = load_items("color.txt")
        index = lst.index(selected_color) if selected_color in lst else 0
        final_color = "" if selected_color == "無" or "(找不到" in selected_color else selected_color
        return (final_color, index)

NODE_CLASS_MAPPINGS["MyColorSelector"] = ColorSelector
NODE_DISPLAY_NAME_MAPPINGS["MyColorSelector"] = "🎨 顏色選擇器 (Color)"

# ==========================================
# 3. 角色服裝總控大節點 (全圖示版)
# ==========================================
class MasterOutfitSelector:
    @classmethod
    def INPUT_TYPES(s):
        color_list = load_items("color.txt")
        
        return {
            "required": {
                "📝 基礎咒語 (base_prompt)": ("STRING", {"multiline": True, "default": "以圖1為基礎影像,保留其光照、環境及背景。維持圖像1中人物動作,大小比例保持一致性,完美的邊緣細節和透明度,確保高品質、細節清晰,達到4K解析度更變人物身上的著裝"}),
                
                # 在標題加上 Emoji 與清楚的中英文對照
                "💇‍♀️ 髮型 (hair)": (load_items("hair.txt"), ),
                "🎨 髮型主色 (hair_color_main)": (color_list, ),
                "🎨 髮型副色 (hair_color_sub)": (color_list, ),
                
                "👕 上著 (tops)": (load_items("tops.txt"), ),
                "🎨 上著顏色 (tops_color)": (color_list, ),
                
                "👖 下著 (bottoms)": (load_items("bottoms.txt"), ),
                "🎨 下著顏色 (bottoms_color)": (color_list, ),
                
                "👟 鞋子 (shoes)": (load_items("shoes.txt"), ),
                "🎨 鞋子顏色 (shoes_color)": (color_list, ),
                
                "💍 飾品 (accessories)": (load_items("accessories.txt"), ),
                "🎨 飾品顏色 (accessories_color)": (color_list, ),
                
                "🎒 包包 (bags)": (load_items("bags.txt"), ),
                "🎨 包包顏色 (bags_color)": (color_list, ),
                
                "🧣 頸部配件 (neckwear)": (load_items("neckwear.txt"), ),
                "🎨 頸部顏色 (neckwear_color)": (color_list, ),
                
                "⌚ 腕部配件 (wrist)": (load_items("wrist.txt"), ),
                "🎨 腕部顏色 (wrist_color)": (color_list, ),
            },
            "optional": {
                # 連線端點也加上符號，整理 Subgraph 時會更清晰
                "🔗 髮型主色連線 (in_hair_main)": ("STRING", {"forceInput": True}),
                "🔗 髮型副色連線 (in_hair_sub)": ("STRING", {"forceInput": True}),
                "🔗 上著顏色連線 (in_tops)": ("STRING", {"forceInput": True}),
                "🔗 下著顏色連線 (in_bottoms)": ("STRING", {"forceInput": True}),
                "🔗 鞋子顏色連線 (in_shoes)": ("STRING", {"forceInput": True}),
                "🔗 飾品顏色連線 (in_accessories)": ("STRING", {"forceInput": True}),
                "🔗 包包顏色連線 (in_bags)": ("STRING", {"forceInput": True}),
                "🔗 頸部顏色連線 (in_neckwear)": ("STRING", {"forceInput": True}),
                "🔗 腕部顏色連線 (in_wrist)": ("STRING", {"forceInput": True}),
            }
        }
    
    RETURN_TYPES = ("STRING", "STRING", "STRING", "STRING", "STRING", "STRING", "STRING", "STRING", "STRING")
    RETURN_NAMES = (
        "髮型 Prompt", "上著 Prompt", "下著 Prompt", "鞋子 Prompt", 
        "飾品 Prompt", "包包 Prompt", "頸部 Prompt", "腕部 Prompt", 
        "Debug Prompt",
        "🌟 最終總組合 Prompt"
    )
    FUNCTION = "build_prompt"
    CATEGORY = "MyCustomNodes/Character_Outfit"

    # 使用 **kwargs 來接收帶有特殊符號的變數名稱
    def build_prompt(self, **kwargs):
        
        # 1. 從 kwargs 中安全地把帶有 Emoji 的變數取出來
        base_prompt = kwargs.get("📝 基礎咒語 (base_prompt)", "")
        
        hair = kwargs.get("💇‍♀️ 髮型 (hair)", "無")
        hair_color_main = kwargs.get("🎨 髮型主色 (hair_color_main)", "無")
        hair_color_sub = kwargs.get("🎨 髮型副色 (hair_color_sub)", "無")
        
        tops = kwargs.get("👕 上著 (tops)", "無")
        tops_color = kwargs.get("🎨 上著顏色 (tops_color)", "無")
        
        bottoms = kwargs.get("👖 下著 (bottoms)", "無")
        bottoms_color = kwargs.get("🎨 下著顏色 (bottoms_color)", "無")
        
        shoes = kwargs.get("👟 鞋子 (shoes)", "無")
        shoes_color = kwargs.get("🎨 鞋子顏色 (shoes_color)", "無")
        
        accessories = kwargs.get("💍 飾品 (accessories)", "無")
        accessories_color = kwargs.get("🎨 飾品顏色 (accessories_color)", "無")
        
        bags = kwargs.get("🎒 包包 (bags)", "無")
        bags_color = kwargs.get("🎨 包包顏色 (bags_color)", "無")
        
        neckwear = kwargs.get("🧣 頸部配件 (neckwear)", "無")
        neckwear_color = kwargs.get("🎨 頸部顏色 (neckwear_color)", "無")
        
        wrist = kwargs.get("⌚ 腕部配件 (wrist)", "無")
        wrist_color = kwargs.get("🎨 腕部顏色 (wrist_color)", "無")
        
        in_hair_main = kwargs.get("🔗 髮型主色連線 (in_hair_main)")
        in_hair_sub = kwargs.get("🔗 髮型副色連線 (in_hair_sub)")
        in_tops = kwargs.get("🔗 上著顏色連線 (in_tops)")
        in_bottoms = kwargs.get("🔗 下著顏色連線 (in_bottoms)")
        in_shoes = kwargs.get("🔗 鞋子顏色連線 (in_shoes)")
        in_accessories = kwargs.get("🔗 飾品顏色連線 (in_accessories)")
        in_bags = kwargs.get("🔗 包包顏色連線 (in_bags)")
        in_neckwear = kwargs.get("🔗 頸部顏色連線 (in_neckwear)")
        in_wrist = kwargs.get("🔗 腕部顏色連線 (in_wrist)")

        # 2. 判斷要使用連線顏色還是下拉選單顏色
        def resolve_color(dropdown, linked):
            if linked is not None and isinstance(linked, str) and linked.strip() != "":
                return linked
            return dropdown

        c_hair_main = resolve_color(hair_color_main, in_hair_main)
        c_hair_sub = resolve_color(hair_color_sub, in_hair_sub)
        c_tops = resolve_color(tops_color, in_tops)
        c_bottoms = resolve_color(bottoms_color, in_bottoms)
        c_shoes = resolve_color(shoes_color, in_shoes)
        c_acc = resolve_color(accessories_color, in_accessories)
        c_bags = resolve_color(bags_color, in_bags)
        c_neck = resolve_color(neckwear_color, in_neckwear)
        c_wrist = resolve_color(wrist_color, in_wrist)

        # 3. 組合 Prompt 的邏輯
        def format_part(item, color, prefix):
            if item == "無" or "(找不到" in item: return ""
            if color == "無": return f"{prefix}{item}"
            return f"{prefix}{color}的{item}"

        p_hair = ""
        o_hair = ""
        if hair != "無" and "(找不到" not in hair:
            if c_hair_main != "無" and c_hair_sub != "無":
                p_hair = f"留著主色{c_hair_main}與副色{c_hair_sub}相間的{hair}"
                o_hair = f"{c_hair_main}{c_hair_sub}的{hair}\n"
            elif c_hair_main != "無":
                p_hair = f"留著{c_hair_main}的{hair}"
                o_hair = f"{c_hair_main}的{hair}\n"
            else:
                p_hair = f"留著{hair}"
                o_hair = f"{hair}\n"

        p_tops = format_part(tops, c_tops, "上半身穿著")
        o_tops = format_part(tops, c_tops, "\n")
        p_bottoms = format_part(bottoms, c_bottoms, "下半身穿著")
        o_bottoms = format_part(bottoms, c_bottoms, "\n")
        p_shoes = format_part(shoes, c_shoes, "腳上穿著")
        o_shoes = format_part(shoes, c_shoes, "\n")
        p_acc = format_part(accessories, c_acc, "配戴著")
        o_acc = format_part(accessories, c_acc, "\n")
        p_bags = format_part(bags, c_bags, "背著")
        o_bags = format_part(bags, c_bags, "\n")
        p_neck = format_part(neckwear, c_neck, "脖子上圍著")
        o_neck = format_part(neckwear, c_neck, "\n")
        p_wrist = format_part(wrist, c_wrist, "手腕上配戴著")
        o_wrist = format_part(wrist, c_wrist, "\n")

        all_parts = [base_prompt.strip()] if base_prompt.strip() else []
        for p in [p_hair, p_tops, p_bottoms, p_shoes, p_acc, p_bags, p_neck, p_wrist]:
            if p:
                all_parts.append(p)
        
        final_prompt = ", ".join(all_parts)
        
        debug_parts = ""
        for o in [o_hair, o_tops, o_bottoms, o_shoes, o_acc, o_bags, o_neck, o_wrist]:
            if p:
                debug_parts.append(o)
        
        return (o_hair, o_tops, o_bottoms, o_shoes, o_acc, o_bags, o_neck, o_wrist, debug_parts, final_prompt)

NODE_CLASS_MAPPINGS["MasterOutfitSelector"] = MasterOutfitSelector
NODE_DISPLAY_NAME_MAPPINGS["MasterOutfitSelector"] = "👑 角色服裝總控中心 (Master Outfit)"


# 節點註冊對照表
NODE_CLASS_MAPPINGS["TextModeSwitch"] =  TextModeSwitch
NODE_DISPLAY_NAME_MAPPINGS["TextModeSwitch"] =  "Dual Text Switch (A/B)"


__all__ = ['NODE_CLASS_MAPPINGS', 'NODE_DISPLAY_NAME_MAPPINGS']