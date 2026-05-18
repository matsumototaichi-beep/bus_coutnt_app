import streamlit as st
from datetime import datetime
import os
import csv

# ==========================================
# 1. 画面の設定（スマホ最適化）
# ==========================================
st.set_page_config(page_title="バス混雑度フィードバック", page_icon="🚌", layout="centered")

DATA_FILE = "user_feedback.csv"

# セッション状態の初期化（4つのページ遷移・選択状態の完全管理）
if "step" not in st.session_state:
    st.session_state.step = 1
if "selected_choice" not in st.session_state:
    st.session_state.selected_choice = None
if "approx_val" not in st.session_state:
    st.session_state.approx_val = None
if "birth_year" not in st.session_state:
    st.session_state.birth_year = None
if "birth_month" not in st.session_state:
    st.session_state.birth_month = None

# ==========================================
# 2. プルダウンメニュー（selectbox）の巨大化＆丸み（角丸）CSS
# ==========================================
selectbox_css = """
<style>
/* セレクトボックスの枠線を大きく、丸みを帯びさせる */
div[data-testid="stSelectbox"] div[data-baseweb="select"] {
    border-radius: 16px !important;
}
div[data-testid="stSelectbox"] [data-baseweb="select"] > div {
    border-radius: 16px !important;
    min-height: 58px !important; /* スマホでタップしやすい圧倒的な高さ */
    font-size: 18px !important;   /* 文字を大きくして視認性向上 */
    display: flex;
    align-items: center;
}
/* 入力項目のラベルタイトルも太く大きく */
div[data-testid="stSelectbox"] label p {
    font-size: 16px !important;
    font-weight: bold !important;
    color: #333 !important;
}
/* 通常のボタンもすべて丸みを帯びさせる */
div.stButton > button {
    border-radius: 16px !important;
    font-size: 18px !important;
    min-height: 50px !important;
}
</style>
"""
st.markdown(selectbox_css, unsafe_allow_html=True)

# ==========================================
# 3. 多言語対応辞書（Step 3 & 4 の新規文言を追加）
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
        "step3_title": "🎉 ご回答ありがとうございます！",
        "step3_sub": "このページを閉じてもらって構いません。",
        "step3_label": "🔢 【任意協力】正確な乗車人数を教えてください",
        "step3_default": "選択しない（ここで終了）",
        "step3_btn": "💥 人数を確定して送信する",
        "step3_fix_btn": "⬅️ 混雑度の回答を修正する",
        "step4_title": "🙌 ご協力ありがとうございました！",
        "step4_sub": "詳細な人数データを記録しました。<br>ブラウザを閉じて大丈夫です。",
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
        "step3_title": "🎉 Thank you for your answer!",
        "step3_sub": "You can close this browser now.",
        "step3_label": "🔢 [Optional] Please tell us the exact passenger count",
        "step3_default": "Skip (Finish here)",
        "step3_btn": "💥 Confirm & Submit Number",
        "step3_fix_btn": "⬅️ Fix Congestion Answer",
        "step4_title": "🙌 Thank you for your cooperation!",
        "step4_sub": "Detailed passenger data recorded.<br>You can close the browser.",
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
# 4. 【画面遷移】ステップ1：誕生年月入力（丸型巨大プルダウン）
# ==========================================
if st.session_state.step == 1:
    current_year = datetime.now().year
    year_options = [str(y) for y in range(current_year - 15, current_year - 90, -1)]
    month_options = [str(m) for m in range(1, 13)]
    
    col_y, col_m = st.columns(2)
    with col_y:
        birth_year_sel = st.selectbox(LANG_DICT[lang]["birth_year_label"], year_options, index=10)
    with col_m:
        birth_month_sel = st.selectbox(LANG_DICT[lang]["birth_month_label"], month_options, index=0)
        
    st.markdown("<br>", unsafe_allow_html=True)
    if st.button(LANG_DICT[lang]["next_btn"], use_container_width=True, type="primary"):
        st.session_state.birth_year = birth_year_sel
        st.session_state.birth_month = birth_month_sel
        st.session_state.step = 2
        st.rerun()

# ==========================================
# 5. 【画面遷移】ステップ2：アンケート本体（3巨大ボタン＋ノンバーバルハイライト）
# ==========================================
elif st.session_state.step == 2:
    sel = st.session_state.selected_choice
    highlight_css = ""
    if sel == 1:
        highlight_css = "div[data-testid='stHorizontalBlock'] > div:nth-child(1) button { border-width: 6px !important; box-shadow: 0 0 15px rgba(0,0,0,0.4) !important; transform: scale(1.04) !important; }"
    elif sel == 2:
        highlight_css = "div[data-testid='stHorizontalBlock'] > div:nth-child(2) button { border-width: 6px !important; box-shadow: 0 0 15px rgba(0,0,0,0.4) !important; transform: scale(1.04) !important; }"
    elif sel == 3:
        highlight_css = "div[data-testid='stHorizontalBlock'] > div:nth-child(3) button { border-width: 6px !important; box-shadow: 0 0 15px rgba(0,0,0,0.4) !important; transform: scale(1.04) !important; }"

    base_btn_css = """
    <style>
    div[data-testid="stHorizontalBlock"] button {
        height: 230px !important;    
        width: 100% !important;
        white-space: pre-wrap !important; 
        font-size: 15px !important;
        font-weight: bold !important;
        border-radius: 20px !important;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1) !important;
        transition: all 0.2s ease !important;
    }
    div[data-testid="stHorizontalBlock"] button:active {
        transform: scale(0.92) !important;   
        box-shadow: 0 2px 4px rgba(0,0,0,0.2) !important;
    }
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
    """
    st.markdown(base_btn_css, unsafe_allow_html=True)
    if highlight_css:
        st.markdown(f"<style>{highlight_css}</style>", unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)
    pressed_choice = None

    with col1:
        if st.button(LANG_DICT[lang]["btn1_text"], key="b1", use_container_width=True): pressed_choice = 1
    with col2:
        if st.button(LANG_DICT[lang]["btn2_text"], key="b2", use_container_width=True): pressed_choice = 2
    with col3:
        if st.button(LANG_DICT[lang]["btn3_text"], key="b3", use_container_width=True): pressed_choice = 3

    if pressed_choice is not None:
        st.session_state.selected_choice = pressed_choice
        # まずは基本の混雑度だけで即時CSV保存（離脱対策）
        save_feedback(pressed_choice, LANG_DICT[lang]["step3_default"])
        # ボタンを押したら即座に「ステップ3」へ進む
        st.session_state.step = 3
        st.rerun()

# ==========================================
# 6. 【画面遷移】ステップ3：中央配置の受付完了 ＆ 1〜40人詳細入力ページ
# ==========================================
elif st.session_state.step == 3:
    # 🌟 "ご回答ありがとうございます!" を中央に綺麗に配置
    st.markdown(f"""
    <div style="text-align: center; margin-top: 10px; margin-bottom: 25px;">
        <h2 style="color: #333; font-weight: bold;">{LANG_DICT[lang]["step3_title"]}</h2>
        <p style="color: #666; font-size: 15px;">{LANG_DICT[lang]["step3_sub"]}</p>
    </div>
    """, unsafe_allow_html=True)
    
    # 🌟 1〜"40人以上" のプルダウンメニューを動的生成
    suffix = "人" if lang == "JA" else " ppl"
    max_suffix = "40人以上" if lang == "JA" else "40+ ppl"
    
    approx_options = [LANG_DICT[lang]["step3_default"]] + [f"{i}{suffix}" for i in range(1, 40)] + [max_suffix]
    
    default_idx = 0
    if st.session_state.approx_val in approx_options:
        default_idx = approx_options.index(st.session_state.approx_val)
        
    selected_approx = st.selectbox(
        LANG_DICT[lang]["step3_label"], 
        approx_options, 
        index=default_idx
    )
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # 🌟 人数確定ボタン
    if st.button(LANG_DICT[lang]["step3_btn"], use_container_width=True, type="primary"):
        st.session_state.approx_val = selected_approx
        # 詳細人数を伴ってCSVに最新データを追記保存
        save_feedback(st.session_state.selected_choice, selected_approx)
        # 最終ページ（ステップ4）へ
        st.session_state.step = 4
        st.rerun()
        
    # 🌟 回答修正リンク（目立たないように下部に配置し、前画面に戻れるコメダ親切設計）
    st.markdown("<br><br><br><hr style='border-top: 1px dashed #ccc;'><br>", unsafe_allow_html=True)
    if st.button(LANG_DICT[lang]["step3_fix_btn"], use_container_width=True):
        st.session_state.step = 2
        st.rerun()

# ==========================================
# 7. 【画面遷移】ステップ4：最終お礼ページ（ここでドカンと風船演出🎈）
# ==========================================
elif st.session_state.step == 4:
    # 盛大に風船を飛ばして協力を称える
    st.balloons()
    
    st.markdown(f"""
    <div style="text-align: center; margin-top: 60px;">
        <h1 style="color: #00c853; font-size: 36px; font-weight: bold; margin-bottom: 25px;">
            {LANG_DICT[lang]["step4_title"]}
        </h1>
        <p style="color: #555; font-size: 18px; line-height: 1.6;">
            {LANG_DICT[lang]["step4_sub"]}
        </p>
    </div>
    """, unsafe_allow_html=True)
