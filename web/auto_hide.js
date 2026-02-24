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
            
            // 建立一個專門控制顯示/隱藏的函式
            const toggleWidget = (nodeInstance, inputName, isConnected) => {
                let targetWidgetName = null;
                if (inputName === "color") targetWidgetName = "color_dropdown";
                if (inputName === "color_main") targetWidgetName = "color_main_dropdown";
                if (inputName === "color_sub") targetWidgetName = "color_sub_dropdown";

                if (targetWidgetName) {
                    const widget = nodeInstance.widgets?.find(w => w.name === targetWidgetName);
                    if (widget) {
                        if (isConnected) {
                            // 【終極隱藏法】：三管齊下，徹底封殺顯示
                            if (!widget.origType) widget.origType = widget.type;
                            widget.type = "hidden";      // 1. 欺騙 ComfyUI
                            widget.hidden = true;        // 2. 觸發 LiteGraph 原生隱藏機制
                            widget.computeSize = () => [0, -4]; // 3. 抹除佔用高度
                        } else {
                            // 【恢復原狀】
                            widget.type = widget.origType || "combo";
                            widget.hidden = false;
                            delete widget.computeSize;
                        }
                        
                        // 強制刷新節點大小與畫布
                        setTimeout(() => {
                            nodeInstance.setSize(nodeInstance.computeSize());
                            app.graph.setDirtyCanvas(true, true);
                        }, 10);
                    } else {
                        console.warn(`[MyCustomNodes] 找不到選單: ${targetWidgetName}`);
                    }
                }
            };

            // 1. 攔截「動態連線發生改變」的瞬間
            const onConnectionsChange = node.onConnectionsChange;
            node.onConnectionsChange = function(type, index, connected, link_info) {
                if (onConnectionsChange) {
                    onConnectionsChange.apply(this, arguments);
                }
                if (type === 1) { // 1 代表 Input 發生變化
                    const input = this.inputs[index];
                    toggleWidget(this, input.name, connected);
                }
            };

            // 2. 【關鍵新增】：節點剛載入 (或按 F5 重整) 時，自動檢查一遍已接上的線
            setTimeout(() => {
                if (node.inputs) {
                    node.inputs.forEach((input) => {
                        // 如果該洞口已經有連線 (link !== null)，就立刻執行隱藏
                        if (input.link != null) {
                            toggleWidget(node, input.name, true);
                        }
                    });
                }
            }, 100);
            
        }
    }
});