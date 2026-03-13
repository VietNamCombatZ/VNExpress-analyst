import re
from bs4 import BeautifulSoup

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


# ---------------------------
# Khởi tạo Selenium
# ---------------------------
def init_driver():

    chrome_options = Options()
    chrome_options.add_argument("--headless")  # chạy không mở browser
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

        wait = WebDriverWait(driver, 0.5)

        element = wait.until(
            EC.presence_of_element_located((By.ID, "total_comment"))
        )

        wait.until(lambda d: element.text.strip().isdigit())

        return int(element.text.strip())

    except:
        return 0



# ---------------------------
# Crawl bài viết
# ---------------------------
def crawl_article(url):

    driver = init_driver()

    try:

        driver.get(url)

        html = driver.page_source

        soup = BeautifulSoup(html, "html.parser")

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

        # comment count
        data["nums_of_comments"] = get_comment_count(driver)

        data["url"] = url

        driver.quit()

        return data

    except Exception as e:

        driver.quit()
        print("Crawl error:", e)


# ---------------------------
# Test
# ---------------------------
if __name__ == "__main__":

    # test_url = "https://vnexpress.net/thu-ky-dep-quen-tuoi-5045931.html"
    test_url = "https://vnexpress.net/dan-hoa-hau-dien-ao-dai-tren-pho-di-bo-nguyen-hue-5047609.html"

    article = crawl_article(test_url)

    print("\n===== RESULT =====\n")

    for k, v in article.items():

        if k == "content":
            print(k, ":", v[:200], "...")

        else:
            print(k, ":", v)
