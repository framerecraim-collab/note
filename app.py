import time
import requests
import streamlit as st

# ページの設定
st.set_page_config(
    page_title="note スキ履歴チェッカー", page_icon="📝", layout="centered"
)

st.title("📝 note スキ履歴チェッカー")
st.write(
    "特定のフォロワーさんが、あなたのどの記事にスキしてくれたかを一発で検索する自分専用アプリです。"
)

# 入力フォーム
st.sidebar.header("設定")
my_user_id = st.sidebar.text_input(
    "あなたのnote ID",
    placeholder="例: username (URLの末尾)",
)
target_user_id = st.text_input(
    "🔍 調べたいフォロワーのID",
    placeholder="例: yominikuikamo",
)

st.markdown("---")

if st.button("スキ履歴を検索する", type="primary"):
  if not my_user_id or not target_user_id:
    st.warning(
        "⚠️ サイドバーに「あなたのnote ID」、入力欄に「調べたいフォロワーのID」"
        "を入力してください。"
    )
  else:
    with st.spinner(
        "記事とスキ履歴を取得中…（記事数が多いと少し時間がかかります）"
    ):
      all_notes = []
      page = 1

      # 1. 自分の全記事を取得
      while True:
        url = f"https://note.com/api/v2/creators/{my_user_id}/contents?kind=note&page={page}"
        res = requests.get(url)
        if res.status_code != 200:
          break
        data = res.json().get("data", {})
        contents = data.get("contents", [])
        if not contents:
          break

        for note in contents:
          all_notes.append({"id": note["key"], "title": note["name"]})

        if data.get("isLastPage", True):
          break
        page += 1
        time.sleep(0.3)

      if not all_notes:
        st.error(
            "❌ 記事が見つかりませんでした。あなたのnote IDが正しいか確認してください。"
        )
      else:
        matched_articles = []
        target = target_user_id.strip().lower()

        # 2. 各記事のスキ一覧をチェック（size=100を指定して取得数を拡張）
        for note in all_notes:
          note_id = note["id"]
          likes_url = f"https://note.com/api/v3/notes/{note_id}/likes?size=100"
          res = requests.get(likes_url)

          if res.status_code == 200:
            likes_data = res.json().get("data", {}).get("likes", [])
            for like in likes_data:
              user = like.get("user", {})
              # 複数のキー（urlname, key, nickname等）を照合して一致を確認
              u_urlname = str(user.get("urlname", "")).lower()
              u_key = str(user.get("key", "")).lower()
              u_nickname = str(user.get("nickname", "")).lower()

              if target in [u_urlname, u_key] or target == u_nickname:
                matched_articles.append(
                    {
                        "title": note["title"],
                        "url": f"https://note.com/{my_user_id}/n/{note_id}",
                    }
                )
                break  # 同じ記事で複数回ヒットするのを防ぐ
          time.sleep(0.2)

        # 結果表示
        st.success(f"🎉 検索完了！全 {len(all_notes)} 記事をチェックしました。")
        st.subheader("🎯 該当する記事一覧")

        if matched_articles:
          for item in matched_articles:
            st.markdown(f"- [{item['title']}]({item['url']})")
        else:
          st.info(
              "ℹ️ 指定したフォロワーからのスキは見つかりませんでした。"
              "（※過去のスキ件数が多すぎる場合、一部が制限にかかっている可能性があります）"
          )
