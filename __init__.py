import os

current_dir = os.path.dirname(os.path.abspath(__file__))

# 1. 讀取函式 (自動在最上面加入「無」)
def load_items(file_name):
    file_path = os.path.join(current_dir, file_name)
    items = ["無"] # 預設第一個選項為「無」
    
    if os.path.exists(file_path):
        with open(file_path, "r", encoding="utf-8") as f:
            for line in f:
                item = line.strip()
                if item and item != "無":
                    items.append(item)
                    
    if len(items) == 1: # 如果檔案不存在或只有「無」
        items.append(f"(找不到 {file_name})")
        
    return items

NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}

# ==========================================
# 2. 獨立顏色選擇器 (保留下來供其他用途使用)
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
        
        # 貼心小設計：如果選了「無」，就輸出空字串，避免你的 Prompt 裡出現奇怪的「無」字
        final_color = "" if selected_color == "無" or "(找不到" in selected_color else selected_color
        
        return (final_color, index)

NODE_CLASS_MAPPINGS["MyColorSelector"] = ColorSelector
NODE_DISPLAY_NAME_MAPPINGS["MyColorSelector"] = "🎨 顏色選擇器 (Color)"


# ==========================================
# 3. 角色服裝總控大節點 (Master Node)
# ==========================================
class MasterOutfitSelector:
    @classmethod
    def INPUT_TYPES(s):
        # 預先載入共用的顏色清單
        color_list = load_items("color.txt")
        
        return {
            "required": {
                # 基礎咒語
                "base_prompt": ("STRING", {"multiline": True, "default": "1girl, masterpiece, best quality"}),
                
                # 所有部位都採用純下拉選單
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
            }
        }
    
    # 取消編號，只保留 8 個部位的獨立字串，以及最後 1 個總組合字串
    RETURN_TYPES = ("STRING", "STRING", "STRING", "STRING", "STRING", "STRING", "STRING", "STRING", "STRING")
    RETURN_NAMES = (
        "髮型 Prompt", "上著 Prompt", "下著 Prompt", "鞋子 Prompt", 
        "飾品 Prompt", "包包 Prompt", "頸部 Prompt", "腕部 Prompt", 
        "🌟 最終總組合 Prompt"
    )
    FUNCTION = "build_prompt"
    CATEGORY = "MyCustomNodes/Character_Outfit"

    def build_prompt(self, base_prompt, hair, hair_color_main, hair_color_sub,
                     tops, tops_color, bottoms, bottoms_color,
                     shoes, shoes_color, accessories, accessories_color,
                     bags, bags_color, neckwear, neckwear_color,
                     wrist, wrist_color):
        
        # 輔助函式：判斷是否為「無」，並自動組合前綴詞與顏色
        def format_part(item, color, prefix):
            if item == "無" or "(找不到" in item: 
                return ""
            if color == "無": 
                return f"{prefix}{item}"
            return f"{prefix}{color}的{item}"

        # 髮型組合邏輯
        p_hair = ""
        if hair != "無" and "(找不到" not in hair:
            if hair_color_main != "無" and hair_color_sub != "無":
                p_hair = f"留著主色{hair_color_main}與副色{hair_color_sub}的{hair}"
            elif hair_color_main != "無":
                p_hair = f"留著{hair_color_main}的{hair}"
            else:
                p_hair = f"留著{hair}"

        # 其他部位組合邏輯
        p_tops = format_part(tops, tops_color, "上半身穿著")
        p_bottoms = format_part(bottoms, bottoms_color, "下半身穿著")
        p_shoes = format_part(shoes, shoes_color, "腳上穿著")
        p_acc = format_part(accessories, accessories_color, "配戴著")
        p_bags = format_part(bags, bags_color, "背著")
        p_neck = format_part(neckwear, neckwear_color, "脖子上圍著")
        p_wrist = format_part(wrist, wrist_color, "手腕上配戴著")

        # 收集所有「非空白」的字串，準備組裝最終 Prompt
        all_parts = [base_prompt.strip()] if base_prompt.strip() else []
        for p in [p_hair, p_tops, p_bottoms, p_shoes, p_acc, p_bags, p_neck, p_wrist]:
            if p:
                all_parts.append(p)
        
        # 用逗號串接全部
        final_prompt = ", ".join(all_parts)
        
        return (p_hair, p_tops, p_bottoms, p_shoes, p_acc, p_bags, p_neck, p_wrist, final_prompt)

NODE_CLASS_MAPPINGS["MasterOutfitSelector"] = MasterOutfitSelector
NODE_DISPLAY_NAME_MAPPINGS["MasterOutfitSelector"] = "👑 角色服裝總控中心 (Master Outfit)"

__all__ = ['NODE_CLASS_MAPPINGS', 'NODE_DISPLAY_NAME_MAPPINGS']