import cv2
import numpy as np
import os

# directoryの内の画像を対象にする
directories = ["bulldog", "phantom", "vandal"]

def apply_filter(img):
    """
    画像にHSVフィルターと領域マスクを適用する関数
    
    Parameters:
    img (numpy.ndarray): 入力画像
    
    Returns:
    numpy.ndarray: フィルター適用後のマスク
    """
    # HSV色空間に変換
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

    # HSVのカラーフィルター範囲を設定
    lower_bound = np.array([10, 60, 50])
    upper_bound = np.array([20, 255, 100])

    # カラーフィルターを適用
    mask = cv2.inRange(hsv, lower_bound, upper_bound)

    # 画像の中心を取得
    height, width = img.shape[:2]
    center_y, center_x = height // 2, width // 2

    # マスクを作成（すべて0で初期化）
    region_mask = np.zeros_like(mask)

    # 指定された領域を1に設定
    region_mask[
        center_y - 200:center_y + 10,  # y方向の範囲
        center_x - 60:center_x + 60    # x方向の範囲
    ] = 1

    # カラーフィルターとリージョンマスクを組み合わせる
    final_mask = cv2.bitwise_and(mask, mask, mask=region_mask)
    
    return final_mask

def find_object_centers(mask, min_size=0):
    """
    マスク画像から物体の中心座標を検出する関数
    
    Parameters:
    mask (numpy.ndarray): 二値マスク画像
    min_size (int): 物体とみなす最小ピクセル数
    
    Returns:
    tuple: (デバッグ用画像, 物体情報リスト)
        - デバッグ用画像: 中心点を可視化した画像
        - 物体情報リスト: (ラベル, x座標, y座標) のリスト
    """
    # 連結成分のラベリングを実行
    num_labels, labels = cv2.connectedComponents(mask, connectivity=8)
    
    # デバッグ用の画像（カラー）を作成
    debug_image = cv2.cvtColor(mask, cv2.COLOR_GRAY2BGR)
    
    # 物体情報を格納するリスト
    objects_info = []
    
    # 各物体の重心を計算
    for label in range(1, num_labels):  # 0はバックグラウンド
        y_coords, x_coords = np.where(labels == label)
        
        if len(y_coords) > min_size:
            # 重心を計算
            center_x = int(np.mean(x_coords))
            center_y = int(np.mean(y_coords))
            
            # 赤い点を描画
            cv2.circle(debug_image, (center_x, center_y), 2, (0, 0, 255), -1)
            
            # 物体情報を追加
            objects_info.append((label, center_x, center_y))
    
    return debug_image, objects_info

def process_images():
    for dir_name in directories:
        input_directory = os.path.join(os.getcwd(), dir_name)
        if not os.path.exists(input_directory):
            print(f"Directory {dir_name} not found")
            continue

        output_directory = os.path.join(os.getcwd(), f"{dir_name}_processed")
        if not os.path.exists(output_directory):
            os.makedirs(output_directory)
            
        for filename in os.listdir(input_directory):
            if filename.endswith(('.png', '.jpg', '.jpeg')):
                image_path = os.path.join(input_directory, filename)
                
                img = cv2.imread(image_path)
                if img is None:
                    continue

                # フィルターを適用
                final_mask = apply_filter(img)

                # 物体検出を実行
                debug_image, objects_info = find_object_centers(final_mask)

                # 検出結果を表示
                for label, x, y in objects_info:
                    print(f"Object {label} center: ({x}, {y})")

                # 画像を保存
                output_path = os.path.join(output_directory, filename)
                debug_output_path = os.path.join(output_directory, f"debug_{filename}")
                
                cv2.imwrite(output_path, final_mask)
                cv2.imwrite(debug_output_path, debug_image)


# 関数を実行
process_images()