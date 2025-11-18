#!/usr/bin/env python3
"""
多源爬虫测试脚本 / Multi-Source Crawler Test Script

测试GitHub和CSDN爬虫功能，展示数据聚合流程
"""
import sys
from pathlib import Path

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent))

import logging
from app.models.user_config import UserConfig
from app.sources.crawlers.models import CrawlerConfig
from app.sources.multi_source_provider import MultiSourceCrawlerProvider
from app.sources.crawlers.github_crawler import GitHubCrawler
from app.sources.crawlers.csdn_crawler import CSDNCrawler

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def test_single_crawler(crawler_class, domain: str, name: str):
    """测试单个爬虫"""
    logger.info("=" * 70)
    logger.info(f"Testing {name} Crawler for domain: {domain}")
    logger.info("=" * 70)

    config = CrawlerConfig(
        max_items=10,
        timeout=10,
        sleep_between_requests=0.5,  # 测试时减少间隔
        use_cache=False  # 禁用缓存以获取最新数据
    )

    crawler = crawler_class(config)

    # 根据领域获取关键词
    keywords = []
    if domain == 'llm_application':
        keywords = ['LLM', 'RAG', 'GPT']
    elif domain == 'backend':
        keywords = ['backend', 'microservice']
    elif domain == 'cv_segmentation':
        keywords = ['segmentation', 'computer vision']

    result = crawler.crawl(domain=domain, keywords=keywords)

    logger.info(f"\n{name} Crawl Result:")
    logger.info(f"  Success: {result.success}")
    logger.info(f"  Items crawled: {result.crawled_count}")
    logger.info(f"  Duration: {result.duration_ms}ms")

    if not result.success:
        logger.error(f"  Error: {result.error_message}")
        return result

    # 显示前3个结果
    logger.info(f"\n  Top {min(3, len(result.items))} items:")
    for i, item in enumerate(result.items[:3], 1):
        logger.info(f"\n    {i}. {item.title}")
        logger.info(f"       URL: {item.url}")
        logger.info(f"       Tags: {', '.join(item.tags[:5])}")
        logger.info(f"       Engagement: {item.engagement}")
        logger.info(f"       Snippet: {item.snippet[:100]}...")

    return result


def test_multi_source_provider(domain: str):
    """测试多源提供者"""
    logger.info("\n" + "=" * 70)
    logger.info(f"Testing Multi-Source Provider for domain: {domain}")
    logger.info("=" * 70)

    config = CrawlerConfig(
        max_items=15,
        timeout=15,
        sleep_between_requests=0.5,
        use_cache=False
    )

    provider = MultiSourceCrawlerProvider(
        config=config,
        enable_github=True,
        enable_csdn=True
    )

    # 创建用户配置
    user_config = UserConfig(
        mode='job',
        target_desc=f'{domain} 开发工程师',
        domain=domain,
        resume_text='测试简历内容',
        level='mid'
    )

    # 检索外部信息
    summary = provider.retrieve_external_info(
        user_config=user_config,
        resume_keywords=['Python', 'algorithm']
    )

    if not summary:
        logger.error("Failed to retrieve external info")
        return

    logger.info(f"\n  Aggregation Results:")
    logger.info(f"  Job Descriptions: {len(summary.job_descriptions)}")
    logger.info(f"  Interview Experiences: {len(summary.interview_experiences)}")
    logger.info(f"  Aggregated Keywords: {len(summary.aggregated_keywords)}")
    logger.info(f"  Aggregated Topics: {len(summary.aggregated_topics)}")
    logger.info(f"  High Frequency Questions: {len(summary.high_frequency_questions)}")

    # 显示关键词
    if summary.aggregated_keywords:
        logger.info(f"\n  Top Keywords:")
        logger.info(f"    {', '.join(summary.aggregated_keywords[:15])}")

    # 显示主题
    if summary.aggregated_topics:
        logger.info(f"\n  Top Topics:")
        logger.info(f"    {', '.join(summary.aggregated_topics[:10])}")

    # 显示高频问题
    if summary.high_frequency_questions:
        logger.info(f"\n  Sample High-Frequency Questions:")
        for i, q in enumerate(summary.high_frequency_questions[:3], 1):
            logger.info(f"    {i}. {q}")

    # 显示Prompt摘要
    prompt_summary = provider.get_prompt_summary(summary)
    logger.info(f"\n  Prompt Summary Preview:")
    lines = prompt_summary.split('\n')
    for line in lines[:10]:  # 显示前10行
        logger.info(f"    {line}")

    return summary


def main():
    """主函数"""
    logger.info("GrillRadar Multi-Source Crawler Test Script")
    logger.info("=" * 70)

    # 选择测试场景
    scenarios = [
        ('llm_application', 'LLM Application Development'),
        ('backend', 'Backend Development'),
        ('cv_segmentation', 'Computer Vision - Segmentation')
    ]

    print("\nAvailable test scenarios:")
    for i, (domain, desc) in enumerate(scenarios, 1):
        print(f"  {i}. {desc} ({domain})")
    print("  4. Test all scenarios")
    print("  5. Test individual crawlers only")

    try:
        choice = input("\nSelect scenario (1-5) [default: 1]: ").strip()
        if not choice:
            choice = '1'

        if choice == '5':
            # 测试单个爬虫
            test_domain = scenarios[0][0]
            logger.info(f"\nTesting individual crawlers for: {test_domain}")

            # 测试GitHub爬虫
            github_result = test_single_crawler(GitHubCrawler, test_domain, "GitHub")

            # 测试CSDN爬虫
            csdn_result = test_single_crawler(CSDNCrawler, test_domain, "CSDN")

            logger.info("\n" + "=" * 70)
            logger.info("Individual Crawler Tests Completed!")
            logger.info(f"  GitHub: {github_result.crawled_count} items")
            logger.info(f"  CSDN: {csdn_result.crawled_count} items")

        elif choice == '4':
            # 测试所有场景
            for domain, desc in scenarios:
                logger.info(f"\n\n{'='*70}")
                logger.info(f"Scenario: {desc}")
                logger.info(f"{'='*70}")
                test_multi_source_provider(domain)

        else:
            # 测试单个场景
            idx = int(choice) - 1
            if 0 <= idx < len(scenarios):
                domain, desc = scenarios[idx]
                test_multi_source_provider(domain)
            else:
                logger.error("Invalid choice")
                return

    except KeyboardInterrupt:
        logger.info("\n\nTest interrupted by user")
    except Exception as e:
        logger.error(f"\nTest failed: {e}", exc_info=True)

    logger.info("\n" + "=" * 70)
    logger.info("Test completed!")
    logger.info("=" * 70)


if __name__ == '__main__':
    main()
