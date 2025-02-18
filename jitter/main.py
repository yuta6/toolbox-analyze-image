# Pythonでひとつのファイルにコンパイルする方法
# nuitka --standalone --onefile --follow-imports jitter_dist.py

# Jitterマクロに必要なプログラム 1.5 1.9 2.2
###########################################################################
import win32con
import win32api
import ctypes

import time
import math
import random
import csv
from ctypes import windll

import xinput
import joystickapi

L1=4
R1=5
L2=6
R2=7
VK_LBUTTON=0x01
VK_RBUTTON=0x02


XINPUT=0
DIRECTINPUT=1
NOTFOUND=2

JITTERMACRO="""
     ██╗██╗████████╗████████╗███████╗██████╗ 
     ██║██║╚══██╔══╝╚══██╔══╝██╔════╝██╔══██╗
     ██║██║   ██║      ██║   █████╗  ██████╔╝
██   ██║██║   ██║      ██║   ██╔══╝  ██╔══██╗
╚█████╔╝██║   ██║      ██║   ███████╗██║  ██║
"""

def init_pad()->tuple[str,int]:
    
    # XInput 
    tf_turple=XInput.get_connected()
    for id in range(4) :
        if tf_turple[id] :
            print("Xboxコントローラー")
            return XINPUT, id

    # DirectInput 
    num = joystickapi.joyGetNumDevs()
    for id in range(num):
        ret, caps = joystickapi.joyGetDevCaps(id)
        if ret:
            print("PlaystationまたはSwitchコントローラー")
            return DIRECTINPUT,id

    print("コントローラーをさしてください.")
    time.sleep(3)
    clear()
    print(JITTERMACRO)
    return NOTFOUND, 0

def getkeystate(keycode) :
    return bool(ctypes.windll.user32.GetAsyncKeyState(keycode) and 0x8000) 

def padbuttonstate(pad,code) :
    
    input_method=pad[0]
    pad_id=pad[1]

    # XInput (XBOX用)
    if input_method==XINPUT :
        try : 
            state=XInput.get_state(pad_id)
        except :
            return False # XBOXコントローラーが切断された場合
        
        if code==L2 :
            if 8<state.Gamepad.bLeftTrigger<256 :
                return True 
            else :
                return False 
        elif code==R2 : 
            if 8<state.Gamepad.bRightTrigger<256 :
                return True 
            else : 
                return False 
        else : 
            return False

    # DirectInput (PS4用)
    elif input_method==DIRECTINPUT :
        info = joystickapi.joyGetPosEx(pad_id)[1]
        if info is None :
            return False 
        elif code is not None :
            return (1 << code) & info.dwButtons != 0 
        else :
            return False
    else :
        pass    
    
def mouse_move(dx,dy) :
    win32api.mouse_event(win32con.MOUSEEVENTF_MOVE, int(dx), int(dy), 0, 0) 


RANDOM_THETA=math.pi/48
THETA=math.pi/6
JITTER_RADIUS=26
INTERVAL=0.004
dx,dy=26,20
# X:26 Y:20 
# X:20 Y:16

def jitter(pad) : 

    while True :    
        if padbuttonstate(pad,R2) and padbuttonstate(pad,L2)  :

            #theta=random.uniform(THETA-RANDOM_THETA,THETA+RANDOM_THETA)
            #dx=JITTER_RADIUS*math.cos(theta)
            #dy=JITTER_RADIUS*math.sin(theta)

            mouse_move(dx,-dy+1)
            time.sleep(INTERVAL)
            mouse_move(-dx,dy+1)
            time.sleep(INTERVAL)



# ライセンス認証
############################################################################

import sys
import time
import os
import hashlib

OK="""           
 █▀█ █▄▀ █
 █▄█ █░█ ▄            
"""

def clear():
    os.system('cls & title ジッターマクロ')  # clear console, change title

def getchecksum():
    md5_hash = hashlib.md5()
    file = open(''.join(sys.argv), "rb")
    md5_hash.update(file.read())
    digest = md5_hash.hexdigest()
    return digest

keyauthapp = api(
    name = "Jitter",
    ownerid = "6s2lqruf9B",
    secret = "f73fbee765d457e46a3646801b1f29d026b3946b4dc05a2996dea8f1e588cd72",
    version = "1.0",
    hash_to_check = getchecksum()
)

KEY_TEXT_NAME="jitter_key.txt"

def auth():
    # keyの保存しているファイルがある場合は読み込み
    try :
        with open("jitter_key.txt",encoding='utf-8',mode='r') as keytxt : 
            key   =keytxt.read()
            result=keyauthapp.license(key)
            if result :
                print("Key :"+key)
                print(OK)
                time.sleep(1)
                return 
            else :
                pass
    except :
        pass
        
    # keyを保存しているテキストがない場合
    key   = input('Key :')
    result=keyauthapp.license(key)
    if result :
        with open("jitter_key.txt",encoding='utf-8',mode='w') as keytxt : 
            keytxt.write(key)
        print(OK)
        time.sleep(1)
        return 
    else :
        print("Keyがちがいます. ")
        time.sleep(1)
        clear()
        print(JITTERMACRO)
        auth()



# メイン関数
#############################
def main() :

    clear()
    print(JITTERMACRO)

    #auth()

    pad=init_pad()
    while pad[0]==NOTFOUND : # コントローラーがささっていない場合
        pad=init_pad()

    windll.winmm.timeBeginPeriod(1)
    jitter(pad)
    windll.winmm.timeEndPeriod(1)

if __name__ == "__main__":
    main()


"""

# キーマウの感度を推奨感度に変更する
#######################################
def read_old_mouse_sensitive() :
    with open("/Users/"+ str(os.getlogin())+ "/Saved Games/Respawn/Apex/local/settings.cfg") as apex_setting_file :
        reader = csv.reader(apex_setting_file) # iterator
        
def write_new_mouse_sensitive() : 
    pass

"""