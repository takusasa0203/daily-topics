"""ニュースやトピックを「国内」「海外」「テック系」の3大ジャンル別に取得するモジュール。
"""

import feedparser
from typing import List, Dict

CATEGORIZED_FEEDS = {
    "domestic": [
        {
            "name": "Yahoo!ニュース (主要)",
            "url": "https://news.yahoo.co.jp/rss/topics/top-picks.xml"
        },
        {
            "name": "Google News (日本・国内)",
            "url": "https://news.google.com/rss/headlines/section/topic/NATION?hl=ja&gl=JP&ceid=JP:ja"
        }
    ],
    "world": [
        {
            "name": "Google News (国際)",
            "url": "https://news.google.com/rss/headlines/section/topic/WORLD?hl=ja&gl=JP&ceid=JP:ja"
        },
        {
            "name": "BBC News (日本語版)",
            "url": "https://feeds.bbci.co.uk/japanese/rss.xml"
        }
    ],
    "tech": [
        {
            "name": "Google News (テクノロジー)",
            "url": "https://news.google.com/rss/headlines/section/topic/TECHNOLOGY?hl=ja&gl=JP&ceid=JP:ja"
        },
        {
            "name": "はてなブックマーク (テクノロジー人気エントリー)",
            "url": "https://b.hatena.ne.jp/hotentry/it.rss"
        }
    ]
}

def fetch_feed_articles(feed_list: List[Dict[str, str]], limit_per_feed: int = 5) -> List[Dict[str, str]]:
    """指定されたフィードリストから記事を取得し、重複を除外してリストを返す。"""
    articles = []
    seen_titles = set()
    user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"

    for feed_info in feed_list:
        feed_name = feed_info["name"]
        url = feed_info["url"]
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
            print(f"Error fetching {feed_name}: {e}")

    return articles

def fetch_all_categories() -> Dict[str, List[Dict[str, str]]]:
    """「国内」「海外」「テック系」の全ジャンルの記事を一括取得して辞書で返す。"""
    return {
        "domestic": fetch_feed_articles(CATEGORIZED_FEEDS["domestic"], limit_per_feed=4),
        "world": fetch_feed_articles(CATEGORIZED_FEEDS["world"], limit_per_feed=4),
        "tech": fetch_feed_articles(CATEGORIZED_FEEDS["tech"], limit_per_feed=4)
    }
