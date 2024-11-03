
from enum import Enum
from typing import Optional

# 武器の基本クラス
class Weapon:
    def __init__(self, name: str, cost: int, category: str):
        self.name = name
        self.cost = None
        self.category = category

# 武器カテゴリーの定義
class WeaponCategory(Enum):
    SIDEARM = "Sidearm"
    SMG = "SMG"
    RIFLE = "Rifle"
    SNIPER = "Sniper"
    SHOTGUN = "Shotgun"
    MACHINE_GUN = "Machine Gun"
    MELEE = "Melee"

# 具体的な武器の定義
class Weapons:
    class Sidearms(Enum):
        CLASSIC = Weapon("Classic", 0, WeaponCategory.SIDEARM)
        SHORTY = Weapon("Shorty", 150, WeaponCategory.SIDEARM)
        FRENZY = Weapon("Frenzy", 450, WeaponCategory.SIDEARM)
        GHOST = Weapon("Ghost", 500, WeaponCategory.SIDEARM)
        SHERIFF = Weapon("Sheriff", 800, WeaponCategory.SIDEARM)

    class SMGs(Enum):
        STINGER = Weapon("Stinger", 950, WeaponCategory.SMG)
        SPECTRE = Weapon("Spectre", 1600, WeaponCategory.SMG)

    class Rifles(Enum):
        BULLDOG = Weapon("Bulldog", 2050, WeaponCategory.RIFLE)
        GUARDIAN = Weapon("Guardian", 2250, WeaponCategory.RIFLE)
        PHANTOM = Weapon("Phantom", 2900, WeaponCategory.RIFLE)
        VANDAL = Weapon("Vandal", 2900, WeaponCategory.RIFLE)

    class Snipers(Enum):
        MARSHAL = Weapon("Marshal", 950, WeaponCategory.SNIPER)
        OUTLAW = Weapon("Outlaw", 2400, WeaponCategory.SNIPER)
        OPERATOR = Weapon("Operator", 4700, WeaponCategory.SNIPER)

    class Shotguns(Enum):
        BUCKY = Weapon("Bucky", 850, WeaponCategory.SHOTGUN)
        JUDGE = Weapon("Judge", 1850, WeaponCategory.SHOTGUN)

    class MachineGuns(Enum):
        ARES = Weapon("Ares", 1600, WeaponCategory.MACHINE_GUN)
        ODIN = Weapon("Odin", 3200, WeaponCategory.MACHINE_GUN)

    class Melee(Enum):
        KNIFE = Weapon("Knife", 0, WeaponCategory.MELEE)

    @staticmethod
    def get_weapon_by_name(name: str)-> Optional[Weapon]:
        # 各カテゴリ内で名前が一致する武器を検索
        for category in [Weapons.Sidearms, Weapons.SMGs, Weapons.Rifles, Weapons.Snipers, Weapons.Shotguns, Weapons.MachineGuns, Weapons.Melee]:
            for weapon in category:
                if weapon.value.name.lower() == name.lower():
                    return weapon.value
        return None