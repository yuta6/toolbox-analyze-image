import time
from contextlib import contextmanager

from windows_capture import WindowsCapture, InternalCaptureControl, Frame
from windows_capture import Frame

from weapon import triggercheacker
from proccesor import Detector
import directkey as dkey

@contextmanager
def fps_limiter(target_fps=60, debug=False):
    frame_start = time.perf_counter()
    yield frame_start
    
    # フレーム処理後、必要な待機時間を計算
    elapsed = time.perf_counter() - frame_start
    target_frame_time = 1.0 / target_fps
    sleep_time = max(0, target_frame_time - elapsed)
    
    if sleep_time > 0:
        time.sleep(sleep_time)
    
    actual_fps = 1.0 / (time.perf_counter() - frame_start)
    
    if debug:
        print(f"FPS: {int(actual_fps)}")


def main() :

    camera = WindowsCapture(
        cursor_capture=False,
        draw_border=None,
        monitor_index=None,
        window_name=None,
    )

    detector = Detector(debug=True)

    def on_frame_arrived(frame: Frame, capture_control: InternalCaptureControl) :
        with fps_limiter(target_fps=500, debug=True) :
            if  (detector.is_exist_yellow_in_mid(frame)
            and triggercheacker(frame.convert_to_bgr().frame_buffer)):
                print("trigger")
                dkey.PressKey(0x01)
                time.sleep(0.02)
                dkey.ReleaseKey(0x01)
                time.sleep(0.1)

    def on_closed() :
        print("Exiting...")
        print("unmask all")

    camera.event(on_frame_arrived)
    camera.event(on_closed)    

    try:
        camera.start()
    except Exception as e:
        print(e)
    finally:
        on_closed()

if __name__ == "__main__" :
    main()
