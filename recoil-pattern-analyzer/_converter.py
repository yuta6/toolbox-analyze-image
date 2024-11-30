"""
- スクリーン上のピクセル差分dx,dyをゲーム内部の視点移動のpitchとyawに変換する
- 算出したpitchとyawに対して、移動すべきマウスのdx,dyを算出する

A. スクリーン上のピクセル差分 dx, dy 
B. ゲーム内部の視点移動の dyaw, dpitch
C. 移動すべきマウスの dx, dy

1. AからBを計算するには？
    必要な値:ゲーム内の水平視野角、垂直視野角、スクリーンの解像度

    自身からスクリーンまでの距離をDとすると

    tan(103°/2) = (W / 2)/D
    tan(dYaw) = dx/D  


2. BからCを計算するには？
    必要な値：ゲーム内のマウス感度
    必要ないのはDPI


    実験結果：
    ローインプットを有効化必須
    マウス感度:0.36 水平方向360度回るのに必要なインプット:14286
    マウス感度:0.50 水平方向360度回るのに必要なインプット:10286
    マウス感度:1.00 水平方向360度回るのに必要なインプット:5143
"""

import math
import ctypes

class ScreenSize:
    user32 = ctypes.windll.user32
    user32.SetProcessDPIAware()  
    width = user32.GetSystemMetrics(0)
    height = user32.GetSystemMetrics(1)
    center = (width // 2, height // 2)

    @classmethod
    def center_region(cls, size):
        """
        指定された幅と高さで中心領域を計算し、タプルを返す
        size: 中心領域の (width, height) を示すタプル
        """
        center_x, center_y = cls.center
        region_x = center_x - size[0] // 2
        region_y = center_y - size[1] // 2
        return (region_x, region_y, region_x + size[0], region_y + size[1])


class Converter:
    # スクリーンサイズと視野角の初期化
    width = ScreenSize.width
    height = ScreenSize.height
    aspect = width / height
    fov_h_deg = 103  
    fov_h_rad = math.radians(fov_h_deg) 
    fov_v_rad = 2 * math.atan(math.tan(fov_h_rad / 2) / aspect)  
    fov_v_deg = math.degrees(fov_v_rad) 

    @classmethod
    def convert_from_pixel_to_pitch_yaw(cls, dx: int, dy: int):
        """
        スクリーン上のピクセル差分から視点角度差分（dyaw, dpitch）を計算する。
        結果は度単位で返される。
        """
        # 中心からの正規化ピクセル差分
        x_norm = dx / (cls.width / 2)
        y_norm = dy / (cls.height / 2)

        # dyaw と dpitch の計算（度単位）
        dyaw_rad = math.atan(x_norm * math.tan(cls.fov_h_rad / 2))
        dpitch_rad = math.atan(y_norm * math.tan(cls.fov_v_rad / 2))

        # ラジアンから度に変換
        d_yaw = math.degrees(dyaw_rad)
        d_pitch = math.degrees(dpitch_rad)

        return d_yaw, d_pitch