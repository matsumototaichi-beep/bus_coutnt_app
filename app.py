import streamlit as st
from datetime import datetime
import os
import csv

# ==========================================
# 1. 画面の設定（スマホで見やすい縦長レイアウト）
# ==========================================
st.set_page_config(page_title="バス混雑度フィードバック", page_icon="🚌", layout="centered")

# 回答データを保存するCSVファイルのパス
DATA_FILE = "user_feedback.csv"

# ==========================================
# 2. 多言語対応のための辞書（日本語 / English）
# ==========================================
LANG_DICT = {
    "JA": {
        "title": "🚌 奈良交通 混雑度アンケート",
        "subtitle": "現在の車内の混雑状況を教えてください。システム改善に活用します。",
        "lang_select": "Language / 言語",
        "q_congestion": "今の車内の様子はどれに近いですか？",
        "class1": "🟢 1. ガラガラ（全員座れる）",
        "class2": "🟡 2. 少し混雑（数人が立っている）",
        "class3": "🔴 3. 大混雑（通路までギッシリ）",
        "btn_submit": "回答を送信する",
        "success_msg": "ご協力ありがとうございました！🙌",
        "error_msg": "すでに回答が送信されているか、エラーが発生しました。"
    },
    "EN": {
        "title": "🚌 Bus Congestion Survey",
        "subtitle": "Please tell us the current congestion status inside the bus.",
        "lang_select": "Language / 言語",
        "q_congestion": "How crowded is the bus right now?",
        "class1": "🟢 1. Empty (Seats Available)",
        "class2": "🟡 2. Standing (A few people standing)",
        "class3": "🔴 3. Crowded (Packed to the aisle)",
        "btn_submit": "Submit Feedback",
        "success_msg": "Thank you for your cooperation! 🙌",
        "error_msg": "An error occurred or already submitted."
    }
}

# ==========================================
# 3. アプリのUI画面構築
# ==========================================

# 右上に言語切り替えスイッチを配置
# ※最新版の仕様変更に対応：空文字を避け、label_visibility="collapsed"で隠す
selected_lang = st.selectbox("言語選択", ["日本語", "English"], label_visibility="collapsed")
lang = "JA" if selected_lang == "日本語" else "EN"

# タイトルと説明文
st.title(LANG_DICT[lang]["title"])
st.caption(LANG_DICT[lang]["subtitle"])

st.markdown("---")

# 擬似的なURLパラメータの取得（最新の st.query_params に修正）
# 例: http://localhost:8501/?route_id=311341
route_id = st.query_params.get("route_id", "311341")
st.info(f"📍 Route ID: {route_id}")

# 質問項目
st.subheader(LANG_DICT[lang]["q_congestion"])

# 3つの選択肢
choice = st.radio(
    "混雑度選択", # ※最新版の仕様変更に対応：空文字を避ける
    [
        LANG_DICT[lang]["class1"],
        LANG_DICT[lang]["class2"],
        LANG_DICT[lang]["class3"]
    ],
    label_visibility="collapsed"
)

st.markdown("---")

# 送信ボタン
if st.button(LANG_DICT[lang]["btn_submit"], use_container_width=True):
    # 選択されたクラス（文字列から数値の1, 2, 3を抽出）
    if "1" in choice:
        user_class = 1
    elif "2" in choice:
        user_class = 2
    else:
        user_class = 3
        
    # 現在の時刻を取得
    now_ts = int(datetime.now().timestamp())
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # バックエンドで学習データとして使うためのCSV保存処理
    file_exists = os.path.isfile(DATA_FILE)
    with open(DATA_FILE, mode='a', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        # ファイルが新規作成ならヘッダーを書き込む
        if not file_exists:
            writer.writerow(["timestamp", "datetime", "route_id", "user_class"])
        # 回答データの書き込み
        writer.writerow([now_ts, now_str, route_id, user_class])
        
    # 送信完了メッセージ
    st.success(LANG_DICT[lang]["success_msg"])
    st.balloons() # 画面にお祝いの風船を飛ばす演出