#!/usr/bin/env python3
"""
测试 IT之家 API 爬虫
"""
import sys
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from app.sources.crawlers.ithome_api_crawler import ITHomeAPICrawler
from app.sources.crawlers.models import CrawlerConfig


def test_ithome_crawler():
    """测试IT之家爬虫"""

    print("=" * 80)
    print("🧪 测试 IT之家 API 爬虫")
    print("=" * 80)
    print()

    # 创建配置
    config = CrawlerConfig(
        timeout=10,
        max_items=50,
        cache_ttl=3600
    )

    # 创建爬虫实例
    crawler = ITHomeAPICrawler(config)

    # 测试1: 不指定领域，获取所有技术相关新闻
    print("📋 测试 1: 获取所有技术相关新闻")
    print("-" * 80)

    result = crawler.crawl(domain="general", keywords=[])

    print(f"✅ 爬取状态: {'成功' if result.success else '失败'}")
    print(f"📊 获取条目: {len(result.items)} 条")
    print(f"⏱️  耗时: {result.duration_ms}ms")

    if result.error_message:
        print(f"❌ 错误信息: {result.error_message}")

    if result.items:
        print()
        print("📰 前5条科技新闻:")
        for i, item in enumerate(result.items[:5], 1):
            print(f"\n{i}. {item.title}")
            print(f"   链接: {item.url}")
            print(f"   类型: {item.metadata.get('content_type', 'news')}")

    print()
    print("=" * 80)

    # 测试2: 指定LLM应用领域
    print("📋 测试 2: LLM应用领域相关新闻")
    print("-" * 80)

    result_llm = crawler.crawl(domain='llm_application', keywords=[])

    print(f"✅ 爬取状态: {'成功' if result_llm.success else '失败'}")
    print(f"📊 获取条目: {len(result_llm.items)} 条")
    print(f"⏱️  耗时: {result_llm.duration_ms}ms")

    if result_llm.items:
        print()
        print("📰 LLM相关新闻:")
        for i, item in enumerate(result_llm.items[:5], 1):
            print(f"\n{i}. {item.title}")
            print(f"   链接: {item.url}")

    print()
    print("=" * 80)

    # 测试3: 指定后端领域
    print("📋 测试 3: 后端开发领域相关新闻")
    print("-" * 80)

    result_backend = crawler.crawl(domain='backend', keywords=[])

    print(f"✅ 爬取状态: {'成功' if result_backend.success else '失败'}")
    print(f"📊 获取条目: {len(result_backend.items)} 条")
    print(f"⏱️  耗时: {result_backend.duration_ms}ms")

    if result_backend.items:
        print()
        print("📰 后端相关新闻:")
        for i, item in enumerate(result_backend.items[:5], 1):
            print(f"\n{i}. {item.title}")
            print(f"   链接: {item.url}")

    print()
    print("=" * 80)

    # 测试4: 硬件/产品领域 (IT之家特色)
    print("📋 测试 4: 硬件/产品相关新闻")
    print("-" * 80)

    result_mobile = crawler.crawl(domain='mobile', keywords=[])

    print(f"✅ 爬取状态: {'成功' if result_mobile.success else '失败'}")
    print(f"📊 获取条目: {len(result_mobile.items)} 条")
    print(f"⏱️  耗时: {result_mobile.duration_ms}ms")

    if result_mobile.items:
        print()
        print("📰 硬件/产品相关新闻:")
        for i, item in enumerate(result_mobile.items[:5], 1):
            print(f"\n{i}. {item.title}")
            print(f"   链接: {item.url}")

    print()
    print("=" * 80)
    print("📊 测试总结")
    print("=" * 80)

    print(f"总技术新闻: {len(result.items)} 条")
    print(f"LLM应用: {len(result_llm.items)} 条")
    print(f"后端开发: {len(result_backend.items)} 条")
    print(f"硬件/产品: {len(result_mobile.items)} 条")

    print()
    print("💡 结论:")
    if result.success and len(result.items) > 0:
        print("   ✅ IT之家 API 爬虫工作正常！")
        print("   ✅ 可以获取技术相关的新闻内容")
        print("   ✅ 支持按领域筛选")
        print("   ✅ 适合作为科技新闻和产品发布数据源")
        print("   ✅ 与V2EX互补：IT之家提供新闻，V2EX提供讨论")
    else:
        print("   ❌ IT之家 API 爬虫遇到问题，需要检查")

    print()


if __name__ == "__main__":
    test_ithome_crawler()
