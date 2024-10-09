import ctypes
import pystray
from pystray import MenuItem as item
from PIL import Image, ImageDraw
import tkinter as tk
from ctypes import windll, wintypes
from rich import print 

# マウスの位置を取得
def get_mouse_position():
    pt = wintypes.POINT()
    windll.user32.GetCursorPos(ctypes.byref(pt))
    print(pt.x, pt.y)
    return pt.x, pt.y

# 指定した位置のピクセル色を取得
def get_color_at_position(x, y):
    hdc = windll.user32.GetDC(0)
    color = windll.gdi32.GetPixel(hdc, x, y)
    windll.user32.ReleaseDC(0, hdc)
    return (color & 0xFF), ((color >> 8) & 0xFF), ((color >> 16) & 0xFF)

# カラーピッカーの表示用ウィンドウ
def color_picker_window():
    root = tk.Tk()
    root.geometry("50x50")
    root.overrideredirect(True)
    root.attributes("-topmost", True)

    # ウィンドウの色を変更
    def update_color():
        x, y = get_mouse_position()
        color = get_color_at_position(x, y)
        root.configure(bg='#%02x%02x%02x' % color)
        root.geometry(f"+{x+20}+{y+20}")
        root.after(100, update_color)

    update_color()
    root.mainloop()

# システムトレイアイコンの設定
def setup_tray():
    ctypes.windll.user32.SetProcessDPIAware()
    icon_image = Image.new('RGB', (64, 64), color=(73, 109, 137))
    draw = ImageDraw.Draw(icon_image)
    draw.rectangle([16, 16, 48, 48], fill=(255, 255, 255))

    tray_icon = pystray.Icon("color_picker", icon_image, menu=pystray.Menu(
        item("Start", lambda: color_picker_window()),
        item("Exit", lambda: tray_icon.stop())
    ))
    tray_icon.run()

setup_tray()
