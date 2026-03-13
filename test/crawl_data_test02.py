import requests
from bs4 import BeautifulSoup
import pandas as pd
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
import time

BASE_URLS = [
    "https://vnexpress.net/suc-khoe",
    "https://vnexpress.net/giai-tri"
]

HEADERS = {
    "User-Agent": "Mozilla/5.0"
}

# ---------------------------
# Lấy URL bài viết từ list page
# ---------------------------
def get_article_urls(page_url):

    try:
        res = requests.get(page_url, headers=HEADERS, timeout=10)
        soup = BeautifulSoup(res.text, "html.parser")

        articles = soup.find_all("h3", class_="title-news") + \
                   soup.find_all("h2", class_="title-news")

        urls = []

        for art in articles:
            a = art.find("a")
            if a and a.get("href"):
                urls.append(a["href"])

        print(f"{page_url} -> {len(urls)} urls")

        return urls

    except Exception as e:
        print("Error:", page_url, e)
        return []


# ---------------------------
# Lấy toàn bộ URL
# ---------------------------
def get_all_urls():

    all_urls = []

    for base in BASE_URLS:
        for i in range(1, 21):

            page_url = f"{base}-p{i}"
            urls = get_article_urls(page_url)

            all_urls.extend(urls)

            time.sleep(0.3)

    unique_urls = list(set(all_urls))

    print("Total unique urls:", len(unique_urls))

    return unique_urls


# ---------------------------
# Crawl nội dung bài viết
# ---------------------------
def crawl_article(url):

    try:

        res = requests.get(url, headers=HEADERS, timeout=10)
        soup = BeautifulSoup(res.text, "html.parser")

        data = {}

        # title
        title = soup.find("h1", class_="title-detail")
        data["title"] = title.get_text(strip=True) if title else None

        # description
        desc = soup.find("p", class_="description")
        data["description"] = desc.get_text(strip=True) if desc else None

        # date
        date = soup.find("span", class_="date")
        data["date"] = date.get_text(strip=True) if date else None

        # content
        paragraphs = soup.select("article p.Normal")

        seen = set()
        content = []

        for p in paragraphs:

            text = p.get_text(strip=True)

            if (
                text
                and text not in seen
                and not text.startswith("Video")
                and not text.startswith("Ảnh")
            ):
                seen.add(text)
                content.append(text)

        data["content"] = "\n".join(content)

        # thumbnail
        img = soup.find("meta", property="og:image")
        data["thumbnail"] = img["content"] if img else None

        # author
        author = soup.find("p", class_="author_mail")
        data["author"] = author.get_text(strip=True) if author else None

        # tags
        tag_meta = soup.find("meta", attrs={"name": "its_tag"})
        if tag_meta and tag_meta.get("content"):
            data["tags"] = tag_meta["content"]
        else:
            data["tags"] = None

        # group + category
        breadcrumb = soup.find("ul", class_="breadcrumb")

        if breadcrumb:

            cats = [a.get_text(strip=True) for a in breadcrumb.find_all("a")]

            if len(cats) > 0:
                data["group"] = cats[0]
                data["category"] = cats[1] if len(cats) > 1 else cats[0]
            else:
                data["group"] = None
                data["category"] = None

        else:

            data["group"] = None
            data["category"] = None

        # comments
        cmt = soup.find("label", id="total_comment")
        data["nums_of_comments"] = int(cmt.text) if cmt else 0

        data["url"] = url

        return data

    except Exception as e:

        print("Error:", url, e)
        return None


# ---------------------------
# Crawl đa luồng
# ---------------------------
def crawl_all_articles(urls):

    results = []

    with ThreadPoolExecutor(max_workers=10) as executor:

        for data in executor.map(crawl_article, urls):

            if data:
                results.append(data)

    return results


# ---------------------------
# Main pipeline
# ---------------------------
def crawl_data():

    urls = get_all_urls()

    articles = crawl_all_articles(urls)

    df = pd.DataFrame(articles)

    df = df.drop_duplicates(subset=["url"])

    df.to_csv("vnexpress_raw_data.csv", index=False, encoding="utf-8-sig")

    print("Saved:", len(df), "articles")


if __name__ == "__main__":
    crawl_data()