import requests
from bs4 import BeautifulSoup

url = "https://vnexpress.net/phuong-phap-ngu-trua-giup-than-thai-doc-va-phuc-hoi-5048172.html"

headers = {
    "User-Agent": "Mozilla/5.0"
}

response = requests.get(url, headers=headers)

if response.status_code != 200:
    print("Không tải được trang")
    exit()

soup = BeautifulSoup(response.text, "html.parser")

data = {}

# tìm breadcrumb
breadcrumb = soup.find("ul", class_="breadcrumb")

if breadcrumb:
    links = breadcrumb.find_all('a')
    categories = [link.get_text(strip=True) for link in links]

    if len(categories) > 0:
            data['group'] = categories[0]
            data['category'] = categories[1] if len(categories) > 1 else categories[0]
    else:
        data['group'] = "Khác"
        data['category'] = "Khác"

else:
    data['group'] = "Khác"
    data['category'] = "Khác"

print("Group:", data['group'])
print("Category:", data['category'])