#!/usr/bin/env python3
"""
测试本地数据集提供者 - 验证真实JD和面经数据的加载和聚合
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import logging
from app.models.user_config import UserConfig
from app.sources.local_dataset_provider import LocalDatasetProvider

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def main():
    logger.info("=" * 70)
    logger.info("测试本地数据集提供者（LocalDatasetProvider）")
    logger.info("=" * 70)
    print()

    # 创建提供者
    provider = LocalDatasetProvider()

    # 创建用户配置 - 字节跳动 LLM应用工程师
    user_config = UserConfig(
        mode='job',
        target_desc='字节跳动 LLM应用工程师',
        domain='llm_application',
        resume_text='我是一名有3年经验的LLM应用工程师，熟悉RAG、Prompt工程和大模型微调。参与过多个项目的开发，包括智能客服和文档问答系统。',
        level='junior',
        enable_external_info=True,
        target_company='字节跳动'
    )

    print(f"📋 用户配置:")
    print(f"   目标: {user_config.target_desc}")
    print(f"   领域: {user_config.domain}")
    print(f"   公司: {user_config.target_company}")
    print(f"   级别: {user_config.level}")
    print()

    # 检索外部信息
    print("🔍 检索外部信息...")
    summary = provider.retrieve_external_info(user_config)

    if not summary:
        print("❌ 未找到相关外部信息")
        return

    print(f"✅ 成功检索外部信息！")
    print()

    # 显示统计
    print("📊 数据统计:")
    print(f"   JD数量: {len(summary.job_descriptions)}")
    print(f"   面经数量: {len(summary.interview_experiences)}")
    print(f"   关键词: {len(summary.aggregated_keywords)}")
    print(f"   主题: {len(summary.aggregated_topics)}")
    print(f"   高频问题: {len(summary.high_frequency_questions)}")
    print()

    # 显示JD详情
    if summary.job_descriptions:
        print("💼 职位描述 (Top 3):")
        for i, jd in enumerate(summary.job_descriptions[:3], 1):
            print(f"\n   {i}. {jd.company} - {jd.position}")
            print(f"      地点: {jd.location}")
            print(f"      薪资: {jd.salary_range}")
            print(f"      关键词: {', '.join(jd.keywords[:8])}...")
        print()

    # 显示面经详情
    if summary.interview_experiences:
        print("📝 面试经验 (Top 3):")
        for i, exp in enumerate(summary.interview_experiences[:3], 1):
            print(f"\n   {i}. {exp.company} - {exp.position}")
            print(f"      类型: {exp.interview_type}")
            print(f"      难度: {exp.difficulty or 'N/A'}")
            print(f"      主题: {', '.join(exp.topics[:8]) if exp.topics else 'N/A'}")
        print()

    # 显示关键词趋势
    if summary.keyword_trends:
        print("📈 关键词趋势 (Top 15):")
        for i, trend in enumerate(summary.keyword_trends[:15], 1):
            print(f"   {i:2d}. {trend.keyword:20s} | 频次:{trend.frequency:3d} | 权重:{trend.weight:6.2f}")
        print()

    # 显示主题趋势
    if summary.topic_trends:
        print("🎯 主题趋势 (Top 10):")
        for i, topic in enumerate(summary.topic_trends[:10], 1):
            print(f"   {i:2d}. {topic.topic:30s} | 频次:{topic.frequency:3d}")
        print()

    # 显示高频问题
    if summary.high_frequency_questions:
        print("❓ 高频面试问题 (Top 5):")
        for i, q in enumerate(summary.high_frequency_questions[:5], 1):
            print(f"   {i}. {q}")
        print()

    # 显示Prompt摘要
    print("💡 Prompt摘要预览 (前20行):")
    print("-" * 70)
    prompt_lines = []

    # 构建简单的prompt摘要
    prompt_lines.append("## 外部信息摘要")
    prompt_lines.append(f"- JD数量: {len(summary.job_descriptions)}")
    prompt_lines.append(f"- 面经数量: {len(summary.interview_experiences)}")
    prompt_lines.append("")
    prompt_lines.append("### 高频关键词:")
    prompt_lines.append(", ".join([t.keyword for t in summary.keyword_trends[:10]]))
    prompt_lines.append("")
    prompt_lines.append("### 热门主题:")
    for topic in summary.topic_trends[:5]:
        prompt_lines.append(f"- {topic.topic} (频次: {topic.frequency})")
    prompt_lines.append("")
    prompt_lines.append("### 高频问题:")
    for q in summary.high_frequency_questions[:5]:
        prompt_lines.append(f"- {q}")

    for line in prompt_lines[:20]:
        print(f"   {line}")
    print("-" * 70)
    print()

    print("=" * 70)
    print("✨ 测试完成！本地数据集提供者工作正常")
    print("=" * 70)


if __name__ == '__main__':
    main()
