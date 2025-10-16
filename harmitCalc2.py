"""
streamlitで使えるようにするため、
アプリ：banlistを作成したときにキャラリストを更新したため
新規ファイルで作成

2025-10-09
作成再開。
画像表示が作成を難しくしているので、一度数値のみで作成する方針に変更

2025-10-10
数値のみでの動作を確認。

2025-10-16
キャッシュで速度を改善。

"""
#作成日：2025/09/09

#隠者戦HP計算機
#機能ごとに段階的に作成
#【１：HP表示・通常攻撃/治療のみ】
#   一人分で表示まで完成
#   複数人の計算←今ここ
#   複数人の表示
#【２：予測表示】
#   例：「赤：0.4,青：1.2」
#___ここで実用実験___
#【３：キャラごとのスキル反映】
#【４：別タブにて地図の表示】

import streamlit as st
from PIL import Image
from io import BytesIO
import requests

st.title("【試験中】隠者戦HP計算機")
#説明
with st.expander("使い方"):
    st.write("""
             第五人格の隠者戦においてHPを数値で確認するためのツール。
             """)

@st.cache_data
def img_from_url(tag):
    url=f"https://raw.githubusercontent.com/may-hatch/IDV_hermitCalc/main/assets/{tag}.png"
    return Image.open(BytesIO(requests.get(url).content)).convert("RGBA")

#session_stateで管理するもの：hp(0~2000),hp_show(hp/1000) charge_type(電荷)
if "hp" not in st.session_state:
    st.session_state["hp"]=[0,0,0,0]
if "hp_show" not in st.session_state:
    st.session_state["hp_show"]=[0,0,0,0]
#if "hp_height" not in st.session_state:
#    st.session_state["hp_height"]=[0,0,0,0]
if "charge_type" not in st.session_state:
    st.session_state["charge_type"]=["none","none","none","none"]
#無、赤、青で人数カウント
if "charge_count" not in st.session_state:
    st.session_state["charge_count"]=[4,0,0]

for s  in range(4):
    key_ctn=f"s{s+1}"
    key_atk=f"attack_{s+1}"
    key_hl=f"heal_{s+1}"
    key_chg=f"charge_{s+1}"
    with st.container(border=True,horizontal=True):
        with st.container(key=key_ctn):
            with st.container(horizontal=True):
                #攻撃ボタン(通常攻撃→1200)
                if st.button("攻撃",key=key_atk):
                    #対象となる極性を記録
                    tgt_chg=st.session_state["charge_type"][s]
                    #ダメージ算出
                    if st.session_state["charge_type"][s]=="red":
                        dmg=1200/int(st.session_state["charge_count"][1])
                    elif st.session_state["charge_type"][s]=="blue":
                        dmg=1200/int(st.session_state["charge_count"][2])
                    else:
                        dmg=1200
                    #ダメージ反映
                    for i in range(4):
                        #電荷なかった時：本人だけにダメージ付与してfor終了
                        if tgt_chg=="none":
                            if st.session_state["hp"][s]+dmg>2000:
                                st.session_state["hp"][s]=2000
                            else:
                                st.session_state["hp"][s]+=dmg
                            #表示に反映
                            st.session_state["hp_show"][s]=st.session_state["hp"][s]/1000
                            break
                        #電荷があった時：同じ属性ならダメージ、属性リセット
                        if st.session_state["charge_type"][i]==tgt_chg:
                            if st.session_state["hp"][i]+dmg>2000:
                                st.session_state["hp"][i]=2000
                            else:
                                st.session_state["hp"][i]+=dmg
                            #ダメージを付与して属性リセット
                            st.session_state["charge_type"][i]="none"
                            st.session_state["hp_show"][i]=st.session_state["hp"][i]/1000
                    #いったん人数カウントを全部0に
                        st.session_state["charge_count"]=[0,0,0]
                    #人数カウントに反映
                    for type in st.session_state["charge_type"]:
                        if type=="none":
                            st.session_state["charge_count"][0]+=1
                        elif type=="red":
                            st.session_state["charge_count"][1]+=1
                        else:
                            st.session_state["charge_count"][2]+=1

                #治療ボタン(汎用性の都合で500ずつ)
                if st.button("治療",key=key_hl):
                    if st.session_state["hp"][s]>500:
                        st.session_state["hp"][s]-=500
                    else:
                        st.session_state["hp"][s]=0
                    st.session_state["hp_show"][s]=st.session_state["hp"][s]/1000

            #電荷切り替えボタン
            if st.button("切り替え",key=key_chg):
                if st.session_state["charge_type"][s]=="none":
                    st.session_state["charge_type"][s]="red"
                    st.session_state["charge_count"][0]-=1
                    st.session_state["charge_count"][1]+=1
                elif st.session_state["charge_type"][s]=="red":
                    st.session_state["charge_type"][s]="blue"
                    st.session_state["charge_count"][1]-=1
                    st.session_state["charge_count"][2]+=1
                else:
                    st.session_state["charge_type"][s]="none"
                    st.session_state["charge_count"][2]-=1
                    st.session_state["charge_count"][0]+=1
        with st.container():
        #HPと電荷を表示（文字）
            st.text(f"ダメージ：{st.session_state["hp"][s]}")
            st.text(f"({st.session_state["hp_show"][s]})")
            st.text(f"極性：{st.session_state["charge_type"][s]}")

        #HPと電荷を表示(画像)
        buffer = BytesIO()
        #【画像】枠・極性
        overlay_img=img_from_url(st.session_state["charge_type"][s])
        overlay_img.save(buffer,format="PNG")
        buffer.seek(0)

        #【画像】hpゲージの表示
        #hp用元画像の取得
        img_hp=img_from_url("hp_show")
        #画像サイズを合わせるために透明背景画像を利用
        img_bg=img_from_url("blank")
        #高さ計算用にhp数値取得
        #HPゲージ用画像の高さを計算(エラー対策で必ず+1px表示)
        height_hp=int(round(st.session_state["hp_show"][s]*64))+1
        #HPゲージの高さを調整
        img_hp.resize((128,height_hp))
        #このあと合成するとき用の高さ(幅は固定なのでx=0)
        #128pxを超えてしまうときは元ゲームの仕様も加味して128pxに固定
        x=0
        if height_hp<=128:
            y=128-height_hp
        else:
            y=0
        #hpゲージの画像を128x128で作成
        img_bg.paste(img_hp,(x,y),img_hp)
        img_bg.save(buffer,format="PNG")
        buffer.seek(0)

        #枠・極性と合成
        img_bg.paste(overlay_img,(0,0),overlay_img)
        img_bg.save(buffer,format="PNG")
        buffer.seek(0)
        st.image(buffer,width=128)