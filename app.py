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
# 2. 多言語対応辞書（視覚表現を強化）
# ==========================================
LANG_DICT = {
    "JA": {
        "title": "🚌 混雑度アンケート",
        "subtitle": "今の車内の様子をタップして教えてください！",
        "class1_name": "ガラガラ",
        "class2_name": "少し混雑",
        "class3_name": "大混雑",
        "success_msg": "ご協力ありがとうございました！🙌",
        "error_msg": "エラーが発生しました。"
    },
    "EN": {
        "title": "🚌 Congestion Survey",
        "subtitle": "Tap the card that matches the current bus!",
        "class1_name": "Empty",
        "class2_name": "Standing",
        "class3_name": "Crowded",
        "success_msg": "Thank you for your cooperation! 🙌",
        "error_msg": "An error occurred."
    }
}

# ==========================================
# 3. 画面レイアウト構築
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

# 🌟【ここが肝】巨大な正方形カード型ボタンを実現するHTML/CSS
# 各クラスに合わせて人の絵文字の数を調整
icon_class1 = "🟢<br><span style='font-size:35px;'>💺💺💺<br>💺💺🧍</span>" # 空席多数、人1人
icon_class2 = "🟡<br><span style='font-size:35px;'>🧍🧍🧍<br>💺💺🧍</span>" # 立ち数人、空席減る
icon_class3 = "🔴<br><span style='font-size:35px;'>🧍🧍🧍🧍<br>🧍🧍🧍🧍<br>🧍🧍🧍🧍</span>" # ギッシリ

html_card_template = """
<style>
/* カード（ボタン）の全体デザイン */
.congest-card {{
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: space-between;
    height: 180px;              /* 巨大な正方形の高さ */
    border: 3px solid #ddd;     /* 太めの枠線 */
    border-radius: 20px;        /* 角丸 */
    padding: 15px;
    margin: 5px;
    text-align: center;
    cursor: pointer;            /* カーソルを指マークに */
    transition: all 0.3s ease;  /* アニメーション */
    box-shadow: 0 4px 6px rgba(0,0,0,0.1); /* 影 */
    background-color: white;
}}
/* タップ・ホップ時の視覚効果 */
.congest-card:hover {{
    transform: translateY(-5px); /* 少し浮く */
    box-shadow: 0 8px 15px rgba(0,0,0,0.2);
}}
/* クラスご用の枠線色 */
.card-1 {{ border-color: #00c853; background-color: #f1fbf5; }} /* 緑 */
.card-2 {{ border-color: #ffd600; background-color: #fffdef; }} /* 黄 */
.card-3 {{ border-color: #d50000; background-color: #fff1f1; }} /* 赤 */

.card-title {{ font-size: 18px; font-weight: bold; color: #333; margin-top: 5px; }}
.card-icons {{ font-size: 20px; line-height: 1.2; flex-grow: 1; display: flex; align-items: center; justify-content: center; }}
.card-bus {{ font-size: 24px; margin-bottom: 5px; }}
</style>

<div style="display: flex; justify-content: space-between;">
    <div class="congest-card card-1" onclick="document.getElementById('hidden_btn_1').click();">
        <div class="card-title">{title1}</div>
        <div class="card-icons">{icons1}</div>
        <div class="card-bus">🚌</div>
    </div>
    <div class="congest-card card-2" onclick="document.getElementById('hidden_btn_2').click();">
        <div class="card-title">{title2}</div>
        <div class="card-icons">{icons2}</div>
        <div class="card-bus">🚌</div>
    </div>
    <div class="congest-card card-3" onclick="document.getElementById('hidden_btn_3').click();">
        <div class="card-title">{title3}</div>
        <div class="card-icons">{icons3}</div>
        <div class="card-bus">🚌</div>
    </div>
</div>
"""

# HTMLを描画
st.markdown(html_card_template.format(
    title1=LANG_DICT[lang]["class1_name"], icons1=icon_class1,
    title2=LANG_DICT[lang]["class2_name"], icons2=icon_class2,
    title3=LANG_DICT[lang]["class3_name"], icons3=icon_class3
), unsafe_allow_html=True)

# 🌟【裏技】HTMLカードのクリックをStreamlitに伝えるための「隠しボタン」
# CSSで画面外に吹き飛ばして見えなくしている
st.markdown("""<style>div[data-testid="stHidden"] { display: none; }</style>""", unsafe_allow_html=True)
user_class = None
with st.container(data_testid="stHidden"):
    if st.button("hidden1", key="hidden_btn_1"): user_class = 1
    if st.button("hidden2", key="hidden_btn_2"): user_class = 2
    if st.button("hidden3", key="hidden_btn_3"): user_class = 3


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
