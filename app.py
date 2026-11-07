import time
import requests
import streamlit as st

st.set_page_config(
    page_title="note スキチェッカー デバッグ",
    page_icon="🐛",
    layout="centered",
)

st.title("🐛 note スキチェッカー（デバッグモード）")
st.write(
    "APIからどのようなデータが返ってきているかを確認するテスト用画面です。"
)

# 入力フォーム
my_user_id = st.sidebar.text_input(
    "あなたのnote ID", placeholder="例: username"
)
target_user_id = st.text_input("🔍 調べたいフォロワーのID", placeholder="例: yominikuikamo")

if st.button("デバッグ実行する", type="primary"):
  if not my_user_id or not target_user_id:
    st.warning("⚠️ 双方のIDを入力してください。")
  else:
    with st.spinner("テストデータを取得中..."):
      # 1. 自分の記事を1件だけ取得してみる
      url = f"https://note.com/api/v2/creators/{my_user_id}/contents?kind=note&page=1"
      res = requests.get(url)

      if res.status_code != 200:
        st.error(
            f"❌ 記事一覧の取得に失敗しました (ステータスコード: {res.status_code})"
        )
      else:
        contents = res.json().get("data", {}).get("contents", [])
        if not contents:
          st.error("❌ 記事が1件も見つかりませんでした。")
        else:
          st.success("✅ 自分の記事一覧の取得には成功しました！")

          # 2. 最新の1記事のスキ一覧APIを叩いて生データを見る
          sample_note_id = contents[0].get("key")
          sample_title = contents[0].get("name")
          likes_url = f"https://note.com/api/v3/notes/{sample_note_id}/likes?size=20"

          st.write(
              f"**【テスト対象記事】** {sample_title} (ID: `{sample_note_id}`)"
          )
          st.write(f"**【叩いたAPI】** `{likes_url}`")

          likes_res = requests.get(likes_url)
          st.write(f"**【APIの応答ステータス】** `{likes_res.status_code}`")

          if likes_res.status_code == 200:
            data = likes_res.json()
            st.write(
                "▼ **APIから返ってきた実際のデータ（中身の構造）**:"
            )
            st.json(data)  # 生データを画面にそのまま表示
          else:
            st.error(
                "❌ スキ一覧の取得がブロックされたか、エラーになりました。"
            )
