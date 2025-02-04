import cv2
import numpy as np
from pathlib import Path
import logging
from weapon import Weapons, WeaponCategory

# HUD領域の設定
x1, y1 = 2160, 916
x2 = 2460
h=52
h2=48
y2 = y1 +h +h2
y3 = y2 +h +h2

# 領域の定義
regions = {
    "knife": (y1, y1+h),
    "sidearm": (y2, y2+h),
    "primary": (y3, y3+h),
}

def resize(image: np.ndarray, region_name: str) -> np.ndarray:
    """指定された領域で画像をリサイズ"""
    y_start, y_end = regions[region_name]
    weapon_image = image[y_start:y_end, x1:x2]
    return weapon_image


def process_image(image: np.ndarray) -> np.ndarray:
    # Step 1: BGRからHSVに変換
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    
    # Step 2: HSVでフィルタリング（Sが10以下、Vが200以上）
    lower_bound = np.array([0, 0, 160])  # Hの範囲は問わない、S <= 10、V >= 200
    upper_bound = np.array([179, 10, 220])  # Hは全範囲、S <= 10、Vの最大値
    
    # Step 3: マスク生成
    mask = cv2.inRange(hsv, lower_bound, upper_bound)
    
    # Step 4: ノイズ除去と穴埋め処理
    #kernel = np.ones((2, 2), np.uint8)  # 小さなカーネルを定義
    
    # 小さなノイズを取り除くためのオープニング処理
    #mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
    
    # 小さな穴を埋めるためのクロージング処理
    #mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
    
    return mask

def main():
    # ログ設定
    logging.basicConfig(level=logging.INFO)
    
    # 武器画像の取得
    weapon_image_paths = Path("weapon-images-raw").glob("*.png")
    output_dir_trimming = Path("weapon-images-trimming")
    output_dir_trimming.mkdir(exist_ok=True)
    output_dir_processed = Path("weapon-images-processed")
    output_dir_processed.mkdir(exist_ok=True)

    for path in weapon_image_paths:
        image = cv2.imread(str(path))
        if image is None:
            logging.warning(f"Failed to load image: {path}")
            continue
            
        weapon_name = path.stem
        weapon = Weapons.get_weapon_by_name(weapon_name)
        logging.info(f"Processing weapon: {weapon}")
        
        if weapon is None:
            logging.warning(f"Weapon not found: {weapon_name}")
            continue

        # カテゴリーによって領域を選択
        match weapon.category:
            case WeaponCategory.MELEE:
                image = resize(image, "knife")
            case WeaponCategory.SIDEARM:
                image = resize(image, "sidearm")
            case _:
                image = resize(image, "primary")

        # リサイズ後の画像を保存
        output_resized_path = output_dir_trimming / f"{weapon_name}.png"
        cv2.imwrite(str(output_resized_path), image)
        logging.info(f"Saved processed image to {output_resized_path}")

        # プロセス後の画像を保存
        output_processed_path = output_dir_processed / f"{weapon_name}.png"
        processed_image = process_image(image)
        print(processed_image.shape)
        cv2.imwrite(str(output_processed_path), processed_image)
        logging.info(f"Saved processed image to {output_processed_path}")


if __name__ == "__main__":
    main()
