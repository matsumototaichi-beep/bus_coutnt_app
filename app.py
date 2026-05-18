import streamlit as st
from datetime import datetime
import os
import csv

# ==========================================
# 1. 画面の設定（スマホ最適化）
# ==========================================
st.set_page_config(page_title="バス混雑度フィードバック", page_icon="🚌", layout="centered")

DATA_FILE = "user_feedback.csv"

# セッション状態の初期化（ページ遷移・選択状態の管理）
if "step" not in st.session_state:
    st.session_state.step = 1
if "selected_choice" not in st.session_state:
    st.session_state.selected_choice = None
if "approx_val" not in st.session_state:
    st.session_state.approx_val = None
if "trigger_balloons" not in st.session_state:
    st.session_state.trigger_balloons = False
if "birth_year" not in st.session_state:
    st.session_state.birth_year = None
if "birth_month" not in st.session_state:
    st.session_state.birth_month = None

# ==========================================
# 2. 多言語対応辞書（主観補正の人数帯をボタン文字に内包）
# ==========================================
LANG_DICT = {
    "JA": {
        "title": "🚌 混雑度アンケート",
        "subtitle": "今の車内の様子を教えてください！",
        "birth_year_label": "誕生年 (Birth Year)",
        "birth_month_label": "誕生月 (Birth Month)",
        "next_btn": "アンケート画面へ進む ➡️",
        "btn1_text": "ガラガラ\n[ 0〜3人 ]\n\n🟢\n💺 💺 💺\n💺 💺 🧍\n\n🚌",
        "btn2_text": "少し混雑\n[ 4〜9人 ]\n\n🟡\n🧍 🧍 🧍\n💺 💺 🧍\n\n🚌",
        "btn3_text": "大混雑\n[ 10人以上 ]\n\n🔴\n🧍🧍🧍\n🧍🧍🧍\n🧍🧍🧍\n\n🚌",
        "optional_section": "📊 【任意協力】もう少し詳しく教えてください",
        "approx_label": "車内の「だいたいの合計人数」は？",
        "approx_default": "選択しない（スキップ）",
        "success_msg": "ご協力ありがとうございました！🙌",
        "error_msg": "エラーが発生しました。"
    },
    "EN": {
        "title": "🚌 Congestion Survey",
        "subtitle": "Please tell us about the current bus!",
        "birth_year_label": "Birth Year",
        "birth_month_label": "Birth Month",
        "next_btn": "Go to Survey ➡️",
        "btn1_text": "Empty\n[ 0 - 3 ppl ]\n\n🟢\n💺 💺 💺\n💺 💺 🧍\n\n🚌",
        "btn2_text": "Standing\n[ 4 - 9 ppl ]\n\n🟡\n🧍 🧍 🧍\n💺 💺 🧍\n\n🚌",
        "btn3_text": "Crowded\n[ 10+ ppl ]\n\n🔴\n🧍🧍🧍\n🧍🧍🧍\n🧍🧍🧍\n\n🚌",
        "optional_section": "📊 [Optional] Tell us more details",
        "approx_label": "About how many passengers in total?",
        "approx_default": "Select here (Skip)",
        "success_msg": "Thank you for your cooperation! 🙌",
        "error_msg": "An error occurred."
    }
}

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

# CSVデータ保存関数
def save_feedback(user_choice, approx_count):
    if user_choice is None:
        return
    now_ts = int(datetime.now().timestamp())
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    file_exists = os.path.isfile(DATA_FILE)
    try:
        with open(DATA_FILE, mode='a', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            if not file_exists:
                writer.writerow(["timestamp", "datetime", "route_id", "busstop_id", "user_class", "birth_year", "birth_month", "approx_count"])
            writer.writerow([
                now_ts, now_str, route_id, busstop_id, user_choice, 
                st.session_state.birth_year, st.session_state.birth_month, approx_count
            ])
    except Exception as e:
        st.error(LANG_DICT[lang]["error_msg"])

# ==========================================
# 3. 【画面遷移】ステップ1：誕生年月の入力画面（コメダ方式）
# ==========================================
if st.session_state.step == 1:
    current_year = datetime.now().year
    year_options = [str(y) for y in range(current_year - 15, current_year - 90, -1)]
    month_options = [str(m) for m in range(1, 13)]
    
    col_y, col_m = st.columns(2)
    with col_y:
        birth_year_sel = st.selectbox(LANG_DICT[lang]["birth_year_label"], year_options, index=10) # デフォルト20代
    with col_m:
        birth_month_sel = st.selectbox(LANG_DICT[lang]["birth_month_label"], month_options, index=0)
        
    st.markdown("<br>", unsafe_allow_html=True)
    if st.button(LANG_DICT[lang]["next_btn"], use_container_width=True, type="primary"):
        st.session_state.birth_year = birth_year_sel
        st.session_state.birth_month = birth_month_sel
        st.session_state.step = 2
        st.rerun()

# ==========================================
# 4. 【画面遷移】ステップ2：アンケート本体画面（スクロールゼロ）
# ==========================================
elif st.session_state.step == 2:
    
    # 🌟 動的CSSの構築：選択されたボタンだけハイライト（枠線が太くなり、少し浮き出る）する
    sel = st.session_state.selected_choice
    highlight_css = ""
    if sel == 1:
        highlight_css = "div[data-testid='stHorizontalBlock'] > div:nth-child(1) button { border-width: 6px !important; box-shadow: 0 0 15px rgba(0,0,0,0.4) !important; transform: scale(1.04) !important; }"
    elif sel == 2:
        highlight_css = "div[data-testid='stHorizontalBlock'] > div:nth-child(2) button { border-width: 6px !important; box-shadow: 0 0 15px rgba(0,0,0,0.4) !important; transform: scale(1.04) !important; }"
    elif sel == 3:
        highlight_css = "div[data-testid='stHorizontalBlock'] > div:nth-child(3) button { border-width: 6px !important; box-shadow: 0 0 15px rgba(0,0,0,0.4) !important; transform: scale(1.04) !important; }"

    # Streamlit標準ボタンを巨大カード化するCSS + 動的ハイライト
    st.markdown(f"""
    <style>
    /* 3つのボタン共通の巨大化・カード化設定 */
    div[data-testid="stHorizontalBlock"] button {{
        height: 230px !important;    
        width: 100% !important;
        white-space: pre-wrap !important; 
        font-size: 15px !important;
        font-weight: bold !important;
        border-radius: 20px !important;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1) !important;
        transition: all 0.2s ease !important;
    }}
    /* スマホでタップした瞬間にボタンがグッと沈み込む効果（物理的な押し心地） */
    div[data-testid="stHorizontalBlock"] button:active {{
        transform: scale(0.92) !important;   
        box-shadow: 0 2px 4px rgba(0,0,0,0.2) !important;
    }}
    /* 通常時のボタン色（緑、黄、赤） */
    div[data-testid="stHorizontalBlock"] > div:nth-child(1) button {{
        border: 3px solid #00c853 !important; background-color: #f1fbf5 !important; color: #333 !important;
    }}
    div[data-testid="stHorizontalBlock"] > div:nth-child(2) button {{
        border: 3px solid #ffd600 !important; background-color: #fffdef !important; color: #333 !important;
    }}
    div[data-testid="stHorizontalBlock"] > div:nth-child(3) button {{
        border: 3px solid #d50000 !important; background-color: #fff1f1 !important; color: #333 !important;
    }}
    
    /* 選択状態のハイライト適用 */
    {highlight_css}
    </style>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)
    pressed_choice = None

    with col1:
        if st.button(LANG_DICT[lang]["btn1_text"], key="b1", use_container_width=True): pressed_choice = 1
    with col2:
        if st.button(LANG_DICT[lang]["btn2_text"], key="b2", use_container_width=True): pressed_choice = 2
    with col3:
        if st.button(LANG_DICT[lang]["btn3_text"], key="b3", use_container_width=True): pressed_choice = 3

    # 巨大ボタンが押された時の処理（押し直し・修正時もここを通る）
    if pressed_choice is not None:
        st.session_state.selected_choice = pressed_choice
        # すでに選ばれている任意の値があればそれを引き継ぎ、無ければデフォルトで即CSV保存
        current_approx = st.session_state.approx_val if st.session_state.approx_val else LANG_DICT[lang]["approx_default"]
        save_feedback(pressed_choice, current_approx)
        st.session_state.trigger_balloons = True # 風船フラグをセット
        st.rerun()

    # 風船と成功メッセージの動的描画（ハイライトが適用された後に飛ぶように制御）
    if st.session_state.trigger_balloons:
        st.balloons()
        st.success(LANG_DICT[lang]["success_msg"])
        st.session_state.trigger_balloons = False

    # 🌟【新機能】任意報告の欄をボタンの下に配置（ボタンを押した後に初めて出現！）
    if st.session_state.selected_choice is not None:
        st.markdown("<br>", unsafe_allow_html=True)
        st.write(f"### {LANG_DICT[lang]['optional_section']}")
        approx_options = [
            LANG_DICT[lang]["approx_default"], 
            "0〜2人", "3〜5人", "6〜10人", "11〜15人", "16〜20人", "21〜25人", "26人以上"
        ]
        
        default_idx = 0
        if st.session_state.approx_val in approx_options:
            default_idx = approx_options.index(st.session_state.approx_val)
            
        selected_approx = st.selectbox(
            LANG_DICT[lang]["approx_label"], 
            approx_options, 
            index=default_idx,
            key="approx_selectbox"
        )
        
        # 任意項目の選択が変更されたら、トースト通知を出しつつ、最新状態でCSVに再追記
        if st.session_state.approx_val != selected_approx:
            st.session_state.approx_val = selected_approx
            if selected_approx != LANG_DICT[lang]["approx_default"]:
                save_feedback(st.session_state.selected_choice, selected_approx)
                st.toast("詳細な人数データを記録しました！ 📊")
