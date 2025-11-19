#!/usr/bin/env python3
"""
Debug GitHub Trending Page HTML Structure
获取并分析GitHub trending页面的实际HTML结构
"""
import httpx
from bs4 import BeautifulSoup

def main():
    print("=" * 70)
    print("GitHub Trending Page HTML Structure Analysis")
    print("=" * 70)
    print()

    # 获取GitHub trending页面
    url = "https://github.com/trending?since=daily"
    print(f"📡 Fetching: {url}")

    try:
        response = httpx.get(url, timeout=10, follow_redirects=True)
        print(f"✓ Status: {response.status_code}")
        print(f"✓ Content length: {len(response.text)} chars")
        print()

        # 解析HTML
        soup = BeautifulSoup(response.text, 'html.parser')

        # 查找可能的仓库容器
        print("🔍 Looking for repository containers...")
        print()

        # 尝试多种可能的选择器
        selectors = [
            ('article.Box-row', 'Original selector (article.Box-row)'),
            ('article', 'All articles'),
            ('div.Box-row', 'div.Box-row'),
            ('h2.h3', 'h2.h3 (repo name headers)'),
            ('h2', 'All h2 elements'),
            ('.Box-row', 'Class: Box-row'),
            ('[class*="Box"]', 'Any element with Box in class'),
            ('[class*="repo"]', 'Any element with repo in class'),
        ]

        for selector, description in selectors:
            elements = soup.select(selector)
            print(f"  {selector:30s} [{description:40s}]: {len(elements):3d} found")

        print()
        print("=" * 70)

        # 保存HTML到文件用于详细分析
        output_file = "/tmp/github_trending.html"
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(response.text)
        print(f"💾 Full HTML saved to: {output_file}")
        print()

        # 查找前几个看起来像仓库的元素
        print("📝 Sample repository-like elements:")
        print()

        # 尝试找到包含repo链接的元素
        repo_links = soup.find_all('a', href=lambda x: x and '/' in str(x) and not x.startswith('http'))
        print(f"  Found {len(repo_links)} internal links")

        # 显示前5个看起来像仓库的链接
        repo_count = 0
        for link in repo_links[:50]:
            href = link.get('href', '')
            # GitHub仓库链接格式: /owner/repo
            if href.count('/') == 2 and not href.startswith('/topics') and not href.startswith('/trending'):
                repo_count += 1
                text = link.get_text(strip=True)
                print(f"  {repo_count}. {href:50s} | {text[:40]}")
                if repo_count >= 10:
                    break

        print()
        print("=" * 70)
        print("✨ Analysis complete!")

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    main()
