import streamlit as st
from datetime import datetime
import os
import csv

# ==========================================
# 1. 画面の設定（スマホ最適化）
# ==========================================
st.set_page_config(page_title="バス混雑度フィードバック", page_icon="🚌", layout="centered")

DATA_FILE = "user_feedback.csv"

# ==========================================
# 2. 視覚的アニメーション＆スタイル（カスタムCSS）
# ==========================================
st.markdown("""
<style>
/* 3つのボタン共通の巨大化・カード化設定 */
div[data-testid="stHorizontalBlock"] button {
    height: 220px !important;    
    width: 100% !important;
    white-space: pre-wrap !important; 
    font-size: 15px !important;
    font-weight: bold !important;
    border-radius: 20px !important;
    box-shadow: 0 4px 6px rgba(0,0,0,0.1) !important;
    transition: all 0.2s ease !important;
}

/* スマホでタップした瞬間にボタンがグッと沈み込む効果（最高の押し心地） */
div[data-testid="stHorizontalBlock"] button:active {
    transform: scale(0.92) !important;   
    box-shadow: 0 2px 4px rgba(0,0,0,0.2) !important;
}

/* 通常時のボタン色（緑、黄、赤） */
div[data-testid="stHorizontalBlock"] > div:nth-child(1) button {
    border: 3px solid #00c853 !important; background-color: #f1fbf5 !important; color: #333 !important;
}
div[data-testid="stHorizontalBlock"] > div:nth-child(2) button {
    border: 3px solid #ffd600 !important; background-color: #fffdef !important; color: #333 !important;
}
div[data-testid="stHorizontalBlock"] > div:nth-child(3) button {
    border: 3px solid #d50000 !important; background-color: #fff1f1 !important; color: #333 !important;
}
</style>
""", unsafe_allow_html=True)

# ==========================================
# 3. 多言語対応辞書（主観補正用の人数帯を追加）
# ==========================================
LANG_DICT = {
    "JA": {
        "title": "🚌 混雑度アンケート",
        "subtitle": "今の車内の様子をタップして教えてください！",
        "birth_year_label": "誕生年 (Birth Year)",
        "birth_month_label": "誕生月 (Birth Month)",
        "optional_section": "📊 【任意協力】もう少し詳しく教えてください",
        "approx_label": "車内の「だいたいの合計人数」は？",
        "approx_default": "選択しない（スキップ）",
        # 🌟 主観補正用の人数帯を明記！
        "btn1_text": "ガラガラ\n[ 0 〜 3人 ]\n\n🟢\n💺 💺 💺\n💺 💺 🧍\n\n🚌",
        "btn2_text": "少し混雑\n[ 4 〜 9人 ]\n\n🟡\n🧍 🧍 🧍\n💺 💺 🧍\n\n🚌",
        "btn3_text": "大混雑\n[ 10人以上 ]\n\n🔴\n🧍🧍🧍\n🧍🧍🧍\n🧍🧍🧍\n\n🚌",
        "success_msg": "ご回答ありがとうございました！🙌"
    },
    "EN": {
        "title": "🚌 Congestion Survey",
        "subtitle": "Tap the card that matches the current bus!",
        "birth_year_label": "Birth Year",
        "birth_month_label": "Birth Month",
        "optional_section": "📊 [Optional] Tell us more details",
        "approx_label": "About how many passengers in total?",
        "approx_default": "Select here (Skip)",
        "btn1_text": "Empty\n[ 0 - 3 ppl ]\n\n🟢\n💺 💺 💺\n💺 💺 🧍\n\n🚌",
        "btn2_text": "Standing\n[ 4 - 9 ppl ]\n\n🟡\n🧍 🧍 🧍\n💺 💺 🧍\n\n🚌",
        "btn3_text": "Crowded\n[ 10+ ppl ]\n\n🔴\n🧍🧍🧍\n🧍🧍🧍\n🧍🧍🧍\n\n🚌",
        "success_msg": "Thank you for your cooperation! 🙌"
    }
}

# 画面構築
selected_lang = st.selectbox("Language / 言語", ["日本語", "English"], label_visibility="collapsed")
lang = "JA" if selected_lang == "日本語" else "EN"

st.title(LANG_DICT[lang]["title"])
st.caption(LANG_DICT[lang]["subtitle"])

# ==========================================
# 4. コメダ/タリーズ方式：属性入力（横並びでスマートに選択）
# ==========================================
current_year = datetime.now().year
year_options = [str(y) for y in range(current_year - 15, current_year - 90, -1)]
month_options = [str(m) for m in range(1, 13)]

col_y, col_m = st.columns(2)
with col_y:
    birth_year = st.selectbox(LANG_DICT[lang]["birth_year_label"], year_options, index=10) # デフォルトで20代半ば付近
with col_m:
    birth_month = st.selectbox(LANG_DICT[lang]["birth_month_label"], month_options, index=0)

# パラメータ取得
route_id = st.query_params.get("route_id", "不明(Unknown)")
busstop_id = st.query_params.get("busstop_id", "不明(Unknown)")
st.info(f"📍 Route: {route_id} / Busstop: {busstop_id}")

st.markdown("---")

# ==========================================
# 5. 【新機能】下部のおおよその人数入力（AI用の宝の山データ）
# ==========================================
st.write(f"### {LANG_DICT[lang]['optional_section']}")
approx_options = [
    LANG_DICT[lang]["approx_default"], 
    "0〜2人", "3〜5人", "6〜10人", "11replace〜15人", "16〜20人", "21〜25人", "26人以上"
]
selected_approx = st.selectbox(LANG_DICT[lang]["approx_label"], approx_options, label_visibility="visible")

st.markdown("---")

# ==========================================
# 6. メインUI：巨大3色ボタンエリア
# ==========================================
col1, col2, col3 = st.columns(3)
pressed_choice = None

with col1:
    if st.button(LANG_DICT[lang]["btn1_text"], key="b1", use_container_width=True): pressed_choice = 1
with col2:
    if st.button(LANG_DICT[lang]["btn2_text"], key="b2", use_container_width=True): pressed_choice = 2
with col3:
    if st.button(LANG_DICT[lang]["btn3_text"], key="b3", use_container_width=True): pressed_choice = 3

# ==========================================
# 7. 保存処理（誕生年月＋詳細人数をCSVに記録）
# ==========================================
if pressed_choice is not None:
    now_ts = int(datetime.now().timestamp())
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    file_exists = os.path.isfile(DATA_FILE)
    
    try:
        with open(DATA_FILE, mode='a', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            if not file_exists:
                # CSVのヘッダーを一新。永続IDを廃止し、birth_year, birth_month, approx_countを記録
                writer.writerow([
                    "timestamp", "datetime", "route_id", "busstop_id", 
                    "user_class", "birth_year", "birth_month", "approx_count"
                ])
            writer.writerow([
                now_ts, now_str, route_id, busstop_id, 
                pressed_choice, birth_year, birth_month, selected_approx
            ])
            
        # 🌟 何度リログされても、連打されても、毎回盛大に風船を飛ばしてUXを最高にする！
        st.balloons()
        st.success(f"### {LANG_DICT[lang]['success_msg']}")
        
    except Exception as e:
        st.error("Save Error")
