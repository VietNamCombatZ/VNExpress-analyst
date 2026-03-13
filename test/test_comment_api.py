import requests
import re

url = "https://vnexpress.net/thu-ky-dep-quen-tuoi-5045931.html"

headers = {
    "User-Agent": "Mozilla/5.0"
}

r = requests.get(url, headers=headers)

html = r.text

match = re.search(r'"total_comment":\s*(\d+)', html)

if match:
    print("Comment count:", match.group(1))
else:
    print("Comment count not found")