
class TextModeSwitch:
    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "mode": (["手動調整", "自動生成"], {"default": "手動調整"}),
                "textA1": ("STRING", {"forceInput": True}),
                "textA2": ("STRING", {"forceInput": True}),
                "textB1": ("STRING", {"forceInput": True}),
                "textB2": ("STRING", {"forceInput": True}),
            },
        }

    RETURN_TYPES = ("STRING", "STRING")
    RETURN_NAMES = ("text1", "text2")
    FUNCTION = "switch_logic"
    CATEGORY = "MyCustomNodes"

    def switch_logic(self, mode, textA1, textA2, textB1, textB2):
        if mode == "Mode_A":
            # 模式 A：將 A1, A2 導向輸出
            return (textA1, textA2)
        else:
            # 模式 B：將 B1, B2 導向輸出
            return (textB1, textB2)