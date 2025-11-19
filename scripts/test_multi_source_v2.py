#!/usr/bin/env python3
"""
测试改进的多源爬虫系统
Test improved multi-source crawler (GitHub + Juejin + Zhihu)
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import logging
from app.sources.crawlers.models import CrawlerConfig
from app.sources.multi_source_provider import MultiSourceCrawlerProvider
from app.models.user_config import UserConfig

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def main():
    print("=" * 70)
    print("🚀 Testing Improved Multi-Source Crawler System")
    print("=" * 70)
    print("   Sources: GitHub + Juejin + Zhihu")
    print("=" * 70)
    print()

    # 创建爬虫配置
    config = CrawlerConfig(
        max_items=15,
        timeout=15,
        sleep_between_requests=0.5,
        use_cache=False
    )

    # 创建多源提供者（启用3个爬虫）
    provider = MultiSourceCrawlerProvider(
        config=config,
        enable_github=True,
        enable_juejin=True,
        enable_zhihu=True,
        enable_csdn=False  # CSDN暂时禁用
    )

    # 创建测试用户配置
    user_config = UserConfig(
        mode='job',
        target_desc='LLM应用工程师',
        domain='llm_application',
        resume_text='这是一个测试简历，包含LLM、RAG、Prompt工程等关键词。',
        level='junior',
        enable_external_info=True
    )

    print(f"📋 测试配置:")
    print(f"   领域: {user_config.domain}")
    print(f"   目标: {user_config.target_desc}")
    print(f"   爬虫数量: 3 (GitHub, Juejin, Zhihu)")
    print()

    # 检索外部信息
    print("🔍 开始爬取实时数据...")
    print()

    summary = provider.retrieve_external_info(
        user_config=user_config,
        resume_keywords=['LLM', 'RAG']
    )

    if not summary:
        print("❌ 未获取到任何数据")
        return

    print()
    print("=" * 70)
    print("✅ 爬取成功！")
    print("=" * 70)
    print()

    # 显示统计
    print("📊 数据统计:")
    print(f"   JD数量: {len(summary.job_descriptions)}")
    print(f"   面经数量: {len(summary.interview_experiences)}")
    print(f"   关键词: {len(summary.aggregated_keywords)}")
    print(f"   主题: {len(summary.aggregated_topics)}")
    print(f"   高频问题: {len(summary.high_frequency_questions)}")
    print()

    # 显示JD来源分布
    if summary.job_descriptions:
        print("💼 JD来源分布:")
        sources = {}
        for jd in summary.job_descriptions:
            source = jd.source_url.split('/')[2] if jd.source_url else 'unknown'
            if 'github' in source:
                source = 'GitHub'
            elif 'juejin' in source:
                source = 'Juejin'
            elif 'zhihu' in source:
                source = 'Zhihu'
            sources[source] = sources.get(source, 0) + 1

        for source, count in sources.items():
            print(f"   {source}: {count}")
        print()

    # 显示样本JD
    if summary.job_descriptions:
        print("📄 样本JD (前3个):")
        for i, jd in enumerate(summary.job_descriptions[:3], 1):
            print(f"\n   {i}. {jd.company} - {jd.position}")
            print(f"      地点: {jd.location or 'N/A'}")
            if jd.keywords:
                print(f"      关键词: {', '.join(jd.keywords[:5])}...")
            if jd.source_url:
                print(f"      来源: {jd.source_url[:60]}...")
        print()

    # 显示聚合关键词
    if summary.aggregated_keywords:
        print("🔑 聚合关键词 (Top 15):")
        for i, keyword in enumerate(summary.aggregated_keywords[:15], 1):
            print(f"   {i:2d}. {keyword}")
        print()

    # 显示聚合主题
    if summary.aggregated_topics:
        print("🎯 聚合主题 (Top 10):")
        for i, topic in enumerate(summary.aggregated_topics[:10], 1):
            print(f"   {i:2d}. {topic}")
        print()

    # 显示高频问题
    if summary.high_frequency_questions:
        print("❓ 高频面试问题 (Top 5):")
        for i, q in enumerate(summary.high_frequency_questions[:5], 1):
            print(f"   {i}. {q}")
        print()

    # 获取prompt摘要
    prompt_summary = provider.get_prompt_summary(summary)
    print("💡 Prompt摘要预览 (前20行):")
    print("-" * 70)
    lines = prompt_summary.split('\n')
    for line in lines[:20]:
        print(f"   {line}")
    print("-" * 70)
    print()

    print("=" * 70)
    print("✨ 测试完成！多源爬虫系统工作正常")
    print("=" * 70)


if __name__ == '__main__':
    main()
