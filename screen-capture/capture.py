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
    def __init__(self, region : Point):
        s = ScreenSize()
        self.tup = (
            s.center.x - region.x//2,  # 左
            s.center.y - region.y//2,  # 上
            s.center.x + region.x//2,  # 右
            s.center.y + region.y//2   # 下
        )

def save_capture(np_image, directory: Path, extension: str = 'png'):
    base_filename = 'pic'
    index = 1  # 初期値

    # 保存先ディレクトリを指定
    directory = Path('../images') / directory  # カレントディレクトリをPathオブジェクトで指定
    if not directory.exists():
        directory.mkdir()

    path = directory / f'{base_filename}{index}.{extension}'
    while path.exists():
        index += 1
        path = directory / f'{base_filename}{index}.{extension}'
    
    # 画像を保存
    success = cv2.imwrite(str(path), np_image)
    return  str(path) if success else None

def capture_and_save(camera: dxcam.DXCamera , region: CaptureRegion, directory: Path, extension: str = 'png'):
    t1 = time.time()
    capture_nparray = camera.grab(region=region.tup) if region else camera.grab()
    if capture_nparray is None:
        print("キャプチャに失敗しました。")
        return

    t2 = time.time()
    filename = save_capture(capture_nparray, directory, extension)
    t3 = time.time()
    print("処理時間: {:2f} ms + {:2f} ms = {:2f} ms".format((t2 - t1) * 1000, (t3 - t2) * 1000, (t3 - t1) * 1000))
    print(
        "スクリーンショットをとりました。ファイル名:{}".format(filename) 
        if filename else "保存に失敗しました。"
    )

def parse_arguments():
    parser = argparse.ArgumentParser(description="スクリーンショットを撮影して保存します。")
    parser.add_argument("save_directory", type=str, nargs="?", default="", help="スクリーンショットの保存先ディレクトリ")
    parser.add_argument("-r", "--region", type=int, nargs="*", help="キャプチャ領域の幅と高さを指定")
    parser.add_argument("-ex", "--extension", type=str, default="png", help="拡張子")
    args = parser.parse_args()

    directory = Path(args.save_directory)

    match args.region:
        case None:
            region = None
        case [value1]:
            region = Point(value1, value1)
        case [value1, value2]:
            region = Point(value1, value2)
        case _:
            raise ValueError("キャプチャ領域は1つまたは2つの値を指定してください")

    return directory, region, args.extension


def main():
    print("Altキーでスクリーンショットを保存します。ENDキーで終了します。")

    directory, region, extension = parse_arguments()

    camera = dxcam.create(output_color="BGR")
    region = CaptureRegion(region) if region else None

    keyboard.add_hotkey('alt', capture_and_save, args=(camera, region, directory, extension))
    keyboard.wait('end')

    print("終了します")

main()
