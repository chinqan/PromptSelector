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
                            if (connected) {
                                // 【關鍵修復】：使用 ComfyUI 原生的隱藏標籤 "converted-widget"
                                if (widget.type !== "converted-widget") {
                                    widget.origType = widget.type;
                                    widget.type = "converted-widget"; 
                                    widget.computeSize = () => [0, -4]; // 消除佔用的高度
                                }
                            } else {
                                // 恢復原狀
                                if (widget.type === "converted-widget") {
                                    widget.type = widget.origType || "combo";
                                    delete widget.computeSize;
                                }
                            }
                            
                            // 【關鍵修復】：加入 10 毫秒的微小延遲，確保 LiteGraph 畫布更新完畢後再縮放節點
                            setTimeout(() => {
                                this.setSize(this.computeSize());
                                app.graph.setDirtyCanvas(true, true);
                            }, 10);
                        }
                    }
                }
            };
        }
    }
});