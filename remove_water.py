import tkinter as tk
from tkinter import filedialog, messagebox
import cv2
import numpy as np
from PIL import Image, ImageTk, ImageDraw


class WatermarkRemoverApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Python 图片去水印小工具")
        self.root.geometry("1000x700")

        # 初始化变量
        self.original_image_cv = None  # OpenCV格式的原图
        self.display_image = None  # 用于显示的PIL格式图
        self.mask_image = None  # 用于记录涂抹轨迹的Mask (PIL 'L' mode)
        self.draw = None  # Mask的绘图笔
        self.brush_size = 15  # 笔刷大小
        self.scale_ratio = 1.0  # 图片缩放比例

        # UI 布局
        self._setup_ui()

    def _setup_ui(self):
        # 顶部按钮区
        btn_frame = tk.Frame(self.root, pady=10)
        btn_frame.pack(side=tk.TOP, fill=tk.X)

        tk.Button(btn_frame, text="1. 打开图片", command=self.load_image, bg="#e1f5fe").pack(side=tk.LEFT, padx=10)
        tk.Button(btn_frame, text="2. 去除水印", command=self.remove_watermark, bg="#c8e6c9").pack(side=tk.LEFT,
                                                                                                   padx=10)
        tk.Button(btn_frame, text="3. 保存图片", command=self.save_image, bg="#fff9c4").pack(side=tk.LEFT, padx=10)
        tk.Button(btn_frame, text="重置", command=self.reset_canvas).pack(side=tk.LEFT, padx=10)

        # 笔刷大小滑块
        tk.Label(btn_frame, text="笔刷大小:").pack(side=tk.LEFT, padx=(20, 5))
        self.scale_slider = tk.Scale(btn_frame, from_=3, to=50, orient=tk.HORIZONTAL, command=self.change_brush_size)
        self.scale_slider.set(15)
        self.scale_slider.pack(side=tk.LEFT)

        # 画布区域
        self.canvas_frame = tk.Frame(self.root)
        self.canvas_frame.pack(fill=tk.BOTH, expand=True)

        self.canvas = tk.Canvas(self.canvas_frame, bg="gray", cursor="cross")
        self.canvas.pack(fill=tk.BOTH, expand=True)

        # 绑定鼠标事件
        self.canvas.bind("<B1-Motion>", self.paint)
        self.canvas.bind("<ButtonPress-1>", self.paint)

    def change_brush_size(self, val):
        self.brush_size = int(val)

    def load_image(self):
        file_path = filedialog.askopenfilename(filetypes=[("Image files", "*.jpg *.jpeg *.png *.bmp")])
        if not file_path:
            return

        # 读取图片 (处理中文路径问题)
        self.original_image_cv = cv2.imdecode(np.fromfile(file_path, dtype=np.uint8), -1)
        # 如果有透明通道，转为RGB
        if self.original_image_cv.shape[2] == 4:
            self.original_image_cv = cv2.cvtColor(self.original_image_cv, cv2.COLOR_BGRA2BGR)

        self.reset_canvas()

    def reset_canvas(self):
        if self.original_image_cv is None:
            return

        # 转换 OpenCV (BGR) -> PIL (RGB)
        image_rgb = cv2.cvtColor(self.original_image_cv, cv2.COLOR_BGR2RGB)
        pil_image = Image.fromarray(image_rgb)

        # 计算缩放比例以适应窗口
        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()

        # 简单的自适应缩放逻辑
        img_w, img_h = pil_image.size
        ratio = min(canvas_width / img_w, canvas_height / img_h, 1.0)
        self.scale_ratio = ratio

        new_w = int(img_w * ratio)
        new_h = int(img_h * ratio)

        self.display_image = pil_image.resize((new_w, new_h), Image.Resampling.LANCZOS)
        self.tk_image = ImageTk.PhotoImage(self.display_image)

        # 绘制到画布中心
        self.canvas.delete("all")
        self.canvas.create_image(canvas_width // 2, canvas_height // 2, image=self.tk_image, anchor=tk.CENTER)

        # 获取图片在画布上的偏移量，用于坐标转换
        self.offset_x = (canvas_width - new_w) // 2
        self.offset_y = (canvas_height - new_h) // 2

        # 创建一个与原图一样大的空白 Mask，用于记录涂抹区域
        self.mask_image = Image.new("L", (img_w, img_h), 0)
        self.draw = ImageDraw.Draw(self.mask_image)

    def paint(self, event):
        if self.original_image_cv is None:
            return

        # 1. 在屏幕 Canvas 上绘制红色痕迹 (视觉反馈)
        x1, y1 = (event.x - self.brush_size), (event.y - self.brush_size)
        x2, y2 = (event.x + self.brush_size), (event.y + self.brush_size)
        self.canvas.create_oval(x1, y1, x2, y2, fill="red", outline="red")

        # 2. 在 Mask 图片上绘制白色痕迹 (逻辑处理)
        # 需要将屏幕坐标映射回原图坐标
        real_x = int((event.x - self.offset_x) / self.scale_ratio)
        real_y = int((event.y - self.offset_y) / self.scale_ratio)

        # 根据缩放调整笔刷在原图上的大小
        real_brush = int(self.brush_size / self.scale_ratio)

        self.draw.ellipse([real_x - real_brush, real_y - real_brush,
                           real_x + real_brush, real_y + real_brush], fill=255, outline=255)

    def remove_watermark(self):
        if self.original_image_cv is None:
            return

        # 将 PIL Mask 转换为 OpenCV 格式
        mask_np = np.array(self.mask_image)

        # 核心算法：Telea 算法 (也可以尝试 cv2.INPAINT_NS)
        # 3 是修复半径，半径越小细节越好，半径越大适合去除大块水印
        result = cv2.inpaint(self.original_image_cv, mask_np, 3, cv2.INPAINT_TELEA)

        # 更新当前图像
        self.original_image_cv = result
        self.reset_canvas()
        messagebox.showinfo("完成", "水印去除成功！如果效果不满意可以重置后调整笔刷。")

    def save_image(self):
        if self.original_image_cv is None:
            return
        file_path = filedialog.asksaveasfilename(defaultextension=".jpg",
                                                 filetypes=[("JPEG", "*.jpg"), ("PNG", "*.png")])
        if file_path:
            # OpenCV保存不支持中文路径，使用imencode
            is_success, im_buf = cv2.imencode(".jpg", self.original_image_cv)
            if is_success:
                im_buf.tofile(file_path)
                messagebox.showinfo("保存", "图片保存成功！")


if __name__ == "__main__":
    root = tk.Tk()
    app = WatermarkRemoverApp(root)
    root.mainloop()