import { app } from "../../scripts/app.js";
import { api } from "../../scripts/api.js";

// ============================================================
// myImageSave — 節點預覽圖（使用 ComfyUI 原生 node.imgs 機制）
//               + 解析度文字 widget
// ============================================================
app.registerExtension({
    name: "MyCustomNodes.myImageSave",

    async nodeCreated(node) {
        if (node.comfyClass !== "myImageSave") return;

        // 加入解析度文字 widget（顯示在節點底部）
        const resWidget = node.addWidget("text", "📐 解析度", "", () => {}, {
            serialize: false,   // 不寫入工作流 JSON
        });
        resWidget.disabled = true;  // 唯讀

        // 監聽執行完成事件
        const onExecuted = node.onExecuted;
        node.onExecuted = function (message) {
            if (onExecuted) onExecuted.apply(this, arguments);

            const images = message?.images;
            if (!images || images.length === 0) return;

            // 只取第一張圖
            const first = images[0];
            const { filename, subfolder, type, width, height } = first;

            // ── 1. 設定 node.imgs，讓 ComfyUI 原生機制渲染預覽 ──
            const imgEl = new Image();
            imgEl.src = api.apiURL(
                `/view?filename=${encodeURIComponent(filename)}`
                + `&type=${type || "output"}`
                + `&subfolder=${encodeURIComponent(subfolder || "")}`
                + `&rand=${Math.random()}`
            );
            this.imgs = [imgEl];

            // 圖片載入後自動調整節點尺寸
            imgEl.onload = () => {
                if (this.setSizeForImage) this.setSizeForImage();
                app.graph.setDirtyCanvas(true, true);
            };

            // ── 2. 更新解析度 widget ──
            if (width && height) {
                resWidget.value = `${width} × ${height} px`;
            } else {
                resWidget.value = filename;
            }

            app.graph.setDirtyCanvas(true, true);
        };
    },
});
