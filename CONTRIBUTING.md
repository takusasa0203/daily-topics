# Contributing to daily-topics

`daily-topics` へのコントリビューションをご検討いただきありがとうございます！
バグ報告、機能提案、ドキュメントの改善、プルリクエストなど、あらゆる貢献を歓迎します。

---

## 開発環境のセットアップ

1. **リポジトリの Fork & Clone**:
   ```bash
   git clone https://github.com/<あなたのユーザー名>/daily-topics.git
   cd daily-topics
   ```

2. **仮想環境の作成とパッケージインストール**:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

3. **ローカルテスト（API消費なし）**:
   `--dry-run` フラグを使用することで、Gemini APIキー不要でトピック取得と設定ファイルの構文テストを実行できます。
   ```bash
   python3 src/main.py --dry-run
   ```

---

## 開発の流れ

1. 新しいブランチを作成します:
   ```bash
   git checkout -b feature/awesome-feature
   # または
   git checkout -b fix/issue-description
   ```

2. 変更を加え、構文チェックを実行します:
   ```bash
   python3 -m py_compile src/*.py
   python3 src/main.py --dry-run
   ```

3. わかりやすいコミットメッセージを記述します（Conventional Commits 推奨）:
   ```bash
   git commit -m "feat: add new RSS feed for AI trends"
   ```

4. あなたの Fork へプッシュし、Pull Request を作成してください！

---

## 行動規範

本プロジェクトへのすべての参加者は、[CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md) に定められた行動規範を遵守することが求められます。
