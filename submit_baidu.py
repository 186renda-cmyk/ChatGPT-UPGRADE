import requests

# 百度站长平台 API 配置
# 接口调用地址
api_url = "http://data.zz.baidu.com/urls?site=https://gpt-upgrade.top&token=MkpV4it8Aq1PaVbS"

# 需要提交的 URL 列表
# 务必确保这些链接是 UTF-8 编码，且每行一个
host = "gpt-upgrade.top"
url_list = [
    f"https://{host}/",
    f"https://{host}/privacy",
    f"https://{host}/terms",
    f"https://{host}/blog",
    f"https://{host}/blog/how-to-subscribe-chatgpt",
    f"https://{host}/blog/chatgpt-go-vs-plus",
    f"https://{host}/blog/chatgpt-plus-vs-pro"
]

# 构造请求体：每行一个 URL
payload = "\n".join(url_list)

print("正在向百度搜索资源平台提交以下 URL:")
for url in url_list:
    print(f"- {url}")

try:
    # 发送 POST 请求
    # 百度 API 要求 Content-Type 为 text/plain
    response = requests.post(
        api_url, 
        data=payload, 
        headers={"Content-Type": "text/plain"}
    )
    
    # 解析响应
    result = response.json()
    
    if "success" in result:
        print(f"\n✅ 提交成功！")
        print(f"成功推送条数: {result['success']}")
        print(f"当天剩余可推送条数: {result['remain']}")
        
        # 检查是否有非本站链接或非法链接
        if result.get("not_same_site"):
            print(f"⚠️ 非本站链接: {result['not_same_site']}")
        if result.get("not_valid"):
            print(f"⚠️ 不合法链接: {result['not_valid']}")
            
    else:
        print(f"\n❌ 提交失败")
        print(f"错误码: {result.get('error')}")
        print(f"错误信息: {result.get('message')}")

except Exception as e:
    print(f"\n❌ 发生错误: {e}")
