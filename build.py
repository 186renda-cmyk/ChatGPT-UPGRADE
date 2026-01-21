import os
import re
import json
import datetime
from bs4 import BeautifulSoup, Tag

# Configuration
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
BLOG_DIR = os.path.join(BASE_DIR, 'blog')
INDEX_PATH = os.path.join(BASE_DIR, 'index.html')
BLOG_INDEX_PATH = os.path.join(BLOG_DIR, 'index.html')
POSTS_PER_PAGE = 6

CATEGORIES = {
    'all': {'name': '全部', 'slug': 'all'},
    'reviews': {'name': '深度评测', 'slug': 'reviews'},
    'tutorials': {'name': '实操教程', 'slug': 'tutorials'},
    'news': {'name': '行业资讯', 'slug': 'news'},
}

def assign_category(meta):
    """Determine category based on keywords and title"""
    text = (meta['title'] + " " + " ".join(meta['keywords'])).lower()
    
    if any(k in text for k in ['vs', 'comparison', '评测', '对比', '体验', '区别', '深度', '报告', '测试']):
        return 'reviews'
    if any(k in text for k in ['教程', '指南', '攻略', '怎么', '开通', '注册', '充值', '购买', '订阅', '方法', '步骤', '如何']):
        return 'tutorials'
    if any(k in text for k in ['资讯', '更新', '发布', '限制', '额度', '价格', '方案', '优惠', '降价', '新闻', 'openai', 'google', 'gemini']):
        return 'news'
        
    return 'reviews' # Default fallback to reviews or news if ambiguous, or add 'insights'

# Varied Card Styles for Homepage/List Page
CARD_STYLES = [
    {
        'bg_gradient': 'from-indigo-900/20 to-purple-900/20',
        'hover_border': 'hover:border-indigo-500/30',
        'icon_shadow': 'drop-shadow-[0_0_15px_rgba(99,102,241,0.5)]',
        'text_highlight': 'group-hover:text-indigo-300',
        'link_color': 'text-indigo-400',
        # Sparkles (AI/Magic)
        'icon_path': 'M9.813 15.904L9 18.75l-.813-2.846a4.5 4.5 0 00-3.09-3.09L2.25 12l2.846-.813a4.5 4.5 0 003.09-3.09L9 5.25l.813 2.846a4.5 4.5 0 003.09 3.09L15.75 12l-2.846.813a4.5 4.5 0 00-3.09 3.09zM18.259 8.715L18 9.75l-.259-1.035a3.375 3.375 0 00-2.455-2.456L14.25 6l1.036-.259a3.375 3.375 0 002.455-2.456L18 2.25l.259 1.035a3.375 3.375 0 002.456 2.456L21.75 6l-1.035.259a3.375 3.375 0 00-2.456 2.456zM16.894 20.567L16.5 21.75l-.394-1.183a2.25 2.25 0 00-1.423-1.423L13.5 18.75l1.183-.394a2.25 2.25 0 001.423-1.423l.394-1.183.394 1.183a2.25 2.25 0 001.423 1.423l1.183.394-1.183.394a2.25 2.25 0 00-1.423 1.423z'
    },
    {
        'bg_gradient': 'from-cyan-900/20 to-blue-900/20',
        'hover_border': 'hover:border-cyan-500/30',
        'icon_shadow': 'drop-shadow-[0_0_15px_rgba(34,211,238,0.5)]',
        'text_highlight': 'group-hover:text-cyan-300',
        'link_color': 'text-cyan-400',
        # Cube (Tech/Structure)
        'icon_path': 'M21 7.5l-9-5.25L3 7.5m18 0l-9 5.25m9-5.25v9l-9 5.25M3 7.5l9 5.25M3 7.5v9l9 5.25m0-9v9'
    },
    {
        'bg_gradient': 'from-emerald-900/20 to-teal-900/20',
        'hover_border': 'hover:border-emerald-500/30',
        'icon_shadow': 'drop-shadow-[0_0_15px_rgba(16,185,129,0.5)]',
        'text_highlight': 'group-hover:text-emerald-300',
        'link_color': 'text-emerald-400',
        # BadgeCheck (Security/Verified)
        'icon_path': 'M9 12.75L11.25 15 15 9.75M21 12c0 1.268-.63 2.39-1.593 3.068a3.745 3.745 0 01-1.043 3.296 3.745 3.745 0 01-3.296 1.043A3.745 3.745 0 0112 21c-1.268 0-2.39-.63-3.068-1.593a3.746 3.746 0 01-3.296-1.043 3.745 3.745 0 01-1.043-3.296A3.745 3.745 0 013 12c0-1.268.63-2.39 1.593-3.068a3.745 3.745 0 011.043-3.296 3.746 3.746 0 013.296-1.043A3.746 3.746 0 0112 3c1.268 0 2.39.63 3.068 1.593a3.746 3.746 0 013.296 1.043 3.746 3.746 0 011.043 3.296A3.745 3.745 0 0121 12z'
    },
    {
        'bg_gradient': 'from-rose-900/20 to-pink-900/20',
        'hover_border': 'hover:border-rose-500/30',
        'icon_shadow': 'drop-shadow-[0_0_15px_rgba(244,63,94,0.5)]',
        'text_highlight': 'group-hover:text-rose-300',
        'link_color': 'text-rose-400',
        # Scale (Comparison/Vs)
        'icon_path': 'M12 3v17.25m0 0c-1.472 0-2.882.265-4.185.75M12 20.25c1.472 0 2.882.265 4.185.75M18.75 4.97A48.416 48.416 0 0012 4.5c-2.291 0-4.545.16-6.75.47m13.5 0c1.01.143 2.01.317 3 .52m-3-.52l2.62 10.726c.122.499-.106 1.028-.589 1.202a5.988 5.988 0 01-2.031.352 5.988 5.988 0 01-2.031-.352c-.483-.174-.711-.703-.59-1.202L18.75 4.971zm-16.5.52c.99-.203 1.99-.377 3-.52m0 0l2.62 10.726c.122.499-.106 1.028-.589 1.202a5.989 5.989 0 01-2.031.352 5.989 5.989 0 01-2.031-.352c-.483-.174-.711-.703-.59-1.202L5.25 4.971z'
    },
    {
        'bg_gradient': 'from-amber-900/20 to-orange-900/20',
        'hover_border': 'hover:border-amber-500/30',
        'icon_shadow': 'drop-shadow-[0_0_15px_rgba(245,158,11,0.5)]',
        'text_highlight': 'group-hover:text-amber-300',
        'link_color': 'text-amber-400',
        # LightBulb (Tutorial/Idea)
        'icon_path': 'M12 18v-5.25m0 0a6.01 6.01 0 001.5-.189m-1.5.189a6.01 6.01 0 01-1.5-.189m3.75 7.478a12.06 12.06 0 01-4.5 0m3.75 2.383a14.406 14.406 0 01-3 0M14.25 18v-.192c0-.983.658-1.823 1.508-2.316a7.5 7.5 0 10-7.517 0c.85.493 1.509 1.333 1.509 2.316V18'
    }
]

def clean_url(url):
    """
    Phase 1: Link Governance
    1. Remove .html suffix
    2. Enforce root path (start with /)
    3. Handle index.html -> /
    """
    if not url: return url
    if url.startswith(('http:', 'https:', 'mailto:', 'tel:', 'data:', '#')):
        return url
    
    # Handle anchors
    anchor = ''
    if '#' in url:
        parts = url.split('#', 1)
        url = parts[0]
        anchor = '#' + parts[1]
    
    # Remove .html
    if url.endswith('.html'):
        url = url[:-5]
    
    # Handle index variants
    if url.endswith('/index'):
        url = url[:-6]
    if url == 'index':
        url = ''
    if url.endswith('index.html'):
        url = url.replace('index.html', '')
        
    # Enforce root path
    if not url.startswith('/'):
        url = '/' + url
        
    # Ensure trailing slash for directory-like paths if desired, 
    # but for now let's just ensure no .html
    # If it ends with /, keep it.
    
    if url == '/': return '/' + anchor
    
    return url.rstrip('/') + anchor

def slugify(text):
    """Create URL-friendly slug from text"""
    # Lowercase
    text = text.lower()
    # Replace spaces with hyphens
    text = re.sub(r'\s+', '-', text)
    # Remove multiple hyphens
    text = re.sub(r'-+', '-', text)
    return text.strip('-')

def is_safe_zone(tag):
    """
    Check if tag is inside safe zones (aside, sticky-sidebar)
    Strictly forbidden to modify these areas.
    """
    for parent in tag.parents:
        if parent.name == 'aside':
            return True
        if parent.get('class') and 'sticky-sidebar' in parent.get('class'):
            return True
    return False

def fix_links(soup, replace_sales_links=False):
    """
    Apply Clean URL logic to all links, skipping safe zones.
    Also adds rel="noopener" to external links.
    Optionally replaces sales redirects with homepage anchors for blog posts.
    """
    # Fix Sidebar Promo Card Link (Special Case for ../go/gpt-topup)
    # The promo card in blog posts often uses a relative link that might escape standard logic
    for a in soup.find_all('a', href=True):
        if a['href'] == '../go/gpt-topup':
            a['href'] = '/go/gpt-topup'

    # Sales Link Replacement (Prevent Link Equity Loss)
    if replace_sales_links:
        sales_map = {
            '/go/gpt-topup': '/#pricing-high',
            '/go/gpt-shared': '/#pricing-low',
            '/go/gpt-exclusive': '/#pricing',
            # Handle potentially uncleaned relative paths
            '../go/gpt-topup': '/#pricing-high',
            '../go/gpt-shared': '/#pricing-low',
            '../go/gpt-exclusive': '/#pricing'
        }
        for a in soup.find_all('a', href=True):
            if a['href'] in sales_map:
                a['href'] = sales_map[a['href']]

    for a in soup.find_all('a', href=True):
        if is_safe_zone(a): continue
        
        href = a['href']
        # External Link Security/SEO
        if href.startswith(('http:', 'https:')):
            if 'gpt-upgrade.top' not in href and 'localhost' not in href:
                # Preserve existing rel if any, else add
                rel = a.get('rel', [])
                if isinstance(rel, str): rel = rel.split()
                if 'noopener' not in rel: rel.append('noopener')
                # Optional: Add nofollow for untrusted
                # if 'nofollow' not in rel: rel.append('nofollow') 
                a['rel'] = rel
                a['target'] = '_blank'
            continue
            
        a['href'] = clean_url(a['href'])
        
    # Also fix local images to be absolute paths
    for img in soup.find_all('img', src=True):
        if is_safe_zone(img): continue
        src = img['src']
        if not src.startswith(('http', 'data:')):
             if not src.startswith('/'):
                 # Ensure absolute path
                 img['src'] = '/' + src.lstrip('./')

def extract_layout():
    """Phase 3: Extract Header and Footer"""
    if not os.path.exists(INDEX_PATH):
        raise FileNotFoundError("index.html not found")
        
    with open(INDEX_PATH, 'r', encoding='utf-8') as f:
        soup = BeautifulSoup(f.read(), 'html.parser')
        
    nav = soup.find('nav', id='navbar')
    footer = soup.find('footer')
    
    if not nav or not footer:
        raise ValueError("Could not find <nav id='navbar'> or <footer> in index.html")
        
    # Clean links in the extracted layout
    fix_links(nav)
    fix_links(footer)
    
    return nav, footer

def get_article_metadata(soup, filename):
    title_tag = soup.find('title')
    title = title_tag.string.split('|')[0].strip() if title_tag else filename
    
    meta_desc = soup.find('meta', attrs={'name': 'description'})
    description = meta_desc['content'] if meta_desc else ""
    
    meta_keys = soup.find('meta', attrs={'name': 'keywords'})
    keywords = [k.strip().lower() for k in meta_keys['content'].split(',')] if meta_keys else []
    
    # Robust date extraction
    date = datetime.date.today().isoformat()
    # Try finding in meta first (custom or standard)
    meta_date = soup.find('meta', property='article:published_time')
    if meta_date:
        date = meta_date['content'][:10]
    else:
        # Try Regex in content
        text = soup.get_text()
        date_match = re.search(r'(\d{4}[.-]\d{2}[.-]\d{2})', text)
        if date_match:
            date = date_match.group(1).replace('.', '-')
        else:
            # Fallback to file mtime
            filepath = os.path.join(BLOG_DIR, filename)
            mtime = os.path.getmtime(filepath)
            date = datetime.date.fromtimestamp(mtime).isoformat()
            
    url = clean_url(f'/blog/{filename}')
    
    return {
        'filename': filename,
        'title': title,
        'description': description,
        'keywords': keywords,
        'date': date,
        'url': url
    }

def reorder_head(soup):
    """
    Reorganize <head> tags for better readability and standard compliance.
    Order: Charset -> Viewport -> Title -> Meta (Desc/Key/SEO) -> Links -> Styles -> Scripts
    """
    if not soup.head: return
    head = soup.head
    
    # Collect all tags
    tags = {
        'charset': [],
        'viewport': [],
        'title': [],
        'meta_desc': [],
        'meta_keys': [],
        'meta_seo': [], # robots, distribution, language
        'meta_og': [],
        'meta_other': [],
        'link_canonical': [],
        'link_alternate': [], # hreflang
        'link_icon': [],
        'link_css': [], # stylesheets, preconnect
        'style': [],
        'script_ld': [], # json-ld
        'script_other': [],
        'other': []
    }
    
    for tag in head.contents:
        if isinstance(tag, Tag):
            # Meta
            if tag.name == 'meta':
                if tag.get('charset'): tags['charset'].append(tag)
                elif tag.get('name') == 'viewport': tags['viewport'].append(tag)
                elif tag.get('name') == 'description': tags['meta_desc'].append(tag)
                elif tag.get('name') == 'keywords': tags['meta_keys'].append(tag)
                elif tag.get('name') in ['robots', 'distribution'] or tag.get('http-equiv') == 'content-language':
                    tags['meta_seo'].append(tag)
                elif tag.get('property', '').startswith('og:'): tags['meta_og'].append(tag)
                else: tags['meta_other'].append(tag)
            # Title
            elif tag.name == 'title': tags['title'].append(tag)
            # Link
            elif tag.name == 'link':
                rel = tag.get('rel', [])
                if isinstance(rel, list): rel = rel[0] if rel else ''
                
                if rel == 'canonical': tags['link_canonical'].append(tag)
                elif rel == 'alternate': tags['link_alternate'].append(tag)
                elif 'icon' in rel: tags['link_icon'].append(tag)
                elif rel == 'stylesheet' or 'preconnect' in rel or 'dns-prefetch' in rel:
                    tags['link_css'].append(tag)
                else: tags['other'].append(tag)
            # Style
            elif tag.name == 'style': tags['style'].append(tag)
            # Script
            elif tag.name == 'script':
                if tag.get('type') == 'application/ld+json': tags['script_ld'].append(tag)
                else: tags['script_other'].append(tag)
            else:
                tags['other'].append(tag)
                
    # Clear head
    head.clear()
    
    # Re-insert in order with comments/spacing
    order = [
        ('charset', None),
        ('viewport', None),
        ('title', None),
        ('meta_desc', None),
        ('meta_keys', None),
        ('meta_seo', 'SEO Config'),
        ('meta_og', 'Open Graph'),
        ('meta_other', None),
        ('link_canonical', 'Canonical'),
        ('link_alternate', 'Alternates'),
        ('link_icon', 'Favicon'),
        ('link_css', 'Styles & Fonts'),
        ('style', 'Inline Styles'),
        ('script_other', 'Scripts'),
        ('script_ld', 'Schema.org'),
        ('other', None)
    ]
    
    for key, comment in order:
        group = tags[key]
        if group:
            # Add section comment if needed (optional)
            # if comment: head.append(soup.new_string(f'\n    <!-- {comment} -->\n'))
            
            for tag in group:
                head.append(tag)
                head.append(soup.new_string('\n')) # Force newline for better formatting

def inject_favicons(soup):
    """Phase 2.5: Inject Standard Favicons"""
    if not soup.head:
        soup.insert(0, soup.new_tag('head'))
    
    head = soup.head
    
    # Remove existing icons
    for link in head.find_all('link'):
        rel = link.get('rel', [])
        if isinstance(rel, list): rel = ' '.join(rel)
        if 'icon' in rel or 'manifest' in rel or 'apple-touch-icon' in rel:
            link.decompose()
            
    # Inject new icons
    icons = [
        {'rel': 'apple-touch-icon', 'sizes': '180x180', 'href': '/assets/apple-touch-icon.png'},
        {'rel': 'icon', 'type': 'image/png', 'sizes': '32x32', 'href': '/assets/favicon-32x32.png'},
        {'rel': 'icon', 'type': 'image/png', 'sizes': '16x16', 'href': '/assets/favicon-16x16.png'},
        {'rel': 'manifest', 'href': '/assets/site.webmanifest'},
        {'rel': 'shortcut icon', 'href': '/assets/favicon.ico'}
    ]
    
    for icon_attrs in icons:
        link = soup.new_tag('link', **icon_attrs)
        head.append(link)

def inject_seo(soup, meta):
    """Phase 2: SEO Injection Engine"""
    if not soup.head:
        soup.insert(0, soup.new_tag('head'))
    
    head = soup.head
    
    # 1. Remove old SEO tags to avoid duplication
    tags_to_remove = [
        {'name': 'robots'},
        {'name': 'distribution'},
        {'http-equiv': 'content-language'},
        {'rel': 'canonical'},
        {'rel': 'alternate', 'hreflang': True},
        {'type': 'application/ld+json'}
    ]
    
    for attrs in tags_to_remove:
        # Construct filter args safely
        name = attrs.get('name')
        http_equiv = attrs.get('http-equiv')
        rel = attrs.get('rel')
        type_ = attrs.get('type')
        
        # Find and decompose
        if name:
            for tag in head.find_all('meta', attrs={'name': name}): tag.decompose()
        elif http_equiv:
            for tag in head.find_all('meta', attrs={'http-equiv': http_equiv}): tag.decompose()
        elif rel:
            for tag in head.find_all('link', attrs={'rel': rel}): tag.decompose()
        elif type_:
             for tag in head.find_all('script', attrs={'type': type_}): tag.decompose()
            
    # 2. Inject Global Chinese Positioning
    # <meta http-equiv="content-language" content="zh-CN" />
    tag = soup.new_tag('meta')
    tag['http-equiv'] = 'content-language'
    tag['content'] = 'zh-CN'
    head.append(tag)
    
    # Hreflang Matrix
    # x-default, zh, zh-CN -> Current Clean URL
    full_url = f"https://gpt-upgrade.top{meta['url']}"
    
    for lang in ['x-default', 'zh', 'zh-CN']:
        link = soup.new_tag('link')
        link['rel'] = 'alternate'
        link['hreflang'] = lang
        link['href'] = full_url
        head.append(link)
        
    # 3. Double Indexing Insurance
    # <meta name="robots" content="index, follow, max-image-preview:large" />
    tag = soup.new_tag('meta')
    tag['name'] = 'robots'
    tag['content'] = 'index, follow, max-image-preview:large'
    head.append(tag)
    
    # <meta name="distribution" content="global" />
    tag = soup.new_tag('meta')
    tag['name'] = 'distribution'
    tag['content'] = 'global'
    head.append(tag)
    
    # Canonical
    link = soup.new_tag('link')
    link['rel'] = 'canonical'
    link['href'] = full_url
    head.append(link)
    
    # 4. Structured Data
    # BlogPosting
    blog_schema = {
        "@context": "https://schema.org",
        "@type": "BlogPosting",
        "headline": meta['title'],
        "description": meta['description'],
        "datePublished": meta['date'],
        "dateModified": datetime.date.today().isoformat(),
        "author": {
            "@type": "Organization",
            "name": "GPT-Upgrade",
            "url": "https://gpt-upgrade.top"
        },
        "mainEntityOfPage": {
            "@type": "WebPage",
            "@id": full_url
        }
    }
    
    # BreadcrumbList
    breadcrumb_schema = {
        "@context": "https://schema.org",
        "@type": "BreadcrumbList",
        "itemListElement": [
            {
                "@type": "ListItem",
                "position": 1,
                "name": "首页",
                "item": "https://gpt-upgrade.top/"
            },
            {
                "@type": "ListItem",
                "position": 2,
                "name": "博客",
                "item": "https://gpt-upgrade.top/blog/"
            },
            {
                "@type": "ListItem",
                "position": 3,
                "name": meta['title'],
                "item": full_url
            }
        ]
    }
    
    script = soup.new_tag('script', type='application/ld+json')
    script.string = json.dumps([blog_schema, breadcrumb_schema], indent=2, ensure_ascii=False)
    head.append(script)
    
    # Reorder Head for perfect layout
    reorder_head(soup)

def inject_breadcrumbs(soup, meta):
    """Phase 3: Visual Breadcrumbs"""
    main = soup.find('main')
    if not main: return
    
    # Remove existing breadcrumbs
    for nav in main.find_all('nav', attrs={'aria-label': 'Breadcrumb'}):
        nav.decompose()
        
    breadcrumb_html = f'''
    <nav aria-label="Breadcrumb" class="mb-8 overflow-x-auto whitespace-nowrap">
        <ol class="flex items-center gap-2 text-sm text-gray-500">
            <li><a href="/" class="hover:text-white transition">首页</a></li>
            <li>/</li>
            <li><a href="/blog/" class="hover:text-white transition">博客</a></li>
            <li>/</li>
            <li class="text-gray-300" aria-current="page">{meta['title']}</li>
        </ol>
    </nav>
    '''
    main.insert(0, BeautifulSoup(breadcrumb_html, 'html.parser'))

def inject_related_posts(soup, current_meta, all_articles):
    """Phase 3: Smart Interlinking"""
    article = soup.find('article')
    if not article: return
    
    # Remove existing tags container if any (cleanup)
    for div in article.find_all('div', class_='tags-container'):
        div.decompose()
    
    # Remove existing related posts
    for div in article.find_all('div', class_='related-posts-container'):
        div.decompose()
        
    # Calculate similarity
    scores = []
    current_keywords = set(current_meta['keywords'])
    
    for other in all_articles:
        if other['filename'] == current_meta['filename']: continue
        other_keywords = set(other['keywords'])
        overlap = len(current_keywords.intersection(other_keywords))
        scores.append((overlap, other))
        
    scores.sort(key=lambda x: x[0], reverse=True)
    related = [x[1] for x in scores[:2]]
    
    # Fallback to recent if no overlap
    if len(related) < 2:
        for other in all_articles:
            if other['filename'] == current_meta['filename']: continue
            if other not in related:
                related.append(other)
                if len(related) >= 2: break
                
    if not related: return
    
    cards_html = ""
    for post in related:
        cards_html += f'''
        <a href="{post['url']}" class="block group p-5 rounded-2xl bg-white/5 hover:bg-white/10 transition border border-white/5">
            <div class="text-[10px] text-gray-500 mb-2 font-mono uppercase">Related Article</div>
            <h4 class="text-white font-bold mb-2 group-hover:text-cyan-300 transition line-clamp-2">{post['title']}</h4>
            <p class="text-xs text-gray-400 line-clamp-2">{post['description']}</p>
        </a>
        '''
        
    container_html = f'''
    <div class="mt-16 pt-10 border-t border-white/10 related-posts-container">
        <h3 class="text-lg font-bold text-white mb-6">推荐阅读</h3>
        <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
            {cards_html}
        </div>
    </div>
    '''
    
    article.append(BeautifulSoup(container_html, 'html.parser'))

def create_card_html(post, index):
    """Generate consistent card HTML for lists"""
    style = CARD_STYLES[index % len(CARD_STYLES)]
    return f'''
    <article class="group relative flex flex-col rounded-[2rem] bg-white/[0.02] border border-white/5 {style['hover_border']} overflow-hidden transition-all duration-300 hover:-translate-y-1">
        <a href="{post['url']}" class="absolute inset-0 z-10" aria-label="阅读文章"></a>
        <div class="h-48 bg-gradient-to-br {style['bg_gradient']} relative overflow-hidden">
            <div class="absolute inset-0 bg-[url('https://grainy-gradients.vercel.app/noise.svg')] opacity-20 mix-blend-overlay"></div>
            <div class="absolute inset-0 flex items-center justify-center opacity-20 group-hover:opacity-40 transition-opacity duration-500">
                <svg class="w-24 h-24 text-white {style['icon_shadow']}" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1" d="{style['icon_path']}"></path>
                </svg>
            </div>
        </div>
        <div class="p-8 flex flex-col flex-grow">
            <div class="flex items-center gap-3 text-xs text-gray-500 mb-4">
                <span>{post['date']}</span>
                <span class="w-1 h-1 rounded-full bg-gray-700"></span>
                <span>Article</span>
            </div>
            <h2 class="text-xl font-bold text-white mb-3 {style['text_highlight']} transition-colors">{post['title']}</h2>
            <p class="text-sm text-gray-400 leading-relaxed mb-6 flex-grow line-clamp-3">{post['description']}</p>
            <div class="flex items-center text-sm font-bold {style['link_color']} group-hover:translate-x-1 transition-transform">
                阅读全文 <svg class="w-4 h-4 ml-1" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 8l4 4m0 0l-4 4m4-4H3"></path></svg>
            </div>
        </div>
    </article>
    '''

def update_homepage(articles):
    """Update Homepage Latest News"""
    if not os.path.exists(INDEX_PATH): return
    with open(INDEX_PATH, 'r', encoding='utf-8') as f:
        soup = BeautifulSoup(f.read(), 'html.parser')
        
    blog_section = soup.find(id='blog')
    if not blog_section: return
    
    grid = blog_section.find('div', class_=re.compile(r'grid.*cols'))
    if not grid: return
    grid.clear()
    
    for i, post in enumerate(articles[:3]):
        style = CARD_STYLES[i % len(CARD_STYLES)]
        card_html = f'''
        <article class="group reveal relative rounded-[2rem] p-8 bg-white/[0.02] border border-white/5 {style['hover_border']} transition-all duration-300 flex flex-col h-full cursor-pointer">
            <a href="{post['url']}" class="absolute inset-0 z-30" aria-label="{post['title']}"></a>
            <div class="flex items-center justify-between mb-6">
                <div class="px-3 py-1 rounded-full bg-white/5 border border-white/10 text-xs font-bold text-gray-400">最新文章</div>
                <span class="text-xs text-gray-500">{post['date']}</span>
            </div>
            <h3 class="text-xl font-bold text-white mb-3 {style['text_highlight']} transition-colors">{post['title']}</h3>
            <p class="text-sm text-gray-400 leading-relaxed mb-6 flex-grow line-clamp-3">{post['description']}</p>
            <div class="flex items-center gap-2 text-sm font-medium {style['link_color']}">
                <span>阅读全文</span>
                <svg class="w-4 h-4 transition-transform group-hover:translate-x-1" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 8l4 4m0 0l-4 4m4-4H3"></path></svg>
            </div>
        </article>
        '''
        grid.append(BeautifulSoup(card_html, 'html.parser'))
        
    fix_links(soup)
    inject_favicons(soup)
    with open(INDEX_PATH, 'w', encoding='utf-8') as f: f.write(str(soup))

def update_blog_index(articles, layout_nav, layout_footer):
    """Rebuild /blog/ index with Client-Side Filtering & Pagination"""
    if not os.path.exists(BLOG_INDEX_PATH): return
    
    # 1. Prepare Template
    with open(BLOG_INDEX_PATH, 'r', encoding='utf-8') as f:
        template_html = f.read()
        
    soup = BeautifulSoup(template_html, 'html.parser')

    # --- CLEANUP: Remove existing generated elements ---
    # 1. Remove Category Filters
    target_filter_classes = {"flex", "flex-wrap", "justify-center", "gap-4", "mb-12"}
    for div in soup.find_all('div'):
        classes = div.get('class', [])
        if target_filter_classes.issubset(set(classes)):
             # Check content loose match
             text = div.get_text()
             if "全部" in text and "深度评测" in text:
                div.decompose()

    # 2. Remove Pagination (Static)
    target_pagination_classes = {"flex", "justify-center", "items-center", "gap-4", "mt-16"}
    for div in soup.find_all('div'):
        classes = div.get('class', [])
        if target_pagination_classes.issubset(set(classes)):
             if "页" in div.get_text() or "Page" in div.get_text():
                div.decompose()

    # 3. Remove Old Scripts
    for script in soup.find_all('script'):
        if script.string and 'const pageSize' in script.string:
            script.decompose()

    # --- A. Update Layout ---
    if soup.body:
        old_nav = soup.body.find('nav', id='navbar') or soup.body.find('nav')
        if old_nav: old_nav.decompose()
        
        current_nav = BeautifulSoup(str(layout_nav), 'html.parser')
        blog_link = current_nav.find('a', href=re.compile(r'^(?:/|#)blog/?$'))
        if blog_link: blog_link['href'] = '/blog/'
        soup.body.insert(0, current_nav)
        
        old_footer = soup.find('footer')
        if old_footer: old_footer.decompose()
        soup.body.append(BeautifulSoup(str(layout_footer), 'html.parser'))

    main = soup.find('main')
    if main:
        # --- B. Inject Client-Side Category Buttons ---
        intro = main.find('div', class_='text-center')
        
        # Use <button> instead of <a> for client-side action
        filter_html = '<div class="flex flex-wrap justify-center gap-4 mb-12">'
        for c_slug, c_info in CATEGORIES.items():
            # Default style (will be updated by JS)
            classes = "px-5 py-2 rounded-full bg-white/5 border border-white/10 text-gray-400 font-medium text-sm hover:bg-white/10 hover:text-white transition-all"
            filter_html += f'<button data-cat="{c_slug}" class="{classes}">{c_info["name"]}</button>'
        filter_html += '</div>'
        
        if intro:
            intro.insert_after(BeautifulSoup(filter_html, 'html.parser'))

        # --- C. Inject All Articles ---
        grid = main.find('div', class_=re.compile(r'grid.*cols'))
        if grid:
            grid.clear()
            for i, post in enumerate(articles):
                cat_slug = assign_category(post)
                # Create card
                card_soup = BeautifulSoup(create_card_html(post, i), 'html.parser')
                article_tag = card_soup.find('article')
                if article_tag:
                    article_tag['data-category'] = cat_slug
                    # Default hidden (JS will reveal)
                    article_tag['class'] = article_tag.get('class', []) + ['hidden']
                grid.append(article_tag)

    # --- D. Inject Client-Side Logic ---
    js_logic = """
    <script>
        document.addEventListener('DOMContentLoaded', () => {
            const pageSize = 6;
            const grid = document.querySelector('div[class*="grid-cols"]');
            if (!grid) return;
            
            const cards = Array.from(grid.querySelectorAll('article'));
            const filterButtons = Array.from(document.querySelectorAll('button[data-cat]'));
            
            // Create Pager UI
            const pager = document.createElement('div');
            pager.id = 'pager';
            pager.className = 'flex justify-center items-center gap-4 mt-16';
            pager.innerHTML = `
                <button id="prevPage" class="px-4 py-2 rounded-lg bg-white/5 border border-white/10 text-gray-400 hover:text-white hover:bg-white/10 transition disabled:opacity-50 disabled:cursor-not-allowed">上一页</button>
                <span id="pageInfo" class="text-gray-500 text-sm">第 1 页</span>
                <button id="nextPage" class="px-4 py-2 rounded-lg bg-white/5 border border-white/10 text-gray-400 hover:text-white hover:bg-white/10 transition disabled:opacity-50 disabled:cursor-not-allowed">下一页</button>
            `;
            grid.parentNode.appendChild(pager);

            const prevBtn = document.getElementById('prevPage');
            const nextBtn = document.getElementById('nextPage');
            const pageInfo = document.getElementById('pageInfo');

            let currentCat = new URLSearchParams(location.search).get('cat') || 'all';
            let currentPage = parseInt(new URLSearchParams(location.search).get('page') || '1', 10);

            function getFiltered() {
                if (currentCat === 'all') return cards;
                return cards.filter(c => c.getAttribute('data-category') === currentCat);
            }

            function render() {
                const filtered = getFiltered();
                const totalPages = Math.max(1, Math.ceil(filtered.length / pageSize));
                
                // Ensure page validity
                if (currentPage > totalPages) currentPage = totalPages;
                if (currentPage < 1) currentPage = 1;

                // Hide all first
                cards.forEach(c => c.classList.add('hidden'));

                // Show current slice
                const start = (currentPage - 1) * pageSize;
                const end = start + pageSize;
                const toShow = filtered.slice(start, end);
                toShow.forEach(c => c.classList.remove('hidden'));

                // Update UI
                pageInfo.textContent = `第 ${currentPage} / ${totalPages} 页`;
                prevBtn.disabled = currentPage <= 1;
                nextBtn.disabled = currentPage >= totalPages;

                // Update Buttons State
                filterButtons.forEach(b => {
                    const isActive = b.getAttribute('data-cat') === currentCat;
                    if (isActive) {
                        b.className = "px-5 py-2 rounded-full bg-indigo-500 text-white font-bold text-sm shadow-lg shadow-indigo-500/25 transition-all";
                    } else {
                        b.className = "px-5 py-2 rounded-full bg-white/5 border border-white/10 text-gray-400 font-medium text-sm hover:bg-white/10 hover:text-white transition-all";
                    }
                });
            }

            // Event Listeners
            filterButtons.forEach(b => {
                b.addEventListener('click', () => {
                    currentCat = b.getAttribute('data-cat');
                    currentPage = 1;
                    render();
                    updateUrl();
                });
            });

            prevBtn.addEventListener('click', () => {
                if (currentPage > 1) {
                    currentPage--;
                    render();
                    updateUrl();
                    grid.scrollIntoView({ behavior: 'smooth' });
                }
            });

            nextBtn.addEventListener('click', () => {
                const filtered = getFiltered();
                const totalPages = Math.ceil(filtered.length / pageSize);
                const maxPage = Math.max(1, totalPages);
                if (currentPage < maxPage) {
                    currentPage++;
                    render();
                    updateUrl();
                    grid.scrollIntoView({ behavior: 'smooth' });
                }
            });

            function updateUrl() {
                const params = new URLSearchParams();
                if (currentCat !== 'all') params.set('cat', currentCat);
                if (currentPage > 1) params.set('page', currentPage);
                const newUrl = location.pathname + (params.toString() ? '?' + params.toString() : '');
                history.replaceState(null, '', newUrl);
            }

            // Initial Render
            render();
        });
    </script>
    """
    soup.body.append(BeautifulSoup(js_logic, 'html.parser'))

    # --- E. Final Polish ---
    fix_links(soup)
    inject_favicons(soup)
    reorder_head(soup)
    
    with open(BLOG_INDEX_PATH, 'w', encoding='utf-8') as f:
        f.write(soup.prettify())

def sync_static_pages(layout_nav, layout_footer):
    """
    Sync layout and governance for static pages (privacy.html, terms.html)
    """
    static_pages = ['privacy.html', 'terms.html']
    
    for filename in static_pages:
        filepath = os.path.join(BASE_DIR, filename)
        if not os.path.exists(filepath):
            print(f"Warning: Static page {filename} not found.")
            continue
            
        print(f"Processing static page: {filename}...")
        
        with open(filepath, 'r', encoding='utf-8') as f:
            soup = BeautifulSoup(f.read(), 'html.parser')
            
        # 1. Link Governance
        fix_links(soup)
        
        # Inject Favicons
        inject_favicons(soup)
        
        # 2. Layout Sync
        if soup.body:
            # Replace Nav
            old_nav = soup.body.find('nav')
            if old_nav: old_nav.decompose()
            soup.body.insert(0, BeautifulSoup(str(layout_nav), 'html.parser'))
            
            # Replace Footer
            old_footer = soup.find('footer')
            if old_footer: old_footer.decompose()
            soup.body.append(BeautifulSoup(str(layout_footer), 'html.parser'))
            
        # 3. Head Governance
        reorder_head(soup)
        
        # Save
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(soup.prettify())



def update_sitemap(articles):
    """Generate sitemap.xml"""
    sitemap_path = os.path.join(BASE_DIR, 'sitemap.xml')
    base_url = "https://gpt-upgrade.top"
    today = datetime.date.today().isoformat()
    
    xml_content = ['<?xml version="1.0" encoding="UTF-8"?>']
    xml_content.append('<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">')
    
    # Helper to add url
    def add_url(loc, lastmod, freq, priority):
        xml_content.append('  <url>')
        xml_content.append(f'    <loc>{base_url}{loc}</loc>')
        xml_content.append(f'    <lastmod>{lastmod}</lastmod>')
        xml_content.append(f'    <changefreq>{freq}</changefreq>')
        xml_content.append(f'    <priority>{priority}</priority>')
        xml_content.append('  </url>')

    # 1. Homepage
    add_url('/', today, 'daily', '1.0')
    
    # 2. Blog Index
    add_url('/blog/', today, 'daily', '0.9')
    
    # 3. Blog Posts
    for post in articles:
        # url already comes clean from get_article_metadata (e.g. /blog/post-name)
        add_url(post['url'], post['date'], 'weekly', '0.8')
        
    # 4. Category Pages (Generated in update_blog_index)
    # We should add them for better SEO coverage
    for cat_slug in CATEGORIES.keys():
        if cat_slug == 'all': continue
        add_url(f'/blog/category/{cat_slug}', today, 'weekly', '0.8')
        
    # 5. Static Pages
    static_pages = ['privacy', 'terms']
    for page in static_pages:
        # Check if file exists to get mtime? Or just use today
        # For simplicity, use today as we are rebuilding
        add_url(f'/{page}', today, 'monthly', '0.5')
        
    xml_content.append('</urlset>')
    
    with open(sitemap_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(xml_content))

def main():
    print("Starting build process...")
    
    # 1. Prepare
    layout_nav, layout_footer = extract_layout()
    
    all_articles = []
    
    # Scan articles
    if not os.path.exists(BLOG_DIR):
        print("Blog directory not found.")
        return

    for filename in os.listdir(BLOG_DIR):
        if not filename.endswith('.html') or filename == 'index.html': continue
        filepath = os.path.join(BLOG_DIR, filename)
        with open(filepath, 'r', encoding='utf-8') as f:
            soup = BeautifulSoup(f.read(), 'html.parser')
        all_articles.append(get_article_metadata(soup, filename))
        
    # Sort by date
    all_articles.sort(key=lambda x: x['date'], reverse=True)
    
    # 2. Process Blog Posts
    for meta in all_articles:
        filepath = os.path.join(BLOG_DIR, meta['filename'])
        print(f"Processing {meta['filename']}...")
        
        with open(filepath, 'r', encoding='utf-8') as f:
            soup = BeautifulSoup(f.read(), 'html.parser')
            
        # Link Governance (Global)
        # Enable sales link replacement for blog posts to prevent weight loss
        fix_links(soup, replace_sales_links=True)
        
        # Inject Favicons
        inject_favicons(soup)
        
        # SEO Injection
        inject_seo(soup, meta)
        
        # Layout Sync
        # Replace Nav
        if soup.body:
            old_nav = soup.body.find('nav', id='navbar')
            if old_nav: old_nav.decompose()
            
            # 3. Modify Nav for Blog Context (Point "情报局" to /blog/)
            current_nav = BeautifulSoup(str(layout_nav), 'html.parser')
            # Find the link to #blog, /blog, or /blog/ and ensure it points to /blog/
            # Regex matches: #blog, /blog, /blog/
            blog_link = current_nav.find('a', href=re.compile(r'^(?:/|#)blog/?$'))
            if blog_link:
                blog_link['href'] = '/blog/'
            
            # Insert new nav at top of body
            soup.body.insert(0, current_nav)
            
            old_footer = soup.find('footer')
            if old_footer: old_footer.decompose()
            soup.body.append(BeautifulSoup(str(layout_footer), 'html.parser'))
            
        # Visual Breadcrumbs
        inject_breadcrumbs(soup, meta)
        
        # Smart Interlinking
        inject_related_posts(soup, meta, all_articles)
        
        # *** CONVERT TO RELATIVE PATHS FOR LOCAL PREVIEW ***
        # make_paths_relative(soup)

        # Save
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(str(soup))
            
    # 3. Update Homepage
    print("Updating Homepage...")
    update_homepage(articles=all_articles)

    # 4. Rebuild Blog Index
    print("Updating Blog Index...")
    update_blog_index(all_articles, layout_nav, layout_footer)
    
    # 5. Sync Static Pages
    print("Syncing Static Pages...")
    sync_static_pages(layout_nav, layout_footer)
    
    # 6. Update Sitemap
    print("Updating Sitemap...")
    update_sitemap(all_articles)
    
    print("Build Complete!")

if __name__ == "__main__":
    main()
