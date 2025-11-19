#!/usr/bin/env python3
"""
调试掘金HTML结构 - 分析实际的CSS选择器
"""
import sys
from pathlib import Path
import time
import httpx
from bs4 import BeautifulSoup
from urllib.parse import quote

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from app.sources.crawlers.anti_detection import AntiDetectionHelper


def debug_juejin_html():
    """调试掘金HTML结构"""

    keyword = "ChatGPT"
    url = f"https://juejin.cn/search?query={quote(keyword)}&type=0"

    print("=" * 70)
    print(f"🔍 调试掘金HTML: {keyword}")
    print("=" * 70)
    print(f"URL: {url}")
    print()

    # 使用反检测工具
    anti_detect = AntiDetectionHelper()
    headers = anti_detect.get_browser_headers(
        referer='https://juejin.cn/',
        accept='text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8'
    )

    # 添加随机延迟
    delay = anti_detect.get_random_delay(0.5, 1.5)
    time.sleep(delay)

    # 发送请求
    print("📡 发送请求...")
    with httpx.Client(timeout=30.0, verify=False, follow_redirects=True) as client:
        response = client.get(url, headers=headers)
        print(f"   状态码: {response.status_code}")
        print(f"   内容长度: {len(response.text)} 字符")
        print()

        if response.status_code != 200:
            print(f"❌ 请求失败: {response.status_code}")
            return

        # 解析HTML
        soup = BeautifulSoup(response.text, 'html.parser')

        # 保存HTML到文件
        debug_file = project_root / "scripts" / "juejin_debug.html"
        with open(debug_file, "w", encoding="utf-8") as f:
            f.write(response.text)
        print(f"💾 HTML已保存到: {debug_file}")
        print()

        # 尝试不同的选择器
        print("🔍 尝试查找文章卡片...")
        print()

        selectors = [
            ('div.result-item', 'result-item'),
            ('div.item', 'item'),
            ('article', 'article'),
            ('div[class*="result"]', 'result'),
            ('div[class*="article"]', 'article'),
            ('div[class*="card"]', 'card'),
            ('div[class*="entry"]', 'entry'),
            ('div[class*="list-item"]', 'list-item'),
        ]

        for selector, name in selectors:
            cards = soup.select(selector)
            print(f"   {name:20s}: {len(cards):3d} 个")
            if cards and len(cards) > 0:
                print(f"      示例class: {cards[0].get('class')}")

        print()
        print("=" * 70)
        print("💡 提示: 查看 juejin_debug.html 找到正确的选择器")
        print("=" * 70)


if __name__ == "__main__":
    debug_juejin_html()
