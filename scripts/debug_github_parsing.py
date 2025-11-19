#!/usr/bin/env python3
"""
Debug GitHub Trending Parsing
详细分析为什么原始解析器返回0结果
"""
import httpx
from bs4 import BeautifulSoup

def main():
    print("=" * 70)
    print("GitHub Trending Parsing Debug")
    print("=" * 70)
    print()

    url = "https://github.com/trending?since=daily"
    response = httpx.get(url, timeout=10, follow_redirects=True)
    soup = BeautifulSoup(response.text, 'html.parser')

    # 查找trending repositories
    repo_articles = soup.find_all('article', class_='Box-row')
    print(f"✓ Found {len(repo_articles)} articles with class 'Box-row'")
    print()

    if not repo_articles:
        print("❌ No articles found!")
        return

    # 详细分析第一个article
    print("📋 Analyzing first article structure:")
    print("=" * 70)
    first_article = repo_articles[0]

    # 查找h2
    h2 = first_article.find('h2', class_='h3')
    print(f"1. h2 with class 'h3': {'Found' if h2 else 'NOT FOUND'}")
    if h2:
        print(f"   h2 HTML: {str(h2)[:200]}...")
        print()

        # 查找链接
        link = h2.find('a')
        print(f"2. Link inside h2: {'Found' if link else 'NOT FOUND'}")
        if link:
            href = link.get('href', '')
            print(f"   href: {href}")
            print(f"   text: {link.get_text(strip=True)}")
            print()

    # 查找描述
    desc_p = first_article.find('p', class_='col-9')
    print(f"3. Description (p.col-9): {'Found' if desc_p else 'NOT FOUND'}")
    if not desc_p:
        # 尝试其他可能的选择器
        all_p = first_article.find_all('p')
        print(f"   Total <p> tags found: {len(all_p)}")
        if all_p:
            print(f"   First p tag classes: {all_p[0].get('class', [])}")
            print(f"   First p tag text: {all_p[0].get_text(strip=True)[:100]}")
    else:
        print(f"   Description: {desc_p.get_text(strip=True)[:100]}")
    print()

    # 查找star数
    star_span = first_article.find('span', class_='d-inline-block')
    print(f"4. Star count (span.d-inline-block): {'Found' if star_span else 'NOT FOUND'}")
    if not star_span:
        # 尝试查找所有span
        all_spans = first_article.find_all('span')
        print(f"   Total <span> tags found: {len(all_spans)}")
        # 查找包含数字的span
        for i, span in enumerate(all_spans[:10]):
            text = span.get_text(strip=True)
            classes = span.get('class', [])
            if text and (text[0].isdigit() or ',' in text or 'k' in text.lower()):
                print(f"   Span {i}: classes={classes}, text='{text}'")
    else:
        print(f"   Star text: {star_span.get_text(strip=True)}")
    print()

    # 查找语言
    lang_span = first_article.find('span', {'itemprop': 'programmingLanguage'})
    print(f"5. Language (span[itemprop='programmingLanguage']): {'Found' if lang_span else 'NOT FOUND'}")
    if lang_span:
        print(f"   Language: {lang_span.get_text(strip=True)}")
    print()

    print("=" * 70)
    print("📄 Full first article HTML:")
    print("=" * 70)
    print(str(first_article)[:1500])
    print("...")
    print()

if __name__ == '__main__':
    main()
