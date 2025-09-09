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

#管理するもの：hp, charge_type(電荷)
if "hp" not in st.session_state:
    st.session_state.hp=[0]
if "charge_type" not in st.session_state:
    st.session_state.charge_type=["none"]

#電荷切り替えボタン
#透明化
st.markdown("""
            <style>
            div.stbutton > button{
            backgrond-color:rgba(0,0,0,0);
            color:transparent;
            boder:none
            height:128px
            width:128px;
            cursor:pointer:
            }
            </style>
            """,unsafe_allow_html=True)
#機能
if st.button("切り替え"):
    if st.session_state["charge_type"]==["none"]:
        st.session_state["charge_type"]=["red"]
    elif st.session_state["charge_type"]==["red"]:
        st.session_state["charge_type"]=["blue"]
    else:
        st.session_state["charge_type"]=["none"]

#攻撃ボタン(通常攻撃→1250)
if st.button("攻撃"):
    st.session_state["hp"]+=1250
#恐怖の一撃ボタン(1250+1000)
if st.button("恐怖"):
    st.session_state["hp"]+=2250

#治療ボタン(汎用性の都合で500ずつ)
if st.button("治療"):
    st.session_state["hp"]-=500