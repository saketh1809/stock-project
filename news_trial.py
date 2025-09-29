import feedparser

def get_news_from_google():
    feed_url = "https://news.google.com/news/rss?hl=en-IN&gl=IN&ceid=IN:en"
    news_feed = feedparser.parse(feed_url)

    print("\n📰 Top News from Google News:\n")
    for i, entry in enumerate(news_feed.entries[:5], start=1):
        print(f"{i}. {entry.title}")
        print(f"   Link: {entry.link}\n")

get_news_from_google()