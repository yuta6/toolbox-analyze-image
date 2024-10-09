import ctypes
import pystray
from pystray import MenuItem as item
from PIL import Image, ImageDraw
import tkinter as tk
from ctypes import windll, wintypes
from rich import print
import sys
import os
from concurrent.futures import ThreadPoolExecutor
import threading

# Pointクラスの定義
class Point:
    def __init__(self, x=0, y=0):
        self.x = x
        self.y = y

    @classmethod
    def get_mouse_position(cls):
        pt = wintypes.POINT()
        windll.user32.GetCursorPos(ctypes.byref(pt))
        print(pt.x, pt.y)
        return cls(pt.x, pt.y)
    
    def __str__(self) :
        return f"({self.x},{self.y})"

# Colorクラスの定義
class Color:
    def __init__(self, r=0, g=0, b=0):
        self.r = r
        self.g = g
        self.b = b

    @classmethod
    def get_color_at_position(cls, x, y):
        hdc = windll.user32.GetDC(0)
        color = windll.gdi32.GetPixel(hdc, x, y)
        windll.user32.ReleaseDC(0, hdc)
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

# カラーピッカーの表示用ウィンドウ
def color_picker_window(stop_event):
    root = tk.Tk()
    root.geometry("160x32")  # 長方形のウィンドウサイズに変更
    root.overrideredirect(True) # ウィンドウのデフォルトのタイトルバーや枠を削除
    root.attributes("-topmost", True) # ウィンドウを常に最前面に

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