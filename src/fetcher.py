"""ニュースやトピックのRSSフィードを取得・抽出するモジュール。
"""

import feedparser
import urllib.parse
from typing import List, Dict

# デフォルトのトピックソース（日本のテクノロジー・ITトレンドRSS）
DEFAULT_FEEDS = [
    {
        "name": "Google News (テクノロジー)",
        "url": "https://news.google.com/rss/headlines/section/topic/TECHNOLOGY?hl=ja&gl=JP&ceid=JP:ja"
    },
    {
        "name": "はてなブックマーク (テクノロジー人気エントリー)",
        "url": "https://b.hatena.ne.jp/hotentry/it.rss"
    }
]

def fetch_topics(limit_per_feed: int = 5) -> List[Dict[str, str]]:
    """設定されたフィードから最新記事を取得し、重複を除外してリストを返す。"""
    articles = []
    seen_titles = set()

    for feed_info in DEFAULT_FEEDS:
        feed_name = feed_info["name"]
        url = feed_info["url"]
        try:
            parsed = feedparser.parse(url)
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
            print(f"Error fetching {feed_name}: {e}")

    return articles
