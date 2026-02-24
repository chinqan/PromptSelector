import os
import glob

current_dir = os.path.dirname(os.path.abspath(__file__))

# 1. 通用的檔案讀取函式
def load_items(file_path):
    items = []
    if os.path.exists(file_path):
        with open(file_path, "r", encoding="utf-8") as f:
            for line in f:
                item = line.strip()
                if item:
                    items.append(item)
    return items if items else ["(檔案為空)"]

# 準備要註冊給 ComfyUI 的清單
NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}

# ==========================================
# 2. 獨立建立【顏色選擇器】節點
# ==========================================
color_file = os.path.join(current_dir, "color.txt")
class ColorSelector:
    @classmethod
    def INPUT_TYPES(s):
        return {"required": {"selected_color": (load_items(color_file), )}}
    
    RETURN_TYPES = ("STRING", "INT")
    RETURN_NAMES = ("顏色字串", "顏色編號")
    FUNCTION = "get_selection"
    CATEGORY = "MyCustomNodes/Selectors"

    def get_selection(self, selected_color):
        lst = load_items(color_file)
        index = lst.index(selected_color) if selected_color in lst else 0
        return (selected_color, index)

NODE_CLASS_MAPPINGS["MyColorSelector"] = ColorSelector
NODE_DISPLAY_NAME_MAPPINGS["MyColorSelector"] = "🎨 顏色選擇器 (Color)"


# ==========================================
# 3. 動態工廠：為每一個 item*.txt 自動生成專屬節點
# ==========================================
# 自動抓取資料夾內所有開頭是 item 且結尾是 .txt 的檔案 (例如 item1.txt, item2.txt)
item_files = glob.glob(os.path.join(current_dir, "item*.txt"))

def create_item_node(file_path, filename_no_ext):
    class DynamicItemSelector:
        @classmethod
        def INPUT_TYPES(s):
            # 每個節點只載入自己專屬檔案的內容
            return {"required": {"selected_item": (load_items(file_path), )}}
        
        RETURN_TYPES = ("STRING", "INT")
        RETURN_NAMES = ("物品字串", "物品編號")
        FUNCTION = "get_selection"
        CATEGORY = "MyCustomNodes/Items"

        def get_selection(self, selected_item):
            lst = load_items(file_path)
            index = lst.index(selected_item) if selected_item in lst else 0
            return (selected_item, index)
            
    return DynamicItemSelector

# 迴圈掃描所有檔案，並逐一註冊成新節點
for f_path in item_files:
    f_name = os.path.splitext(os.path.basename(f_path))[0] # 取得檔名(如 item1)
    
    node_class = create_item_node(f_path, f_name)
    class_id = f"DynamicSelector_{f_name}"
    
    NODE_CLASS_MAPPINGS[class_id] = node_class
    NODE_DISPLAY_NAME_MAPPINGS[class_id] = f"📦 物品選擇器 ({f_name})"


# ==========================================
# 4. 輔助節點：幫你把顏色跟物品組合成一句話
# ==========================================
class CombineColorAndItem:
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "color_string": ("STRING", {"forceInput": True}),
                "item_string": ("STRING", {"forceInput": True}),
            }
        }
    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("最終組合 Prompt",)
    FUNCTION = "combine"
    CATEGORY = "MyCustomNodes/Selectors"

    def combine(self, color_string, item_string):
        return (f"{color_string}的{item_string}", )

NODE_CLASS_MAPPINGS["CombineColorAndItem"] = CombineColorAndItem
NODE_DISPLAY_NAME_MAPPINGS["CombineColorAndItem"] = "🔗 組合顏色與物品"

__all__ = ['NODE_CLASS_MAPPINGS', 'NODE_DISPLAY_NAME_MAPPINGS']