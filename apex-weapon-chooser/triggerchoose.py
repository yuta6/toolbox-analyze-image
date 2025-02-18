# NewProjectをPadに対応させる　+ Triggerbotを単発武器のみに制限する
import win32con
import win32api
import ctypes
import time
import threading

import numpy as np

import joystickapi as joystickapi 
import directkey as dkey
from weapon import triggercheacker


##########################################
# 画像の分析および画像の取得に必要な定数　#
##########################################

# ゲーム画面のサイズを取得
SCREENWIDTH=win32api.GetSystemMetrics(0) # 2560
SCREENHEIGHT=win32api.GetSystemMetrics(1) # 1440
CENTERX=int(SCREENWIDTH/2)
CENTERY=int(SCREENHEIGHT/2) # intしないと行列とかをスライスするときエラーが起きる。

"""
def check_gamestate(screen) :
    firemode=judge_firemode(screen)
    ammocol=judge_ammo(screen)
    healing=judge_healing(screen)
    # adsteam=judge_ads_team(screen)
    if healing :
        return INACTIVEMODE
    elif ammocol==SG_COL or firemode==CHOKE or firemode==SINGLEFIRE :
        return TRIGGERBOTMODE
    elif firemode==FULLAUTO and (getkeystate(LBUTTON) or padbuttonstate(R2)) and (getkeystate(RBUTTON) or padbuttonstate(L2)):
        return AIMBOTMODE
    else :
        return INACTIVEMODE
"""
        
##########################################
# マウスやPadに関係する関数 　　　　　　  　#
##########################################

# 射撃ボタン
LBUTTON=0x01
L2=7
# ADSボタン
RBUTTON=0x02
R2=8
# 3とマウスホイール下げ
VK_3=0x33
VK_O=0x4F
VK_F5=0x74
VK_F12=0x7B
VK_RSHIFT=0xA1
VK_L=0x4C
VK_P=0x50
VK_J=0x4A
VK_H=0x48
VK_PAUSE=0x13
VK_LWIN=0x5B
VK_CON=0x1C
VK_HOME=0x24

def getkeystate(keycode) :
    return bool(ctypes.windll.user32.GetAsyncKeyState(keycode) and 0x8000) 

def padbuttonstate(code) :
    info = joystickapi.joyGetPosEx(0)[1]
    if info is None :
        return False 
    elif code==L2 :
        return (1 << 6) & info.dwButtons != 0 
    elif code==R2 :
        return (1 << 7) & info.dwButtons != 0  
    else :
        return False

def triggerchooser(camera) :
    while True :        
        if triggercheacker(camera) :
            print("Press H key")
            dkey.PressKey(VK_H)
            while triggercheacker(camera) :
                time.sleep(0.1)
            print("Release H key")
            dkey.ReleaseKey(VK_H)

def leftclicker():
    while True :
        if getkeystate(LBUTTON) or getkeystate(RBUTTON) or padbuttonstate(R2):
            dkey.PressKey(VK_J)
            while getkeystate(LBUTTON) or getkeystate(RBUTTON) or padbuttonstate(R2):
                time.sleep(0.1)
            dkey.ReleaseKey(VK_J)

def main():
    # ゲーム画面のスクリーンショット
    # camera = dxcam.create(output_color="BGR")
    print("スクリプトを起動しました。")
    leftclicker()
    

if __name__ == "__main__":
    main()