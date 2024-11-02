import tkinter as tk
from tkinter import ttk
import cv2
import numpy as np
import os
from natsort import natsorted


class HSVRange:
    """HSV色空間の範囲を表現するクラス"""
    def __init__(self, h_min=28, h_max=32, s_min=160, s_max=255, v_min=128, v_max=255):
        self.h_min = h_min
        self.h_max = h_max
        self.s_min = s_min
        self.s_max = s_max
        self.v_min = v_min
        self.v_max = v_max

    def to_numpy_array(self):
        """OpenCVで使用できるNumpy配列に変換する"""
        return np.array([self.h_min, self.s_min, self.v_min]), np.array([self.h_max, self.s_max, self.v_max])

class RGBRange:
    """RGB色空間の範囲を表現するクラス"""
    def __init__(self, r_min=0, r_max=255, g_min=0, g_max=255, b_min=0, b_max=255):
        self.r_min = r_min
        self.r_max = r_max
        self.g_min = g_min
        self.g_max = g_max
        self.b_min = b_min
        self.b_max = b_max

    def to_numpy_array(self):
        """OpenCVで使用できるNumpy配列に変換する"""
        return np.array([self.b_min, self.g_min, self.r_min]), np.array([self.b_max, self.g_max, self.r_max])

class ImageProcessor:
    """画像処理を担当するクラス"""
    def __init__(self, image_path):
        self.original_image = cv2.imread(image_path)
        if self.original_image is None:
            raise ValueError(f"画像を読み込めませんでした: {image_path}")

    def apply_hsv_filter(self, hsv_range: HSVRange):
        """HSV範囲に基づいて画像をフィルター処理する"""
        hsv_image = cv2.cvtColor(self.original_image, cv2.COLOR_BGR2HSV)
        if hsv_range.h_min <= hsv_range.h_max:
            # 一つの範囲
            lower_bound = np.array([hsv_range.h_min, hsv_range.s_min, hsv_range.v_min])
            upper_bound = np.array([hsv_range.h_max, hsv_range.s_max, hsv_range.v_max])
            mask = cv2.inRange(hsv_image, lower_bound, upper_bound)
        else:
            # 二つの範囲に分割
            lower_bound1 = np.array([0, hsv_range.s_min, hsv_range.v_min])
            upper_bound1 = np.array([hsv_range.h_max, hsv_range.s_max, hsv_range.v_max])
            lower_bound2 = np.array([hsv_range.h_min, hsv_range.s_min, hsv_range.v_min])
            upper_bound2 = np.array([179, hsv_range.s_max, hsv_range.v_max])
            mask1 = cv2.inRange(hsv_image, lower_bound1, upper_bound1)
            mask2 = cv2.inRange(hsv_image, lower_bound2, upper_bound2)
            mask = cv2.bitwise_or(mask1, mask2)



        filtered_image = cv2.bitwise_and(self.original_image, self.original_image, mask=mask)

        filtered_image = cv2.morphologyEx(            
            filtered_image, 
            cv2.MORPH_CLOSE, 
            cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (40, 40))
        )
        filtered_image = cv2.erode(            
            filtered_image, 
            cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (10, 10))
        )

        return filtered_image

    def apply_rgb_filter(self, rgb_range: RGBRange):
        """RGB範囲に基づいて画像をフィルター処理する"""
        lower_bound, upper_bound = rgb_range.to_numpy_array()
        mask = cv2.inRange(self.original_image, lower_bound, upper_bound)
        filtered_image = cv2.bitwise_and(self.original_image, self.original_image, mask=mask)
        return filtered_image

class ImageViewer:
    """画像を表示するクラス"""
    def __init__(self, master, image, title="Image"):
        self.master = master
        self.title = title

        self.canvas = tk.Label(master, text=title)
        self.canvas.grid(padx=10, pady=5)
        self.update_image(image)

    def update_image(self, image):
        """画像を更新する"""
        height = 640  # 画像の高さを640に固定
        aspect_ratio = image.shape[1] / image.shape[0]
        width = int(height * aspect_ratio)
        resized_image = cv2.resize(image, (width, height))
        rgb_image = cv2.cvtColor(resized_image, cv2.COLOR_BGR2RGB)
        # 画像をPhotoImageに変換
        img = cv2.imencode('.png', cv2.cvtColor(rgb_image, cv2.COLOR_RGB2BGR))[1].tobytes()
        try:
            photo_image = tk.PhotoImage(data=img)
            self.canvas.image = photo_image
            self.canvas.configure(image=photo_image)
        except tk.TclError:
            print("画像の表示に失敗しました。")

class DualSlider(tk.Canvas):
    def __init__(self, master, label, from_, to, initial_min, initial_max, command=None, circular=False, **kwargs):
        super().__init__(master, height=50, **kwargs)
        self.label = label
        self.from_ = from_
        self.to = to
        self.command = command
        self.min_val = initial_min
        self.max_val = initial_max
        self.circular = circular  # 円形スライダーかどうか

        # スライダーのパラメータ
        self.width = 300
        self.height = 50
        self.padding = 20
        self.handle_radius = 10

        self.configure(width=self.width, height=self.height)

        # 描画
        self.create_text(10, 10, anchor='w', text=self.label)
        self.track = self.create_line(self.padding, self.height/2, self.width - self.padding, self.height/2, width=4, fill='grey')

        # ハンドルの位置を計算
        self.min_pos = self.value_to_pos(self.min_val)
        self.max_pos = self.value_to_pos(self.max_val)

        # 範囲線の初期描画（後で更新）
        self.range_line = self.create_line(0, self.height/2, 0, self.height/2, width=4, fill='blue')

        # ハンドルを描画
        self.min_handle = self.create_oval(self.min_pos - self.handle_radius, self.height/2 - self.handle_radius,
                                          self.min_pos + self.handle_radius, self.height/2 + self.handle_radius,
                                          fill='green', outline='black', tags="min_handle")
        self.max_handle = self.create_oval(self.max_pos - self.handle_radius, self.height/2 - self.handle_radius,
                                          self.max_pos + self.handle_radius, self.height/2 + self.handle_radius,
                                          fill='red', outline='black', tags="max_handle")

        # 範囲線を描画
        self.update_range_line()

        # イベントバインド
        self.bind("<Button-1>", self.click)
        self.bind("<B1-Motion>", self.drag)

        self.current_handle = None

    def value_to_pos(self, value):
        """値を位置に変換"""
        ratio = (value - self.from_) / (self.to - self.from_)
        return self.padding + ratio * (self.width - 2 * self.padding)

    def pos_to_value(self, pos):
        """位置を値に変換"""
        ratio = (pos - self.padding) / (self.width - 2 * self.padding)
        ratio = min(max(ratio, 0), 1)
        return int(self.from_ + ratio * (self.to - self.from_))

    def click(self, event):
        """クリック時の処理"""
        x = event.x
        y = event.y
        if self.is_over_handle(x, y, self.min_handle):
            self.current_handle = 'min'
        elif self.is_over_handle(x, y, self.max_handle):
            self.current_handle = 'max'
        else:
            self.current_handle = None

    def drag(self, event):
        """ドラッグ時の処理"""
        if self.current_handle is None:
            return
        x = min(max(event.x, self.padding), self.width - self.padding)
        value = self.pos_to_value(x)
        if self.circular and self.label.lower() == "hue":
            # Hueスライダーが円形の場合
            self.handle_circular_drag(value)
        else:
            # 通常のスライダー
            self.handle_linear_drag(x, value)
        self.update_range_line()
        if self.command:
            self.command(self.min_val, self.max_val)

    def handle_linear_drag(self, x, value):
        """線形スライダーのドラッグ処理"""
        if self.current_handle == 'min':
            if value > self.max_val:
                value = self.max_val
            self.min_val = value
            self.coords(self.min_handle, x - self.handle_radius, self.height/2 - self.handle_radius,
                        x + self.handle_radius, self.height/2 + self.handle_radius)
        elif self.current_handle == 'max':
            if value < self.min_val:
                value = self.min_val
            self.max_val = value
            self.coords(self.max_handle, x - self.handle_radius, self.height/2 - self.handle_radius,
                        x + self.handle_radius, self.height/2 + self.handle_radius)

    def handle_circular_drag(self, value):
        """円形スライダーのドラッグ処理"""
        # Hueの範囲は0-179
        if self.current_handle == 'min':
            self.min_val = value % 180
            self.coords(self.min_handle, self.value_to_pos(self.min_val) - self.handle_radius, self.height/2 - self.handle_radius,
                        self.value_to_pos(self.min_val) + self.handle_radius, self.height/2 + self.handle_radius)
        elif self.current_handle == 'max':
            self.max_val = value % 180
            self.coords(self.max_handle, self.value_to_pos(self.max_val) - self.handle_radius, self.height/2 - self.handle_radius,
                        self.value_to_pos(self.max_val) + self.handle_radius, self.height/2 + self.handle_radius)

    def is_over_handle(self, x, y, handle):
        """ハンドルの上にカーソルがあるか確認"""
        coords = self.coords(handle)
        x0, y0, x1, y1 = coords
        return x0 <= x <= x1 and y0 <= y <= y1

    def update_range_line(self):
        """範囲線を更新"""
        if self.circular and self.label.lower() == "hue":
            # 円形スライダーの場合、範囲が一つか二つに分かれる
            if self.min_val <= self.max_val:
                # 一つの範囲
                self.coords(self.range_line, self.value_to_pos(self.min_val), self.height/2,
                            self.value_to_pos(self.max_val), self.height/2)
                self.itemconfig(self.range_line, fill='blue')
            else:
                # 二つの範囲に分割
                # 最初の範囲 [min, to]
                self.coords(self.range_line, self.value_to_pos(self.min_val), self.height/2,
                            self.width - self.padding, self.height/2)
                self.itemconfig(self.range_line, fill='blue')
                # 二つ目の範囲 [from, max]
                # 既存の追加ラインを削除
                existing_lines = [item for item in self.find_all() if self.type(item) == 'line' and item != self.track and item != self.range_line]
                for line in existing_lines:
                    self.delete(line)
                self.create_line(self.padding, self.height/2, self.value_to_pos(self.max_val), self.height/2, width=4, fill='blue')
        else:
            # 通常のスライダー
            self.coords(self.range_line, self.value_to_pos(self.min_val), self.height/2,
                        self.value_to_pos(self.max_val), self.height/2)

    def get_values(self):
        """現在のminとmaxの値を取得"""
        return self.min_val, self.max_val

class HSVControlPanel:
    """HSVスライダーのコントロールパネルを表現するクラス"""
    def __init__(self, master, hsv_range: HSVRange, on_change_callback):
        self.master = master
        self.hsv_range = hsv_range
        self.on_change_callback = on_change_callback

        self.frame = ttk.LabelFrame(self.master, text="HSV Controls")
        # self.frame.pack(fill="both", expand=True, padx=10, pady=10)  # 削除
        # 内部レイアウトをgridで管理
        self.frame.columnconfigure(0, weight=1)

        # Hueスライダーと値表示
        hue_frame = ttk.Frame(self.frame)
        hue_frame.grid(row=0, column=0, sticky="ew", padx=5, pady=5)
        hue_frame.columnconfigure(0, weight=1)
        self.hue_slider = DualSlider(hue_frame, "Hue", 0, 179, self.hsv_range.h_min, self.hsv_range.h_max, 
                                     self.on_hue_change, circular=True)
        self.hue_slider.grid(row=0, column=0, sticky="ew")
        self.hue_min_label = ttk.Label(hue_frame, text=f"Min: {self.hsv_range.h_min}")
        self.hue_min_label.grid(row=0, column=1, padx=5)
        self.hue_max_label = ttk.Label(hue_frame, text=f"Max: {self.hsv_range.h_max}")
        self.hue_max_label.grid(row=0, column=2, padx=5)

        # Saturationスライダーと値表示
        sat_frame = ttk.Frame(self.frame)
        sat_frame.grid(row=1, column=0, sticky="ew", padx=5, pady=5)
        sat_frame.columnconfigure(0, weight=1)
        self.sat_slider = DualSlider(sat_frame, "Saturation", 0, 255, self.hsv_range.s_min, self.hsv_range.s_max, 
                                     self.on_sat_change)
        self.sat_slider.grid(row=0, column=0, sticky="ew")
        self.sat_min_label = ttk.Label(sat_frame, text=f"Min: {self.hsv_range.s_min}")
        self.sat_min_label.grid(row=0, column=1, padx=5)
        self.sat_max_label = ttk.Label(sat_frame, text=f"Max: {self.hsv_range.s_max}")
        self.sat_max_label.grid(row=0, column=2, padx=5)

        # Valueスライダーと値表示
        val_frame = ttk.Frame(self.frame)
        val_frame.grid(row=2, column=0, sticky="ew", padx=5, pady=5)
        val_frame.columnconfigure(0, weight=1)
        self.val_slider = DualSlider(val_frame, "Value", 0, 255, self.hsv_range.v_min, self.hsv_range.v_max, 
                                     self.on_val_change)
        self.val_slider.grid(row=0, column=0, sticky="ew")
        self.val_min_label = ttk.Label(val_frame, text=f"Min: {self.hsv_range.v_min}")
        self.val_min_label.grid(row=0, column=1, padx=5)
        self.val_max_label = ttk.Label(val_frame, text=f"Max: {self.hsv_range.v_max}")
        self.val_max_label.grid(row=0, column=2, padx=5)

    def on_hue_change(self, min_val, max_val):
        self.hsv_range.h_min = min_val
        self.hsv_range.h_max = max_val
        self.hue_min_label.config(text=f"Min: {self.hsv_range.h_min}")
        self.hue_max_label.config(text=f"Max: {self.hsv_range.h_max}")
        self.on_change_callback()

    def on_sat_change(self, min_val, max_val):
        self.hsv_range.s_min = min_val
        self.hsv_range.s_max = max_val
        self.sat_min_label.config(text=f"Min: {self.hsv_range.s_min}")
        self.sat_max_label.config(text=f"Max: {self.hsv_range.s_max}")
        self.on_change_callback()

    def on_val_change(self, min_val, max_val):
        self.hsv_range.v_min = min_val
        self.hsv_range.v_max = max_val
        self.val_min_label.config(text=f"Min: {self.hsv_range.v_min}")
        self.val_max_label.config(text=f"Max: {self.hsv_range.v_max}")
        self.on_change_callback()

class RGBControlPanel:
    """RGBスライダーのコントロールパネルを表現するクラス"""
    def __init__(self, master, rgb_range: RGBRange, on_change_callback):
        self.master = master
        self.rgb_range = rgb_range
        self.on_change_callback = on_change_callback

        self.frame = ttk.LabelFrame(self.master, text="RGB Controls")
        # self.frame.pack(fill="both", expand=True, padx=10, pady=10)  # 削除
        # 内部レイアウトをgridで管理
        self.frame.columnconfigure(0, weight=1)

        # Redスライダーと値表示
        r_frame = ttk.Frame(self.frame)
        r_frame.grid(row=0, column=0, sticky="ew", padx=5, pady=5)
        r_frame.columnconfigure(0, weight=1)
        self.r_slider = DualSlider(r_frame, "Red", 0, 255, self.rgb_range.r_min, self.rgb_range.r_max, 
                                   self.on_r_change)
        self.r_slider.grid(row=0, column=0, sticky="ew")
        self.r_min_label = ttk.Label(r_frame, text=f"Min: {self.rgb_range.r_min}")
        self.r_min_label.grid(row=0, column=1, padx=5)
        self.r_max_label = ttk.Label(r_frame, text=f"Max: {self.rgb_range.r_max}")
        self.r_max_label.grid(row=0, column=2, padx=5)

        # Greenスライダーと値表示
        g_frame = ttk.Frame(self.frame)
        g_frame.grid(row=1, column=0, sticky="ew", padx=5, pady=5)
        g_frame.columnconfigure(0, weight=1)
        self.g_slider = DualSlider(g_frame, "Green", 0, 255, self.rgb_range.g_min, self.rgb_range.g_max, 
                                   self.on_g_change)
        self.g_slider.grid(row=0, column=0, sticky="ew")
        self.g_min_label = ttk.Label(g_frame, text=f"Min: {self.rgb_range.g_min}")
        self.g_min_label.grid(row=0, column=1, padx=5)
        self.g_max_label = ttk.Label(g_frame, text=f"Max: {self.rgb_range.g_max}")
        self.g_max_label.grid(row=0, column=2, padx=5)

        # Blueスライダーと値表示
        b_frame = ttk.Frame(self.frame)
        b_frame.grid(row=2, column=0, sticky="ew", padx=5, pady=5)
        b_frame.columnconfigure(0, weight=1)
        self.b_slider = DualSlider(b_frame, "Blue", 0, 255, self.rgb_range.b_min, self.rgb_range.b_max, 
                                   self.on_b_change)
        self.b_slider.grid(row=0, column=0, sticky="ew")
        self.b_min_label = ttk.Label(b_frame, text=f"Min: {self.rgb_range.b_min}")
        self.b_min_label.grid(row=0, column=1, padx=5)
        self.b_max_label = ttk.Label(b_frame, text=f"Max: {self.rgb_range.b_max}")
        self.b_max_label.grid(row=0, column=2, padx=5)

    def on_r_change(self, min_val, max_val):
        self.rgb_range.r_min = min_val
        self.rgb_range.r_max = max_val
        self.r_min_label.config(text=f"Min: {self.rgb_range.r_min}")
        self.r_max_label.config(text=f"Max: {self.rgb_range.r_max}")
        self.on_change_callback()

    def on_g_change(self, min_val, max_val):
        self.rgb_range.g_min = min_val
        self.rgb_range.g_max = max_val
        self.g_min_label.config(text=f"Min: {self.rgb_range.g_min}")
        self.g_max_label.config(text=f"Max: {self.rgb_range.g_max}")
        self.on_change_callback()

    def on_b_change(self, min_val, max_val):
        self.rgb_range.b_min = min_val
        self.rgb_range.b_max = max_val
        self.b_min_label.config(text=f"Min: {self.rgb_range.b_min}")
        self.b_max_label.config(text=f"Max: {self.rgb_range.b_max}")
        self.on_change_callback()


class PhotoFinder:
    """カレントディレクトリから画像ファイルを検索するクラス"""
    IMAGE_EXTENSIONS = ('.png', '.jpg', '.jpeg', '.bmp', '.gif', '.tiff')

    def __init__(self, directory='../images'):
        self.directory = directory

    def find_images(self):
        """画像ファイルのリストを返す"""
        return natsorted([f for f in os.listdir(self.directory)
                if f.lower().endswith(self.IMAGE_EXTENSIONS) and os.path.isfile(os.path.join(self.directory, f))]
            )

class FinderPanel:
    """画像ファイル名の一覧を表示するパネル"""
    def __init__(self, parent, photo_finder, on_select_callback):
        self.frame = ttk.Frame(parent, width=200)
        self.frame.pack_propagate(False)  # 固定幅にする
        self.label = ttk.Label(self.frame, text="Image Files")
        self.label.pack(padx=5, pady=5)
        
        self.listbox = tk.Listbox(self.frame)
        self.listbox.pack(fill='both', expand=True, padx=5, pady=5)
        
        self.scrollbar = ttk.Scrollbar(self.listbox, orient='vertical', command=self.listbox.yview)
        self.listbox.config(yscrollcommand=self.scrollbar.set)
        self.scrollbar.pack(side='right', fill='y')
        
        self.photo_finder = photo_finder
        self.on_select_callback = on_select_callback
        self.populate_list()

        self.listbox.bind('<<ListboxSelect>>', self.on_select)

    def populate_list(self):
        """リストボックスに画像ファイル名を追加"""
        images = self.photo_finder.find_images()
        for img in images:
            self.listbox.insert(tk.END, img)

    def on_select(self, event):
        """リストボックスで選択が変更されたときの処理"""
        selection = event.widget.curselection()
        if selection:
            index = selection[0]
            filename = event.widget.get(index)
            self.on_select_callback(filename)

class ColorReacherApp:
    """メインアプリケーションクラス"""
    def __init__(self, root):
        self.root = root
        self.root.title("Color Reacher App")

        # PhotoFinderとFinderPanelの初期化
        self.photo_finder = PhotoFinder()
        self.finder_panel = FinderPanel(self.root, self.photo_finder, self.on_image_selected)
        self.finder_panel.frame.grid(row=0, column=0, rowspan=2, padx=10, pady=10, sticky="ns")

        # 既存のUIのレイアウトを調整
        self.main_frame = ttk.Frame(self.root)
        self.main_frame.grid(row=0, column=1, rowspan=2, sticky="nsew")
        self.root.columnconfigure(1, weight=1)
        self.root.rowconfigure(0, weight=1)
        self.root.rowconfigure(1, weight=1)

        # 初期画像表示用のプレースホルダー
        self.image_processor = None
        self.hsv_range = HSVRange()
        self.rgb_range = RGBRange()

        # GUIのレイアウトを4分割
        self.main_frame.columnconfigure(0, weight=1)
        self.main_frame.columnconfigure(1, weight=1)
        self.main_frame.rowconfigure(0, weight=1)
        self.main_frame.rowconfigure(1, weight=1)

        # 左上にRGBフィルタ画像
        self.rgb_filtered_image_viewer = ImageViewer(self.main_frame, np.zeros((300, 300, 3), dtype=np.uint8), "RGB Filtered Image")
        self.rgb_filtered_image_viewer.canvas.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")

        # 右上にHSVフィルタ画像
        self.hsv_filtered_image_viewer = ImageViewer(self.main_frame, np.zeros((300, 300, 3), dtype=np.uint8), "HSV Filtered Image")
        self.hsv_filtered_image_viewer.canvas.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")

        # 左下にRGBControlPanel
        self.rgb_control_panel = RGBControlPanel(self.main_frame, self.rgb_range, self.update_filtered_images)
        self.rgb_control_panel.frame.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")

        # 右下にHSVControlPanel
        self.hsv_control_panel = HSVControlPanel(self.main_frame, self.hsv_range, self.update_filtered_images)
        self.hsv_control_panel.frame.grid(row=1, column=1, padx=10, pady=10, sticky="nsew")

    def on_image_selected(self, filename):
        """FinderPanelで画像が選択されたときの処理"""
        image_path = os.path.join(self.photo_finder.directory, filename)
        try:
            self.image_processor = ImageProcessor(image_path)
            self.update_filtered_images()
        except Exception as e:
            print(f"画像の読み込みに失敗しました: {e}")

    def update_filtered_images(self):
        """フィルター処理された画像を更新する"""
        if not self.image_processor:
            return
        try:
            # RGBフィルタリング
            rgb_filtered_image = self.image_processor.apply_rgb_filter(self.rgb_range)
            self.rgb_filtered_image_viewer.update_image(rgb_filtered_image)

            # HSVフィルタリング
            hsv_filtered_image = self.image_processor.apply_hsv_filter(self.hsv_range)
            self.hsv_filtered_image_viewer.update_image(hsv_filtered_image)
        except Exception as e:
            print(f"画像のフィルター処理中にエラーが発生しました: {e}")

if __name__ == "__main__":
    root = tk.Tk()
    app = ColorReacherApp(root)
    root.mainloop()