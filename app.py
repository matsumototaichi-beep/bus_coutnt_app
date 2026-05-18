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

# ==========================================
# 2. 多言語対応辞書（主観補正の人数帯をカード内に内包）
# ==========================================
LANG_DICT = {
    "JA": {
        "title": "🚌 混雑度アンケート",
        "subtitle": "今の車内の様子を教えてください！",
        "birth_year_label": "誕生年 (Birth Year)",
        "birth_month_label": "誕生月 (Birth Month)",
        "next_btn": "アンケート画面へ進む ➡️",
        # 🌟 主観を補正するための「想定人数帯」をデザインの一部としてタイトルに埋め込み
        "class1_name": "ガラガラ<br><span style='font-size:11px; font-weight:normal; color:#666;'>[ 0〜3人 ]</span>",
        "class2_name": "少し混雑<br><span style='font-size:11px; font-weight:normal; color:#666;'>[ 4〜9人 ]</span>",
        "class3_name": "大混雑<br><span style='font-size:11px; font-weight:normal; color:#666;'>[ 10人以上 ]</span>",
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
        "class1_name": "Empty<br><span style='font-size:11px; font-weight:normal; color:#666;'>[ 0 - 3 ppl ]</span>",
        "class2_name": "Standing<br><span style='font-size:11px; font-weight:normal; color:#666;'>[ 4 - 9 ppl ]</span>",
        "class3_name": "Crowded<br><span style='font-size:11px; font-weight:normal; color:#666;'>[ 10+ ppl ]</span>",
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
    # アイコンの定義
    icon_class1 = "🟢<br><span style='font-size:30px;'>💺💺💺<br>💺💺🧍</span>"
    icon_class2 = "🟡<br><span style='font-size:30px;'>🧍🧍🧍<br>💺💺🧍</span>"
    icon_class3 = "🔴<br><span style='font-size:30px;'>🧍🧍🧍🧍<br>🧍🧍🧍🧍<br>🧍🧍🧍🧍</span>"

    # 選択状態（ハイライト）のCSSクラス動的判定
    sel = st.session_state.selected_choice
    h_class1 = " selected-card" if sel == 1 else ""
    h_class2 = " selected-card" if sel == 2 else ""
    h_class3 = " selected-card" if sel == 3 else ""

    html_card_template = f"""
    <style>
    /* カード（ボタン）の全体デザイン */
    .congest-card {{
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: space-between;
        height: 190px;
        width: 31%;                 /* スマホで3列綺麗に並べるための幅固定 */
        border: 3px solid #ddd;
        border-radius: 20px;
        padding: 10px;
        text-align: center;
        cursor: pointer;
        transition: all 0.2s ease;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        background-color: white;
    }}
    /* タップ時の凹むアニメーション（物理的な押し心地） */
    .congest-card:active {{
        transform: scale(0.93) !important;
        box-shadow: 0 2px 4px rgba(0,0,0,0.2) !important;
    }}
    .card-1 {{ border-color: #00c853; background-color: #f1fbf5; }}
    .card-2 {{ border-color: #ffd600; background-color: #fffdef; }}
    .card-3 {{ border-color: #d50000; background-color: #fff1f1; }}

    /* 🔥【新機能】文字を一切使わない、デザイン（太枠・拡大・強シャドウ）だけのハイライト効果 */
    .selected-card {{
        border-width: 6px !important;
        box-shadow: 0 0 15px rgba(0,0,0,0.4) !important;
        transform: scale(1.04);
    }}

    .card-title {{ font-size: 14px; font-weight: bold; color: #333; margin-top: 5px; line-height: 1.3; }}
    .card-icons {{ font-size: 18px; line-height: 1.2; flex-grow: 1; display: flex; align-items: center; justify-content: center; }}
    .card-bus {{ font-size: 20px; margin-bottom: 5px; }}
    </style>

    <div style="display: flex; justify-content: space-between; width: 100%;">
        <div class="congest-card card-1{h_class1}" onclick="document.getElementById('hidden_btn_1').click();">
            <div class="card-title">{{title1}}</div>
            <div class="card-icons">{{icons1}}</div>
            <div class="card-bus">🚌</div>
        </div>
        <div class="congest-card card-2{h_class2}" onclick="document.getElementById('hidden_btn_2').click();">
            <div class="card-title">{{title2}}</div>
            <div class="card-icons">{{icons2}}</div>
            <div class="card-bus">🚌</div>
        </div>
        <div class="congest-card card-3{h_class3}" onclick="document.getElementById('hidden_btn_3').click();">
            <div class="card-title">{{title3}}</div>
            <div class="card-icons">{{icons3}}</div>
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

    # 隠しボタンの配置
    st.markdown("""<style>div[data-testid="stHidden"] { display: none; }</style>""", unsafe_allow_html=True)
    user_class = None
    with st.container(data_testid="stHidden"):
        if st.button("hidden1", key="hidden_btn_1"): user_class = 1
        if st.button("hidden2", key="hidden_btn_2"): user_class = 2
        if st.button("hidden3", key="hidden_btn_3"): user_class = 3

    # 巨大ボタンが押された時の処理（押し直し・修正時もここを通る）
    if user_class is not None:
        st.session_state.selected_choice = user_class
        # すでに選ばれている任意の値があればそれを引き継ぎ、無ければデフォルトで即CSV保存
        current_approx = st.session_state.get("approx_val", LANG_DICT[lang]["approx_default"])
        save_feedback(user_class, current_approx)
        st.session_state.trigger_balloons = True # 風船フラグをセット
        st.rerun()

    # 風船と成功メッセージの動的描画（ハイライトが適用された後に飛ぶように制御）
    if st.session_state.get("trigger_balloons", False):
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
