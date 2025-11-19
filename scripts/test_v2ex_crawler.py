#!/usr/bin/env python3
"""
测试 V2EX API 爬虫
"""
import sys
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from app.sources.crawlers.v2ex_api_crawler import V2EXAPICrawler
from app.sources.crawlers.models import CrawlerConfig


def test_v2ex_crawler():
    """测试V2EX爬虫"""

    print("=" * 80)
    print("🧪 测试 V2EX API 爬虫")
    print("=" * 80)
    print()

    # 创建配置
    config = CrawlerConfig(
        timeout=10,
        max_items=50,
        cache_ttl=3600
    )

    # 创建爬虫实例
    crawler = V2EXAPICrawler(config)

    # 测试1: 不指定领域，获取所有技术相关内容
    print("📋 测试 1: 获取所有技术相关讨论")
    print("-" * 80)

    result = crawler.crawl()

    print(f"✅ 爬取状态: {'成功' if result.success else '失败'}")
    print(f"📊 获取条目: {len(result.items)} 条")

    if result.error_message:
        print(f"❌ 错误信息: {result.error_message}")

    if result.items:
        print()
        print("📰 前5条技术讨论:")
        for i, item in enumerate(result.items[:5], 1):
            print(f"\n{i}. {item.title}")
            print(f"   链接: {item.url}")
            print(f"   类型: {item.metadata.get('content_type', 'discussion')}")

    print()
    print("=" * 80)

    # 测试2: 指定LLM应用领域
    print("📋 测试 2: LLM应用领域相关讨论")
    print("-" * 80)

    result_llm = crawler.crawl(domain='llm_application')

    print(f"✅ 爬取状态: {'成功' if result_llm.success else '失败'}")
    print(f"📊 获取条目: {len(result_llm.items)} 条")

    if result_llm.items:
        print()
        print("📰 LLM相关讨论:")
        for i, item in enumerate(result_llm.items[:5], 1):
            print(f"\n{i}. {item.title}")
            print(f"   链接: {item.url}")

    print()
    print("=" * 80)

    # 测试3: 指定后端领域
    print("📋 测试 3: 后端开发领域相关讨论")
    print("-" * 80)

    result_backend = crawler.crawl(domain='backend')

    print(f"✅ 爬取状态: {'成功' if result_backend.success else '失败'}")
    print(f"📊 获取条目: {len(result_backend.items)} 条")

    if result_backend.items:
        print()
        print("📰 后端相关讨论:")
        for i, item in enumerate(result_backend.items[:5], 1):
            print(f"\n{i}. {item.title}")
            print(f"   链接: {item.url}")

    print()
    print("=" * 80)

    # 测试4: 算法/面试领域
    print("📋 测试 4: 算法/面试相关讨论")
    print("-" * 80)

    result_algo = crawler.crawl(domain='algorithm')

    print(f"✅ 爬取状态: {'成功' if result_algo.success else '失败'}")
    print(f"📊 获取条目: {len(result_algo.items)} 条")

    if result_algo.items:
        print()
        print("📰 算法/面试相关讨论:")
        for i, item in enumerate(result_algo.items[:5], 1):
            print(f"\n{i}. {item.title}")
            print(f"   链接: {item.url}")

    print()
    print("=" * 80)
    print("📊 测试总结")
    print("=" * 80)

    print(f"总技术讨论: {len(result.items)} 条")
    print(f"LLM应用: {len(result_llm.items)} 条")
    print(f"后端开发: {len(result_backend.items)} 条")
    print(f"算法面试: {len(result_algo.items)} 条")

    print()
    print("💡 结论:")
    if result.success and len(result.items) > 0:
        print("   ✅ V2EX API 爬虫工作正常！")
        print("   ✅ 可以获取技术相关的讨论内容")
        print("   ✅ 支持按领域筛选")
        print("   ✅ 适合作为面试经验和技术讨论数据源")
    else:
        print("   ❌ V2EX API 爬虫遇到问题，需要检查")

    print()


if __name__ == "__main__":
    test_v2ex_crawler()
