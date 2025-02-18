
##########################################
# 武器判定に必要な関数　　　　　　　　　　#
##########################################



# ケアパケ　色(R:202, G:0, B:62),   位置(2432, 1280),カラーコード:0xCA003
# スナイパ　色(R:127, G:130, B:255),位置(2432, 1280),カラーコード:0x7F82FF
# ボセック　色(R:232, G:194, B:91), 位置(2432, 1280),カラーコード:0xE8C25B
# エネルギ　色(R:198, G:221, B:58), 位置(2432, 1280),カラーコード:0xC6DD3A
# ライト　　色(R:244, G:154, B:74), 位置(2432, 1280),カラーコード:0xF49A4A
# ヘビー　　色(R:107, G:206, B:168),位置(2432, 1280),カラーコード:0x6BCEA8
# ショット　色(R:255, G:44, B:0),   位置(2432, 1280),カラーコード:0xFF2C00

### 座標 ###
SINGLEFIRE_POSITION=(2270,1352)  # (2268,1352)が白となるのは単発武器のときだけ。　1
CHOKE_POSITION=(2276,1360)      # (2272,1336)が白となるのはチョーク武器のときだけ。 (2276, 1360)
BURST_POSITON=(2272,1352)      # これが白ということは　バースト武器か単発武器。 3
FULLAUTO_POSITION=(2267, 1359) # これが白ということはフルオートか単発武器。 4
AMMOCOLOR_POSITION=(2432,1280) # ここで武器の弾薬の種類を確認する。
HEALING_POSITION=(2212,936)    # 色(R:135, G:135, B:135),位置(2212, 936),位置(2212, 936) 確実性が低いけど1色であやる。

# この座標の色でアタッチメント(スコープ)のレアリティを判断
ATTACHMENT1_POSITION=(2080,1364) # x:2068-2092 y:1364
ATTACHMENT1_CENTER_POSITION=(2080,1348)
ATTACHMENT2_POSITION=(2118,1364) # x:2106-2129 y:1364
ATTACHMENT2_CENTER_POSITION=(2118,1348)

## 色 RGB ##
WHITE=(255,255,255)
SG_COL=(255,44,0)
SNIPE_COL=(127,130,255)
ENERGY_COL=(198,221,58)
LIGHT_COL=(244,154,74)
HEAVY_COL=(107,206,168)
XBOW_COL=(232,194,91)
PAKE_COL=(202,0,62)

BLUE_REALITY=(46,188,255)
PURPLE_REALITY=(222, 107, 255)

HEALING_COL=(134,134,134)

## 射撃モード ##
FULLAUTO=1
SINGLEFIRE=2
BURST=3
CHOKE=4

def get_pixel_color(img,position) :
    x=position[0]
    y=position[1]
    color=img[y,x]
    return (color[2],color[1],color[0]) # RGB形式でカラーのタプルを返す。

# 単発武器のとき 1 かつ 3 かつ 4 チョークのとき 2 バーストのとき 3 フルオートのとき4
def judge_firemode(screen) :
    if get_pixel_color(screen,FULLAUTO_POSITION)==WHITE :
        return FULLAUTO
    elif get_pixel_color(screen,CHOKE_POSITION)==WHITE :
        return CHOKE
    elif get_pixel_color(screen,BURST_POSITON)==WHITE :
        return BURST
    elif get_pixel_color(screen,SINGLEFIRE_POSITION)==WHITE :
        return SINGLEFIRE
    else :
        return 0

# 武器の弾薬の種類を判定する
def judge_ammo(screen) :
    return get_pixel_color(screen,AMMOCOLOR_POSITION)

# 巻いてるかどうか判定する
def judge_healing(screen) :
    if get_pixel_color(screen, HEALING_POSITION)==HEALING_COL :
        return True
    else :
        return False


def triggercheacker(screen) :    
    ammocol=judge_ammo(screen)
    firemode=judge_firemode(screen)
    healing=judge_healing(screen)
    triggeractive= (ammocol in [SNIPE_COL , SG_COL, PAKE_COL] ) or (ammocol in [HEAVY_COL, LIGHT_COL, ENERGY_COL,PAKE_COL] and firemode in [SINGLEFIRE, CHOKE])and not healing
    return triggeractive