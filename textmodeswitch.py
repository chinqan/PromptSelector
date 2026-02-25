
class TextModeSwitch:
    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "mode": (["手動調整", "自動生成"], {"default": "手動調整"}),
                "prompt1": ("STRING", {"forceInput": True}),
                "log1": ("STRING", {"forceInput": True}),
                "prompt2": ("STRING", {"forceInput": True}),
                "log2": ("STRING", {"forceInput": True}),
            },
        }

    RETURN_TYPES = ("STRING", "STRING")
    RETURN_NAMES = ("prompt", "log")
    FUNCTION = "switch_logic"
    CATEGORY = "MyCustomNodes"

    def switch_logic(self, mode, prompt1, log1, prompt2, log2):
        if mode == "手動調整":
            # 模式 A：將 A1, A2 導向輸出
            return (prompt1, log1)
        else:
            # 模式 B：將 B1, B2 導向輸出
            return (prompt2, log2)