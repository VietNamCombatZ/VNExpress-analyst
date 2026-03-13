import requests
from bs4 import BeautifulSoup
import re

HEADERS = {
    "User-Agent": "Mozilla/5.0"
}

# ---------------------------
# Lấy số comment qua API
# ---------------------------
def get_comment_count(url):

    try:

        # lấy article_id từ URL
        match = re.search(r'-(\d+)\.html', url)

        if not match:
            return 0

        article_id = match.group(1)

        api = "https://usi-saas.vnexpress.net/index/get"

        params = {
            "objectid": article_id,
            "objecttype": 3,
            "siteid": 1000000,
            "limit": 1,
            "offset": 0
        }

        headers = {
            "User-Agent": "Mozilla/5.0",
            "Referer": url,
            "Accept": "application/json"
        }

        r = requests.get(api, params=params, headers=headers, timeout=10)

        if r.status_code != 200:
            return 0

        data = r.json()

        return data["data"]["totalitem"]

    except:
        return 0


# ---------------------------
# Crawl bài viết
# ---------------------------
def crawl_article(url):

    try:

        res = requests.get(url, headers=HEADERS, timeout=10)

        if res.status_code != 200:
            print("HTTP error:", res.status_code)
            return

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
        content = []

        for p in paragraphs:
            text = p.get_text(strip=True)
            if text:
                content.append(text)

        data["content"] = "\n".join(content)

        # author
        author = soup.find("p", class_="author_mail")
        data["author"] = author.get_text(strip=True) if author else None

        # thumbnail
        img = soup.find("meta", property="og:image")
        data["thumbnail"] = img["content"] if img and img.get("content") else None

        # tags
        tag_meta = soup.find("meta", attrs={"name": "its_tag"})
        data["tags"] = tag_meta.get("content") if tag_meta else None

        # breadcrumb
        breadcrumb = soup.find("ul", class_="breadcrumb")

        if breadcrumb:
            cats = [a.get_text(strip=True) for a in breadcrumb.find_all("a")]

            data["group"] = cats[0] if len(cats) > 0 else None
            data["category"] = cats[1] if len(cats) > 1 else None
        else:
            data["group"] = None
            data["category"] = None

        # comment count (API)
        data["nums_of_comments"] = get_comment_count(url)

        data["url"] = url

        return data

    except Exception as e:
        print("Crawl error:", e)


# ---------------------------
# Test
# ---------------------------
if __name__ == "__main__":

    test_url = "https://vnexpress.net/thu-ky-dep-quen-tuoi-5045931.html"

    article = crawl_article(test_url)

    print("\n===== RESULT =====\n")

    for k, v in article.items():

        if k == "content":
            print(k, ":", v[:200], "...")

        else:
            print(k, ":", v)