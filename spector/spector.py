import os

import cv2
import numpy as np
from rich import print

# 画像が保存されているディレクトリ
directory_path = "./"  # 画像ファイルのディレクトリを指定してください

# 読み込みファイルのリストを取得
file_list = [f for f in os.listdir(directory_path) if f.endswith(('.png', '.jpg', '.jpeg'))]

# 2480,20から2490,36の四角形の座標
x_start, y_start = 2480, 20
x_end, y_end = 2492, 40

# 結果の格納
results = []

for file_name in file_list:
    # 画像のフルパス
    file_path = os.path.join(directory_path, file_name)
    print(f"Processing: {file_path}")
    
    # 画像を読み込む
    image = cv2.imread(file_path)
    if image is None:
        continue  # 画像が正しく読み込めない場合スキップ
    
    height, width, _ = image.shape
    print(f"Image dimensions: {width}x{height}")

    cropped_image = image[y_start:y_end, x_start:x_end]
    print("cropped_image")
    print(cropped_image)
    
    # BGRからHSVに変換
    cvt_image = cv2.cvtColor(cropped_image, cv2.COLOR_BGR2HSV)
    print("cvt_image")
    print(cvt_image)
    
    # HSV条件に基づいてマスクを作成
    mask = cv2.inRange(cvt_image, 
        np.array([0, 0, 191]), 
        np.array([255, 31, 255])
    )
    
    # 条件に一致するピクセル数をカウント
    pixel_count = cv2.countNonZero(mask)
    print(f"Pixel Count: {pixel_count}")
    
    # 結果を保存
    results.append({'file_name': file_name, 'pixel_count': pixel_count})
    
    # トリミングした画像をデバッグ用に表示
    cv2.imshow(f"Cropped: {file_name}", cropped_image)
    cv2.imshow(f"Filtered: {file_name}, Pixel Count: {pixel_count}", mask)
    cv2.waitKey(0)  # キー入力待機
    cv2.destroyAllWindows()

