import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import re

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


DATA_PATH = "../data/raw_data/"

BASE_URLS = [
    "https://vnexpress.net/suc-khoe",
    "https://vnexpress.net/giai-tri"
]

HEADERS = {
    "User-Agent": "Mozilla/5.0"
}


# ---------------------------
# Khởi tạo Selenium (1 driver duy nhất)
# ---------------------------
def init_driver():

    chrome_options = Options()
    chrome_options.add_argument("--headless=new")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")

    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()),
        options=chrome_options
    )

    return driver


# ---------------------------
# Lấy số comment từ DOM
# ---------------------------
def get_comment_count(driver):

    try:

        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

        wait = WebDriverWait(driver, 3)

        element = wait.until(
            EC.presence_of_element_located((By.ID, "total_comment"))
        )

        wait.until(lambda d: element.text.strip().isdigit())

        return int(element.text.strip())

    except:
        return 0


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

                href = a["href"]

                if "vnexpress.net" in href and href.endswith(".html"):
                    urls.append(href)

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
def crawl_article(driver, url):

    try:

        driver.get(url)

        soup = BeautifulSoup(driver.page_source, "html.parser")

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
        author_tag = soup.find('span', class_='author_mail')
        data['author'] = author_tag.get_text(strip=True) if author_tag else None

        if not data['author']:

            authors = soup.find('p', class_='Normal', style='text-align:right;')

            if not authors:
                authors = soup.find('p', class_='Normal', style='align: right;')

            if not authors:
                last_p = soup.select("article p.Normal")
                if last_p:
                    authors = last_p[-1]

            if authors:

                strong = authors.find('strong')

                if strong:
                    data['author'] = strong.get_text(strip=True)
                else:
                    data['author'] = authors.get_text(strip=True)

            else:
                data['author'] = "Không xác định"

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
                data['group'] = cats[0]
                data['category'] = cats[1] if len(cats) > 1 else cats[0]
            else:
                data['group'] = "Khác"
                data['category'] = "Khác"

        else:

            data["group"] = "Khác"
            data["category"] = "Khác"

        # comments
        data["nums_of_comments"] = get_comment_count(driver)

        data["url"] = url

        return data

    except Exception as e:

        print("Error:", url, e)

        return None


# ---------------------------
# Crawl tất cả bài viết
# ---------------------------
def crawl_all_articles(urls):

    driver = init_driver()

    first = True

    saved_urls = []

    with open(DATA_PATH + "vnexpress_raw_data.csv", "w", encoding="utf-8-sig") as f:

        for i, url in enumerate(urls):

            print(f"Crawling {i+1}/{len(urls)}")

            data = crawl_article(driver, url)

            if not data:
                continue

            df = pd.DataFrame([data])

            df.to_csv(
                f,
                index=False,
                header=first,
                mode="a"
            )

            saved_urls.append(url)

            first = False

            time.sleep(0.5)

    driver.quit()

    return saved_urls


# ---------------------------
# Main pipeline
# ---------------------------
def crawl_data():

    urls = get_all_urls()

    success_urls = crawl_all_articles(urls)

    pd.DataFrame(success_urls, columns=["url"]).to_csv(
        DATA_PATH + "vnexpress_urls.csv",
        index=False,
        encoding="utf-8-sig"
    )

    print("Saved:", len(success_urls), "urls")


if __name__ == "__main__":

    crawl_data()