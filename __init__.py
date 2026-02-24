import os
import glob

current_dir = os.path.dirname(os.path.abspath(__file__))

# 1. 讀取顏色專用函式
def load_colors():
    color_file = os.path.join(current_dir, "color.txt")
    colors = []
    if os.path.exists(color_file):
        with open(color_file, "r", encoding="utf-8") as f:
            for line in f:
                item = line.strip()
                if item: colors.append(item)
    return colors if colors else ["找不到 color.txt"]

# 2. 讀取所有物品檔案的函式
def load_items():
    # 抓取資料夾內所有 txt，但排除 color.txt
    txt_files = [f for f in glob.glob(os.path.join(current_dir, "*.txt")) if not f.endswith("color.txt")]
    
    display_list = []
    item_map = {}
    
    for file_path in txt_files:
        # 取得檔名 (不含 .txt，例如從 item1.txt 取得 item1)
        filename = os.path.splitext(os.path.basename(file_path))[0]
        
        with open(file_path, "r", encoding="utf-8") as f:
            lines = f.readlines()
            for index, line in enumerate(lines):
                real_item = line.strip()
                if real_item:
                    # 組合選單上的顯示文字，例如 "[item1] 寶劍"
                    display_text = f"[{filename}] {real_item}"
                    display_list.append(display_text)
                    
                    # 字典記錄：顯示文字對應 -> (真實字串, 檔案內編號)
                    item_map[display_text] = (real_item, index)
                    
    if not display_list:
        display_list = ["找不到任何物品 txt 檔"]
        item_map["找不到任何物品 txt 檔"] = ("無", 0)
        
    return display_list, item_map

# 在啟動時載入資料
COLOR_LIST = load_colors()
ITEM_DISPLAY_LIST, ITEM_MAP = load_items()

class GameAssetSelector:
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "selected_color": (COLOR_LIST, ),
                "selected_item": (ITEM_DISPLAY_LIST, ),
            }
        }
    
    # 定義 5 個輸出
    RETURN_TYPES = ("STRING", "INT", "STRING", "INT", "STRING")
    RETURN_NAMES = ("顏色字串", "顏色編號", "物品字串", "物品編號", "最終組合Prompt")
    FUNCTION = "get_selection"
    CATEGORY = "MyCustomNodes/Data"

    def get_selection(self, selected_color, selected_item):
        color_index = COLOR_LIST.index(selected_color)
        
        # 透過字典，解開選單文字，還原成真實物品與編號
        real_item, item_index = ITEM_MAP.get(selected_item, ("無", 0))
        
        # 組合字串，直接生成 "紅色的寶劍"
        combined_prompt = f"{selected_color}的{real_item}"
        
        return (selected_color, color_index, real_item, item_index, combined_prompt)

NODE_CLASS_MAPPINGS = {
    "GameAssetSelector": GameAssetSelector
}
NODE_DISPLAY_NAME_MAPPINGS = {
    "GameAssetSelector": "遊戲素材 顏色與物品選擇器"
}
__all__ = ['NODE_CLASS_MAPPINGS', 'NODE_DISPLAY_NAME_MAPPINGS']