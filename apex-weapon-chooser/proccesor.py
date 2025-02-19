# 画像が送られてきたら、２値画像化して膨張処理した後に縮小処理を行う
import ctypes

import cv2
from windows_capture import Frame

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

class Detector :
    def __init__(self, debug=False) :
        self.is_debug = debug
        self._mor_kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (50, 50))
        
    def is_exist_yellow_in_mid(self, frame: Frame) -> bool:
        # 画面中央の領域を取得
        large_region = ScreenSize.center_region((1024, 1024))
        small_region = ScreenSize.center_region((256, 256))

        # large_regionを切り出し、256x256にリサイズする
        cropped_large = frame.crop(
            start_width=large_region[0],
            start_height=large_region[1],
            end_width=large_region[2],
            end_height=large_region[3]
        ).convert_to_bgr().frame_buffer
        cropped_large = cv2.resize(cropped_large, (256, 256), interpolation=cv2.INTER_AREA)

        # small_regionをそのまま切り出す（small_regionは元々256x256の想定）
        cropped_small = frame.crop(
            start_width=small_region[0],
            start_height=small_region[1],
            end_width=small_region[2],
            end_height=small_region[3]
        ).convert_to_bgr().frame_buffer

        # HSV色空間に変換
        hsv_large = cv2.cvtColor(cropped_large, cv2.COLOR_BGR2HSV)
        hsv_small = cv2.cvtColor(cropped_small, cv2.COLOR_BGR2HSV)

        # 黄色の閾値設定（例：Hue: 28-32, Saturation: 160-255, Value: 160-255）
        lower = (50, 220, 220)
        upper = (70, 255, 255)
        """
        RED_MIN_HSV = (-4, 160, 160)
        RED_MAX_HSV = (4, 255, 255)

        PURPLE_MIN_HSV = (145, 128, 128)
        PURPLE_MAX_HSV = (155, 255, 255)

        YELLOW_MIN_HSV = (29, 160, 160) # 160?
        YELLOW_MAX_HSV = (31, 255, 255)
        """

        # マスク生成
        mask_hsv_large = cv2.inRange(hsv_large, lower, upper)
        mask_hsv_small = cv2.inRange(hsv_small, lower, upper)

        # モルフォロジー処理（クロージング）でノイズ除去
        mask_mor_large = cv2.morphologyEx(
            mask_hsv_large,
            cv2.MORPH_CLOSE,
            self._mor_kernel,
            borderType=cv2.BORDER_CONSTANT,
            borderValue=0
        )

        mask_mor_small = cv2.morphologyEx(
            mask_hsv_small,
            cv2.MORPH_CLOSE,
            self._mor_kernel,
            borderType=cv2.BORDER_CONSTANT,
            borderValue=0
        )

        erosion_kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
        mask_mor_large = cv2.erode(mask_mor_large, erosion_kernel, iterations=1)
        mask_mor_small = cv2.erode(mask_mor_small, erosion_kernel, iterations=1)

        # 両方のマスクを OR 演算で合成
        combined_mask = cv2.bitwise_or(mask_mor_large, mask_mor_small)

        center_x, center_y = 128, 128  # 256x256 の中心座標
        pixel_value = combined_mask[center_y, center_x]  # 画素値取得

        # ピクセル値が 0 以外（1ならTrue）
        is_yellow_present = pixel_value > 0

        if self.is_debug:
            self._display_for_debug(
                ("Large HSV Mask", mask_hsv_large),
                ("Large Morphed Mask", mask_mor_large),
                ("Small HSV Mask", mask_hsv_small),
                ("Small Morphed Mask", mask_mor_small),
                ("Combined Mask", combined_mask)
            )
                
        # combined_maskに1つでも黄色ピクセルがあればTrueを返す
        return is_yellow_present
    
    
    def _display_for_debug(self, *args):
        for name, image in args:
            cv2.imshow(name, image)
        
        if cv2.waitKey(1) & 0xFF == ord('q'):
            cv2.destroyAllWindows()
            exit()

