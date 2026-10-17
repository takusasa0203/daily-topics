# daily-topic-summary

毎朝Geminiで最新トピックを要約し、音声ダイジェスト（mp3）とともに自動保存するリポジトリです。GitHub Actions の cron スケジュールにより、完全自動で実行されます。

## 概要

- **自動スケジュール**: 毎朝定時（日本時間 朝7:00等）に GitHub Actions が自動起動
- **トピック収集**: 指定したニュース・RSSから最新の重要トピックを自動取得
- **Gemini 要約**: Google Gemini API を使用して、要点を分かりやすくまとめたサマリーを作成
- **音声生成**: 自然な日本語音声（Edge-TTS）でダイジェスト音声（.mp3）を自動生成
- **自動アーカイブ**: 生成されたテキストと音声ファイルを `digests/` フォルダへ自動コミット＆プッシュ

## 📢 最近のダイジェスト
<!-- LATEST_DIGESTS -->


## ディレクトリ構成

```
daily-topic-summary/
├── .github/
│   └── workflows/
│       └── daily_digest.yml   # 毎朝実行されるGitHub Actions定義
├── digests/                   # 日々の要約Markdownと音声mp3が蓄積される場所
├── src/
│   ├── fetcher.py             # トピック取得処理
│   ├── summarizer.py          # Gemini API要約処理
│   ├── tts.py                 # 音声合成（Edge-TTS）処理
│   └── main.py                # 実行エントリーポイント
├── requirements.txt           # 必要パッケージ一覧
└── README.md
```

## 初期セットアップ

### 1. Gemini API キーの登録
1. [Google AI Studio](https://aistudio.google.com/) から API キーを取得します。
2. GitHubリポジトリの **Settings** > **Secrets and variables** > **Actions** を開きます。
3. **New repository secret** をクリックし、以下を登録します：
   - Name: `GEMINI_API_KEY`
   - Secret: 取得したAPIキー

### 2. GitHub Actions の書き込み権限設定
GitHub Actions からリポジトリへ自動コミット・プッシュできるようにするため：
1. リポジトリの **Settings** > **Actions** > **General** を開きます。
2. **Workflow permissions** で **Read and write permissions** を選択し、**Save** をクリックします。
