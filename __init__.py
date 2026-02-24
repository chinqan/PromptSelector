import os

# 1. 自動取得目前這個 __init__.py 所在的資料夾路徑，並指向 color.txt
current_dir = os.path.dirname(os.path.abspath(__file__))
file_path = os.path.join(current_dir, "color.txt")

# 2. 建立一個讀取文字檔的函式
def load_items_from_file():
    items = []
    # 檢查檔案是否存在，避免 ComfyUI 啟動時找不到檔案而崩潰
    if os.path.exists(file_path):
        with open(file_path, "r", encoding="utf-8") as f:
            for line in f:
                item = line.strip() # 去除頭尾的空白與換行符號
                if item:            # 確保不是空白行
                    items.append(item)
                    
    # 防呆機制：如果檔案不存在或裡面沒寫東西，給一個預設清單
    if not items:
        items = ["找不到檔案或檔案為空"]
        
    return items

# 在伺服器啟動時，讀取文字檔並把結果存入 COLOR_LIST
COLOR_LIST = load_items_from_file()

class DynamicFileSelector:
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                # 將讀取到的清單變數 COLOR_LIST 放入下拉選單
                "selected_item": (COLOR_LIST, ),
            }
        }
    
    # 3. 定義兩個輸出：第一個是字串 (STRING)，第二個是整數編號 (INT)
    RETURN_TYPES = ("STRING", "INT")
    RETURN_NAMES = ("顏色字串", "顏色編號") # 節點上顯示的輸出端點名稱
    
    FUNCTION = "get_selection"
    CATEGORY = "MyCustomNodes/Data"

    def get_selection(self, selected_item):
        # 找出選中的字串在 COLOR_LIST 裡面是第幾個 (這就是它的編號)
        # 注意：程式語言的索引是從 0 開始。如果你希望編號從 1 開始，請在後面加上 + 1 (例如: index = COLOR_LIST.index(selected_item) + 1)
        index = COLOR_LIST.index(selected_item)
        
        # 同時回傳字串與編號 (順序必須和 RETURN_TYPES 呼應)
        return (selected_item, index)

# 註冊節點
NODE_CLASS_MAPPINGS = {
    "DynamicFileSelector": DynamicFileSelector
}

# 節點顯示名稱
NODE_DISPLAY_NAME_MAPPINGS = {
    "DynamicFileSelector": "動態文字檔下拉選單 (File Selector)"
}