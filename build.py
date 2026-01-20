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
    
    # Remove index
    if url.endswith('/index'):
        url = url[:-6]
    if url == 'index':
        url = ''
        
    # Enforce root path
    if not url.startswith('/'):
        url = '/' + url
        
    if url == '/': return '/' + anchor
    
    return url + anchor

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

def fix_links(soup):
    """
    Apply Clean URL logic to all links, skipping safe zones.
    """
    for a in soup.find_all('a', href=True):
        if is_safe_zone(a): continue
        a['href'] = clean_url(a['href'])
        
    # Also fix local images to be absolute paths
    for img in soup.find_all('img', src=True):
        if is_safe_zone(img): continue
        src = img['src']
        if not src.startswith(('http', 'data:')):
             if not src.startswith('/'):
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
    
    # Remove existing
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
    with open(INDEX_PATH, 'w', encoding='utf-8') as f: f.write(str(soup))

def update_blog_index(articles, layout_nav, layout_footer):
    """Rebuild /blog/index.html"""
    if not os.path.exists(BLOG_INDEX_PATH): return
    with open(BLOG_INDEX_PATH, 'r', encoding='utf-8') as f:
        soup = BeautifulSoup(f.read(), 'html.parser')

    # Layout Sync
    if soup.body:
        old_nav = soup.body.find('nav', id='navbar') or soup.body.find('nav')
        if old_nav: old_nav.decompose()
        soup.body.insert(0, BeautifulSoup(str(layout_nav), 'html.parser'))
        
        old_footer = soup.find('footer')
        if old_footer: old_footer.decompose()
        soup.body.append(BeautifulSoup(str(layout_footer), 'html.parser'))

    # Update List
    main = soup.find('main')
    if main:
        grid = main.find('div', class_=re.compile(r'grid.*cols'))
        if grid:
            grid.clear()
            for i, post in enumerate(articles):
                style = CARD_STYLES[i % len(CARD_STYLES)]
                card_html = f'''
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
                grid.append(BeautifulSoup(card_html, 'html.parser'))

    # Update Schema
    for script in soup.find_all('script', type='application/ld+json'): script.decompose()
    schema_items = []
    for i, post in enumerate(articles):
        schema_items.append({"@type": "ListItem", "position": i + 1, "url": f"https://gpt-upgrade.top{post['url']}"})
    schema_data = {"@context": "https://schema.org", "@type": "CollectionPage", "headline": "GPT-Upgrade 情报局", "description": "最新的 AI 行业资讯、ChatGPT 使用教程与评测。", "mainEntity": {"@type": "ItemList", "itemListElement": schema_items}}
    schema_script = soup.new_tag('script', type='application/ld+json')
    schema_script.string = json.dumps(schema_data, indent=2, ensure_ascii=False)
    if soup.head: soup.head.append(schema_script)

    fix_links(soup)
    reorder_head(soup)
    with open(BLOG_INDEX_PATH, 'w', encoding='utf-8') as f: f.write(soup.prettify())

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
        fix_links(soup)
        
        # SEO Injection
        inject_seo(soup, meta)
        
        # Layout Sync
        # Replace Nav
        if soup.body:
            old_nav = soup.body.find('nav', id='navbar')
            if old_nav: old_nav.decompose()
            # Insert new nav at top of body
            soup.body.insert(0, BeautifulSoup(str(layout_nav), 'html.parser'))
            
            old_footer = soup.find('footer')
            if old_footer: old_footer.decompose()
            soup.body.append(BeautifulSoup(str(layout_footer), 'html.parser'))
            
        # Visual Breadcrumbs
        inject_breadcrumbs(soup, meta)
        
        # Smart Interlinking
        inject_related_posts(soup, meta, all_articles)
        
        # Save
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(str(soup))
            
    # 3. Update Homepage
    print("Updating Homepage...")
    update_homepage(articles=all_articles)

    # 4. Rebuild Blog Index
    print("Updating Blog Index...")
    update_blog_index(all_articles, layout_nav, layout_footer)
    
    print("Build Complete!")

if __name__ == "__main__":
    main()
