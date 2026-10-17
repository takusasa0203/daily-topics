# daily-topic-summary

朝夕2回（7:15 / 17:15）、Gemini と Edge-TTS による **2人のホストによる約20分のNotebookLM風対話ポッドキャスト** を完全自動で生成・配信・蓄積するリポジトリです（毎朝8:00、毎夕18:00には確実に聴ける状態になります）。

## 🎧 番組の特徴

- **朝夕2回の完全自動配信**:
  - **🌅 朝の便（JST 7:15起動・8:00までに完成）**: 今日1日の動きを見据えたエネルギッシュなトークで、通勤・朝の準備中に先取り情報収集。
  - **🌆 夕方の便（JST 17:15起動・18:00までに完成）**: 1日の主要な出来事を振り返り、リラックスして聴ける夜のまとめトーク。

- **3大ジャンルを徹底深掘り（約20分）**:
  - 🇯🇵 **国内ニュース**: 国内の政治・経済・社会の注目トピック
  - 🌍 **海外・国際情勢**: 世界の主要ニュース・国際関係・グローバルトレンド
  - 💻 **最新テック・AI最前線**: AI、最新ガジェット、開発者トレンド、Webの話題
- **NotebookLM スタイルの2人掛け合い対話**:
  - **Keita（ケイタ・男性）**: 落ち着いたトーンで背景やポイントを解説
  - **Nanami（ナナミ・女性）**: 視聴者目線で素朴な疑問やリアクションを挟む進行役
- **全編テキスト書き起こし（トランスクリプト）付き**:
  - 音声だけでなく、記事リンク付きのMarkdownサマリーと全文対話ログを同時に保存。

## 📢 最近のポッドキャスト
<!-- LATEST_DIGESTS -->
- 📅 **2026-10-17 🌅 朝の便**：[まとめ記事・台本](digests/2026-10-17_morning.md) ([🎧 ポッドキャストを聴く](digests/2026-10-17_morning.mp3))


## ディレクトリ構成

```
daily-topic-summary/
├── .github/
│   └── workflows/
│       └── daily_digest.yml   # 朝7時・夕18時の定時実行＆手動実行
├── digests/                   # ポッドキャストmp3とMarkdown書き起こしの保存場所
├── src/
│   ├── fetcher.py             # 国内・海外・テックの各RSS収集
│   ├── summarizer.py          # Gemini APIによる20分対話台本＆サマリー生成
│   ├── tts.py                 # Edge-TTSによる2話者並行音声合成＆結合
│   └── main.py                # 実行エントリーポイント
├── requirements.txt           # 必要パッケージ一覧
└── README.md
```

## セットアップ & 設定

1. **Gemini API キーの登録**:
   * GitHub リポジトリの **Settings** > **Secrets and variables** > **Actions** に `GEMINI_API_KEY` を登録します。
2. **Workflow 書き込み権限**:
   * **Settings** > **Actions** > **General** の **Workflow permissions** で「Read and write permissions」を有効にします。
