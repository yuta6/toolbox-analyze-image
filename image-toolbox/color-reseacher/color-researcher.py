import tkinter as tk
from tkinter import filedialog
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
        photo_image = tk.PhotoImage(data=cv2.imencode('.png', cv2.cvtColor(rgb_image, cv2.COLOR_RGB2BGR))[1].tobytes())
        self.canvas.image = photo_image
        self.canvas.configure(image=photo_image)


class HSVControlPanel:
    """HSVスライダーのコントロールパネルを表現するクラス"""
    def __init__(self, master, hsv_range: HSVRange, on_change_callback):
        self.master = master
        self.hsv_range = hsv_range
        self.on_change_callback = on_change_callback

        self.frame = ttk.LabelFrame(self.master, text="HSV Controls")
        self.frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")

        self.hue_min_slider, self.hue_max_slider = self.create_double_slider("Hue", 0, 179, self.hsv_range.h_min, self.hsv_range.h_max)
        self.sat_min_slider, self.sat_max_slider = self.create_double_slider("Saturation", 0, 255, self.hsv_range.s_min, self.hsv_range.s_max)
        self.val_min_slider, self.val_max_slider = self.create_double_slider("Value", 0, 255, self.hsv_range.v_min, self.hsv_range.v_max)

    def create_double_slider(self, text, from_, to, initial_min, initial_max):
        """minとmaxの両方を指定できるスライダーを作成するヘルパー関数"""
        label = ttk.Label(self.frame, text=text)
        label.pack()
        min_slider = ttk.Scale(self.frame, from_=from_, to=to, orient="horizontal", command=self._on_slider_change)
        min_slider.set(initial_min)
        min_slider.pack(fill="x", padx=5, pady=5)
        max_slider = ttk.Scale(self.frame, from_=from_, to=to, orient="horizontal", command=self._on_slider_change)
        max_slider.set(initial_max)
        max_slider.pack(fill="x", padx=5, pady=5)
        return min_slider, max_slider

    def _on_slider_change(self, event):
        """スライダーの値が変更されたときに呼び出される"""
        self.hsv_range.h_min = int(self.hue_min_slider.get())
        self.hsv_range.h_max = int(self.hue_max_slider.get())
        self.hsv_range.s_min = int(self.sat_min_slider.get()) if hasattr(self, 'sat_min_slider') else 0
        self.hsv_range.s_max = int(self.sat_max_slider.get())
        self.hsv_range.v_min = int(self.val_min_slider.get()) if hasattr(self, 'val_min_slider') else 0
        self.hsv_range.v_max = int(self.val_max_slider.get())
        self.on_change_callback()


class ColorReacherApp:
    """メインアプリケーションクラス"""
    def __init__(self, root, image_path):
        self.root = root
        self.root.title("Color Reacher App")

        self.image_processor = ImageProcessor(image_path)
        self.hsv_range = HSVRange()

        self.original_image_viewer = ImageViewer(self.root, self.image_processor.original_image, "Original Image")
        self.original_image_viewer.canvas.grid(row=0, column=2, padx=10, pady=10)

        self.filtered_image_viewer = ImageViewer(self.root, self.image_processor.original_image, "Filtered Image")
        self.filtered_image_viewer.canvas.grid(row=1, column=2, padx=10, pady=10)

        self.hsv_control_panel = HSVControlPanel(self.root, self.hsv_range, self.update_filtered_image)

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