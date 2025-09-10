"""
streamlitで使えるようにするため、
アプリ：banlistを作成したときにキャラリストを更新したため
新規ファイルで作成
"""
#作成日：2025/09/09

#隠者戦HP計算機
#機能ごとに段階的に作成
#【１：HP表示・通常攻撃/治療のみ】←イマココ
#【２；予測表示】
#【３：キャラごとのスキル反映】
#【４：別タブにて地図の表示】

#１：HP表示・通常攻撃/治療のみ
#まず１人分作成
import streamlit as st
from PIL import Image
from io import BytesIO
import requests

#管理するもの：hp(0~2000),hp_show(hp/1000) charge_type(電荷)
if "hp" not in st.session_state:
    st.session_state["hp"]=[0]
if "hp_show" not in st.session_state:
    st.session_state["hp_show"]=[0]
if "charge_type" not in st.session_state:
    st.session_state["charge_type"]=["none"]

#攻撃ボタン(通常攻撃→1250)
if st.button("攻撃",key="attack"):
    st.session_state["hp"][0]+=1200
#    st.text(f"攻撃ボタンが押された：{st.session_state["hp"][0]}")
    st.session_state["hp_show"][0]=st.session_state["hp"][0]/1000
#    st.text(f"表示に反映した：{st.session_state["hp_show"][0]}")
#恐怖の一撃ボタン(1250+1000)
if st.button("恐怖",key="terror"):
    st.session_state["hp"][0]+=2200
    st.session_state["hp_show"][0]=st.session_state["hp"][0]/1000

#治療ボタン(汎用性の都合で500ずつ)
if st.button("治療",key="heal"):
    st.session_state["hp"][0]-=500
    st.session_state["hp_show"][0]=st.session_state["hp"][0]/1000

st.write(st.session_state["hp_show"][0])

#電荷切り替えボタン
#機能(無→赤→青→無で切り替え)
if st.button("切り替え",key="charge_button_1"):
    if st.session_state["charge_type"][0]=="none":
        st.session_state["charge_type"][0]="red"
    elif st.session_state["charge_type"][0]=="red":
        st.session_state["charge_type"][0]="blue"
    else:
        st.session_state["charge_type"][0]="none"

#【画像】電荷の色
charge_type=st.session_state["charge_type"][0]
charge_url = f"https://raw.githubusercontent.com/may-hatch/IDV_hermitCalc/main/assets/{charge_type}.png"
img_charge=Image.open(BytesIO(requests.get(charge_url).content)).convert("RGBA")
#st.image(charge_txt,width=128)

#【画像】枠
frame_url = "https://raw.githubusercontent.com/may-hatch/IDV_hermitCalc/main/assets/frame.png"
img_frame=Image.open(BytesIO(requests.get(frame_url).content)).convert("RGBA")
#st.image("assets/frame.png",width=128)

#【画像】重ねる
buffer = BytesIO()
img_marged1=Image.alpha_composite(img_frame,img_charge)
img_marged1.save(buffer,format="PNG")
buffer.seek(0)
#st.image(buffer,width=128)

#【画像】hpゲージの表示
#プログレスバーを縦向きに変更...はいったん保留
num_hp=st.session_state["hp_show"][0]
img_hp_url="https://raw.githubusercontent.com/may-hatch/IDV_hermitCalc/main/assets/hp_show.png"
img_hp=Image.open(BytesIO(requests.get(img_hp_url).content)).convert("RGBA")
bg_url="https://raw.githubusercontent.com/may-hatch/IDV_hermitCalc/main/assets/none.png"
img_bg=Image.open(BytesIO(requests.get(bg_url).content)).convert("RGBA")
#HPゲージ用画像の高さを指定(エラー対策で1px必ず表示)
height_hp=int(round(num_hp*64))+1
img_hp.resize((128,height_hp))
#このあと合成するとき用の高さを記入
x=0
y=128-height_hp
#hpゲージの画像を作成
img_bg.paste(img_hp,(x,y),img_hp)
img_bg.save(buffer,format="PNG")
buffer.seek(0)
#上で作った画像と合成
img_bg.paste(img_marged1,(0,0),img_marged1)
img_bg.save(buffer,format="PNG")
buffer.seek(0)
st.image(buffer,width=128)

