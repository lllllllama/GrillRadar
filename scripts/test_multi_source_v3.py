#!/usr/bin/env python3
"""
测试多源爬虫系统 V3 - GitHub + V2EX
"""
import sys
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from app.sources.multi_source_provider import MultiSourceCrawlerProvider
from app.sources.crawlers.models import CrawlerConfig
from app.models.user_config import UserConfig


def test_multi_source_v3():
    """测试多源爬虫系统 V3 - GitHub + V2EX"""

    print("=" * 80)
    print("🚀 测试多源爬虫系统 V3 (GitHub + V2EX)")
    print("=" * 80)
    print("   数据源: GitHub Trending + V2EX技术讨论")
    print("=" * 80)
    print()

    # 创建配置
    config = CrawlerConfig(
        max_items=50,
        timeout=15,
        use_cache=True,
        cache_ttl=3600
    )

    # 创建多源提供者
    provider = MultiSourceCrawlerProvider(
        config=config,
        enable_github=True,
        enable_v2ex=True,
        enable_juejin=False,
        enable_zhihu=False,
        enable_csdn=False
    )

    print(f"📋 已启用爬虫: {len(provider.crawlers)} 个")
    for crawler in provider.crawlers:
        print(f"   - {crawler.source_name}")
    print()

    # 测试不同领域
    test_domains = [
        ('llm_application', 'LLM应用工程师'),
        ('backend', '后端开发工程师'),
        ('algorithm', '算法工程师'),
    ]

    for domain, position in test_domains:
        print("=" * 80)
        print(f"🔍 测试领域: {domain} ({position})")
        print("=" * 80)

        user_config = UserConfig(
            mode="job",
            domain=domain,
            target_position=position,
            target_company="字节跳动",
            target_desc=f"我想应聘{position}职位，希望能够得到相关的面试指导和准备建议",
            resume_text="资深工程师，具有5年以上项目经验，熟悉主流技术栈"
        )

        try:
            external_info = provider.retrieve_external_info(user_config)

            if external_info:
                print(f"✅ 获取成功!")
                print()

                # 显示摘要内容（前800字符）
                print(f"📝 摘要预览:")
                print("-" * 80)
                if hasattr(external_info, 'summary') and external_info.summary:
                    summary_preview = external_info.summary[:800]
                    print(summary_preview)
                    if len(external_info.summary) > 800:
                        print("...")
                else:
                    print("（无摘要内容）")
                print("-" * 80)
                print()

            else:
                print(f"❌ 获取失败 - 返回 None")

        except Exception as e:
            print(f"❌ 测试失败: {e}")
            import traceback
            traceback.print_exc()

        print()

    print("=" * 80)
    print("✨ 测试完成！")
    print("=" * 80)
    print()
    print("💡 结论:")
    print("   如果看到 GitHub 和 V2EX 的数据，说明多源系统工作正常")
    print("   V2EX 提供技术讨论和面试相关内容")
    print("   GitHub 提供开源项目和技术趋势")
    print()


if __name__ == "__main__":
    test_multi_source_v3()
