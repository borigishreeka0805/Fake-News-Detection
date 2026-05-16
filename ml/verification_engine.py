import requests
import re
from concurrent.futures import ThreadPoolExecutor

NEWS_API_KEY = "4624f62f1e9e4fbd80402a71b187a55c"


# ------------------------
# Trusted domains
# ------------------------

trusted_sources = [
    "bbc.com",
    "reuters.com",
    "thehindu.com",
    "theguardian.com",
    "nasa.gov",
    "nature.com",
    "nytimes.com",
    "washingtonpost.com"
]


def check_trusted_source(url):

    if not url:
        return None

    for source in trusted_sources:

        if source in url.lower():

            return True

    return False

def check_fake_domain(url):

    fake_sources = [
        "worldnewsdailyreport.com",
        "empirenews.net",
        "nationalreport.net",
        "huzlers.com",
        "theonion.com"
    ]

    for site in fake_sources:
        if site in url:
            return True

    return False
# ------------------------
# Extract keywords
# ------------------------

def extract_keywords(text):

    words = re.findall(r"\b[A-Za-z]{4,}\b", text.lower())

    words = list(set(words))

    return " ".join(words[:6])


# ------------------------
# NewsAPI verification
# ------------------------

def check_newsapi(text):

    query = extract_keywords(text)

    url = f"https://newsapi.org/v2/everything?q={query}&language=en&apiKey={NEWS_API_KEY}"

    try:

        r = requests.get(url, timeout=3)

        data = r.json()

        return data.get("totalResults", 0)

    except:

        return 0


# ------------------------
# Google News RSS
# ------------------------

def check_google_news(text):

    query = extract_keywords(text)

    url = f"https://news.google.com/rss/search?q={query}"

    try:

        r = requests.get(url, timeout=3)

        return r.text.count("<item>")

    except:

        return 0


# ------------------------
# Fact-check patterns
# ------------------------

def fact_check_score(text):

    suspicious = [

        "miracle cure",
        "secret government",
        "hidden discovery",
        "doctors hate this",
        "scientists shocked",
        "instant cure",
        "government hiding",
        "aliens discovered",
        "shocking truth",
        "what doctors don't tell you"
    ]

    score = 0

    text = text.lower()

    for s in suspicious:

        if s in text:

            score += 20

    return score


# ------------------------
# Run verification in parallel
# ------------------------

def run_verification(text):

    with ThreadPoolExecutor(max_workers=3) as executor:

        newsapi_future = executor.submit(check_newsapi, text)

        google_future = executor.submit(check_google_news, text)

        fact_future = executor.submit(fact_check_score, text)

        newsapi_hits = newsapi_future.result()

        google_hits = google_future.result()

        fact_score = fact_future.result()

    return newsapi_hits, google_hits, fact_score