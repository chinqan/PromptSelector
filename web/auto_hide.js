import { app } from "../../scripts/app.js";

app.registerExtension({
    name: "MyCustomNodes.AutoHideWidgets",
    async nodeCreated(node) {
        // 定義哪些節點需要套用這個自動隱藏的魔法
        const targetNodes = [
            "MyHairSelector", "AccessoriesSelector", "BagsSelector", 
            "BottomsSelector", "NeckwearSelector", "ShoesSelector", 
            "TopsSelector", "WristSelector"
        ];

        if (targetNodes.includes(node.comfyClass)) {
            // 攔截「連線發生改變」的瞬間事件
            const onConnectionsChange = node.onConnectionsChange;
            node.onConnectionsChange = function(type, index, connected, link_info) {
                // 先執行節點原本的底層邏輯
                if (onConnectionsChange) {
                    onConnectionsChange.apply(this, arguments);
                }
                
                // type === 1 代表發生改變的是「輸入端點 (Input)」
                if (type === 1) {
                    const input = this.inputs[index];
                    let targetWidgetName = null;

                    // 判斷接線的是哪個洞，並對應到畫面上的下拉選單變數
                    if (input.name === "color") targetWidgetName = "color_dropdown";
                    if (input.name === "color_main") targetWidgetName = "color_main_dropdown";
                    if (input.name === "color_sub") targetWidgetName = "color_sub_dropdown";

                    if (targetWidgetName) {
                        // 找出畫面上的那個下拉選單
                        const widget = this.widgets?.find(w => w.name === targetWidgetName);
                        if (widget) {
                            if (connected) {
                                // 【接上線時】：把選單的型態改成隱藏，並消除它佔用的高度
                                if (widget.type !== "hidden") {
                                    widget.origType = widget.type;
                                    widget.type = "hidden";
                                    widget.computeSize = () => [0, -4]; // 縮減高度讓介面保持緊湊
                                }
                            } else {
                                // 【拔掉線時】：把選單恢復原狀
                                if (widget.type === "hidden") {
                                    widget.type = widget.origType || "combo";
                                    delete widget.computeSize;
                                }
                            }
                            // 強制刷新 ComfyUI 畫布，讓變更立刻肉眼可見
                            app.graph.setDirtyCanvas(true, true);
                        }
                    }
                }
            };
        }
    }
});