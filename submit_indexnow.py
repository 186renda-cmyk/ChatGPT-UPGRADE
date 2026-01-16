import requests
import json

# 配置信息
host = "gpt-upgrade.top"
key = "7b3d72e5dd7346fcb45156486fcb65d3"
key_location = f"https://{host}/{key}.txt"

# 需要提交的 URL 列表
url_list = [
    f"https://{host}/",
    f"https://{host}/privacy",
    f"https://{host}/terms",
    f"https://{host}/blog",
    f"https://{host}/blog/how-to-subscribe-chatgpt",
    f"https://{host}/blog/chatgpt-go-vs-plus",
    f"https://{host}/blog/chatgpt-plus-vs-pro"
]

# 构造请求数据
data = {
    "host": host,
    "key": key,
    "keyLocation": key_location,
    "urlList": url_list
}

# IndexNow API 地址 (Bing 和 Yandex 共享)
api_url = "https://api.indexnow.org/indexnow"

print("正在向 IndexNow 提交以下 URL:")
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
