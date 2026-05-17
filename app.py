import streamlit as st
from datetime import datetime
import os
import csv

# ==========================================
# 1. 画面の設定
# ==========================================
st.set_page_config(page_title="バス混雑度フィードバック", page_icon="🚌", layout="centered")

# 🌟【追加】ボタンを「大きな正方形」にして、改行を許可するCSS
st.markdown("""
<style>
/* Streamlitのボタンに対するカスタムデザイン */
div.stButton > button:first-child {
    height: 160px;             /* ボタンの高さを広げて正方形に近づける */
    white-space: pre-wrap;     /* 文字と絵文字の改行(\n)を許可する */
    font-size: 16px;           /* 文字の大きさ */
    font-weight: bold;         /* 文字を太く */
    border-radius: 15px;       /* 角を少し丸くしてアプリっぽく */
    border: 2px solid #ddd;    /* 枠線を少し太く */
}
/* ボタンにマウスを乗せたとき・押したときの色変更 */
div.stButton > button:first-child:hover {
    border-color: #ff4b4b;
    color: #ff4b4b;
}
</style>
""", unsafe_allow_html=True)

DATA_FILE = "user_feedback.csv"

# ==========================================
# 2. 多言語対応＆ピクトグラム辞書
# ==========================================
LANG_DICT = {
    "JA": {
        "title": "🚌 混雑度アンケート",
        "subtitle": "今の車内の様子をタップして教えてください！",
        "btn_1": "🟢\nガラガラ\n\n💺 💺 💺",
        "btn_2": "🟡\n少し混雑\n\n🧍 🧍 🧍",
        "btn_3": "🔴\n大混雑\n\n🧍🧍🧍\n🧍🧍🧍",
        "success_msg": "ご協力ありがとうございました！🙌",
        "error_msg": "エラーが発生しました。"
    },
    "EN": {
        "title": "🚌 Congestion Survey",
        "subtitle": "Tap the button that matches the current bus!",
        "btn_1": "🟢\nEmpty\n\n💺 💺 💺",
        "btn_2": "🟡\nStanding\n\n🧍 🧍 🧍",
        "btn_3": "🔴\nCrowded\n\n🧍🧍🧍\n🧍🧍🧍",
        "success_msg": "Thank you for your cooperation! 🙌",
        "error_msg": "An error occurred."
    }
}

# ==========================================
# 3. アプリのUI画面構築
# ==========================================

# 言語切り替え
selected_lang = st.selectbox("Language / 言語", ["日本語", "English"], label_visibility="collapsed")
lang = "JA" if selected_lang == "日本語" else "EN"

st.title(LANG_DICT[lang]["title"])
st.caption(LANG_DICT[lang]["subtitle"])

# URLパラメータ取得
route_id = st.query_params.get("route_id", "不明(Unknown)")
busstop_id = st.query_params.get("busstop_id", "不明(Unknown)")
st.info(f"📍 Route ID: {route_id} / Busstop ID: {busstop_id}")

st.markdown("---")

# 🌟【変更】3つのカラム（列）を横並びに作成
col1, col2, col3 = st.columns(3)

# どのボタンが押されたかを記録する変数
user_class = None

# 各カラムに大きなボタンを配置
with col1:
    if st.button(LANG_DICT[lang]["btn_1"], use_container_width=True):
        user_class = 1
with col2:
    if st.button(LANG_DICT[lang]["btn_2"], use_container_width=True):
        user_class = 2
with col3:
    if st.button(LANG_DICT[lang]["btn_3"], use_container_width=True):
        user_class = 3

# ==========================================
# 4. ボタンが押されたときの保存処理
# ==========================================
if user_class is not None:
    now_ts = int(datetime.now().timestamp())
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    file_exists = os.path.isfile(DATA_FILE)
    try:
        with open(DATA_FILE, mode='a', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            if not file_exists:
                writer.writerow(["timestamp", "datetime", "route_id", "busstop_id", "user_class"])
            writer.writerow([now_ts, now_str, route_id, busstop_id, user_class])
            
        st.success(LANG_DICT[lang]["success_msg"])
        st.balloons()
        
    except Exception as e:
        st.error(LANG_DICT[lang]["error_msg"])
