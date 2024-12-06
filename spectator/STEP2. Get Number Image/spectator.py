import pathlib

import cv2
import numpy as np
from rich import print
from rich.progress import track
import os

# 画像が保存されているディレクトリ
directory_path = "./images"  # カレントディレクトリを指定

# 保存先ディレクトリ（フィルタ後の画像を保存するディレクトリ）
output_directory = "./filtered_images/"
os.makedirs(output_directory, exist_ok=True)

# フィルターの設定
# ここではHSV色空間を使用しています。必要に応じてRGBに変更してください。
# 例として、V（明度）が200〜255、S（彩度）が0〜10、H（色相）は全範囲（0〜255）の場合

# HSVの下限と上限を設定
lower_hsv = np.array([0, 0, 223])    # H: 0, S: 0, V: 200
upper_hsv = np.array([255, 32, 255])  # H: 255, S: 10, V: 255

# フィルタリングの詳細をファイル名に含めるための設定文字列
filter_name = f"H_{lower_hsv[0]}-{upper_hsv[0]}_S_{lower_hsv[1]}-{upper_hsv[1]}_V_{lower_hsv[2]}-{upper_hsv[2]}"

# 画像ファイルの拡張子リスト
image_extensions = ['.png', '.jpg', '.jpeg', '.bmp', '.tiff', '.gif']

# カレントディレクトリ内の画像ファイルを取得
current_dir = pathlib.Path(directory_path)
image_files = [file for file in current_dir.iterdir() if file.suffix.lower() in image_extensions]

if not image_files:
    print("[bold red]画像ファイルが見つかりませんでした。ディレクトリを確認してください。[/bold red]")
    exit()

print(f"見つかった画像ファイル数: [bold green]{len(image_files)}[/bold green]")

# 画像処理のループ
for image_file in track(image_files, description="画像を処理中..."):
    try:
        # 画像の読み込み
        image = cv2.imread(str(image_file))
        if image is None:
            print(f"[yellow]読み込みに失敗しました: {image_file.name}[/yellow]")
            continue

        # 画像をHSV色空間に変換
        hsv_image = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

        # フィルタリングの適用
        mask = cv2.inRange(hsv_image, lower_hsv, upper_hsv)

        # マスクを適用してフィルタリングされた部分を抽出
        filtered_image = cv2.bitwise_and(image, image, mask=mask)

        # 元のファイル名とフィルター設定を組み合わせて新しいファイル名を作成
        original_name = image_file.stem
        new_filename = f"{original_name}_{filter_name}.png"
        save_path = pathlib.Path(output_directory) / new_filename

        # 画像を保存
        cv2.imwrite(str(save_path), filtered_image)

        print(f"[green]保存しました:[/green] {save_path}")

    except Exception as e:
        print(f"[red]エラーが発生しました:{image_file.name}[/red]")
        print(e)

print("[bold blue]全ての画像の処理が完了しました。[/bold blue]")
