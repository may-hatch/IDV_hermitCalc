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
UIを調整。

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
import time
import threading

#説明
with st.expander("使い方・更新予定"):
    st.text("""
            隠者戦でHPを数値で確認するためのツール。
            画像読込の都合上、起動は少し時間がかかります。

            【使い方】
            茶色のゲージが次の攻撃で食らう分、黄色がすでに食らった分です。
            赤・青はゲーム内と同様に表示されます。
            ★メイン機能
                リセット：
                    完全リセット。
                ひとつ戻る：
                    最後に押した攻撃もしくは治療を取り消します。
                    現時点では電極は戻らない&ひとつしか戻れないので注意。
                攻撃対象：
                    余剰ダメージを表示するための選択ボタン。
                    左上、右上、左下、右下の順に対応。
                    次の攻撃でダウンする場合、
                    「何ダメージ分消失するか」が余剰ダメージです。
                引き留める/恐怖：
                    トグルがオンの間、攻撃ボタンのダメージが2.2になります。
                赤/青/無ボタン：
                    極性の切り替え。
                攻撃/治療ボタン：
                    各ボタンの真上にあるゲージを増減。
                    同じ極性がいる場合は自動で他の人にも反映されます。
            ★サイドバー
                スキルのメモ用。今後スキルタイマー機能を合わせてつける予定。

            【作業予定リスト】
            ひとつ戻るボタンの調整
            ひとつ進むボタンの実装
            UI調整
            スキルタイマー実装

            【履歴】
            2025-10-19
                ひとつ戻るボタンを仮実装。
            2025-10-18
                治療時に表示が更新されるように修正。
                引き留める・恐怖に対応する用のスイッチを追加。
                余剰ダメ表示を仮実装。
            2025-10-16
                キャッシュで速度を改善。
                UIを調整。
            2025-10-10
                簡易的に動作を確認。
            """)
    
#【関数】予測
def estimate_hp():
    for e in range(4):
        if st.session_state["charge_type"][e]=="red":
            st.session_state["hp_estimate"][e]=st.session_state["damage_full"]/int(st.session_state["charge_count"][1])
        elif st.session_state["charge_type"][e]=="blue":
            st.session_state["hp_estimate"][e]=st.session_state["damage_full"]/int(st.session_state["charge_count"][2])
        else:
            st.session_state["hp_estimate"][e]=st.session_state["damage_full"]

#【関数】人数カウント
def count_charge():
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

#【関数】ひとつ戻る
def undo():
    if st.session_state["last_operation"][0]=="attack":
        for h in range(4):
            st.session_state["hp"][h]=st.session_state["last_operation"][h+2]
        estimate_hp()
        count_charge()
        st.rerun()
    elif st.session_state["last_operation"][0]=="cure":
        charanum=st.session_state["last_operation"][1]
        st.session_state["hp"][charanum]=st.session_state["last_operation"][charanum+2]
        estimate_hp()
        count_charge()
        st.rerun()

#【関数】画像をキャッシュ
@st.cache_data
def img_from_url(tag):
    url=f"https://raw.githubusercontent.com/may-hatch/IDV_hermitCalc/main/assets/{tag}.png"
    return Image.open(BytesIO(requests.get(url).content)).convert("RGBA")

#【関数】タイマー
def skill_timer(CT):
    CoolTime=1
    CT_bar=st.sidebar.progress(1)
    for timer in range(CT):
        CoolTime=(CT-timer)/CT
        CT_bar.progress(CoolTime)
        time.sleep(0.9)

#【データ】session_stateで管理するもの：hp(0~2000),hp_show(hp/1000) charge_type(電荷)
if "hp" not in st.session_state:
    st.session_state["hp"]=[0,0,0,0]
if "hp_show" not in st.session_state:
    st.session_state["hp_show"]=[0,0,0,0]
if "charge_type" not in st.session_state:
    st.session_state["charge_type"]=["none","none","none","none"]
#無、赤、青で人数カウント
if "charge_count" not in st.session_state:
    st.session_state["charge_count"]=[4,0,0]
#予測ダメージ量(0~2000)
if "hp_estimate" not in st.session_state:
    st.session_state["hp_estimate"]=[0,0,0,0]
#通常攻撃によるダメージ量
if "damage_full" not in st.session_state:
    st.session_state["damage_full"]=1200
#ひとつ戻る用：最後に行った操作を記録
#操作種別(攻撃or治療)、キャラ番号、HP１～４
if "last_operation" not in st.session_state:
    st.session_state["last_operation"]=["",0,0,0,0,0]

#サイドバー
with st.container():
    st.sidebar.text("メモ(機能未実装)")
    skill=st.sidebar.selectbox("【特質】",["神出鬼没","瞬間移動","移形","異常","巡視者","監視者","リッスン"])
    if skill=="神出鬼没":
        CT_full=150
    elif skill=="瞬間移動"or skill=="移形":
        CT_full=100
    elif skill=="異常"or skill=="巡視者":
        CT_full=90
    else:
        CT_full=0
    #with st.container():
    #    if st.sidebar.button("CTカウント(目安)",key="button_timer"):
    #        tm=threading.Thread(skill_timer(CT_full))
    #        tm.start()

    st.sidebar.markdown("**【人格】**")
    with st.container():
        st.sidebar.checkbox("閉鎖空間")
        st.sidebar.checkbox("裏向きカード")
        st.sidebar.checkbox("引き留める")
        st.sidebar.checkbox("傲慢")

#リセット、引き留める
with st.container(horizontal=True):
    if st.button("リセット"):
        st.session_state.clear()
        st.rerun()
    if st.button("ひとつ戻る"):
        undo()

#攻撃対象、予測余剰ダメ
with st.container(horizontal=True,border=True):
    with st.container(border=True,width=140):
        chase=st.selectbox("次の攻撃対象：",[1,2,3,4],width=100)

    nextDamage=st.session_state["hp_estimate"][chase-1]
    if nextDamage<=st.session_state["damage_full"]:
        target_charge=st.session_state["charge_type"][chase-1]
        if target_charge=="red":
            cnt=st.session_state["charge_count"][1]
        elif target_charge=="blue":
            cnt=st.session_state["charge_count"][2]
        else:
            cnt=1
        nextDamage=nextDamage*cnt
        over=nextDamage-(2000-st.session_state["hp"][chase-1])
    else:
        over=1200-(2000-st.session_state["hp"][chase-1])
    if over<=0:
        over=0

    with st.container():
        st.markdown(f"**余剰：{over}({round(over/1000,2)})**")
        noOne=st.toggle("引き留める/恐怖")
        if noOne:
            st.session_state["damage_full"]=2200
            estimate_hp()
        else:
            st.session_state["damage_full"]=1200
            estimate_hp()

#全体のボタンや数値表示の管理(自動実行)
with st.container(horizontal=True):
    img_from_url("red")
    img_from_url("blue")
    for s in range(4):
        key_ctn=f"s{s+1}"
        key_atk=f"attack_{s+1}"
        key_hl=f"heal_{s+1}"
        key_red=f"red_{s+1}"
        key_blue=f"blue_{s+1}"
        key_none=f"none_{s+1}"
        with st.container(key=key_ctn):
    #HPと電荷を表示(画像)
            buffer = BytesIO()
            #【画像】枠・極性
            overlay_img=img_from_url(st.session_state["charge_type"][s])
            overlay_img.save(buffer,format="PNG")
            buffer.seek(0)

            #【画像】hpゲージの表示
            #hp用元画像の取得
            img_hp=img_from_url("hp_show")
            #hp予測用元画像の取得
            img_est=img_from_url("hp_estimate")
            #画像サイズを合わせるために透明背景画像を利用
            img_bg=img_from_url("blank")
            #高さ計算用にhp数値取得
            #HPゲージ用画像の高さを計算(エラー対策で必ず+1px表示)
            st.session_state["hp_show"][s]=st.session_state["hp"][s]/1000
            estimate_hp()
            height_hp=int(round(st.session_state["hp_show"][s]*64))+1
            height_est=height_hp+int(round(st.session_state["hp_estimate"][s]/1000*64))
            #HPゲージの高さを調整
            img_hp.resize((128,height_hp))
            img_est.resize((128,height_est))
            #このあと合成するとき用の高さ(幅は固定なのでx=0)
            #128pxを超えてしまうときは元ゲームの仕様も加味して128pxに固定
            x=0
            if height_hp<=128:
                y=128-height_hp
            else:
                y=0
            #予測も高さを調整
            if height_est<=128:
                y_e=128-height_est
            else:
                y_e=0
            #hpゲージの画像を128x128で作成
            #予測
            img_bg.paste(img_est,(x,y_e),img_est)
            #実値
            img_bg.paste(img_hp,(x,y),img_hp)
            img_bg.save(buffer,format="PNG")
            buffer.seek(0)

            #枠・極性と合成
            img_bg.paste(overlay_img,(0,0),overlay_img)
            img_bg.save(buffer,format="PNG")
            buffer.seek(0)
            st.image(buffer,width=128)
            
            #HPを表示（文字）
            with st.container():
                st.text(f"恐怖値：{st.session_state["hp"][s]}({st.session_state["hp_show"][s]})")

            with st.container(horizontal=True):
                #攻撃ボタン(通常攻撃→1200)
                if st.button("攻撃",key=key_atk):
                    #戻せるように状態を記録：
                    st.session_state["last_operation"][0]="attack"
                    st.session_state["last_operation"][1]=int(s)
                    st.session_state["last_operation"][2]=st.session_state["hp"][0]
                    st.session_state["last_operation"][3]=st.session_state["hp"][1]
                    st.session_state["last_operation"][4]=st.session_state["hp"][2]
                    st.session_state["last_operation"][5]=st.session_state["hp"][3]
                    #対象となる極性を記録
                    tgt_chg=st.session_state["charge_type"][s]
                    #ダメージ算出
                    if st.session_state["charge_type"][s]=="red":
                        dmg=int(st.session_state["damage_full"]/int(st.session_state["charge_count"][1]))
                    elif st.session_state["charge_type"][s]=="blue":
                        dmg=int(st.session_state["damage_full"]/int(st.session_state["charge_count"][2]))
                    else:
                        dmg=st.session_state["damage_full"]
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
                    count_charge()
                    estimate_hp()
                    st.rerun()

                #治療ボタン(汎用性の都合で500ずつ)
                if st.button("治療",key=key_hl):
                    #戻せるように状態を記録：
                    st.session_state["last_operation"][0]="attack"
                    st.session_state["last_operation"][1]=int(s)
                    st.session_state["last_operation"][2]=st.session_state["hp"][0]
                    st.session_state["last_operation"][3]=st.session_state["hp"][1]
                    st.session_state["last_operation"][4]=st.session_state["hp"][2]
                    st.session_state["last_operation"][5]=st.session_state["hp"][3]
                    #１ダメ以上の時のみ治療可。
                    if st.session_state["hp"][s]>1000:
                        st.session_state["hp"][s]-=1000
                    else:
                        pass
                    st.session_state["hp_show"][s]=st.session_state["hp"][s]/1000
                    estimate_hp()
                    st.rerun()

            #電荷切り替えボタン
            with st.container(horizontal=True):
                if st.button("赤",key=key_red):
                    st.session_state["charge_type"][s]="red"
                    count_charge()
                    estimate_hp()
                    st.rerun()
                if st.button("青",key=key_blue):
                    st.session_state["charge_type"][s]="blue"
                    count_charge()
                    estimate_hp()
                    st.rerun()
                if st.button("無",key=key_none):
                    st.session_state["charge_type"][s]="none"
                    count_charge()
                    estimate_hp()
                    st.rerun()