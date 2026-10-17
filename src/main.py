"""トピック収集、Gemini要約、音声生成、ファイル保存を統括するメインスクリプト。
"""

import os
import sys
from datetime import datetime
import pytz

from fetcher import fetch_topics
from summarizer import generate_summary
from tts import text_to_speech

def get_jst_now() -> datetime:
    """日本時間（JST）の現在日時を取得する。"""
    jst = pytz.timezone("Asia/Tokyo")
    return datetime.now(jst)

def update_readme_index(digest_date: str, md_filename: str, audio_filename: str):
    """README.md に最新ダイジェストへのリンクを追記・更新する。"""
    readme_path = os.path.join(os.path.dirname(__file__), "..", "README.md")
    if not os.path.exists(readme_path):
        return

    entry = f"- 📅 [{digest_date}](digests/{md_filename}) ([🎙 音声を聞く](digests/{audio_filename}))\n"
    marker = "<!-- LATEST_DIGESTS -->"

    with open(readme_path, "r", encoding="utf-8") as f:
        content = f.read()

    if marker in content:
        # マーカーの直後に最新のダイジェストを挿入
        parts = content.split(marker)
        new_content = parts[0] + marker + "\n" + entry + parts[1].lstrip("\n")
        with open(readme_path, "w", encoding="utf-8") as f:
            f.write(new_content)

def main():
    jst_now = get_jst_now()
    date_str = jst_now.strftime("%Y-%m-%d")
    print(f"=== [{date_str}] 朝のトピックダイジェスト生成開始 ===")

    # 1. トピック取得
    print("1. トピックを収集中...")
    articles = fetch_topics()
    if not articles:
        print("トピックが取得できませんでした。処理を中断します。")
        sys.exit(1)
    print(f"-> {len(articles)} 件の記事を取得しました。")

    # 2. Geminiによる要約と読み上げ原稿生成
    print("2. Gemini API で要約と音声原稿を生成中...")
    md_summary, speech_script = generate_summary(articles, date_str)

    # 保存先ディレクトリの準備
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    digests_dir = os.path.join(base_dir, "digests")
    os.makedirs(digests_dir, exist_ok=True)

    audio_filename = f"{date_str}.mp3"
    audio_path = os.path.join(digests_dir, audio_filename)

    # 3. 音声ファイル（mp3）の生成
    print(f"3. 音声ファイル（{audio_filename}）を合成中...")
    text_to_speech(speech_script, audio_path)
    print("-> 音声合成が完了しました。")

    # 4. Markdown ファイルの保存
    md_filename = f"{date_str}.md"
    md_path = os.path.join(digests_dir, md_filename)

    full_md_content = f"""{md_summary}

---

### 🎙 音声ダイジェスト
- [音声ファイルを開く・ダウンロード ({audio_filename})]({audio_filename})

<audio controls src="{audio_filename}"></audio>

<details>
<summary><b>読み上げ用原稿を表示する</b></summary>

{speech_script}

</details>
"""

    with open(md_path, "w", encoding="utf-8") as f:
        f.write(full_md_content)
    print(f"-> Markdownを保存しました: {md_path}")

    # 5. README の最新インデックス更新
    update_readme_index(date_str, md_filename, audio_filename)
    print("=== 全処理が正常に完了しました ===")

if __name__ == "__main__":
    main()
