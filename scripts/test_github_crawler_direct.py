#!/usr/bin/env python3
"""
直接测试GitHub爬虫的trending功能
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import httpx
from bs4 import BeautifulSoup
import re

def parse_github_number(text: str) -> int:
    """解析GitHub的数字格式"""
    text = text.strip().replace(',', '').replace(' ', '')
    if 'k' in text.lower():
        return int(float(text.lower().replace('k', '')) * 1000)
    try:
        return int(text)
    except:
        return 0

def main():
    print("=" * 70)
    print("GitHub Trending Crawler - Direct Test")
    print("=" * 70)
    print()

    # 测试trending页面（不带语言过滤）
    url = "https://github.com/trending?since=daily"
    print(f"📡 Fetching: {url}")

    response = httpx.get(url, timeout=10, follow_redirects=True)
    print(f"✓ Status: {response.status_code}")
    print()

    soup = BeautifulSoup(response.text, 'html.parser')
    repo_articles = soup.find_all('article', class_='Box-row')
    print(f"✓ Found {len(repo_articles)} articles")
    print()

    items_parsed = 0
    for i, article in enumerate(repo_articles[:5]):
        try:
            print(f"📦 Repository {i+1}:")
            print("-" * 70)

            # 提取repo名称和URL
            h2 = article.find('h2', class_='h3')
            if not h2:
                print("   ❌ No h2 found")
                continue

            link = h2.find('a')
            if not link:
                print("   ❌ No link found")
                continue

            repo_path = link.get('href', '').strip()
            repo_url = f"https://github.com{repo_path}"
            repo_name = link.get_text(strip=True)

            print(f"   Name: {repo_name}")
            print(f"   URL: {repo_url}")

            # 提取描述
            desc_p = article.find('p', class_='col-9')
            description = desc_p.get_text(strip=True) if desc_p else ""
            print(f"   Description: {description[:100]}...")

            # 提取star数
            star_link = article.find('a', href=lambda x: x and '/stargazers' in x)
            if star_link:
                star_text = star_link.get_text(strip=True)
                star_count = parse_github_number(star_text)
                print(f"   Stars: {star_text} → {star_count}")
            else:
                print(f"   Stars: NOT FOUND")

            # 提取语言
            lang_color = article.find('span', class_='repo-language-color')
            if lang_color:
                # 尝试多种方式获取语言名
                lang_text = lang_color.next_sibling
                language_name = "Unknown"
                if isinstance(lang_text, str):
                    language_name = lang_text.strip()
                elif hasattr(lang_text, 'get_text'):
                    language_name = lang_text.get_text(strip=True)

                # 如果next_sibling不work，尝试找父元素中的文本
                if language_name == "Unknown" or not language_name:
                    parent = lang_color.parent
                    if parent:
                        # 移除颜色span，剩下的就是语言名
                        parent_copy = parent.__copy__()
                        for span in parent_copy.find_all('span', class_='repo-language-color'):
                            span.decompose()
                        language_name = parent_copy.get_text(strip=True)

                print(f"   Language: {language_name}")
            else:
                print(f"   Language: NOT FOUND (no color span)")

            print(f"   ✓ Parsed successfully")
            items_parsed += 1

        except Exception as e:
            print(f"   ❌ Error: {e}")
            import traceback
            traceback.print_exc()

        print()

    print("=" * 70)
    print(f"✨ Parsing complete: {items_parsed}/{min(5, len(repo_articles))} items parsed")

if __name__ == '__main__':
    main()
