from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from typing import List
import feedparser
from datetime import datetime

app = FastAPI(
    title="News API",
    description="Aggregates news from multiple sources and provides structured content with keywords.",
    version="1.1.0"
)

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
    "engadget": "https://www.engadget.com/rss.xml",
    "nytimes": "https://rss.nytimes.com/services/xml/rss/nyt/HomePage.xml",
    "guardian": "https://www.theguardian.com/world/rss",
    "aljazeera": "https://www.aljazeera.com/xml/rss/all.xml",
    "washingtonpost": "http://feeds.washingtonpost.com/rss/world",
    "apnews": "https://apnews.com/rss/apf-topnews",
    "npr": "https://feeds.npr.org/1001/rss.xml",
    "abcnews": "https://abcnews.go.com/abcnews/topstories",
    "foxnews": "http://feeds.foxnews.com/foxnews/latest",
    "cbc": "https://www.cbc.ca/cmlink/rss-topstories",
    "skynews": "https://feeds.skynews.com/feeds/rss/world.xml",
    "hackernews": "https://hnrss.org/frontpage",
    "techcrunch": "http://feeds.feedburner.com/TechCrunch/",
    "wired": "https://www.wired.com/feed/rss",
    "bloomberg": "https://www.bloomberg.com/feed/podcast/etf-report.xml",
    "financialtimes": "https://www.ft.com/?format=rss"
}

class NewsItem(BaseModel):
    source: str
    title: str
    subtitle: str
    link: str
    published: str
    html: str
    keywords: List[str]

class NewsResponse(BaseModel):
    news: List[NewsItem]

def parse_feeds():
    from newspaper import Article
    news_list = []
    for source, url in RSS_FEEDS.items():
        feed = feedparser.parse(url)
        for entry in feed.entries[:5]:  # Limit to latest 5 per source
            article_url = entry.get("link", "")
            full_content = ""
            subtitle = entry.get("subtitle", "") or entry.get("summary", "")
            keywords = []
            if article_url:
                try:
                    article = Article(article_url)
                    article.download()
                    article.parse()
                    article.nlp()
                    full_content = article.text
                    keywords = article.keywords
                except Exception:
                    full_content = ""
                    keywords = []
            # Structure as HTML
            html = f"<h1>{entry.get('title', '')}</h1>"
            if subtitle:
                html += f"<h2>{subtitle}</h2>"
            html += f"<p>{full_content}</p>"
            news_item = {
                "source": source,
                "title": entry.get("title", ""),
                "subtitle": subtitle,
                "link": article_url,
                "published": entry.get("published", datetime.utcnow().isoformat()),
                "html": html,
                "keywords": keywords
            }
            news_list.append(news_item)
    # Sort by publish date if available
    news_list.sort(key=lambda x: x["published"], reverse=True)
    return news_list

@app.get("/", summary="Root endpoint", tags=["General"])
def root():
    """
    Welcome endpoint for the News API.
    """
    return {"message": "Welcome to the News API!"}

@app.get("/news", response_model=NewsResponse, summary="Get latest news", tags=["News"])
def get_news():
    """
    Returns the latest news articles from all sources, each with structured HTML and keywords.
    """
    news = parse_feeds()
    return {"news": news}

@app.get("/news/today", response_model=NewsResponse, summary="Get today's news", tags=["News"])
def get_today_news():
    """
    Returns only today's news articles from all sources.
    """
    today_str = datetime.utcnow().date().isoformat()
    filtered = [n for n in parse_feeds() if n["published"].startswith(today_str)]
    return {"news": filtered}

@app.get("/docs", response_class=HTMLResponse, include_in_schema=False)
def custom_docs():
    """
    Simple HTML frontend to view sample news.
    """
    news = parse_feeds()[:5]
    items_html = ""
    for item in news:
        items_html += f"""
        <div style='border:1px solid #ccc; margin:20px; padding:20px; border-radius:8px;'>
            {item['html']}
            <p><b>Source:</b> {item['source']} | <a href="{item['link']}" target="_blank">Read original</a></p>
            <p><b>Published:</b> {item['published']}</p>
            <p><b>Keywords:</b> {" , ".join(item['keywords'])}</p>
        </div>
        """
    html = f"""
    <html>
    <head>
        <title>News API Sample Frontend</title>
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <style>
            body {{ font-family: Arial, sans-serif; background: #f9f9f9; }}
            h1, h2 {{ margin-bottom: 0.5em; }}
            .container {{ max-width: 800px; margin: auto; }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>News API Sample Frontend</h1>
            <p>This is a sample frontend for the <b>News API</b>. Below are some sample articles:</p>
            {items_html}
            <hr>
            <p>Try the <a href="/docs" target="_blank">OpenAPI docs</a> for more info.</p>
        </div>
    </body>
    </html>
    """
    return HTMLResponse(content=html)

if __name__ == "__main__":
    import uvicorn
    import os
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True)
