"""設定ファイル（config.yaml）に基づいてニュースやトピックをジャンル別に取得するモジュール。
"""

import feedparser
from typing import List, Dict, Any, Optional
from config_loader import load_config

def fetch_feed_articles(feed_list: List[Dict[str, str]], limit_per_feed: int = 4) -> List[Dict[str, str]]:
    """指定されたフィードリストから記事を取得し、重複を除外してリストを返す。"""
    articles = []
    seen_titles = set()
    user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"

    for feed_info in feed_list:
        feed_name = feed_info.get("name", "ニュース")
        url = feed_info.get("url", "")
        if not url:
            continue
        try:
            parsed = feedparser.parse(url, agent=user_agent)
            count = 0
            for entry in parsed.entries:
                title = entry.get("title", "").strip()
                link = entry.get("link", "").strip()
                summary = entry.get("summary", "").strip()

                if not title or title in seen_titles:
                    continue

                seen_titles.add(title)
                articles.append({
                    "source": feed_name,
                    "title": title,
                    "link": link,
                    "summary": summary
                })
                count += 1
                if count >= limit_per_feed:
                    break
        except Exception as e:
            print(f"フィード取得エラー [{feed_name}]: {e}")

    return articles

def fetch_all_categories(config: Optional[Dict[str, Any]] = None) -> Dict[str, List[Dict[str, str]]]:
    """設定ファイルに定義された全カテゴリの記事を一括取得して辞書で返す。"""
    if config is None:
        config = load_config()

    categories_config = config.get("categories", {})
    results: Dict[str, List[Dict[str, str]]] = {}

    for cat_key, cat_data in categories_config.items():
        feeds = cat_data.get("feeds", [])
        limit = cat_data.get("limit_per_feed", 4)
        results[cat_key] = fetch_feed_articles(feeds, limit_per_feed=limit)

    return results
