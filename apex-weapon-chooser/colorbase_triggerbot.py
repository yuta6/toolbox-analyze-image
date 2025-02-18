from windows_capture import WindowsCapture, InternalCaptureControl, Frame
from windows_capture import Frame
import cv2
import numpy as np

def main() :

    camera = WindowsCapture(
        cursor_capture=False,
        draw_border=None,
        monitor_index=None,
        window_name=None,
    )

    def on_frame_arrived(frame: Frame, capture_control: InternalCaptureControl) :


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
