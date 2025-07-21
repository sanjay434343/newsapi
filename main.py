from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import feedparser
from datetime import datetime

app = FastAPI()

# Open CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"]
)

RSS_FEEDS = {
    "bbc": "https://feeds.bbci.co.uk/news/rss.xml",
    "reuters": "https://feeds.reuters.com/reuters/topNews",
    "guardian": "https://www.theguardian.com/world/rss",
    "npr": "https://feeds.npr.org/1001/rss.xml"
}

@app.get("/")
def root():
    return {
        "message": "📰 News Aggregator is running.",
        "endpoints": ["/news", "/news/today"],
        "sources": list(RSS_FEEDS.keys())
    }

def parse_feed(feed_url):
    return feedparser.parse(feed_url).entries

@app.get("/news")
def get_all_news():
    news = []
    for name, url in RSS_FEEDS.items():
        for item in parse_feed(url):
            news.append({
                "source": name,
                "title": item.get("title"),
                "link": item.get("link"),
                "published": item.get("published"),
                "summary": item.get("summary"),
            })
    return {
        "total": len(news),
        "news": news
    }

@app.get("/news/today")
def get_today_news():
    today = datetime.utcnow().date()
    today_news = []

    for name, url in RSS_FEEDS.items():
        for item in parse_feed(url):
            pub = item.get("published_parsed")
            if not pub:
                continue
            pub_date = datetime(*pub[:6]).date()
            if pub_date == today:
                today_news.append({
                    "source": name,
                    "title": item.get("title"),
                    "link": item.get("link"),
                    "published": item.get("published"),
                    "summary": item.get("summary"),
                })

    return {
        "date": str(today),
        "count": len(today_news),
        "news": today_news
    }
