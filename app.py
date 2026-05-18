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
# 2. 【神業】LocalStorageを使った永続デバイスIDの自動付与（リログ・QR再読込対策）
# ==========================================
device_id = st.query_params.get("device_id")

if not device_id:
    # URLにdevice_idがない場合、ブラウザのストレージからIDを読み込む（無ければ新規発行）
    # Cross-Originを回避して画面全体をリダイレクトさせるJavaScript
    js_redirect = """
    <script>
    const topUrl = new URL(window.top.location.href);
    if (!topUrl.searchParams.has('device_id')) {
        let devId = localStorage.getItem('bus_device_id');
        if (!devId) {
            devId = 'dev_' + Math.random().toString(36).substring(2, 11);
            localStorage.setItem('bus_device_id', devId);
        }
        topUrl.searchParams.set('device_id', devId);
        window.top.location.href = topUrl.toString();
    }
    </script>
    """
    st.components.v1.html(js_redirect, height=0, width=0)
    st.info("読み込み中... (Loading...)")
    st.stop()

# ==========================================
# 3. 視覚的アニメーション＆スタイル（カスタムCSS）
# ==========================================
st.markdown("""
<style>
/* 3つのボタン共通の巨大化・カード化設定 */
div[data-testid="stHorizontalBlock"] button {
    height: 200px !important;    
    width: 100% !important;
    white-space: pre-wrap !important; 
    font-size: 16px !important;
    font-weight: bold !important;
    border-radius: 20px !important;
    box-shadow: 0 4px 6px rgba(0,0,0,0.1) !important;
    transition: all 0.2s ease !important;
}

/* スマホでタップした瞬間にボタンがグッと沈み込む効果（連打しても楽しい押し心地） */
div[data-testid="stHorizontalBlock"] button:active {
    transform: scale(0.92) !important;   
    box-shadow: 0 2px 4px rgba(0,0,0,0.2) !important;
}

/* 通常時のボタン色（緑、黄、赤）※連打できるように常に活性化 */
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
# 4. 多言語対応辞書
# ==========================================
LANG_DICT = {
    "JA": {
        "title": "🚌 混雑度アンケート",
        "subtitle": "今の車内の様子をタップして教えてください！",
        "btn1_text": "ガラガラ\n\n🟢\n💺 💺 💺\n💺 💺 🧍\n\n🚌",
        "btn2_text": "少し混雑\n\n🟡\n🧍 🧍 🧍\n💺 💺 🧍\n\n🚌",
        "btn3_text": "大混雑\n\n🔴\n🧍🧍🧍\n🧍🧍🧍\n🧍🧍🧍\n\n🚌",
        "success_msg": "ご回答ありがとうございました！🙌",
        "spam_msg": "すでに回答を受け付けています。"
    },
    "EN": {
        "title": "🚌 Congestion Survey",
        "subtitle": "Tap the card that matches the current bus!",
        "btn1_text": "Empty\n\n🟢\n💺 💺 💺\n💺 💺 🧍\n\n🚌",
        "btn2_text": "Standing\n\n🟡\n🧍 🧍 🧍\n💺 💺 🧍\n\n🚌",
        "btn3_text": "Crowded\n\n🔴\n🧍🧍🧍\n🧍🧍🧍\n🧍🧍🧍\n\n🚌",
        "success_msg": "Thank you for your cooperation! 🙌",
        "spam_msg": "We have already received your answer."
    }
}

# 画面構築
selected_lang = st.selectbox("Language / 言語", ["日本語", "English"], label_visibility="collapsed")
lang = "JA" if selected_lang == "日本語" else "EN"

st.title(LANG_DICT[lang]["title"])
st.caption(LANG_DICT[lang]["subtitle"])

# パラメータ取得（裏側で紐づいた永続デバイスIDを表示）
route_id = st.query_params.get("route_id", "不明(Unknown)")
busstop_id = st.query_params.get("busstop_id", "不明(Unknown)")
st.info(f"📍 Route: {route_id} / Busstop: {busstop_id} / 📱 Device: {device_id}")

st.markdown("---")

# ==========================================
# 5. 裏側での30秒判定ロジック（CSVから最新時間をスキャン）
# ==========================================
def get_last_submit_time(dev_id):
    if not os.path.isfile(DATA_FILE):
        return 0
    try:
        with open(DATA_FILE, mode='r', encoding='utf-8') as f:
            reader = csv.reader(f)
            header = next(reader, None)
            if not header or "device_id" not in header:
                return 0
            dev_idx = header.index("device_id")
            ts_idx = header.index("timestamp")
            
            last_ts = 0
            for row in reader:
                if len(row) > max(dev_idx, ts_idx) and row[dev_idx] == dev_id:
                    last_ts = max(last_ts, int(row[ts_idx]))
            return last_ts
    except:
        return 0

def save_feedback(user_choice, dev_id):
    now_ts = int(datetime.now().timestamp())
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    file_exists = os.path.isfile(DATA_FILE)
    try:
        with open(DATA_FILE, mode='a', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            if not file_exists:
                writer.writerow(["timestamp", "datetime", "route_id", "busstop_id", "user_class", "device_id"])
            writer.writerow([now_ts, now_str, route_id, busstop_id, user_choice, dev_id])
    except Exception as e:
        st.error("Save Error")

# ==========================================
# 6. メインUI：巨大ボタンエリア（連打可能）
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
# 7. ボタンが押されたときのアクション判定
# ==========================================
if pressed_choice is not None:
    current_ts = int(datetime.now().timestamp())
    last_ts = get_last_submit_time(device_id)
    
    # 30秒以内に同じデバイスから再度押されたか判定
    if current_ts - last_ts < 30:
        # 【30秒以内の連打】
        st.session_state.submit_status = "spam"
        # データ集計時に最終行（最新）を有効化するため、CSVには追記を許可する設計
        save_feedback(pressed_choice, device_id)
    else:
        # 【初回、または30秒以上経過した新規回答】
        st.session_state.submit_status = "success"
        save_feedback(pressed_choice, device_id)

# ==========================================
# 8. 結果の動的出力（プログレスバーは完全撤廃、超軽量）
# ==========================================
if "submit_status" in st.session_state:
    st.markdown("---")
    if st.session_state.submit_status == "success":
        # 🌟 風船演出をそのまま完全維持！
        st.balloons()
        # 🌟 文言を元の「ご回答ありがとうございました！」に復旧
        st.success(f"### {LANG_DICT[lang]['success_msg']}")
    elif st.session_state.submit_status == "spam":
        # 🌟 連打時は風船を出さず、デカデカと警告を表示
        st.error(f"## ⚠️ {LANG_DICT[lang]['spam_msg']}")
