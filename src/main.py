"""アプリケーションのエントリーポイント。
CLI引数の解析と初期化を行い、PodcastHandlerに処理を委譲します。
"""

import os
import sys
import argparse

# src ディレクトリを sys.path に確実に登録
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
if CURRENT_DIR not in sys.path:
    sys.path.insert(0, CURRENT_DIR)

from config_loader import load_config
from handler import PodcastHandler

def parse_args() -> argparse.Namespace:
    """コマンドライン引数を解析する。"""
    parser = argparse.ArgumentParser(description="Daily Topic Podcast Generator")
    parser.add_argument("--edition", choices=["morning", "evening", "auto"], default="auto",
                        help="Select edition: morning (朝) or evening (夕)")
    parser.add_argument("--dry-run", action="store_true",
                        help="Run topic fetching without calling Gemini API or Edge-TTS")
    parser.add_argument("--config", type=str, default=None,
                        help="Path to custom config.yaml")
    return parser.parse_args()

def main():
    """初期化とハンドラーの呼び出しのみを行うメイン関数。"""
    args = parse_args()
    config = load_config(args.config)

    handler = PodcastHandler(config)
    handler.run(edition=args.edition, dry_run=args.dry_run)

if __name__ == "__main__":
    main()
