from bs4 import BeautifulSoup
import os

file_path = '/Users/xiaxingyu/Desktop/网站项目/ChatGPT/blog/index.html'

if os.path.exists(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        soup = BeautifulSoup(f.read(), 'html.parser')

    # 1. Cleanup Category Filters (Strict)
    # We found 4 of them earlier, so let's be aggressive
    # Class: flex flex-wrap justify-center gap-4 mb-12
    filters = soup.find_all('div', class_="flex flex-wrap justify-center gap-4 mb-12")
    print(f"Found {len(filters)} category filters. Removing ALL...")
    for div in filters:
        div.decompose()

    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(soup.prettify())
    
    print("Cleanup done.")
else:
    print("File not found.")
