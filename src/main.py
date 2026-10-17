"""朝・夕の20分対話型ポッドキャスト（国内・海外・テック）を生成・保存するメインスクリプト。
"""

import os
import sys
import argparse
from datetime import datetime
import pytz

# カレントディレクトリに関わらず src 直下のモジュールを確実にロード
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
if CURRENT_DIR not in sys.path:
    sys.path.insert(0, CURRENT_DIR)

from config_loader import load_config
from fetcher import fetch_all_categories
from summarizer import generate_podcast_dialogue
from tts import synthesize_podcast

def get_tz_now(tz_name: str = "Asia/Tokyo") -> datetime:
    """指定されたタイムゾーンの現在日時を取得する。"""
    try:
        tz = pytz.timezone(tz_name)
    except Exception:
        tz = pytz.timezone("Asia/Tokyo")
    return datetime.now(tz)

def detect_edition(now: datetime, config: dict) -> str:
    """現在時刻から朝便 (morning) か夕便 (evening) かを自動判定する。"""
    morning_limit = config.get("editions", {}).get("morning", {}).get("trigger_hour_limit", 13)
    return "morning" if now.hour < morning_limit else "evening"

def update_readme_index(date_str: str, edition: str, md_filename: str, audio_filename: str):
    """README.md に最新ポッドキャストへのリンクを追記・更新する。"""
    readme_path = os.path.join(os.path.dirname(__file__), "..", "README.md")
    if not os.path.exists(readme_path):
        return

    edition_jp = "🌅 朝の便" if edition == "morning" else "🌆 夕方の便"
    entry = f"- 📅 **{date_str} {edition_jp}**：[まとめ記事・台本](digests/{md_filename}) ([🎧 ポッドキャストを聴く](digests/{audio_filename}))\n"
    marker = "<!-- LATEST_DIGESTS -->"

    with open(readme_path, "r", encoding="utf-8") as f:
        content = f.read()

    if marker in content:
        parts = content.split(marker)
        new_content = parts[0] + marker + "\n" + entry + parts[1].lstrip("\n")
        with open(readme_path, "w", encoding="utf-8") as f:
            f.write(new_content)

def main():
    parser = argparse.ArgumentParser(description="Generate 20-min daily topic podcast")
    parser.add_argument("--edition", choices=["morning", "evening", "auto"], default="auto",
                        help="Select edition: morning (朝) or evening (夕)")
    parser.add_argument("--dry-run", action="store_true",
                        help="Run topic fetching and configuration check without calling Gemini API or Edge-TTS")
    parser.add_argument("--config", type=str, default=None,
                        help="Path to custom config.yaml")
    args = parser.parse_args()

    config = load_config(args.config)
    tz_name = config.get("general", {}).get("timezone", "Asia/Tokyo")
    now = get_tz_now(tz_name)
    date_str = now.strftime("%Y-%m-%d")

    edition = args.edition
    if edition == "auto":
        edition = detect_edition(now, config)

    edition_label = "🌅 朝の便" if edition == "morning" else "🌆 夕方の便"
    print(f"=== [{date_str} {edition_label}] 20分ポッドキャスト処理開始 ===")
    print(f"モデル: {config.get('general', {}).get('model', 'gemini-3.8-flash')} | タイムゾーン: {tz_name}")

    # 1. 国内・海外・テックの全トピック取得
    print("1. トピックを収集中...")
    categorized = fetch_all_categories(config)
    total_articles = 0
    for cat, items in categorized.items():
        print(f"   - {cat}: {len(items)} 件取得")
        total_articles += len(items)

    if total_articles == 0:
        print("記事が取得できませんでした。処理を中断します。")
        sys.exit(1)

    if args.dry_run:
        print("\n[DRY RUN モード]")
        print("トピック収集と設定ファイルの検証が正常に完了しました。")
        print(f"取得合計記事数: {total_articles} 件")
        print("API呼び出しと音声合成をスキップして終了します。")
        sys.exit(0)

    # 2. Gemini による2人掛け合い対話台本 & Markdownレポート生成
    print(f"2. Gemini API で20分の掛け合い台本を生成中...")
    markdown_report, dialogue_lines = generate_podcast_dialogue(categorized, date_str, edition, config=config)
    print(f"-> 対話セリフ数: {len(dialogue_lines)} 行")

    # 保存先ディレクトリ
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    digests_dir = os.path.join(base_dir, "digests")
    os.makedirs(digests_dir, exist_ok=True)

    file_prefix = f"{date_str}_{edition}"
    audio_filename = f"{file_prefix}.mp3"
    audio_path = os.path.join(digests_dir, audio_filename)

    # 3. 2話者による並行音声合成 & 結合
    print(f"3. 20分ポッドキャスト音声（{audio_filename}）を合成・結合中...")
    synthesize_podcast(dialogue_lines, audio_path, config=config)
    print("-> ポッドキャストの生成が完了しました！")

    # 4. Markdown ファイルの保存
    md_filename = f"{file_prefix}.md"
    md_path = os.path.join(digests_dir, md_filename)

    transcript_md = "\n\n".join([f"**{d['speaker']}**: {d['text']}" for d in dialogue_lines])

    full_md_content = f"""{markdown_report}

---

### 🎧 ポッドキャスト音声（約20分）
- [ポッドキャスト音声ファイルをダウンロード ({audio_filename})]({audio_filename})

<audio controls src="{audio_filename}"></audio>

<details>
<summary><b>📜 ポッドキャスト全文書き起こし（トランスクリプト）を開く</b></summary>

{transcript_md}

</details>
"""

    with open(md_path, "w", encoding="utf-8") as f:
        f.write(full_md_content)
    print(f"-> Markdownを保存しました: {md_path}")

    # 5. README の最新インデックス更新
    update_readme_index(date_str, edition, md_filename, audio_filename)
    print(f"=== [{date_str} {edition_label}] 全処理が正常に完了しました ===")

if __name__ == "__main__":
    main()
