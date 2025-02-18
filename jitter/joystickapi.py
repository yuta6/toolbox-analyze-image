import ctypes


try:
    winmmdll = ctypes.WinDLL('winmm.dll')

    # [joyGetNumDevs](https://docs.microsoft.com/en-us/windows/win32/api/joystickapi/nf-joystickapi-joygetnumdevs)
    """
    UINT joyGetNumDevs();
    """
    joyGetNumDevs_proto = ctypes.WINFUNCTYPE(ctypes.c_uint)
    joyGetNumDevs_func  = joyGetNumDevs_proto(("joyGetNumDevs", winmmdll))

    # [joyGetDevCaps](https://docs.microsoft.com/en-us/windows/win32/api/joystickapi/nf-joystickapi-joygetdevcaps)
    """
    MMRESULT joyGetDevCaps(UINT uJoyID, LPJOYCAPS pjc, UINT cbjc);

    32 bit: joyGetDevCapsA
    64 bit: joyGetDevCapsW

    sizeof(JOYCAPS): 728
    """
    joyGetDevCaps_proto = ctypes.WINFUNCTYPE(ctypes.c_uint, ctypes.c_uint, ctypes.c_void_p, ctypes.c_uint)
    joyGetDevCaps_param = (1, "uJoyID", 0), (1, "pjc", None), (1, "cbjc", 0)
    joyGetDevCaps_func  = joyGetDevCaps_proto(("joyGetDevCapsW", winmmdll), joyGetDevCaps_param)

    # [joyGetPosEx](https://docs.microsoft.com/en-us/windows/win32/api/joystickapi/nf-joystickapi-joygetposex)
    """
    MMRESULT joyGetPosEx(UINT uJoyID, LPJOYINFOEX pji);
    sizeof(JOYINFOEX): 52
    """
    joyGetPosEx_proto = ctypes.WINFUNCTYPE(ctypes.c_uint, ctypes.c_uint, ctypes.c_void_p)
    joyGetPosEx_param = (1, "uJoyID", 0), (1, "pji", None)
    joyGetPosEx_func  = joyGetPosEx_proto(("joyGetPosEx", winmmdll), joyGetPosEx_param)
except:
    winmmdll = None

# joystickapi - joyGetNumDevs
def joyGetNumDevs():
    try:
        num = joyGetNumDevs_func()
    except:
        num = 0
    return num

# joystickapi - joyGetDevCaps
def joyGetDevCaps(uJoyID):
    try:
        buffer = (ctypes.c_ubyte * JOYCAPS.SIZE_W)()
        p1 = ctypes.c_uint(uJoyID)
        p2 = ctypes.cast(buffer, ctypes.c_void_p)
        p3 = ctypes.c_uint(JOYCAPS.SIZE_W)
        ret_val = joyGetDevCaps_func(p1, p2, p3)
        ret = (False, None) if ret_val != JOYERR_NOERROR else (True, JOYCAPS(buffer))   
    except:
        ret = False, None
    return ret 

# joystickapi - joyGetPosEx
def joyGetPosEx(uJoyID):
    try:
        buffer = (ctypes.c_uint32 * (JOYINFOEX.SIZE // 4))()
        buffer[0] = JOYINFOEX.SIZE
        buffer[1] = JOY_RETURNALL
        p1 = ctypes.c_uint(uJoyID)
        p2 = ctypes.cast(buffer, ctypes.c_void_p)
        ret_val = joyGetPosEx_func(p1, p2)
        ret = (False, None) if ret_val != JOYERR_NOERROR else (True, JOYINFOEX(buffer))
    except:
        ret = False, None
    return ret 

JOYERR_NOERROR = 0
JOY_RETURNX = 0x00000001
JOY_RETURNY = 0x00000002
JOY_RETURNZ = 0x00000004
JOY_RETURNR = 0x00000008
JOY_RETURNU = 0x00000010
JOY_RETURNV = 0x00000020
JOY_RETURNPOV = 0x00000040
JOY_RETURNBUTTONS = 0x00000080
JOY_RETURNRAWDATA = 0x00000100
JOY_RETURNPOVCTS = 0x00000200
JOY_RETURNCENTERED = 0x00000400
JOY_USEDEADZONE = 0x00000800
JOY_RETURNALL = (JOY_RETURNX | JOY_RETURNY | JOY_RETURNZ | \
				 JOY_RETURNR | JOY_RETURNU | JOY_RETURNV | \
				 JOY_RETURNPOV | JOY_RETURNBUTTONS)

# joystickapi - JOYCAPS
class JOYCAPS:
    SIZE_W = 728
    OFFSET_V = 4 + 32*2
    def __init__(self, buffer):
        ushort_array = (ctypes.c_uint16 * 2).from_buffer(buffer)
        self.wMid, self.wPid = ushort_array  

        wchar_array = (ctypes.c_wchar * 32).from_buffer(buffer, 4)
        self.szPname = ctypes.cast(wchar_array, ctypes.c_wchar_p).value
        
        uint_array = (ctypes.c_uint32 * 19).from_buffer(buffer, JOYCAPS.OFFSET_V) 
        self.wXmin, self.wXmax, self.wYmin, self.wYmax, self.wZmin, self.wZmax, \
        self.wNumButtons, self.wPeriodMin, self.wPeriodMax, \
        self.wRmin, self.wRmax, self.wUmin, self.wUmax, self.wVmin, self.wVmax, \
        self.wCaps, self.wMaxAxes, self.wNumAxes, self.wMaxButtons = uint_array

# joystickapi - JOYINFOEX
class JOYINFOEX:
  SIZE = 52
  def __init__(self, buffer):
      uint_array = (ctypes.c_uint32 * (JOYINFOEX.SIZE // 4)).from_buffer(buffer) 
      self.dwSize, self.dwFlags, \
      self.dwXpos, self.dwYpos, self.dwZpos, self.dwRpos, self.dwUpos, self.dwVpos, \
      self.dwButtons, self.dwButtonNumber, self.dwPOV, self.dwReserved1, self.dwReserved2 = uint_array


def main () :
    # 利用可能なジョイスティックの数を取得
    numDevs = joyGetNumDevs()
    if numDevs == 0:
        print("No joystick devices found.")
        return

    print(f"Number of joystick devices: {numDevs}")

    # 各ジョイスティックデバイスについて情報を取得して表示
    for i in range(numDevs):
        print(f"\nDevice {i+1}:")

        # デバイスのキャパシティ情報を取得
        result, caps = joyGetDevCaps(i)
        if result:
            print(f"  Product ID: {caps.wPid}")
            print(f"  Product Name: {caps.szPname}")
            print(f"  Num Buttons: {caps.wNumButtons}")
            print(f"  X Axis: min {caps.wXmin}, max {caps.wXmax}")
            print(f"  Y Axis: min {caps.wYmin}, max {caps.wYmax}")
        else:
            print("  Failed to get device capabilities.")

        # デバイスの現在の状態を取得
        result, state = joyGetPosEx(i)
        if result:
            print(f"  X Position: {state.dwXpos}")
            print(f"  Y Position: {state.dwYpos}")
            print(f"  Buttons Pressed: {state.dwButtons}")
        else:
            print("  Failed to get device state.")


if __name__=="__main__" :
    main()