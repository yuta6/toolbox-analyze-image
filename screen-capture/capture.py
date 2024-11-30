from windows_capture import WindowsCapture, Frame, InternalCaptureControl
import os
import ctypes
from time import sleep

# Win32 APIの定数
VK_LMENU = 0xA4  # 左Altキーの仮想キーコード

capture = WindowsCapture(
    cursor_capture=None,
    draw_border=None,
    monitor_index=None,
    window_name=None,
)

# 前回の状態を保持する変数
last_key_state = False

def get_next_image_number(directory):
    existing_files = []
    for filename in os.listdir(directory):
        if filename.startswith('pic') and filename.endswith('.png'):
            try:
                num = int(filename[3:-4])
                existing_files.append(num)
            except ValueError:
                continue
    
    return 1 if not existing_files else max(existing_files) + 1

@capture.event
def on_frame_arrived(frame: Frame, capture_control: InternalCaptureControl):
    global last_key_state
    
    # 左Altキーの状態を取得
    key_state = bool(ctypes.windll.user32.GetAsyncKeyState(VK_LMENU) & 0x8000)
    
    # キーが押された瞬間を検出（前回False で 今回True）
    if not last_key_state and key_state:
        image_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'images')
        
        if not os.path.exists(image_dir):
            os.makedirs(image_dir)
        
        next_num = get_next_image_number(image_dir)
        filename = f"pic{next_num}.png"
        filepath = os.path.join(image_dir, filename)
        
        print(f"Saving screenshot: {filepath}")
        frame.save_as_image(filepath)
    
    # 状態を更新
    last_key_state = key_state

@capture.event
def on_closed():
    print("Capture Session Closed")

capture.start()