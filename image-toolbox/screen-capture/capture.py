from typing import NamedTuple
import ctypes
import dxcam
import time 
import cv2
import keyboard

from pathlib import Path
import argparse

class Point(NamedTuple):
    x: int
    y: int

class ScreenSize: 
    def __init__(self):
        self.width = int(ctypes.windll.user32.GetSystemMetrics(0))  
        self.height = int(ctypes.windll.user32.GetSystemMetrics(1))
        self.center = Point(self.width // 2, self.height // 2)

class CaptureRegion:
    def __init__(self, radius):
        s = ScreenSize()
        self.tup = (
            s.center.x - radius,  # 左
            s.center.y - radius,  # 上
            s.center.x + radius,  # 右
            s.center.y + radius   # 下
        )

def save_capture(np_image, directory: Path):
    base_filename = 'pic'
    file_extension = '.png'
    index = 1  # 初期値

    # 保存先ディレクトリを指定
    directory = Path('.') / directory  # カレントディレクトリをPathオブジェクトで指定
    if not directory.exists():
        directory.mkdir()

    path = directory / f'{base_filename}{index}{file_extension}'
    while path.exists():
        index += 1
        path = directory / f'{base_filename}{index}{file_extension}'
    
    # 画像を保存
    success = cv2.imwrite(str(path), np_image)
    return  str(path) if success else None

def capture_and_save(camera: dxcam.DXCamera , region: CaptureRegion, directory: Path):
    t1 = time.time()
    capture_nparray = camera.grab(region=region.tup) if region else camera.grab()
    t2 = time.time()
    filename = save_capture(capture_nparray, directory)
    t3 = time.time()
    print("処理時間: {:2f} ms + {:2f} ms = {:2f} ms".format((t2 - t1) * 1000, (t3 - t2) * 1000, (t3 - t1) * 1000))
    print(
        "スクリーンショットをとりました。ファイル名:{}".format(filename) 
        if filename else "キャプチャーに失敗しました。"
    ) 


def main():
    print("F1キーでスクリーンショットを保存します。ENDキーで終了します。")

    parser = argparse.ArgumentParser(description="スクリーンショットを撮影して保存します。")
    parser.add_argument("save_directory", type=str, nargs="?", default="output", help="スクリーンショットの保存先ディレクトリ")
    parser.add_argument("-r", "--radius", type=int, default=0, help="キャプチャ領域の半径を指定")
    args = parser.parse_args()

    directory = Path(args.save_directory)
    radius = args.radius
    
    camera = dxcam.create(output_color="BGR")
    region = CaptureRegion(radius) if radius > 0 else None  # 半径480のキャプチャ領域を指定

    # ホットキーの設定
    keyboard.add_hotkey('f1', capture_and_save, args=(camera, region, directory))
    keyboard.wait('end')

    print("終了します")

main()

    