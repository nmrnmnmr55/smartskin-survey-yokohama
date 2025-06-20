import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime

# カスタムCSSの適用
st.markdown("""
<style>
    body {
        color: #333333;
        background-color: #F8F8F8;
        font-family: "Yu Gothic", "游ゴシック", YuGothic, "游ゴシック体", "ヒラギノ角ゴ Pro W3", "メイリオ", sans-serif;
    }
    .stButton>button {
        color: #FFFFFF;
        background-color: #333333;
        border-radius: 20px;
        padding: 10px 24px;
        font-weight: 500;
        font-family: "Yu Gothic", "游ゴシック", YuGothic, "游ゴシック体", sans-serif;
    }
    .stTextInput>div>div>input, .stTextArea>div>div>textarea {
        border-radius: 10px;
        border: 1px solid #CCCCCC;
        font-family: "Yu Gothic", "游ゴシック", YuGothic, "游ゴシック体", sans-serif;
    }
    h1 {
        font-size: 2.5rem;
        font-weight: 700;
        letter-spacing: -0.5px;
        margin-bottom: 2rem;
        font-family: "Yu Gothic", "游ゴシック", YuGothic, "游ゴシック体", sans-serif;
    }
    p {
        font-size: 1.1rem;
        line-height: 1.8;
        margin-bottom: 1.5rem;
    }
    .stRadio > label {
        font-size: 1.1rem;
        padding: 10px 0;
        font-family: "Yu Gothic", "游ゴシック", YuGothic, "游ゴシック体", sans-serif;
    }
    @media (max-width: 768px) {
        h1 {
            font-size: 2rem;
        }
        p {
            font-size: 1rem;
        }
    }
</style>
""", unsafe_allow_html=True)

# Google Sheets API の設定
scopes = [
    'https://www.googleapis.com/auth/spreadsheets',
    'https://www.googleapis.com/auth/drive'
]

try:
    # Streamlit Secrets から認証情報を取得
    credentials = Credentials.from_service_account_info(st.secrets["gcp_service_account"], scopes=scopes)
    client = gspread.authorize(credentials)

    # スプレッドシートを開く（スプレッドシートのIDを指定）
    sheet = client.open_by_key('1R2QKVcLIwAwPE0b4GEr_f1fJ-4wNLt4ZDWyCGK8p-zo').sheet1
except Exception as e:
    st.error(f"Google Sheets APIの設定中にエラーが発生しました: {str(e)}")
    sheet = None

# URLからユーザーIDを取得する関数（更新版）
def get_user_id():
    return st.query_params.get("d")

def main():
    col1, col2, col3 = st.columns([1,3,1])
    with col2:
        st.title("お客様満足度調査")

        if 'page' not in st.session_state:
            st.session_state.page = 1
        if 'choice' not in st.session_state:
            st.session_state.choice = None
        if 'row_index' not in st.session_state:
            st.session_state.row_index = None
        if 'user_id' not in st.session_state:
            st.session_state.user_id = get_user_id()

        if st.session_state.page == 1:
            show_page_1()
        elif st.session_state.page == 2:
            show_page_2()
        elif st.session_state.page == 3:
            show_page_3()
        elif st.session_state.page == 4:
            show_page_4()

def show_page_1():
    st.write("当クリニックではお客様の声を踏まえ、より良いサービスの提供を目指しています。")
    st.write("1問のみ、5秒で終わりますので、満足度調査にご協力をお願い申し上げます。")
    options = ["非常に満足", "満足", "どちらでもない", "不満", "非常に不満"]
    choice = st.radio("選択肢", options)

    if st.button("次へ", key="next_button"):
        st.session_state.choice = choice  # 選択を保存
        row_index = save_page_1_to_sheet(choice)
        st.session_state.row_index = row_index
        if choice in ["非常に満足", "満足"]:
            st.session_state.page = 2
        else:
            st.session_state.page = 3
        st.rerun()

def show_page_2():
    st.write("貴重なご意見をありがとうございます！")
    st.write("★以下に口コミ記載＆スタッフ提示で、サンソリット スキンピールバー(約3,000円相当)を特別プレゼント！★")
    st.markdown("[口コミ記入ページを開く](https://g.page/r/CfKMnigxxDPWEBI/review)")
    st.write("詳細はスタッフまでお尋ねください。")

def show_page_3():
    st.write("この度、満足いただけなかったこと誠に申し訳ございません。心よりお詫び申し上げます。")
    st.write("今後、少しでもよりサービスを提供できるように改善していければと考えております。もし差し支えなければ、ご忌憚のないご意見をお聞かせいただければ幸いです。")
    rating = st.slider("★の数を選択してください", 1, 5, 3, key="rating_slider")
    comment = st.text_area("コメントを記入してください")

    if st.button("送信", key="submit_button"):
        save_page_3_to_sheet(rating, comment)
        st.session_state.page = 4  # 確認ページに遷移
        st.rerun()

def show_page_4():
    st.write("貴重なご意見をいただき誠にありがとうございました。")
    st.write("確かに受領いたしました。")
    st.write("頂いた貴重なご意見をふまえ、少しでも良いサービスを提供できるように改善に努めてまいります。")
    st.write("引き続きどうぞよろしくお願いいたします。")
    
    if st.button("最初に戻る", key="return_button"):
        st.session_state.page = 1  # 最初のページに戻る
        st.session_state.choice = None  # 選択をリセット
        st.session_state.row_index = None  # 行インデックスをリセット
        st.rerun()

def save_page_1_to_sheet(choice):
    if sheet is None:
        st.error("Google Sheetsとの接続に問題があります。")
        return None
    
    try:
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        row = [now, choice, '', '', '', st.session_state.user_id]  # F列にuser_idを追加
        next_row = len(sheet.get_all_values()) + 1
        sheet.insert_row(row, next_row)
        return next_row
    except Exception as e:
        st.error(f"データの保存中にエラーが発生しました: {str(e)}")
        return None

def save_page_3_to_sheet(rating, comment):
    if sheet is None:
        st.error("Google Sheetsとの接続に問題があります。")
        return
    
    try:
        if st.session_state.row_index:
            sheet.update_cell(st.session_state.row_index, 4, rating)
            sheet.update_cell(st.session_state.row_index, 5, comment)
        else:
            st.error("行インデックスが見つかりません。管理者にお問い合わせください。")
    except Exception as e:
        st.error(f"データの更新中にエラーが発生しました: {str(e)}")

if __name__ == "__main__":
    main()