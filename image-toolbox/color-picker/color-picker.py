from concurrent.futures import ThreadPoolExecutor
import tkinter as tk
import ctypes
import threading

import pystray
from pystray import MenuItem as item
from PIL import Image, ImageDraw
from rich import print
import keyboard
import pyperclip
import cv2
import numpy

# Pointクラスの定義
class Point:
    def __init__(self, x=0, y=0):
        self.x = x
        self.y = y

    @classmethod
    def get_mouse_position(cls):
        pt = ctypes.wintypes.POINT()
        ctypes.windll.user32.GetCursorPos(ctypes.byref(pt))
        print(pt.x, pt.y)
        return cls(pt.x, pt.y)
    
    def __str__(self):
        return f"({self.x},{self.y})"

# Colorクラスの定義
class Color:
    def __init__(self, r=0, g=0, b=0):
        self.r = r
        self.g = g
        self.b = b

    @classmethod
    def get_color_at_position(cls, x, y):
        hdc = ctypes.windll.user32.GetDC(0)
        color = ctypes.windll.gdi32.GetPixel(hdc, x, y)
        ctypes.windll.user32.ReleaseDC(0, hdc)
        return cls((color & 0xFF), ((color >> 8) & 0xFF), ((color >> 16) & 0xFF))

    def to_hex(self):
        return '#%02x%02x%02x' % (self.r, self.g, self.b)

    def is_dark(self):
        # 明るさを R^2 + G^2 + B^2 で判定する
        brightness = self.r**2 + self.g**2 + self.b**2
        threshold = (128**2) * 3  # 128 の 2 乗を 3 色分の合計
        return brightness < threshold

    def __str__(self):
        return f"R: {self.r}, G: {self.g}, B: {self.b}"
    
    @property
    def rgb_np(self):
        return numpy.array([self.r, self.g, self.b])

    @property
    def hsv_np(self):
        # NumPyの配列に変換（OpenCVはBGR形式を使用するため、順序を変換）
        rgb_array = numpy.uint8([[self.rgb_np()[::-1]]])  # BGRに並べ替え
        hsv_array = cv2.cvtColor(rgb_array, cv2.COLOR_BGR2HSV)
        return hsv_array[0][0]  # 結果を1次元配列として返す

# カラーピッカーの表示用ウィンドウ
def color_picker_window(stop_event):
    root = tk.Tk()
    root.geometry("160x32")  # 長方形のウィンドウサイズに変更
    root.overrideredirect(True)  # ウィンドウのデフォルトのタイトルバーや枠を削除
    root.attributes("-topmost", True)  # ウィンドウを常に最前面に

    label = tk.Label(root, text="", font=("Helvetica", 8))
    label.place(relx=0.5, rely=0.5, anchor="center")

    # ウィンドウの色を変更
    def update_color():
        if stop_event.is_set():
            root.quit()
            return
        point = Point.get_mouse_position()
        color = Color.get_color_at_position(point.x, point.y)
        root.configure(bg=color.to_hex())
        root.geometry(f"+{point.x+20}+{point.y+20}")
        label.config(
            text=f"{color.to_hex()} {point}\n{color}", 
            fg="white" if color.is_dark() else "black",
            bg=color.to_hex()
        )
        root.after(100, update_color)

    # F1キーで座標と色をクリップボードに保存
    def copy_to_clipboard():
        point = Point.get_mouse_position()
        color = Color.get_color_at_position(point.x, point.y)
        clipboard_text = f"Position: {point}, Color: {color.to_hex()} ({color}, HSV: {color.hsv_np})"
        pyperclip.copy(clipboard_text)
        print(f"Copied to clipboard: {clipboard_text}")

    keyboard.add_hotkey('f1', copy_to_clipboard)
    update_color()
    root.mainloop()

# システムトレイアイコンの設定
def setup_tray(stop_event):
    icon_image = Image.new('RGB', (64, 64), color=(73, 109, 137))
    draw = ImageDraw.Draw(icon_image)
    draw.rectangle([16, 16, 48, 48], fill=(255, 255, 255))

    def on_exit(icon, item):
        stop_event.set()
        icon.stop()

    tray_icon = pystray.Icon("color_picker", icon_image, menu=pystray.Menu(
        item("Exit", on_exit)
    ))
    tray_icon.run()

# メイン関数
def main():
    ctypes.windll.user32.SetProcessDPIAware()
    stop_event = threading.Event()  # ストップ用のイベントを作成

    with ThreadPoolExecutor() as executor:
        executor.submit(color_picker_window, stop_event)
        executor.submit(setup_tray, stop_event)

main()