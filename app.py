import streamlit as st
from datetime import datetime
import os
import csv
import time
import uuid

# ==========================================
# 1. 画面の設定とセッション状態の初期化
# ==========================================
st.set_page_config(page_title="バス混雑度フィードバック", page_icon="🚌", layout="centered")

DATA_FILE = "user_feedback.csv"

# デバイス（ブラウザセッション）を一意に識別するIDを発行
if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())[:8] # 短い一意のID

# 選択状態やタイマーの状態を管理
if "selected_class" not in st.session_state:
    st.session_state.selected_class = None
if "last_submit_time" not in st.session_state:
    st.session_state.last_submit_time = 0.0
if "cooldown_active" not in st.session_state:
    st.session_state.cooldown_active = False

# ==========================================
# 2. 視覚的アニメーション＆スタイル（カスタムCSS）
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
    transition: all 0.2s ease !important; /* アニメーション速度 */
}

/* 🔥【新機能】スマホでタップした瞬間にボタンがグッと沈み込む（縮小する）効果 */
div[data-testid="stHorizontalBlock"] button:active {
    transform: scale(0.92) !important;   /* 8%縮む */
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
# 3. 多言語対応辞書
# ==========================================
LANG_DICT = {
    "JA": {
        "title": "🚌 混雑度アンケート",
        "subtitle": "今の車内の様子をタップして教えてください！",
        "btn1_text": "ガラガラ\n\n🟢\n💺 💺 💺\n💺 💺 🧍\n\n🚌",
        "btn2_text": "少し混雑\n\n🟡\n🧍 🧍 🧍\n💺 💺 🧍\n\n🚌",
        "btn3_text": "大混雑\n\n🔴\n🧍🧍🧍\n🧍🧍🧍\n🧍🧍🧍\n\n🚌",
        "status_title": "【現在選択中】",
        "class1_name": "🟢 ガラガラ (Empty)",
        "class2_name": "🟡 少し混雑 (Standing)",
        "class3_name": "🔴 大混雑 (Crowded)",
        "correction_btn": "↩️ 間違えたので回答を訂正する！",
        "cooldown_msg": "⚠️ 連続送信はできません。30秒間ロックされます...",
        "success_msg": "ご協力ありがとうございました！🙌"
    },
    "EN": {
        "title": "🚌 Congestion Survey",
        "subtitle": "Tap the card that matches the current bus!",
        "btn1_text": "Empty\n\n🟢\n💺 💺 💺\n💺 💺 🧍\n\n🚌",
        "btn2_text": "Standing\n\n🟡\n🧍 🧍 🧍\n💺 💺 🧍\n\n🚌",
        "btn3_text": "Crowded\n\n🔴\n🧍🧍🧍\n🧍🧍🧍\n🧍🧍🧍\n\n🚌",
        "status_title": "[Current Selection]",
        "class1_name": "🟢 Empty",
        "class2_name": "🟡 Standing",
        "class3_name": "🔴 Crowded",
        "correction_btn": "↩️ Correct my answer!",
        "cooldown_msg": "⚠️ Anti-spam lock active for 30 seconds...",
        "success_msg": "Thank you for your cooperation! 🙌"
    }
}

# 画面構築
selected_lang = st.selectbox("Language / 言語", ["日本語", "English"], label_visibility="collapsed")
lang = "JA" if selected_lang == "日本語" else "EN"

st.title(LANG_DICT[lang]["title"])
st.caption(LANG_DICT[lang]["subtitle"])

# パラメータ取得
route_id = st.query_params.get("route_id", "不明(Unknown)")
busstop_id = st.query_params.get("busstop_id", "不明(Unknown)")
st.info(f"📍 Route ID: {route_id} / Busstop ID: {busstop_id} / 📱 User: {st.session_state.session_id}")

st.markdown("---")

# ==========================================
# 4. CSVデータ書き込み関数（セッションID付き）
# ==========================================
def save_feedback(user_choice):
    now_ts = int(datetime.now().timestamp())
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    file_exists = os.path.isfile(DATA_FILE)
    try:
        with open(DATA_FILE, mode='a', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            if not file_exists:
                # 🌟 末尾に session_id を追加
                writer.writerow(["timestamp", "datetime", "route_id", "busstop_id", "user_class", "session_id"])
            writer.writerow([now_ts, now_str, route_id, busstop_id, user_choice, st.session_state.session_id])
    except Exception as e:
        st.error("Save Error")

# ==========================================
# 5. メインUI：巨大ボタンエリア
# ==========================================
col1, col2, col3 = st.columns(3)

# 30秒のクールダウン中、またはすでに選択済みの場合はボタンを無効化（disabled）する
is_disabled = st.session_state.cooldown_active

with col1:
    if st.button(LANG_DICT[lang]["btn1_text"], key="b1", use_container_width=True, disabled=is_disabled):
        st.session_state.selected_class = 1
        st.session_state.last_submit_time = time.time()
        st.session_state.cooldown_active = True
        save_feedback(1)
        st.rerun()

with col2:
    if st.button(LANG_DICT[lang]["btn2_text"], key="b2", use_container_width=True, disabled=is_disabled):
        st.session_state.selected_class = 2
        st.session_state.last_submit_time = time.time()
        st.session_state.cooldown_active = True
        save_feedback(2)
        st.rerun()

with col3:
    if st.button(LANG_DICT[lang]["btn3_text"], key="b3", use_container_width=True, disabled=is_disabled):
        st.session_state.selected_class = 3
        st.session_state.last_submit_time = time.time()
        st.session_state.cooldown_active = True
        save_feedback(3)
        st.rerun()

# ==========================================
# 6. 【新機能】選択状態表示 ＆ 訂正・30秒制限ロジック
# ==========================================
if st.session_state.selected_class is not None:
    st.markdown("---")
    
    # 選択したクラスの名前に変換
    c_name = ""
    if st.session_state.selected_class == 1: c_name = LANG_DICT[lang]["class1_name"]
    elif st.session_state.selected_class == 2: c_name = LANG_DICT[lang]["class2_name"]
    elif st.session_state.selected_class == 3: c_name = LANG_DICT[lang]["class3_name"]
    
    # 🌟 選択した回答を画面上にデカデカと固定表示（安心感UI）
    st.success(f"### {LANG_DICT[lang]['status_title']}\n## {c_name}")
    
    # クールダウンタイマーの計算
    elapsed_time = time.time() - st.session_state.last_submit_time
    remaining_time = 30 - int(elapsed_time)
    
    if remaining_time > 0 and st.session_state.cooldown_active:
        # 🌟 「訂正する！」ボタンを配置（赤色の警告色ボタン）
        # これが押されると、再度ボタンが押せるようになり、最新の選択がCSVに追記されます
        if st.button(LANG_DICT[lang]["correction_btn"], type="primary", use_container_width=True):
            st.session_state.cooldown_active = False
            st.session_state.selected_class = None
            st.balloons() # 訂正受付の演出
            st.rerun()
            
        # 🌟 30秒のビジュアルカウントダウンタイマー
        st.warning(LANG_DICT[lang]["cooldown_msg"])
        progress_bar = st.progress(max(0, min(100, int((remaining_time / 30) * 100))))
        st.write(f"⏱️ あと {remaining_time} 秒 (Seconds remaining...)")
        
        # 1秒ごとに画面を強制リロードしてタイマーを進める
        time.sleep(1.0)
        st.rerun()
    else:
        # 30秒経過したら、自動的に完全完了モードへ
        st.session_state.cooldown_active = False
        st.info(LANG_DICT[lang]["success_msg"])
