import os
import sys
import glob
import re
from urllib.parse import urlparse, urljoin, unquote
from bs4 import BeautifulSoup
import requests
from colorama import init, Fore, Style
from collections import defaultdict
import concurrent.futures

# Initialize colorama
init(autoreset=True)

def load_config():
    """
    Parse index.html to get BASE_URL and keywords.
    """
    if not os.path.exists('index.html'):
        print(f"{Fore.RED}Error: index.html not found in current directory.")
        sys.exit(1)

    with open('index.html', 'r', encoding='utf-8') as f:
        soup = BeautifulSoup(f, 'html.parser')

    # Get BASE_URL
    canonical = soup.find('link', rel='canonical')
    base_url = None
    if canonical and canonical.get('href'):
        base_url = canonical['href']
        # Ensure trailing slash for base URL
        if not base_url.endswith('/'):
            base_url += '/'
    else:
        print(f"{Fore.YELLOW}Warning: <link rel='canonical'> not found in index.html. Using manual check recommended.")
        # Fallback or prompt? Requirement says "Prompt user manual check but continue".
        # We will assume a placeholder or empty if not found, but let's try to proceed without it 
        # or maybe assume it's the current dir if we were serving locally, but for static site audit, 
        # we really need the domain to check "full domain inclusion".
        # Let's set a dummy if missing to avoid crashes, but warn.
        base_url = "https://example.com/" 

    # Get Keywords
    meta_keywords = soup.find('meta', attrs={'name': 'keywords'})
    keywords = []
    if meta_keywords and meta_keywords.get('content'):
        keywords = [k.strip() for k in meta_keywords['content'].split(',')]

    return base_url, keywords

def get_all_html_files():
    """
    recursively find all html files
    """
    return [f for f in glob.glob('**/*.html', recursive=True)]

def resolve_url_to_file(url, current_file_path, base_url):
    """
    Resolve a URL found in current_file_path to a potential file on disk.
    Returns the absolute path to the file if it exists, else None.
    Also handles the mapping of /path/ -> /path/index.html
    """
    # Remove hash and query
    url = url.split('#')[0].split('?')[0]
    
    # Ignore empty or javascript:
    if not url or url.startswith('javascript:') or url.startswith('mailto:') or url.startswith('tel:'):
        return None

    # Handle absolute URLs that point to our own domain
    if url.startswith(base_url):
        path = url[len(base_url):]
        # Ensure it starts with / for consistency in logic below
        if not path.startswith('/'):
            path = '/' + path
    elif url.startswith('http://') or url.startswith('https://'):
        # External link
        return None
    else:
        # Relative path
        if url.startswith('/'):
            path = url
        else:
            # Relative to current file
            # current_file_path is like 'blog/index.html'
            # url is like 'post-1'
            # dir is 'blog'
            current_dir = os.path.dirname(current_file_path)
            # We need to simulate how browser resolves this. 
            # If current file is blog/index.html, it is effectively at /blog/
            # So post-1 becomes /blog/post-1
            
            # Wait, if we are editing static files locally, we need to be careful.
            # Usually /blog/index.html serves as /blog/
            # /blog/post.html serves as /blog/post
            
            # Let's use simple path joining relative to the file's directory
            # If path starts with /, it is root relative (handled above)
            
            # Use os.path.normpath to resolve ../
            path = os.path.join('/', current_dir, url)
            path = os.path.normpath(path)
    
    # Now we have a root-relative path like /blog/post-1 or /about.html
    # We need to find the corresponding file.
    
    # Case 1: The path points directly to a file (e.g. /about.html)
    # Convert to local file path. Remove leading slash.
    local_path = path.lstrip('/')
    if os.path.isfile(local_path):
        return local_path
    
    # Case 2: The path is a clean URL (e.g. /about) -> check for about.html
    candidate = local_path + '.html'
    if os.path.isfile(candidate):
        return candidate
        
    # Case 3: Directory index (e.g. /blog/ -> blog/index.html)
    if os.path.isdir(local_path):
        candidate = os.path.join(local_path, 'index.html')
        if os.path.isfile(candidate):
            return candidate
            
    # Case 4: /blog -> blog/index.html (sometimes servers do this redirect)
    # But usually /blog means blog.html OR blog/index.html.
    # We checked blog.html in Case 2. Now check blog/index.html
    candidate = os.path.join(local_path, 'index.html')
    if os.path.isfile(candidate):
        return candidate

    return None

def check_link_health(urls):
    """
    Check status codes for a list of URLs using HEAD requests.
    Returns a dict {url: status_code}
    """
    results = {}
    
    def check_url(url):
        try:
            headers = {'User-Agent': 'SEOAuditBot/1.0'}
            # Use a timeout to avoid hanging
            response = requests.head(url, headers=headers, timeout=5, allow_redirects=True)
            return url, response.status_code
        except requests.RequestException:
            return url, 0 # 0 indicates failure/connection error

    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        future_to_url = {executor.submit(check_url, url): url for url in urls}
        for future in concurrent.futures.as_completed(future_to_url):
            url, status = future.result()
            results[url] = status
            
    return results

def main():
    base_url, keywords = load_config()
    print(f"正在审计站点: {Fore.CYAN}{base_url} {Style.RESET_ALL}| 核心词: {Fore.GREEN}{keywords}")

    html_files = get_all_html_files()
    
    # Statistics
    inbound_counts = {f: 0 for f in html_files}
    all_external_links = set()
    all_internal_links = set() # Store (source_file, url, line_no, type)
    
    score_deductions = {
        'dead_link': 0,
        '302': 0,
        'clean_url': 0,
        'orphan': 0
    }
    
    print(f"\n{Fore.YELLOW}=== 开始扫描文件 ({len(html_files)} 个) ===")
    
    # We need to cache link health checks to avoid re-checking same URL
    unique_urls_to_check = set()

    for file_path in html_files:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            soup = BeautifulSoup(content, 'html.parser')
            
            # Find all links
            links = soup.find_all('a', href=True)
            
            for link in links:
                href = link['href']
                
                # --- Path Strategy & Clean URL Checks ---
                
                # Check 1: Root Relative Strategy
                is_internal = False
                
                # Skip anchors, mailto, etc.
                if href.startswith('#') or href.startswith('mailto:') or href.startswith('tel:') or href.startswith('javascript:'):
                    continue
                
                if href.startswith(base_url):
                    # Contains full domain -> Warning
                    print(f"{Fore.YELLOW}[警告] 包含完整域名 (建议改为根路径): {href} in {file_path}")
                    is_internal = True
                    # Normalize for further checks
                    normalized_href = href[len(base_url)-1:] # Keep the leading slash
                elif not href.startswith('http') and not href.startswith('//'):
                    # Internal link
                    is_internal = True
                    normalized_href = href
                    
                    if not href.startswith('/'):
                        print(f"{Fore.YELLOW}[警告] 使用相对路径 (建议改为 / 开头): {href} in {file_path}")
                else:
                    # External link
                    all_external_links.add((file_path, href, str(link)))
                    unique_urls_to_check.add(href)
                    continue

                # If internal, proceed with Clean URL checks and Inbound counting
                if is_internal:
                    # Clean URL Checks
                    if normalized_href.endswith('.html') or normalized_href.endswith('.html/'):
                        # Exclude index.html special case if strictly mapped, but usually we want /
                        # Requirement: "Error: link ends with .html ... Prompt to change to /about"
                        # "Error: link contains /index.html ... Prompt to change to /"
                        
                        if 'index.html' in normalized_href:
                             print(f"{Fore.RED}[Clean URL ❌] 包含 index.html: {href} in {file_path} -> 建议改为 /")
                             score_deductions['clean_url'] += 1
                        else:
                             print(f"{Fore.RED}[Clean URL ❌] 包含 .html: {href} in {file_path} -> 建议移除后缀")
                             score_deductions['clean_url'] += 1
                    
                    # Resolve to file for Inbound Counting
                    target_file = resolve_url_to_file(normalized_href, file_path, base_url)
                    if target_file:
                        if target_file in inbound_counts:
                            inbound_counts[target_file] += 1
                    
                    # Add to health check regardless of local existence (check live status)
                    # We need to construct the full URL relative to the current file's location
                    # If href starts with /, it is root relative. urljoin handles this (base + /foo -> base/foo)
                    # If href is relative (e.g. "foo"), urljoin(base, "foo") -> base/foo. 
                    # But if we are in blog/index.html, base should be .../blog/
                    
                    if normalized_href.startswith('/'):
                         full_url = urljoin(base_url, normalized_href)
                    else:
                         # Relative path
                         current_dir = os.path.dirname(file_path)
                         # Construct base for this directory
                         # Ensure trailing slash for directory base
                         dir_base = urljoin(base_url, current_dir if current_dir else '')
                         if not dir_base.endswith('/'):
                             dir_base += '/'
                         full_url = urljoin(dir_base, normalized_href)
                         
                    unique_urls_to_check.add(full_url)

    # --- External Link Audit ---
    print(f"\n{Fore.BLUE}=== 外链审计 ===")
    for file_path, href, link_tag_str in all_external_links:
        # Simple string check for rel attributes
        # Re-parse the tag string or just check original tag object attributes if we stored them?
        # We stored the string representation, but we can't easily parse it back without context.
        # Let's trust the 'link' object from the loop if we were inside it.
        # To be accurate, I should have stored the BS4 tag object or checked inside the loop.
        # Let's redo the check or improve the loop structure.
        pass 
    
    # Better approach: Check rel in the main loop or here if we store data.
    # Let's check in main loop but for the report we need to output.
    # I'll just iterate files again? No, that's inefficient. 
    # Let's do a quick pass inside the main loop for rel check.
    # Wait, I didn't implement the rel check inside the loop.
    # Let's fix the main loop to check rel for external links.
    
    # --- Link Health Check ---
    print(f"\n{Fore.BLUE}=== 链路健康度检测 (检测 {len(unique_urls_to_check)} 个链接) ===")
    url_statuses = check_link_health(list(unique_urls_to_check))
    
    for url, status in url_statuses.items():
        if status == 200:
            pass # OK
        elif status == 301:
            print(f"{Fore.YELLOW}[301 Redirect] {url}")
        elif status in [302, 307]:
            print(f"{Fore.RED}[{status} Temp Redirect] {url} -> 权重不传递，必须修复")
            score_deductions['302'] += 1
        elif status == 404 or status >= 500 or status == 0:
            print(f"{Fore.RED}[{status} Dead Link] {url}")
            score_deductions['dead_link'] += 1

    # --- Inbound Links / Orphans ---
    print(f"\n{Fore.BLUE}=== 权重传递与孤岛页面 ===")
    
    # Top Pages
    sorted_pages = sorted(inbound_counts.items(), key=lambda x: x[1], reverse=True)
    print(f"{Fore.WHITE}Top 10 Pages by Inbound Links:")
    for page, count in sorted_pages[:10]:
        print(f"  {count}: {page}")
        
    # Orphans
    orphans = [p for p, c in inbound_counts.items() if c == 0 and p != 'index.html']
    if orphans:
        print(f"\n{Fore.RED}孤岛页面 (Orphans) - 入度为 0:")
        for o in orphans:
            print(f"  {o}")
            score_deductions['orphan'] += 1
    else:
        print(f"\n{Fore.GREEN}无孤岛页面。")

    # --- External Link Rel Check (Refined) ---
    # We need to re-scan for this specific check to be clean or do it in the first pass.
    # I will just re-open files quickly as it is fast for text scan.
    print(f"\n{Fore.BLUE}=== 外链 Rel 属性检查 ===")
    for file_path in html_files:
        with open(file_path, 'r', encoding='utf-8') as f:
            soup = BeautifulSoup(f.read(), 'html.parser')
            for link in soup.find_all('a', href=True):
                href = link['href']
                if href.startswith('http') and not href.startswith(base_url):
                    rel = link.get('rel', [])
                    if 'nofollow' not in rel and 'noopener' not in rel:
                        # Requirement: check if contains nofollow OR noopener
                        # Usually for SEO we want nofollow for untrusted, but noopener is for security.
                        # The requirement says "check if contains rel=nofollow OR rel=noopener".
                        # If neither, warn? 
                        # Requirement text: "Check ... whether contains ...". Implicitly implies warning if missing.
                        print(f"{Fore.YELLOW}[Security/SEO] 外链缺失 rel='nofollow' 或 'noopener': {href} in {file_path}")

    # --- Final Score ---
    final_score = 100
    final_score -= (score_deductions['dead_link'] * 10)
    final_score -= (score_deductions['302'] * 5)
    final_score -= (score_deductions['clean_url'] * 2)
    final_score -= (score_deductions['orphan'] * 5)
    
    if final_score < 0: final_score = 0
    
    print(f"\n{Fore.MAGENTA}=== 审计完成 ===")
    print(f"最终评分: {Style.BRIGHT}{final_score}/100")
    print("扣分详情:", score_deductions)

if __name__ == "__main__":
    main()
