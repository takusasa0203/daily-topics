"""Gemini API を使用して、朝夕の20分ポッドキャスト対話台本（NotebookLM風）およびMarkdownレポートを生成するモジュール。
"""

import os
import re
from typing import List, Dict, Tuple, Any
from google import genai

MODEL_CANDIDATE = "gemini-3.8-flash"

def call_gemini(client: genai.Client, prompt: str) -> str:
    """Gemini APIを呼び出してテキストを生成する。"""
    try:
        response = client.models.generate_content(
            model=MODEL_CANDIDATE,
            contents=prompt,
        )
        return response.text or ""
    except Exception as e:
        print(f"モデル '{MODEL_CANDIDATE}' 呼び出しエラー: {e}")
        # フォールバック
        for fb in ["gemini-3-flash", "gemini-2.5-flash"]:
            try:
                print(f"フォールバック試行: {fb}")
                response = client.models.generate_content(
                    model=fb,
                    contents=prompt,
                )
                return response.text or ""
            except Exception:
                continue
        raise e

def generate_podcast_dialogue(
    categorized_articles: Dict[str, List[Dict[str, str]]],
    target_date: str,
    edition: str = "morning"
) -> Tuple[str, List[Dict[str, str]]]:
    """「国内」「海外」「テック系」の3大ジャンルを元に、
    20分のNotebookLM風2人掛け合い対話台本と、Markdownレポートを生成する。
    """
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("環境変数 'GEMINI_API_KEY' が設定されていません。")

    client = genai.Client(api_key=api_key)

    is_morning = (edition == "morning")
    edition_label = "朝の便" if is_morning else "夕方の便"
    greeting = "おはようございます！" if is_morning else "お疲れ様です！"
    tone_desc = "今日1日の動きを見据えたエネルギッシュなトーン" if is_morning else "今日1日の出来事を振り返りリラックスして聴けるトーン"

    system_context = f"""あなたはGoogle NotebookLMスタイルの本格的なポッドキャスト番組のプロデューサー兼脚本家です。
2人の人気パーソナリティによる自然で魅力的な掛け合い台本を作成してください。

【パーソナリティ設定】
- **Keita（ケイタ・男性）**: 落ち着いたトーンで、IT・経済・時事に詳しい解説役。「実はこの背景には〜」「ここが重要なポイントでね」
- **Nanami（ナナミ・女性）**: 明るく親しみやすく、視聴者の目線で相槌や素朴な疑問を投げかける進行役。「なるほど！」「それって一般の生活にはどう影響するの？」

【出力ルール】
- 各行は必ず「Keita: セリフ」または「Nanami: セリフ」で始めてください。
- 音声合成（TTS）で読み上げるため、Markdown装飾（**や#など）やURL、絵文字は一切含めず、純粋な話し言葉のみにしてください。
- アルファベットの略語や専門用語は、耳で聞いてわかりやすい読み（例: AIはエーアイ、ITはアイティー、SDVはエス・ディー・ブイなど）を意識してください。
- 相槌（「へぇー！」「確かに！」「それは気になるね」など）や自然な掛け合いをふんだんに盛り込み、聞き飽きないテンポの良い会話にしてください。
"""

    # 1. 各ジャンルの記事テキスト整形
    def format_articles(articles: List[Dict[str, str]]) -> str:
        res = ""
        for idx, a in enumerate(articles, 1):
            res += f"{idx}. [{a['source']}] {a['title']}\n   要約: {a.get('summary', '')[:100]}\n"
        return res

    domestic_text = format_articles(categorized_articles.get("domestic", []))
    world_text = format_articles(categorized_articles.get("world", []))
    tech_text = format_articles(categorized_articles.get("tech", []))

    all_dialogue_lines: List[Dict[str, str]] = []

    # --- チャプター1: オープニング (約1.5〜2分、約500文字) ---
    print("チャプター1: オープニング対話を生成中...")
    prompt_opening = f"""{system_context}

本日（{target_date}）の{edition_label}（{tone_desc}）のオープニングトークを作成してください。
冒頭の挨拶（「{greeting}」）、日付、今日のラインナップ（国内・海外・テックの3大ジャンルをたっぷり約20分で深掘りすること）を魅力的に紹介してください。
長さの目安: 約500文字程度（KeitaとNanamiの掛け合いで6〜8往復程度）。
"""
    opening_res = call_gemini(client, prompt_opening)

    # --- チャプター2: 国内ニュース深掘り (約5〜6分、約1,800文字) ---
    print("チャプター2: 国内ニュース深掘り対話を生成中...")
    prompt_domestic = f"""{system_context}

次は第1コーナー【国内ニュース】の深掘りディスカッションです。
以下の国内ニュースの中から特に重要な1〜2件をピックアップし、単なる読み上げではなく「なぜ起きたのか」「今後の生活や社会にどんな影響があるか」「二人の率直な感想」をじっくり議論してください。

--- 国内ニュース一覧 ---
{domestic_text}
------------------------

長さの目安: 約1,800文字〜2,000文字の充実した長い掛け合い。話を端折らず、ディープに議論してください。
"""
    domestic_res = call_gemini(client, prompt_domestic)

    # --- チャプター3: 海外・国際情勢深掘り (約5〜6分、約1,800文字) ---
    print("チャプター3: 海外・国際情勢深掘り対話を生成中...")
    prompt_world = f"""{system_context}

次は第2コーナー【海外・国際情勢】の深掘りディスカッションです。
以下の国際ニュースの中から注目の1〜2件を取り上げ、世界情勢の背景や日本との関連性、今後の見通しをじっくり対話してください。

--- 海外ニュース一覧 ---
{world_text}
------------------------

長さの目安: 約1,800文字〜2,000文字の充実した長い掛け合い。ディープに議論してください。
"""
    world_res = call_gemini(client, prompt_world)

    # --- チャプター4: テック・AI最前線深掘り (約6〜7分、約2,000文字) ---
    print("チャプター4: テック・AI最前線深掘り対話を生成中...")
    prompt_tech = f"""{system_context}

次は第3コーナー、本番組のメインでもある【最新テック・AI最前線】のディスカッションです。
以下のテックニュースから注目の2〜3件を取り上げ、技術の革新性やビジネス・生活がどう変わるか、ワクワクする未来や課題を二人で熱くディスカッションしてください。

--- テックニュース一覧 ---
{tech_text}
--------------------------

長さの目安: 約2,000文字〜2,200文字の最も濃密な掛け合い。
"""
    tech_res = call_gemini(client, prompt_tech)

    # --- チャプター5: エンディング (約1.5〜2分、約500文字) ---
    print("チャプター5: エンディング対話を生成中...")
    prompt_ending = f"""{system_context}

番組のエンディングトークです。
本日取り上げた国内・海外・テックの全体の総括や、二人のちょっとした雑談（朝なら「今日も一日頑張りましょう！」、夕方なら「今日も一日お疲れ様でした、良い夜を」など）、次回の案内（明日の朝便/夕便もお楽しみに）を入れて締めくくってください。
長さの目安: 約500文字程度（KeitaとNanamiの掛け合いで6〜8往復程度）。
"""
    ending_res = call_gemini(client, prompt_ending)

    # 全対話テキストの合体とパース
    combined_raw_text = f"{opening_res}\n{domestic_res}\n{world_res}\n{tech_res}\n{ending_res}"

    for line in combined_raw_text.split("\n"):
        line = line.strip()
        if not line:
            continue
        # "Keita:" や "Nanami:" の抽出
        match = re.match(r"^(Keita|Nanami|ケイタ|ナナミ)[:：]\s*(.+)$", line, re.IGNORECASE)
        if match:
            spk_raw = match.group(1).lower()
            speaker = "Keita" if "kei" in spk_raw or "ケイ" in spk_raw else "Nanami"
            text = match.group(2).strip()
            # 記号除去
            text = re.sub(r"[\*#_`]", "", text)
            if text:
                all_dialogue_lines.append({"speaker": speaker, "text": text})

    # --- 6. Markdownレポートの生成 ---
    print("Markdown サマリーレポートを生成中...")
    prompt_md = f"""あなたは敏腕ニュースエディターです。
本日（{target_date}）の{edition_label}で配信したポッドキャストのWeb掲載用まとめ記事（Markdown）を作成してください。

--- 国内ニュース ---
{domestic_text}
--- 海外ニュース ---
{world_text}
--- テックニュース ---
{tech_text}

以下の構成で美しく分かりやすいMarkdownを作成してください:
# 🎙 {target_date} {edition_label}：デイリートピック・ポッドキャスト（20分）

## 📌 本日のハイライト（1分でわかる要点）
- 各ジャンルの最も重要なポイントを箇条書き

## 🇯🇵 国内ニュース深掘り
- 主要トピックの解説と論点

## 🌍 海外・国際情勢
- 世界の注目トピックと背景

## 💻 最新テック・AIトレンド
- テクノロジーの注目動向と考察
"""
    markdown_report = call_gemini(client, prompt_md)

    return markdown_report, all_dialogue_lines
