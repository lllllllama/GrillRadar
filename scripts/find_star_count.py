#!/usr/bin/env python3
"""
Find Star Count Selector
查找GitHub trending页面中star数的正确选择器
"""
import httpx
from bs4 import BeautifulSoup
import re

def main():
    print("=" * 70)
    print("Finding Star Count Selector")
    print("=" * 70)
    print()

    url = "https://github.com/trending?since=daily"
    response = httpx.get(url, timeout=10, follow_redirects=True)
    soup = BeautifulSoup(response.text, 'html.parser')

    repo_articles = soup.find_all('article', class_='Box-row')
    print(f"✓ Found {len(repo_articles)} repositories")
    print()

    first_article = repo_articles[0]

    # 获取仓库名称作为参考
    h2 = first_article.find('h2', class_='h3')
    repo_name = h2.find('a').get_text(strip=True) if h2 else "Unknown"
    print(f"📦 Analyzing: {repo_name}")
    print()

    # 策略1: 查找包含"stars"或"star"文本的元素
    print("🔍 Strategy 1: Find elements mentioning 'star'")
    all_elements = first_article.find_all(string=re.compile(r'star', re.I))
    print(f"   Found {len(all_elements)} elements with 'star' in text")
    print()

    # 策略2: 查找包含数字+逗号的元素（典型的star数格式：1,234）
    print("🔍 Strategy 2: Find elements with number patterns (e.g., 1,234)")
    all_text_elements = first_article.find_all(string=re.compile(r'\d{1,3}(,\d{3})*'))
    print(f"   Found {len(all_text_elements)} elements with comma-separated numbers")
    for i, elem in enumerate(all_text_elements[:5]):
        parent = elem.parent
        print(f"   {i+1}. '{elem.strip()}' in <{parent.name}> with class={parent.get('class', [])}")
    print()

    # 策略3: 查找aria-label包含star的元素
    print("🔍 Strategy 3: Find elements with aria-label containing 'star'")
    aria_elements = first_article.find_all(attrs={'aria-label': re.compile(r'star', re.I)})
    print(f"   Found {len(aria_elements)} elements")
    for elem in aria_elements[:3]:
        print(f"   aria-label: {elem.get('aria-label')}")
        print(f"   tag: <{elem.name}>, class: {elem.get('class', [])}")
        print()

    # 策略4: 查找包含"today"的元素（今日star数）
    print("🔍 Strategy 4: Find 'stars today' or similar")
    today_elements = first_article.find_all(string=re.compile(r'today|stars', re.I))
    seen_texts = set()
    for elem in today_elements:
        text = elem.strip()
        if text and text not in seen_texts:
            seen_texts.add(text)
            parent = elem.parent
            print(f"   '{text}' in <{parent.name}> class={parent.get('class', [])}")
    print()

    # 策略5: 查找SVG octicon-star附近的文本
    print("🔍 Strategy 5: Find text near star SVG icons")
    star_svgs = first_article.find_all('svg', class_='octicon-star')
    print(f"   Found {len(star_svgs)} star SVG icons")
    for i, svg in enumerate(star_svgs[:2]):
        print(f"\n   Star SVG {i+1}:")
        # 查找父元素
        parent = svg.parent
        print(f"   Parent: <{parent.name}> class={parent.get('class', [])}")
        # 查找兄弟元素
        next_sibling = parent.find_next_sibling()
        if next_sibling:
            print(f"   Next sibling: <{next_sibling.name if hasattr(next_sibling, 'name') else 'text'}> = '{next_sibling.get_text(strip=True) if hasattr(next_sibling, 'get_text') else next_sibling[:50]}'")
        # 查找父元素的下一个兄弟
        parent_sibling = parent.find_next_sibling()
        if parent_sibling:
            print(f"   Parent's next sibling: <{parent_sibling.name if hasattr(parent_sibling, 'name') else 'text'}> = '{parent_sibling.get_text(strip=True)[:100] if hasattr(parent_sibling, 'get_text') else parent_sibling[:50]}'")

    print()
    print("=" * 70)
    print("📄 Article HTML snippet (searching for star count):")
    print("=" * 70)

    # 打印包含star相关信息的HTML片段
    html_str = str(first_article)
    # 查找包含数字的行
    for line in html_str.split('\n'):
        if re.search(r'\d{1,3}(,\d{3})*|\d+\s*stars?', line, re.I):
            print(line.strip()[:150])

if __name__ == '__main__':
    main()
