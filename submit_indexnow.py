import requests
import json
import xml.etree.ElementTree as ET
import os

# 配置信息
host = "gpt-upgrade.top"
key = "7b3d72e5dd7346fcb45156486fcb65d3"
key_location = f"https://{host}/{key}.txt"
sitemap_file = "sitemap.xml"

def get_urls_from_sitemap(file_path):
    """
    从 sitemap.xml 文件中提取所有 URL
    """
    url_list = []
    try:
        if not os.path.exists(file_path):
            print(f"❌ 找不到文件: {file_path}")
            return []
            
        tree = ET.parse(file_path)
        root = tree.getroot()
        
        # 处理 XML 命名空间
        namespace = {'ns': 'http://www.sitemaps.org/schemas/sitemap/0.9'}
        
        for url in root.findall('ns:url/ns:loc', namespace):
            if url.text:
                url_list.append(url.text.strip())
                
        print(f"✅ 成功从 {file_path} 提取到 {len(url_list)} 个 URL")
        return url_list
        
    except Exception as e:
        print(f"❌ 解析 sitemap.xml 时出错: {e}")
        return []

# 获取 URL 列表
url_list = get_urls_from_sitemap(sitemap_file)

if not url_list:
    print("⚠️ 未找到任何 URL，终止提交。")
    exit(1)

# 构造请求数据
data = {
    "host": host,
    "key": key,
    "keyLocation": key_location,
    "urlList": url_list
}

# IndexNow API 地址 (Bing 和 Yandex 共享)
api_url = "https://api.indexnow.org/indexnow"

print("\n正在向 IndexNow 提交以下 URL:")
for url in url_list:
    print(f"- {url}")

try:
    response = requests.post(api_url, json=data, headers={"Content-Type": "application/json; charset=utf-8"})
    
    if response.status_code == 200:
        print("\n✅ 提交成功！必应 (Bing) 将在近期抓取您的页面。")
    elif response.status_code == 202:
        print("\n✅ 请求已接受 (202)。IndexNow 正在处理。")
    else:
        print(f"\n❌ 提交失败。状态码: {response.status_code}")
        print(f"响应内容: {response.text}")

except Exception as e:
    print(f"\n❌ 发生错误: {e}")
