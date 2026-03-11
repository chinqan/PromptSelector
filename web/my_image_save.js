import { app } from "../../scripts/app.js";
import { api } from "../../scripts/api.js";

// ============================================================
// myImageSave — 節點預覽圖 + 解析度標籤
// ============================================================
app.registerExtension({
    name: "MyCustomNodes.myImageSave",

    async nodeCreated(node) {
        if (node.comfyClass !== "myImageSave") return;

        // ── 建立預覽區域 DOM（嵌入 LiteGraph canvas overlay） ──
        // 我們使用 HTMLElement widget 的方式把預覽插入節點

        // 自訂一個 widget：imgPreview
        const previewWidget = node.addDOMWidget("imgPreview", "preview", (() => {
            const container = document.createElement("div");
            container.style.cssText = `
                width: 100%;
                background: #1a1a1a;
                border-radius: 6px;
                overflow: hidden;
                display: none;           /* 執行前隱藏 */
                flex-direction: column;
                align-items: center;
                gap: 0;
            `;

            const img = document.createElement("img");
            img.style.cssText = `
                width: 100%;
                height: auto;
                display: block;
                object-fit: contain;
            `;

            const resLabel = document.createElement("div");
            resLabel.style.cssText = `
                width: 100%;
                text-align: center;
                font-size: 11px;
                color: #aaaaaa;
                background: #111;
                padding: 3px 0 4px;
                letter-spacing: 0.5px;
                font-family: monospace;
            `;
            resLabel.textContent = "";

            container.appendChild(img);
            container.appendChild(resLabel);

            // 把 img / resLabel 附掛在 container 上，方便外部更新
            container._img = img;
            container._resLabel = resLabel;

            return container;
        })());

        // ── 監聽 ComfyUI 執行完成事件，取出預覽資料 ──
        const onExecuted = node.onExecuted;
        node.onExecuted = function(message) {
            if (onExecuted) onExecuted.apply(this, arguments);

            const images = message?.images;
            if (!images || images.length === 0) return;

            const container = previewWidget.element;
            const imgEl     = container._img;
            const resEl     = container._resLabel;

            // 取第一張（通常 batch 只取第一張預覽）
            const first = images[0];
            const { filename, subfolder, type, width, height } = first;

            // 組出 ComfyUI view 路由 URL
            const params = new URLSearchParams({
                filename,
                subfolder: subfolder || "",
                type:      type || "output",
                rand:      Math.random(),   // 避免瀏覽器快取舊圖
            });
            imgEl.src = `/view?${params.toString()}`;

            // 解析度標籤
            if (width && height) {
                resEl.textContent = `${width} × ${height} px`;
            } else {
                resEl.textContent = filename;
            }

            // 顯示容器
            container.style.display = "flex";

            // 強制節點重新計算尺寸
            setTimeout(() => {
                node.setSize(node.computeSize());
                app.graph.setDirtyCanvas(true, true);
            }, 50);
        };
    },
});
