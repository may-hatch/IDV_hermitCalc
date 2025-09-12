"""
streamlitで使えるようにするため、
アプリ：banlistを作成したときにキャラリストを更新したため
新規ファイルで作成
"""
#作成日：2025/09/09

#隠者戦HP計算機
#機能ごとに段階的に作成
#【１：HP表示・通常攻撃/治療のみ】←イマココ
#   一人分で表示まで完成
#   複数人の計算
#   複数人の表示
#【２：予測表示】
#   赤の人
#【３：キャラごとのスキル反映】
#【４：別タブにて地図の表示】

#１：HP表示・通常攻撃/治療のみ
#まず１人分作成
import streamlit as st
from PIL import Image
from io import BytesIO
import requests

#session_stateで管理するもの：hp(0~2000),hp_show(hp/1000) charge_type(電荷)
if "hp" not in st.session_state:
    st.session_state["hp"]=[0,0,0,0]
if "hp_show" not in st.session_state:
    st.session_state["hp_show"]=[0,0,0,0]
if "hp_height" not in st.session_state:
    st.session_state["hp_height"]=[0,0,0,0]
if "charge_type" not in st.session_state:
    st.session_state["charge_type"]=["none","none","none","none"]


#攻撃ボタン(通常攻撃→1200)
if st.button("攻撃",key=f"attack_1"):
    if st.session_state["hp"][0]>800:
        st.session_state["hp"][0]=2000
    else:
        st.session_state["hp"][0]+=1200
    st.session_state["hp_show"][0]=st.session_state["hp"][0]/1000
    st.session_state["charge_type"][0]="none"

#治療ボタン(汎用性の都合で500ずつ)
if st.button("治療",key=f"heal_1"):
    if st.session_state["hp"][0]>500:
        st.session_state["hp"][0]-=500
    else:
        st.session_state["hp"][0]=0
    st.session_state["hp_show"][0]=st.session_state["hp"][0]/1000

#HPを数値で表示
hp_nums=st.session_state["hp"]
for hs in hp_nums:
    st.text(f"{hs}")
    st.text(f"({round(hs/1000)})")

#電荷切り替えボタン
#機能(無→赤→青→無で切り替え)
for l in range(0,4):
    if st.button("切り替え",key=f"charge_button_{l}"):
        if st.session_state["charge_type"][{l}]=="none":
            st.session_state["charge_type"][{l}]="red"
        elif st.session_state["charge_type"][{l}]=="red":
            st.session_state["charge_type"][{l}]="blue"
        else:
            st.session_state["charge_type"][{l}]="none"

#【画像】電荷の色
#種類の取得
    charge_type=st.session_state["charge_type"]
    charge_imgs=[]
#参照URLの決定、画像の取得・集約
for ct in charge_type:
    charge_url = f"https://raw.githubusercontent.com/may-hatch/IDV_hermitCalc/main/assets/{ct}.png"
    img_charge=Image.open(BytesIO(requests.get(charge_url).content)).convert("RGBA")
    charge_imgs.append(img_charge)
    
#【画像】枠
frame_url = "https://raw.githubusercontent.com/may-hatch/IDV_hermitCalc/main/assets/frame.png"
img_frame=Image.open(BytesIO(requests.get(frame_url).content)).convert("RGBA")

#【画像】重ねる
buffer = BytesIO()
overlay_imgs=[]
#電荷、枠画像の合成
for ci in charge_imgs:
    img_marged=Image.alpha_composite(img_frame,ci)
#合成画像のバッファへの保存
    overlay_imgs.append(img_marged)

#【画像】hpゲージの表示
#hp用元画像の取得
img_hp_url="https://raw.githubusercontent.com/may-hatch/IDV_hermitCalc/main/assets/hp_show.png"
img_hp=Image.open(BytesIO(requests.get(img_hp_url).content)).convert("RGBA")
#画像サイズを合わせるために透明背景画像を利用
bg_url="https://raw.githubusercontent.com/may-hatch/IDV_hermitCalc/main/assets/none.png"
img_bg=Image.open(BytesIO(requests.get(bg_url).content)).convert("RGBA")


list_height=[]
#画像高さ計算用にhp数値取得
#HPゲージ用画像の高さを計算(エラー対策で必ず+1px表示)
for i in range(0,4):
    num_hp=st.session_state["hp_show"][i]
    height_hp=int(round(num_hp*64))+1
    img_hp.resize((128,height_hp))
#このあと合成するとき用の高さを記入(幅は固定なのでx=0)
#128pxを超えてしまうときは元ゲームの仕様も加味して128pxに固定
    x=0
    if height_hp<=128:
        y=128-height_hp
    else:
        y=0
    list_height.append(y)

#hpゲージの画像を作成
    img_bg.paste(img_hp,(x,y),img_hp)
    img_bg.save(buffer,format="PNG")
    
for oi in overlay_imgs:
#上で作った画像と合成
    img_bg.paste(oi,(0,0),oi)
    img_bg.save(buffer,format="PNG")
    buffer.seek(0)
    st.image(buffer,width=128)

