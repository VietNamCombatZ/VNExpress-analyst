import selenium.webdriver # type: ignore
from selenium.webdriver.chrome.service import Service   # type: ignore
from selenium.webdriver.chrome.options import Options # type: ignore
from selenium.webdriver.support.ui import WebDriverWait # type: ignore
from selenium.webdriver.support import expected_conditions as EC # type: ignore
from selenium.webdriver.common.by import By # type: ignore
from tenacity import retry, stop_after_attempt, wait_fixed # type: ignore
from bs4 import BeautifulSoup # type: ignore
import requests 
from pprint import pprint
import pandas as pd # type: ignore
from queue import Queue
import threading

import platform

def get_service():
    system = platform.system()

    if system == "Windows":
        drive_path = "C:\\ChromeDriver\\chromedriver.exe"
        return Service(executable_path=drive_path)

    elif system == "Darwin":   # macOS
        return Service()       # Selenium tự tìm chromedriver

    elif system == "Linux":
        return Service()

    else:
        return Service()

def get_chrome_options():
  chrome_options = Options()
  chrome_options.add_argument("--headless=new")
  chrome_options.add_argument("--disable-gpu")
  chrome_options.add_argument("--no-sandbox")
  chrome_options.add_argument("--disable-dev-shm-usage")
  chrome_options.add_argument("--disable-extensions")
  chrome_options.add_argument("--disable-logging")
  chrome_options.add_argument("--log-level=3")
  chrome_options.add_argument("--disable-images")
  chrome_options.add_argument("--disable-notifications")
  chrome_options.add_argument("--disable-web-security")
  chrome_options.page_load_strategy = "eager"
  return chrome_options

def get_article_urls(page_url):
    response = requests.get(page_url)
    soup = BeautifulSoup(response.content, 'html.parser')
    articles = soup.find_all('h3', class_='title-news') + soup.find_all('h2', class_='title-news')
    urls = [a.find('a')['href'] for a in articles if a.find('a')]
    print(f"URL page: {page_url}, số url: {len(urls)}")
    return urls

# Lấy dữ liệu bài viết từ URL
@retry(stop=stop_after_attempt(3), wait=wait_fixed(5))
def get_article_data(url, driver):
      try:
          driver.get(url)
          WebDriverWait(driver, 5).until(
              EC.presence_of_element_located((By.TAG_NAME, "body"))
          )
          print(f"Loaded {url}")

          soup = BeautifulSoup(driver.page_source, 'html.parser')
          data = {}

          data['title'] = soup.find('h1', class_='title-detail').get_text(strip=True) if soup.find('h1', class_='title-detail') else None
          data['description'] = soup.find('p', class_='description').get_text(strip=True) if soup.find('p', class_='description') else None
          data['date'] = soup.find('span', class_='date').get_text(strip=True) if soup.find('span', class_='date') else None
          breadcrumb = soup.find('ul', class_='breadcrumb')
          if breadcrumb:
              category_links = breadcrumb.find_all('a')
              categories = [link.get_text(strip=True) for link in category_links if link]
              # Remove  category if it is "Công nghệ"
              categories = [cat for cat in categories if cat not in ['Sức khỏe', 'Giải trí']]
              # Remove duplicates
              categories = list(dict.fromkeys(categories))
              # Join with commas
              data['category'] = ', '.join(categories) if categories else 'Khác'
          else:
              print('else')
              data['category'] = soup.find('meta', itemprop='articleSection')['content'] if soup.find('meta', itemprop='articleSection') else 'Khác'
        
          data['content'] = "\n".join([p.get_text(strip=True) for p in soup.find_all('p', class_='Normal')]) or None
          img_tag = soup.find('img', class_='lazy')
          data['thumbnail'] = 'https:' + (img_tag.get('data-src') or img_tag.get('src')) if img_tag and not (img_tag.get('data-src') or img_tag.get('src')).startswith('http') else img_tag.get('data-src') or img_tag.get('src') if img_tag else None
          author_tag = soup.find('span', class_='author_mail')
          data['author'] = author_tag.get_text(strip=True) if author_tag else None
          if not data['author']:
            authors = soup.find('p', class_='Normal', style='text-align:right;')
            # if !authors:
            if not authors:
                authors = soup.find('p', class_='Normal', style='align: right;')
            if not authors:
                authors = soup.find('p', class_='Normal')[-1].get_text(strip=True)
            if authors:
                authors = authors.find('strong').get_text(strip=True) if authors.find('strong') else authors.get_text(strip=True)
                data['author'] = authors
            else:
                data['author'] = "Không xác định"
          data['tags'] = soup.find('meta', attrs={'name': 'its_tag'})['content'].split(', ') if soup.find('meta', attrs={'name': 'its_tag'}) else []
          data['url'] = url
          if "suc-khoe" in url:
            data['group'] = "Sức khỏe"
          elif "giai-tri" in url:
            data['group'] = "Giải trí"
          else:
            data['group'] = "Khác"
          total_comment_label = soup.find('label', id='total_comment')
        #   print(f"total_comment_label: {total_comment_label}")
          data['nums_of_comments'] = int(total_comment_label.get_text(strip=True)) if total_comment_label else 0

          return data
      except Exception as e:
          print(f"Error processing {url}: {e}")
          raise

def fetch_all_articles(unique_urls, max_workers=5):
    queue = Queue()
    for url in unique_urls:
        queue.put(url)

    results = []
    failed_urls = []

    def worker():
        with selenium.webdriver.Chrome(service=get_service(), options=get_chrome_options()) as browser:
            while not queue.empty():
                try:
                    url = queue.get_nowait()
                except Queue.Empty:
                    break
                try:
                    article_info = get_article_data(url, browser)
                    if article_info:
                        results.append(article_info)
                    else:
                        failed_urls.append(url)
                except Exception as e:
                    print(f"Failed to process {url}: {e}")
                    failed_urls.append(url)
                finally:
                    queue.task_done()

    threads = []
    for _ in range(max_workers):
        t = threading.Thread(target=worker)
        t.start()
        threads.append(t)

    for t in threads:
        t.join()

    print(f"Đã thu thập {len(results)} bài báo, thất bại {len(failed_urls)} URL")
    return results, failed_urls

base_url = ["https://vnexpress.net/suc-khoe",
    "https://vnexpress.net/giai-tri"]
def get_all_urls_page(base_url):
    all_urls_page = []
    for url in base_url:
        for i in range(1, 30):
            page_url = f"{url}-p{i}"
            article_urls = get_article_urls(page_url)
            all_urls_page.extend(article_urls)
    # return all_urls_page
    return list(set(all_urls_page))


base_url = ["https://vnexpress.net/suc-khoe",
    "https://vnexpress.net/giai-tri"]
def crawl_data():
    unique_urls = set(get_all_urls_page(base_url))
    print(f"Số lượng URL duy nhất: {len(unique_urls)}")

    with open('vnexpress_urls.csv', 'w', encoding='utf-8') as f:
        for url in unique_urls:
            f.write(url + '\n')

    # Lấy dữ liệu bài viết từ các URL
    all_data, failed_urls = fetch_all_articles(unique_urls, max_workers=5)
    print(f"Số bài báo thu thập được: {len(all_data)}")
    print(f"Số URL thất bại: {len(failed_urls)}")

    pprint(all_data[0])

    # re call failed urls
    if failed_urls:
        print(f"Retrying failed URLs: {len(failed_urls)}")
        retry_data, retry_failed_urls = fetch_all_articles(failed_urls, max_workers=5)
        all_data.extend(retry_data)
        failed_urls = retry_failed_urls
        print(f"After retry, failed URLs: {len(failed_urls)}")
        print(f"Total articles collected: {len(all_data)}")
        print(f"Total failed URLs: {len(failed_urls)}")
    else:
        print("No failed URLs to retry.")

    # xuất dữ liệu
    rows = []
    for article in all_data:
        if article is not None and isinstance(article, dict):
            title = article['title'] if article['title'] is not None else ''
            description = article['description'] if article['description'] is not None else ''
            date = article['date'] if article['date'] is not None else ''
            category = article['category'] if article['category'] is not None else ''
            thumbnail = article['thumbnail'] if article['thumbnail'] is not None else ''
            content = article['content'] if article['content'] is not None else ''
            author = article['author'] if article['author'] is not None else ''
            tags = ', '.join(article['tags'])  if article['tags'] is not None else ''
            group = article['group'] if article['group'] is not None else ''
            nums_of_comments = article['nums_of_comments'] if article['nums_of_comments'] is not None else 0
            url = article['url'] if article['url'] is not None else ''

            # Thêm dòng dữ liệu vào list
            rows.append({
                'title': title,
                'description': description,
                'date': date,
                'category': category,
                'thumbnail': thumbnail,
                'content': content,
                'author': author,
                'tags': tags,
                'group': group,
                'nums_of_comments': nums_of_comments,
                'url': url,
            })
        else:
            print(f"Skipping invalid article: {article}")

    df = pd.DataFrame(rows)
    df.to_csv('vnexpress_raw_data.csv', index=False, encoding='utf-8-sig')
    print("DataFrame đã được lưu thành file vnexpress_raw_data.csv")

if __name__ == "__main__":
    crawl_data()