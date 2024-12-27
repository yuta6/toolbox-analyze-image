from pathlib import Path
from collections import defaultdict

import cv2
import numpy as np

from _weapon import WeaponDetector, Weapon
from _converter import Converter


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
    lower_bound = np.array([6, 30, 40])
    upper_bound = np.array([60, 255, 80])

    # カラーフィルターを適用
    mask = cv2.inRange(hsv, lower_bound, upper_bound)

    # 画像の中心を取得
    height, width = img.shape[:2]
    center_y, center_x = height // 2, width // 2

    # マスクを作成（すべて0で初期化）
    region_mask = np.zeros_like(mask)

    # 指定された領域を1に設定
    region_mask[
        center_y - 240:center_y + 15,  # y方向の範囲
        center_x - 60:center_x + 50    # x方向の範囲
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

    # center_yが大きい順にソート
    objects_info_sorted = sorted(objects_info, key=lambda x: x[2], reverse=True)

    # ソート後の順番で番号を描画
    for index, (label, center_x, center_y) in enumerate(objects_info_sorted):
        # ラベル番号を描画
        cv2.putText(debug_image, str(index + 1), (center_x + 20, center_y), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 128, 255), 1)

    return debug_image, objects_info_sorted

def calc_recoil_pattern(weapon_name: str, object_list: list[tuple]):
    """
    リコイルパターンを計算する関数
    
    Parameters:
    weapon_name (str): 武器の名前
    object_list (list[tuple]): オブジェクト情報のリスト [(label, x, y), ...]
    
    Returns:
    tuple: (pixel_diffs, angle_diffs)
        - pixel_diffs: ピクセル差分ベクトルのリスト [(dx, dy), ...]
        - angle_diffs: 角度差分ベクトルのリスト [(d_yaw, d_pitch), ...]
    """
    if len(object_list) < 2:
        return [], []

    # ピクセル差分ベクトルを計算
    pixel_diffs = []
    for i in range(len(object_list) - 1):
        _, x1, y1 = object_list[i]
        _, x2, y2 = object_list[i + 1]
        dx = x2 - x1
        dy = y2 - y1
        pixel_diffs.append((dx, dy))

    # 角度差分ベクトルを計算
    angle_diffs = []
    for dx, dy in pixel_diffs:
        d_yaw, d_pitch = Converter.convert_from_pixel_to_pitch_yaw(dx, dy)
        angle_diffs.append((d_yaw, d_pitch))

    return pixel_diffs, angle_diffs

def save_text_of_recoil_pattern(weapon_name: str, pixel_diffs: list[tuple], angle_diffs: list[tuple]):
    """
    リコイルパターンのデータをテキストファイルとして保存する関数
    
    Parameters:
    weapon_name (str): 武器の名前
    pixel_diffs (list[tuple]): ピクセル差分ベクトルのリスト
    angle_diffs (list[tuple]): 角度差分ベクトルのリスト
    """
    # 武器のディレクトリパスを作成
    weapon_dir = Path(weapon_name)
    
    # ピクセル差分データを保存
    pixel_file = weapon_dir / 'pixel_diffs.txt'
    with open(pixel_file, 'w') as f:
        f.write("Index\tdx\tdy\n")
        for i, (dx, dy) in enumerate(pixel_diffs, 1):
            f.write(f"{i}\t{dx}\t{dy}\n")

    # 角度差分データを保存
    angle_file = weapon_dir / 'angle_diffs.txt'
    with open(angle_file, 'w') as f:
        f.write("Index\td_yaw\td_pitch\n")
        for i, (d_yaw, d_pitch) in enumerate(angle_diffs, 1):
            f.write(f"{i}\t{d_yaw}\t{d_pitch}\n")

    pitch_list_file = weapon_dir / 'pitch_list.txt'
    with open(pitch_list_file, 'w') as f:
        pitch_list = [d_pitch for _, d_pitch in angle_diffs]
        f.write(str(pitch_list))

def process_images():

    # 直下のresourceディレクトリーからpathlibライブラリーで画像たち(.png, .jpg, .jpeg)を読み込み
    images = []
    for pattern in ['*.png', '*.jpg', '*.jpeg']:
        images.extend(Path('resource').glob(pattern))

    # 武器タイプごとに画像をグループ化
    weapon_groups = defaultdict(list)
    
    # 最初に画像を武器タイプごとに分類
    for image_path in images:
        image = cv2.imread(str(image_path))
        if image is None:
            print(f"Failed to load image: {image_path}")
            continue
            
        weapon:Weapon = WeaponDetector.detect(image)
        weapon_groups[weapon.value.name].append((image_path, image))

    for weapon_name, image_list in weapon_groups.items():
        # 武器の種類に応じたディレクトリを作成
        weapon_dir = Path(weapon_name)
        weapon_dir.mkdir(exist_ok=True)

        # 各武器タイプ内で画像を処理
        for idx, (image_path, image) in enumerate(image_list, 1):
            # フィルター適用とオブジェクト検出
            final_mask = apply_filter(image)
            debug_image, objects_info = find_object_centers(final_mask)
            
            # オブジェクト情報を表示
            for label, x, y in objects_info:
                print(f"Object {label} center: ({x}, {y})")

            pixel_diffs, angle_diffs = calc_recoil_pattern(weapon_name, objects_info)
            save_text_of_recoil_pattern(weapon_name, pixel_diffs, angle_diffs)

            mask_path = weapon_dir / f"{idx}_mask.png"
            debug_path = weapon_dir / f"{idx}_debug.png"
            
            cv2.imwrite(str(mask_path), final_mask)
            cv2.imwrite(str(debug_path), debug_image)
            
            print(f"Processed {image_path.name} -> {weapon_name}/{idx}")


if __name__ == "__main__":
    process_images()