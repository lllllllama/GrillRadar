#!/usr/bin/env python3
"""
测试 newsnow API - 探索TrendRadar使用的API接口
参考项目: https://github.com/sansan0/TrendRadar
"""
import requests
import json
from typing import Dict, Any


def test_newsnow_api(platform_id: str, platform_name: str) -> Dict[str, Any]:
    """测试 newsnow API"""
    url = f"https://newsnow.busiyi.world/api/s?id={platform_id}&latest"

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
        "Connection": "keep-alive",
        "Cache-Control": "no-cache",
    }

    print("=" * 80)
    print(f"🔍 测试平台: {platform_name} ({platform_id})")
    print("=" * 80)
    print(f"URL: {url}")
    print()

    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()

        data = response.json()

        status = data.get("status", "未知")
        items = data.get("items", [])

        print(f"✅ 状态: {status}")
        print(f"📊 条目数: {len(items)}")
        print()

        # 显示前5条新闻
        print("📰 前5条新闻:")
        print("-" * 80)
        for i, item in enumerate(items[:5], 1):
            title = item.get("title", "")
            url_link = item.get("url", "")
            print(f"{i}. {title}")
            print(f"   链接: {url_link}")
            print()

        # 分析技术相关内容
        tech_keywords = [
            "AI", "人工智能", "ChatGPT", "大模型", "LLM", "机器学习",
            "深度学习", "算法", "Python", "Java", "开发", "编程",
            "技术", "代码", "GitHub", "开源"
        ]

        tech_count = 0
        tech_items = []
        for item in items:
            title = item.get("title", "")
            if any(keyword in title for keyword in tech_keywords):
                tech_count += 1
                tech_items.append(title)

        print("-" * 80)
        print(f"🔧 技术相关新闻: {tech_count}/{len(items)}")
        if tech_items:
            print("技术相关标题示例:")
            for title in tech_items[:3]:
                print(f"  - {title}")
        print()

        return data

    except Exception as e:
        print(f"❌ 请求失败: {e}")
        return {}


def main():
    """主函数 - 测试多个平台"""

    # 测试平台列表 (基于TrendRadar的配置)
    platforms = [
        ("zhihu", "知乎"),
        ("36kr", "36氪"),
        ("juejin", "掘金"),
        ("csdn", "CSDN"),
        ("v2ex", "V2EX"),
        ("ithome", "IT之家"),
        ("weibo", "微博"),
        ("toutiao", "今日头条"),
    ]

    print("🚀 开始测试 newsnow API")
    print("=" * 80)
    print()

    results = {}

    for platform_id, platform_name in platforms:
        data = test_newsnow_api(platform_id, platform_name)
        results[platform_id] = data
        print()

    print("=" * 80)
    print("📋 测试总结")
    print("=" * 80)

    for platform_id, platform_name in platforms:
        data = results.get(platform_id, {})
        status = data.get("status", "失败")
        items_count = len(data.get("items", []))

        status_icon = "✅" if status in ["success", "cache"] else "❌"
        print(f"{status_icon} {platform_name:10s} - {status:8s} - {items_count:3d} 条")

    print()
    print("💡 结论:")
    print("   如果 newsnow API 支持技术平台（知乎/掘金/CSDN/36氪等）,")
    print("   可以考虑使用该API替代直接爬虫，优势:")
    print("   - ✅ 绕过反爬虫机制 (403)")
    print("   - ✅ 返回结构化JSON数据")
    print("   - ✅ 无需复杂的反检测措施")
    print("   - ✅ 支持多个平台聚合")
    print()


if __name__ == "__main__":
    main()
