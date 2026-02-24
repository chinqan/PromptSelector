import { app } from "../../scripts/app.js";

app.registerExtension({
    name: "MyCustomNodes.AutoHideWidgets",
    async nodeCreated(node) {
        const targetNodes = [
            "MyHairSelector", "AccessoriesSelector", "BagsSelector", 
            "BottomsSelector", "NeckwearSelector", "ShoesSelector", 
            "TopsSelector", "WristSelector"
        ];

        if (targetNodes.includes(node.comfyClass)) {
            // 偵錯日誌 1：確認腳本有綁定到節點上
            console.log(`[MyCustomNodes] 成功掛載動態隱藏功能到節點: ${node.comfyClass}`);

            const onConnectionsChange = node.onConnectionsChange;
            node.onConnectionsChange = function(type, index, connected, link_info) {
                if (onConnectionsChange) {
                    onConnectionsChange.apply(this, arguments);
                }
                
                // type === 1 代表發生改變的是「輸入端點 (Input)」
                if (type === 1) {
                    const input = this.inputs[index];
                    let targetWidgetName = null;

                    if (input.name === "color") targetWidgetName = "color_dropdown";
                    if (input.name === "color_main") targetWidgetName = "color_main_dropdown";
                    if (input.name === "color_sub") targetWidgetName = "color_sub_dropdown";

                    if (targetWidgetName) {
                        const widget = this.widgets?.find(w => w.name === targetWidgetName);
                        if (widget) {
                            // 偵錯日誌 2：確認連線動作有被觸發
                            console.log(`[MyCustomNodes] 偵測到連線變化: ${input.name} -> ${connected ? "接上" : "拔除"}`);
                            
                            if (connected) {
                                if (widget.type !== "hidden") {
                                    widget.origType = widget.type;
                                    widget.origComputeSize = widget.computeSize;
                                    widget.type = "hidden";
                                    widget.computeSize = () => [0, -4]; 
                                }
                            } else {
                                if (widget.type === "hidden") {
                                    widget.type = widget.origType || "combo";
                                    widget.computeSize = widget.origComputeSize;
                                }
                            }
                            
                            // 【關鍵修復】：強制節點重新計算自己的高度，這樣選單才會真的縮回去！
                            this.setSize(this.computeSize());
                            app.graph.setDirtyCanvas(true, true);
                        }
                    }
                }
            };
        }
    }
});