"""Gemini API を使用してトピック要約および音声読み上げ原稿を生成するモジュール。
"""

import os
from typing import List, Dict, Tuple
from google import genai

def generate_summary(articles: List[Dict[str, str]], target_date: str) -> Tuple[str, str]:
    """記事一覧を元に、(Markdown要約, 音声読み上げ用原稿) のタプルを生成する。"""
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("環境変数 'GEMINI_API_KEY' が設定されていません。")

    client = genai.Client(api_key=api_key)

    # 記事リストをプロンプト用に整形
    articles_text = ""
    for idx, a in enumerate(articles, 1):
        articles_text += f"{idx}. [{a['source']}] {a['title']}\n   URL: {a['link']}\n"

    prompt = f"""あなたは毎朝の最新テックニュースをお届けするプロのラジオパーソナリティ兼エディターです。
以下は本日（{target_date}）収集したトピック一覧です。

--- トピック一覧 ---
{articles_text}
--------------------

以下の2つのパートを作成してください。出力は指定のセパレータ `===SPEECH_SCRIPT===` で区切ってください。

### パート1: Markdownレポート（セパレータの前）
- 朝の忙しい時間でも1分で把握できるように、特に重要・興味深いトピックを3〜5個厳選して要約してください。
- 形式:
  # 📅 {target_date} のトピックダイジェスト
  ## 注目トピック要約
  - **[トピックタイトル]**: 要点を簡潔に解説（2〜3行程度） [記事リンク](URL)
  ## まとめ・考察
  - 本日のトレンドに対する短い一言まとめ

===SPEECH_SCRIPT===
### パート2: 音声読み上げ用原稿（セパレータの後）
- 音声合成（TTS）で読み上げるための、耳で聴いて心地よい自然な日本語の話し言葉の原稿を作成してください。
- 挨拶（「おはようございます！{target_date}の朝のニュースダイジェストです」など）から始めてください。
- Markdown記号（`#`, `*`, `[]()`など）やURLは絶対に含めず、純粋なひらがな・漢字の読みやすい文章にしてください。
- 長さは1分〜2分程度（約400〜600文字）でコンパクトにまとめてください。
"""

    # 利用可能な標準モデル: gemini-2.0-flash, gemini-1.5-flash
    try:
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=prompt,
        )
    except Exception as e:
        print(f"gemini-2.0-flash 呼び出し失敗 ({e})。gemini-1.5-flash にフォールバックします。")
        response = client.models.generate_content(
            model="gemini-1.5-flash",
            contents=prompt,
        )


    response_text = response.text or ""
    if "===SPEECH_SCRIPT===" in response_text:
        parts = response_text.split("===SPEECH_SCRIPT===")
        markdown_summary = parts[0].strip()
        speech_script = parts[1].strip()
    else:
        markdown_summary = response_text.strip()
        speech_script = response_text.strip()

    return markdown_summary, speech_script
