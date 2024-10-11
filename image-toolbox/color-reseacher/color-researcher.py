import tkinter as tk
from tkinter import ttk
import cv2
import numpy as np
import sys

class HSVRange:
    """HSV色空間の範囲を表現するクラス"""
    def __init__(self, h_min=0, h_max=179, s_min=0, s_max=255, v_min=0, v_max=255):
        self.h_min = h_min
        self.h_max = h_max
        self.s_min = s_min
        self.s_max = s_max
        self.v_min = v_min
        self.v_max = v_max

    def to_numpy_array(self):
        """OpenCVで使用できるNumpy配列に変換する"""
        return np.array([self.h_min, self.s_min, self.v_min]), np.array([self.h_max, self.s_max, self.v_max])

class ImageProcessor:
    """画像処理を担当するクラス"""
    def __init__(self, image_path):
        self.original_image = cv2.imread(image_path)

    def apply_hsv_filter(self, hsv_range: HSVRange):
        """HSV範囲に基づいて画像をフィルター処理する"""
        hsv_image = cv2.cvtColor(self.original_image, cv2.COLOR_BGR2HSV)
        lower_bound, upper_bound = hsv_range.to_numpy_array()
        mask = cv2.inRange(hsv_image, lower_bound, upper_bound)
        filtered_image = cv2.bitwise_and(self.original_image, self.original_image, mask=mask)
        return filtered_image

class ImageViewer:
    """画像を表示するクラス"""
    def __init__(self, master, image, title="Image"):
        self.master = master
        self.title = title
        
        self.canvas = tk.Label(master)
        self.canvas.grid(row=1, column=0, padx=10, pady=5)
        self.update_image(image)

    def update_image(self, image):
        """画像を更新する"""
        height = 600
        aspect_ratio = image.shape[1] / image.shape[0]
        width = int(height * aspect_ratio)
        resized_image = cv2.resize(image, (width, height))
        rgb_image = cv2.cvtColor(resized_image, cv2.COLOR_BGR2RGB)
        # 画像をPhotoImageに変換
        img = cv2.imencode('.png', cv2.cvtColor(rgb_image, cv2.COLOR_RGB2BGR))[1].tobytes()
        photo_image = tk.PhotoImage(data=img)
        self.canvas.image = photo_image
        self.canvas.configure(image=photo_image)

class DualSlider(tk.Canvas):
    def __init__(self, master, label, from_, to, initial_min, initial_max, command=None, **kwargs):
        super().__init__(master, height=50, **kwargs)
        self.label = label
        self.from_ = from_
        self.to = to
        self.command = command
        self.min_val = initial_min
        self.max_val = initial_max

        # スライダーのパラメータ
        self.width = 300
        self.height = 50
        self.padding = 20
        self.handle_radius = 10

        self.configure(width=self.width, height=self.height)

        # 描画
        self.create_text(10, 10, anchor='w', text=self.label)
        self.track = self.create_line(self.padding, self.height/2, self.width - self.padding, self.height/2, width=4, fill='grey')
        self.range_line = self.create_line(0, self.height/2, 0, self.height/2, width=4, fill='blue')

        # ハンドルの位置を計算
        self.min_pos = self.value_to_pos(self.min_val)
        self.max_pos = self.value_to_pos(self.max_val)

        # ハンドルを描画
        self.min_handle = self.create_oval(self.min_pos - self.handle_radius, self.height/2 - self.handle_radius,
                                          self.min_pos + self.handle_radius, self.height/2 + self.handle_radius,
                                          fill='green', outline='black', tags="min_handle")
        self.max_handle = self.create_oval(self.max_pos - self.handle_radius, self.height/2 - self.handle_radius,
                                          self.max_pos + self.handle_radius, self.height/2 + self.handle_radius,
                                          fill='red', outline='black', tags="max_handle")

        # 範囲線を描画
        self.range_line = self.create_line(self.min_pos, self.height/2, self.max_pos, self.height/2, width=4, fill='blue')

        # イベントバインド
        self.bind("<Button-1>", self.click)
        self.bind("<B1-Motion>", self.drag)

        self.current_handle = None

    def value_to_pos(self, value):
        """値を位置に変換"""
        ratio = (value - self.from_) / (self.to - self.from_)
        return self.padding + ratio * (self.width - 2 * self.padding)

    def pos_to_value(self, pos):
        """位置を値に変換"""
        ratio = (pos - self.padding) / (self.width - 2 * self.padding)
        ratio = min(max(ratio, 0), 1)
        return int(self.from_ + ratio * (self.to - self.from_))

    def click(self, event):
        """クリック時の処理"""
        x = event.x
        y = event.y
        if self.is_over_handle(x, y, self.min_handle):
            self.current_handle = 'min'
        elif self.is_over_handle(x, y, self.max_handle):
            self.current_handle = 'max'
        else:
            self.current_handle = None

    def drag(self, event):
        """ドラッグ時の処理"""
        if self.current_handle is None:
            return
        x = min(max(event.x, self.padding), self.width - self.padding)
        value = self.pos_to_value(x)
        if self.current_handle == 'min':
            if value > self.max_val:
                value = self.max_val
            self.min_val = value
            self.coords(self.min_handle, x - self.handle_radius, self.height/2 - self.handle_radius,
                        x + self.handle_radius, self.height/2 + self.handle_radius)
        elif self.current_handle == 'max':
            if value < self.min_val:
                value = self.min_val
            self.max_val = value
            self.coords(self.max_handle, x - self.handle_radius, self.height/2 - self.handle_radius,
                        x + self.handle_radius, self.height/2 + self.handle_radius)
        # 更新範囲線
        self.coords(self.range_line, self.value_to_pos(self.min_val), self.height/2,
                    self.value_to_pos(self.max_val), self.height/2)
        if self.command:
            self.command(self.min_val, self.max_val)

    def is_over_handle(self, x, y, handle):
        """ハンドルの上にカーソルがあるか確認"""
        coords = self.coords(handle)
        x0, y0, x1, y1 = coords
        return x0 <= x <= x1 and y0 <= y <= y1

    def get_values(self):
        """現在のminとmaxの値を取得"""
        return self.min_val, self.max_val

class HSVControlPanel:
    """HSVスライダーのコントロールパネルを表現するクラス"""
    def __init__(self, master, hsv_range: HSVRange, on_change_callback):
        self.master = master
        self.hsv_range = hsv_range
        self.on_change_callback = on_change_callback

        self.frame = ttk.LabelFrame(self.master, text="HSV Controls")
        self.frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")

        # デュアルスライダーを作成
        self.hue_slider = DualSlider(self.frame, "Hue", 0, 179, self.hsv_range.h_min, self.hsv_range.h_max, self.on_hue_change)
        self.hue_slider.pack(fill="x", padx=5, pady=5)

        self.sat_slider = DualSlider(self.frame, "Saturation", 0, 255, self.hsv_range.s_min, self.hsv_range.s_max, self.on_sat_change)
        self.sat_slider.pack(fill="x", padx=5, pady=5)

        self.val_slider = DualSlider(self.frame, "Value", 0, 255, self.hsv_range.v_min, self.hsv_range.v_max, self.on_val_change)
        self.val_slider.pack(fill="x", padx=5, pady=5)

    def on_hue_change(self, min_val, max_val):
        self.hsv_range.h_min = min_val
        self.hsv_range.h_max = max_val
        self.on_change_callback()

    def on_sat_change(self, min_val, max_val):
        self.hsv_range.s_min = min_val
        self.hsv_range.s_max = max_val
        self.on_change_callback()

    def on_val_change(self, min_val, max_val):
        self.hsv_range.v_min = min_val
        self.hsv_range.v_max = max_val
        self.on_change_callback()

class ColorReacherApp:
    """メインアプリケーションクラス"""
    def __init__(self, root, image_path):
        self.root = root
        self.root.title("Color Reacher App")

        self.image_processor = ImageProcessor(image_path)
        self.hsv_range = HSVRange()

        # 元画像ビューア
        self.original_image_viewer = ImageViewer(self.root, self.image_processor.original_image, "Original Image")
        self.original_image_viewer.canvas.grid(row=0, column=2, padx=10, pady=10)

        # フィルタ済み画像ビューア
        self.filtered_image_viewer = ImageViewer(self.root, self.image_processor.original_image, "Filtered Image")
        self.filtered_image_viewer.canvas.grid(row=1, column=2, padx=10, pady=10)

        # HSVコントロールパネル
        self.hsv_control_panel = HSVControlPanel(self.root, self.hsv_range, self.update_filtered_image)

        # 初期フィルタ適用
        self.update_filtered_image()

    def update_filtered_image(self):
        """フィルター処理された画像を更新する"""
        filtered_image = self.image_processor.apply_hsv_filter(self.hsv_range)
        self.filtered_image_viewer.update_image(filtered_image)

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python color-reacher.py <image_path>")
        sys.exit(1)
    
    image_path = sys.argv[1]
    root = tk.Tk()
    app = ColorReacherApp(root, image_path)
    root.mainloop()
