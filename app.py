import streamlit as st
from datetime import datetime
import os
import csv

# ==========================================
# 1. 画面の設定（スマホ最適化）
# ==========================================
st.set_page_config(page_title="バス混雑度フィードバック", page_icon="🚌", layout="centered")

DATA_FILE = "user_feedback.csv"

# 🌟【決定版】裏技不要！CSSだけで標準ボタンを巨大な3色の正方形カードに変身させる
st.markdown("""
<style>
/* 3つのボタン共通の巨大化・カード化設定 */
div[data-testid="stHorizontalBlock"] button {
    height: 220px !important;    /* 巨大な正方形にする高さ */
    width: 100% !important;
    white-space: pre-wrap !important; /* ボタン内での改行を絶対に許可する */
    font-size: 16px !important;
    font-weight: bold !important;
    border-radius: 20px !important;
    box-shadow: 0 4px 6px rgba(0,0,0,0.1) !important;
    transition: all 0.3s ease !important;
}
/* ボタンに触れたときに少し浮かすアニメーション（直感UI） */
div[data-testid="stHorizontalBlock"] button:hover {
    transform: translateY(-5px) !important;
    box-shadow: 0 8px 15px rgba(0,0,0,0.2) !important;
}

/* 1番目のカラムのボタン（ガラガラ：緑枠線＋薄緑背景） */
div[data-testid="stHorizontalBlock"] > div:nth-child(1) button {
    border: 3px solid #00c853 !important;
    background-color: #f1fbf5 !important;
    color: #333 !important;
}
/* 2番目のカラムのボタン（少し混雑：黄枠線＋薄黄背景） */
div[data-testid="stHorizontalBlock"] > div:nth-child(2) button {
    border: 3px solid #ffd600 !important;
    background-color: #fffdef !important;
    color: #333 !important;
}
/* 3番目のカラムのボタン（大混雑：赤枠線＋薄赤背景） */
div[data-testid="stHorizontalBlock"] > div:nth-child(3) button {
    border: 3px solid #d50000 !important;
    background-color: #fff1f1 !important;
    color: #333 !important;
}
</style>
""", unsafe_allow_html=True)

# ==========================================
# 2. 多言語対応辞書（ボタンの中に直接ピクトグラムを大量配置）
# ==========================================
LANG_DICT = {
    "JA": {
        "title": "🚌 混雑度アンケート",
        "subtitle": "今の車内の様子をタップして教えてください！",
        "btn1_text": "ガラガラ\n\n🟢\n💺 💺 💺\n💺 💺 🧍\n\n🚌",
        "btn2_text": "少し混雑\n\n🟡\n🧍 🧍 🧍\n💺 💺 🧍\n\n🚌",
        "btn3_text": "大混雑\n\n🔴\n🧍🧍🧍\n🧍🧍🧍\n🧍🧍🧍\n\n🚌",
        "success_msg": "ご協力ありがとうございました！🙌",
        "error_msg": "エラーが発生しました。"
    },
    "EN": {
        "title": "🚌 Congestion Survey",
        "subtitle": "Tap the card that matches the current bus!",
        "btn1_text": "Empty\n\n🟢\n💺 💺 💺\n💺 💺 🧍\n\n🚌",
        "btn2_text": "Standing\n\n🟡\n🧍 🧍 🧍\n💺 💺 🧍\n\n🚌",
        "btn3_text": "Crowded\n\n🔴\n🧍🧍🧍\n🧍🧍🧍\n🧍🧍🧍\n\n🚌",
        "success_msg": "Thank you for your cooperation! 🙌",
        "error_msg": "An error occurred."
    }
}

# ==========================================
# 3. 画面レイアウト構築
# ==========================================
selected_lang = st.selectbox("Language / 言語", ["日本語", "English"], label_visibility="collapsed")
lang = "JA" if selected_lang == "日本語" else "EN"

st.title(LANG_DICT[lang]["title"])
st.caption(LANG_DICT[lang]["subtitle"])

# URLパラメータ取得
route_id = st.query_params.get("route_id", "不明(Unknown)")
busstop_id = st.query_params.get("busstop_id", "不明(Unknown)")
st.info(f"📍 Route ID: {route_id} / Busstop ID: {busstop_id}")

st.markdown("---")

# 3つのカラム（列）を横並びに作成
col1, col2, col3 = st.columns(3)
user_class = None

# Streamlit公式のボタン。上記のCSSの力で、巨大な3色のイラストカードに変貌します。
with col1:
    if st.button(LANG_DICT[lang]["btn1_text"], key="btn_class_1", use_container_width=True):
        user_class = 1
with col2:
    if st.button(LANG_DICT[lang]["btn2_text"], key="btn_class_2", use_container_width=True):
        user_class = 2
with col3:
    if st.button(LANG_DICT[lang]["btn3_text"], key="btn_class_3", use_container_width=True):
        user_class = 3

# ==========================================
# 4. 保存処理（変更なし）
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
