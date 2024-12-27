from enum import Enum
from typing import Optional

import numpy as np
import cv2
from windows_capture import Frame

class Weapon:
    def __init__(self, name: str, cost: int, category: str, ads_multiplier: float, fire_rate: float ,recoil_pattern: Optional[list[tuple]] = None ,model_image: Optional[np.ndarray] = None):
        self.name :str = name
        self.cost :int = cost
        self.category :WeaponCategory = category
        self.ads_multiplier : float = ads_multiplier
        self.fire_rate : float = fire_rate
        self.recoil_pattern : Optional[list[tuple]] = recoil_pattern 
        self.model_image = model_image or self.load_image()

    def load_image(self):
        print(f"Loading image for {self.name}")
        return cv2.imread(f"weapon-images/{self.name.lower()}.png", cv2.IMREAD_UNCHANGED)

class WeaponCategory(Enum):
    SIDEARM = "Sidearm"
    SMG = "SMG"
    RIFLE = "Rifle"
    SNIPER = "Sniper"
    SHOTGUN = "Shotgun"
    MACHINE_GUN = "Machine Gun"
    MELEE = "Melee"

class Weapons(Enum):
    CLASSIC = Weapon("Classic", 0, WeaponCategory.SIDEARM, 1.0, 6.75)
    SHORTY = Weapon("Shorty", 150, WeaponCategory.SIDEARM, 1.0,3.33)
    FRENZY = Weapon("Frenzy", 450, WeaponCategory.SIDEARM, 1.0,10)
    GHOST = Weapon("Ghost", 500, WeaponCategory.SIDEARM, 1.0,6.75)
    SHERIFF = Weapon("Sheriff", 800, WeaponCategory.SIDEARM,1.0,4.0)

    STINGER = Weapon("Stinger", 950, WeaponCategory.SMG,1.15,16.0)
    SPECTRE = Weapon("Spectre", 1600, WeaponCategory.SMG,1.15,13.33)

    BULLDOG = Weapon("Bulldog", 2050, WeaponCategory.RIFLE,1.25,10.0)
    GUARDIAN = Weapon("Guardian", 2250, WeaponCategory.RIFLE,1.5,5.25)
    PHANTOM = Weapon("Phantom", 2900, WeaponCategory.RIFLE,1.25,11.0)
    VANDAL = Weapon("Vandal", 2900, WeaponCategory.RIFLE,1.25,9.75)

    MARSHAL = Weapon("Marshal", 950, WeaponCategory.SNIPER,3.5,1.5)
    OUTLAW = Weapon("Outlaw", 2400, WeaponCategory.SNIPER,3.5,2.75)
    OPERATOR = Weapon("Operator", 4700, WeaponCategory.SNIPER,2.5,0.6)

    BUCKY = Weapon("Bucky", 850, WeaponCategory.SHOTGUN,1.0,1.1)
    JUDGE = Weapon("Judge", 1850, WeaponCategory.SHOTGUN,1.0,3.5)

    ARES = Weapon("Ares", 1600, WeaponCategory.MACHINE_GUN,1.15,13)
    ODIN = Weapon("Odin", 3200, WeaponCategory.MACHINE_GUN,1.15,12)

    KNIFE = Weapon("Knife", 0, WeaponCategory.MELEE,1.0,1.0)

    @classmethod
    def get_weapon_by_name(cls, name: str) -> Optional[Weapon]:
        """
        武器名に基づいてWeaponインスタンスを取得します。
        """
        # Enumの全メンバーをループして名前を比較
        for weapon_enum in cls:
            if weapon_enum.value.name.lower() == name.lower():
                return weapon_enum.value
        return None

    def __str__(self):
        return f"{self.value.name} ({self.value.category.value}) - Cost: {self.value.cost}"

        
class WeaponDetector:

    x1, y1 = 2160, 916
    x2 = 2460
    h=52
    h2=48
    y2 = y1 +h +h2
    y3 = y2 +h +h2

    regions = {
        "knife": (x1, y1, x2, y1 + h),
        "sidearm": (x1, y2, x2, y2 + h),
        "primary": (x1, y3, x2, y3 + h),
    }

    previous_weapon: Optional[Weapon] = None

    @classmethod
    def detect(cls, frame: np.ndarray) -> Optional[Weapon]:
        """
        画面のスクリーンショットから武器を検出するメソッド
        """
        max_similarity = 0
        detected_weapon = None

        for name, region in cls.regions.items():
            # 指定された領域をクロップ
            weapon_hud_image = frame[region[1]:region[3], region[0]:region[2]]
            processed_image = cls._process_image(weapon_hud_image)

            match name:
                case "knife":
                    similarity = cls.calculate_image_similarity(processed_image, Weapons.KNIFE.value.model_image)
                    if similarity > max_similarity:
                        max_similarity = similarity
                        detected_weapon = Weapons.KNIFE
                case "sidearm":
                    sidearms = [weapon for weapon in Weapons if weapon.value.category == WeaponCategory.SIDEARM]
                    for weapon in sidearms:
                        if weapon.value.model_image is not None:
                            similarity = cls.calculate_image_similarity(processed_image, weapon.value.model_image)
                            if similarity > max_similarity:
                                max_similarity = similarity
                                detected_weapon = weapon
                case "primary":
                    non_sidearm_non_knife_list = [
                        weapon for weapon in Weapons 
                        if weapon.value.category not in {WeaponCategory.SIDEARM, WeaponCategory.MELEE}
                    ]
                    for weapon in non_sidearm_non_knife_list:
                        if weapon.value.model_image is not None:
                            similarity = cls.calculate_image_similarity(processed_image, weapon.value.model_image)
                            if similarity > max_similarity:
                                max_similarity = similarity
                                detected_weapon = weapon
        
        detected_weapon = detected_weapon if max_similarity > 0.3 else None
        cls.previous_weapon = detected_weapon

        return detected_weapon
    
    @staticmethod
    def _process_image(image: np.ndarray) -> np.ndarray:
        """
        画像をHSV色空間に変換し、指定された範囲でフィルタリングを行います。
        """
        hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

        lower_bound = np.array([0, 0, 160])    
        upper_bound = np.array([179, 10, 220])

        mask = cv2.inRange(hsv, lower_bound, upper_bound)

        return mask

    def calculate_image_similarity(target_image: np.ndarray, template_image: np.ndarray) -> bool:
        """
        2つの画像の前景部分の一致率を基に比較し、指定した閾値以上であれば一致と判定する。
        前景は白（255）として扱う。
        """        
        # 前景の論理積と論理和を計算
        intersection = np.logical_and(target_image, template_image).sum()
        union = np.logical_or(target_image, template_image).sum()
        
        if union == 0:
            return True
        
        # Jaccard指数（IoU）を計算
        jaccard_index = intersection / union
        
        return jaccard_index
    
