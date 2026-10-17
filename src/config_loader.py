"""設定ファイル（config.yaml）を安全に読み込み、フォールバックを提供するモジュール。
"""

import os
from typing import Dict, Any

# 安全なフォールバック用デフォルト設定
DEFAULT_CONFIG: Dict[str, Any] = {
    "general": {
        "model": "gemini-3.8-flash",
        "target_duration_minutes": 20,
        "timezone": "Asia/Tokyo"
    },
    "speakers": {
        "host1": {
            "name": "Keita",
            "voice": "ja-JP-KeitaNeural",
            "role": "解説役（落ち着いたトーン、背景やポイントを解説）"
        },
        "host2": {
            "name": "Nanami",
            "voice": "ja-JP-NanamiNeural",
            "role": "進行役（明るく親しみやすい、素朴な疑問や相槌を挟む）"
        }
    },
    "editions": {
        "morning": {
            "trigger_hour_limit": 13,
            "greeting": "おはようございます！",
            "tone": "今日1日の動きを見据えたエネルギッシュなトーン"
        },
        "evening": {
            "trigger_hour_limit": 24,
            "greeting": "お疲れ様です！",
            "tone": "今日1日の出来事を振り返りリラックスして聴けるトーン"
        }
    },
    "categories": {
        "domestic": {
            "name": "国内ニュース",
            "limit_per_feed": 4,
            "feeds": [
                {"name": "Yahoo!ニュース (主要)", "url": "https://news.yahoo.co.jp/rss/topics/top-picks.xml"},
                {"name": "Google News (日本・国内)", "url": "https://news.google.com/rss/headlines/section/topic/NATION?hl=ja&gl=JP&ceid=JP:ja"}
            ]
        },
        "world": {
            "name": "海外・国際情勢",
            "limit_per_feed": 4,
            "feeds": [
                {"name": "Google News (国際)", "url": "https://news.google.com/rss/headlines/section/topic/WORLD?hl=ja&gl=JP&ceid=JP:ja"},
                {"name": "BBC News (日本語版)", "url": "https://feeds.bbci.co.uk/japanese/rss.xml"}
            ]
        },
        "tech": {
            "name": "最新テック・AIトレンド",
            "limit_per_feed": 4,
            "feeds": [
                {"name": "Google News (テクノロジー)", "url": "https://news.google.com/rss/headlines/section/topic/TECHNOLOGY?hl=ja&gl=JP&ceid=JP:ja"},
                {"name": "はてなブックマーク (テクノロジー人気エントリー)", "url": "https://b.hatena.ne.jp/hotentry/it.rss"}
            ]
        }
    }
}

def load_config(config_path: str = None) -> Dict[str, Any]:
    """config.yaml を読み込む。ファイルが存在しないかPyYAML未導入の場合はデフォルト設定を返す。"""
    if config_path is None:
        root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        config_path = os.path.join(root_dir, "config.yaml")
        if not os.path.exists(config_path):
            config_path = os.path.join(root_dir, "config.example.yaml")

    if not os.path.exists(config_path):
        return DEFAULT_CONFIG

    try:
        import yaml
        with open(config_path, "r", encoding="utf-8") as f:
            user_config = yaml.safe_load(f) or {}

        # デフォルト設定とマージ（欠けているキーを補完）
        merged = DEFAULT_CONFIG.copy()
        for k, v in user_config.items():
            if isinstance(v, dict) and k in merged:
                merged[k] = {**merged[k], **v}
            else:
                merged[k] = v
        return merged
    except Exception as e:
        print(f"config.yaml 読み込み警告: {e}。デフォルト設定を使用します。")
        return DEFAULT_CONFIG
