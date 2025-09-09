"""
streamlitで使えるようにするため、
アプリ：banlistを作成したときにキャラリストを更新したため
新規ファイルで作成
"""
#作成日：2025/09/09
"""
機能ごとに段階的に作成
【１：HP表示・通常攻撃/治療のみ】
＊視覚的表示
前面↑
    電荷切り替え（透明なボタン）
    電荷（画像。３種類。上のボタンに応じて変更）
    現HP（数値）
    枠（透過画像）
    HPゲージ（縦方向プログレスバー）
背面↓

＊機能ボタン
攻撃ボタン・治療ボタン（押すとHPおよびプログレスバーが変動）

これを４つ縦に並べるつもり。
【２；予測表示】
【３：キャラごとのスキル反映】
【４：別タブにて地図の表示】
"""

"""
作成に当たって使用したツール：
VSCode
streamlit cloud
"""

#１：HP表示・通常攻撃/治療のみ
#まず１人分作成
import streamlit as st
from PIL import Image

#管理するもの：hp(0~2000),hp_show(hp/1000) charge_type(電荷)
if "hp" not in st.session_state:
    st.session_state["hp"]=[0]
if "hp_show" not in st.session_state:
    st.session_state["hp_show"]=[0]
if "charge_type" not in st.session_state:
    st.session_state["charge_type"]=["none"]

#【画像】電荷の色表示
charge_type=st.session_state["charge_type"][0]
charge_image=f"assets/{charge_type}.png"
st.image(Image.open(charge_image),width=128)

#電荷切り替えボタン
#透明化
st.markdown("""
    <style>
    div.stbutton > stbutton{
            background-color:rgba(0,0,0,0);
            color:transparent;
            border:none;
            height:128px;
            width:128px;
            cursor:pointer;
    }
    </style>
""",unsafe_allow_html=True)
#機能(無→赤→青→無で切り替え)
if st.button("",key="charge_button_1"):
    if st.session_state["charge_type"][0]=="none":
        st.session_state["charge_type"][0]="red"
    elif st.session_state["charge_type"][0]=="red":
        st.session_state["charge_type"][0]="blue"
    else:
        st.session_state["charge_type"][0]="none"

#【画像】枠の表示
st.image(Image.open("assets/frame.png"),width=128)

#HP数値の表示
st.write(st.session_state["hp_show"])
#【画像】hpゲージの表示
#プログレスバーを縦向きに変更...はいったん保留
hp=st.session_state["hp_show"][0]
st.markdown(f"""
    <style>
    .hp-bar{{
        height:{round(hp*64)}px;
        width:40px;
        object-fit:cover;
    }}
    </style>
    <img src="assets/hp_show.png" class="hp_bar">
""",unsafe_allow_html=True)
st.image(Image.open("assets/hp_show.png"),width=128)

#攻撃ボタン(通常攻撃→1250)
if st.button("攻撃"):
    st.session_state["hp"][0]+=1250
    st.session_state["hp_show"][0]=round(st.session_state["hp"][0]/1000,2)
#恐怖の一撃ボタン(1250+1000)
if st.button("恐怖"):
    st.session_state["hp"][0]+=2250
    st.session_state["hp_show"][0]=round(st.session_state["hp"][0]/1000,2)

#治療ボタン(汎用性の都合で500ずつ)
if st.button("治療"):
    st.session_state["hp"][0]-=500
    st.session_state["hp_show"][0]=round(st.session_state["hp"][0]/1000,2)