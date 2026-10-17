"""ポッドキャスト生成のワークフロー全体を統括・実行するハンドラーモジュール。
ビジネスロジック、ファイルI/O、README更新などをカプセル化します。
"""

import os
import sys
from datetime import datetime
from typing import Dict, Any, Optional
import pytz

from fetcher import fetch_all_categories
from summarizer import generate_podcast_dialogue
from tts import synthesize_podcast

class PodcastHandler:
    """ポッドキャスト生成・保存・インデックス更新を一元管理するハンドラークラス。"""

    def __init__(self, config: Dict[str, Any], base_dir: Optional[str] = None, output_dir: Optional[str] = None):
        self.config = config
        self.base_dir = base_dir or os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.digests_dir = output_dir if output_dir else os.path.join(self.base_dir, "digests")
        self.readme_path = os.path.join(self.base_dir, "README.md")
        os.makedirs(self.digests_dir, exist_ok=True)


    def get_current_time(self) -> datetime:
        """設定されたタイムゾーンの現在日時を取得する。"""
        tz_name = self.config.get("general", {}).get("timezone", "Asia/Tokyo")
        try:
            tz = pytz.timezone(tz_name)
        except Exception:
            tz = pytz.timezone("Asia/Tokyo")
        return datetime.now(tz)

    def resolve_edition(self, requested_edition: str, now: datetime) -> str:
        """エディション（morning/evening）を決定する。"""
        if requested_edition != "auto":
            return requested_edition
        morning_limit = self.config.get("editions", {}).get("morning", {}).get("trigger_hour_limit", 13)
        return "morning" if now.hour < morning_limit else "evening"

    def update_readme(self, date_str: str, edition: str, md_filename: str, audio_filename: str):
        """README.md の最新ポッドキャスト一覧を更新する。"""
        if not os.path.exists(self.readme_path):
            return

        edition_jp = "🌅 朝の便" if edition == "morning" else "🌆 夕方の便"
        entry = f"- 📅 **{date_str} {edition_jp}**：[まとめ記事・台本](digests/{md_filename}) ([🎧 ポッドキャストを聴く](digests/{audio_filename}))\n"
        marker = "<!-- LATEST_DIGESTS -->"

        with open(self.readme_path, "r", encoding="utf-8") as f:
            content = f.read()

        if marker in content:
            parts = content.split(marker)
            new_content = parts[0] + marker + "\n" + entry + parts[1].lstrip("\n")
            with open(self.readme_path, "w", encoding="utf-8") as f:
                f.write(new_content)

    def save_markdown_report(self, date_str: str, edition: str, md_report: str, dialogue_lines: list, audio_filename: str) -> str:
        """Markdownレポートと対話ログを整形して保存する。"""
        md_filename = f"{date_str}_{edition}.md"
        md_path = os.path.join(self.digests_dir, md_filename)
        transcript_md = "\n\n".join([f"**{d['speaker']}**: {d['text']}" for d in dialogue_lines])

        full_content = f"""{md_report}

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
            f.write(full_content)
        return md_filename

    def run(self, edition: str = "auto", dry_run: bool = False):
        """ポッドキャスト生成パイプラインを実行する。"""
        now = self.get_current_time()
        date_str = now.strftime("%Y-%m-%d")
        resolved_edition = self.resolve_edition(edition, now)
        edition_label = "🌅 朝の便" if resolved_edition == "morning" else "🌆 夕方の便"

        print(f"=== [{date_str} {edition_label}] 20分ポッドキャスト処理開始 ===")
        print(f"モデル: {self.config.get('general', {}).get('model', 'gemini-3.8-flash')}")

        # 1. トピック取得
        print("1. トピックを収集中...")
        categorized = fetch_all_categories(self.config)
        total_articles = sum(len(items) for items in categorized.values())
        for cat, items in categorized.items():
            print(f"   - {cat}: {len(items)} 件取得")

        if total_articles == 0:
            print("記事が取得できませんでした。処理を中断します。")
            sys.exit(1)

        if dry_run:
            print("\n[DRY RUN モード]")
            print(f"トピック収集完了: 合計 {total_articles} 件")
            print("API呼び出しおよび音声合成をスキップして正常終了します。")
            return

        # 2. 台本生成
        print("2. Gemini API で掛け合い台本を生成中...")
        md_report, dialogue_lines = generate_podcast_dialogue(
            categorized, date_str, resolved_edition, config=self.config
        )
        print(f"-> 対話セリフ数: {len(dialogue_lines)} 行")

        # 3. 音声合成
        file_prefix = f"{date_str}_{resolved_edition}"
        audio_filename = f"{file_prefix}.mp3"
        audio_path = os.path.join(self.digests_dir, audio_filename)

        print(f"3. 音声合成中 ({audio_filename})...")
        synthesize_podcast(dialogue_lines, audio_path, config=self.config)
        print("-> 音声合成完了")

        # 4. Markdown保存 & README更新
        md_filename = self.save_markdown_report(date_str, resolved_edition, md_report, dialogue_lines, audio_filename)
        self.update_readme(date_str, resolved_edition, md_filename, audio_filename)

        print(f"=== [{date_str} {edition_label}] 全処理が正常に完了しました ===")
