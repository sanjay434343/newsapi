from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import feedparser
from datetime import datetime

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://laughing-eureka-xjx76p5969vfp56r-5500.app.github.dev"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ✅ List of news RSS feeds
RSS_FEEDS = {
    "bbc": "http://feeds.bbci.co.uk/news/rss.xml",
    "cnn": "http://rss.cnn.com/rss/edition.rss",
    "reuters": "http://feeds.reuters.com/reuters/topNews",
    "theverge": "https://www.theverge.com/rss/index.xml",
    "engadget": "https://www.engadget.com/rss.xml"
}


def parse_feeds():
    news_list = []
    for source, url in RSS_FEEDS.items():
        feed = feedparser.parse(url)
        for entry in feed.entries[:5]:  # Limit to latest 5 per source
            news_item = {
                "source": source,
                "title": entry.get("title", ""),
                "link": entry.get("link", ""),
                "summary": entry.get("summary", ""),
                "published": entry.get("published", datetime.utcnow().isoformat())
            }
            news_list.append(news_item)
    # Sort by publish date if available
    news_list.sort(key=lambda x: x["published"], reverse=True)
    return news_list


@app.get("/")
def root():
    return {"message": "Welcome to the News API!"}


@app.get("/news")
def get_news():
    news = parse_feeds()
    return {"news": news}


@app.get("/news/today")
def get_today_news():
    today_str = datetime.utcnow().date().isoformat()
    filtered = [n for n in parse_feeds() if n["published"].startswith(today_str)]
    return {"news": filtered}

if __name__ == "__main__":
    import uvicorn
    import os
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True)
