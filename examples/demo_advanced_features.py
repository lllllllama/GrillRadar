#!/usr/bin/env python3
"""
GrillRadar Advanced Features Demo

This script demonstrates two advanced features:
1. TrendRadar-style external information acquisition with keyword frequency analysis
2. Multi-agent architecture benefits

Usage:
    python examples/demo_advanced_features.py
    python examples/demo_advanced_features.py --case job_backend
    python examples/demo_advanced_features.py --show-keywords
"""
import sys
import json
import argparse
from pathlib import Path
from typing import Dict, List
from collections import Counter

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Load environment variables
from dotenv import load_dotenv
load_dotenv(override=True)

from app.sources.json_data_provider import json_data_provider
from app.sources.enhanced_info_service import enhanced_info_service
from app.models.user_config import UserConfig
from app.core.report_generator import ReportGenerator


def demo_trendradar_acquisition(case_name: str, domain: str):
    """Demo TrendRadar-style external info acquisition"""
    print("\n" + "=" * 80)
    print("🔍 DEMO 1: TrendRadar-Style Information Acquisition")
    print("=" * 80 + "\n")

    print(f"📊 Analyzing domain: {domain}")
    print()

    # Get JDs for the domain
    jds = json_data_provider.get_jds(domain=domain)
    print(f"  ✓ Retrieved {len(jds)} job descriptions")

    # Get interview experiences
    experiences = json_data_provider.get_experiences()
    print(f"  ✓ Retrieved {len(experiences)} interview experiences")
    print()

    # Analyze keyword frequency
    print("🔥 High-Frequency Keywords Analysis:")
    print()

    high_freq_keywords = json_data_provider.get_high_frequency_keywords(
        jds,
        domain=domain,
        top_k=15,
        min_frequency=2
    )

    if high_freq_keywords:
        print("  Top keywords (sorted by frequency):")
        for i, (keyword, freq) in enumerate(high_freq_keywords, 1):
            bar = "█" * min(freq, 20)
            print(f"  {i:2d}. {keyword:<25} {bar} ({freq} occurrences)")
    else:
        print("  No high-frequency keywords found")

    print()

    # Show trending topics
    print("📈 Trending Interview Topics:")
    print()

    trending_topics = json_data_provider.get_trending_topics(experiences, top_k=10)

    if trending_topics:
        for i, (topic, freq) in enumerate(trending_topics, 1):
            print(f"  {i:2d}. {topic:<30} ({freq} mentions)")
    else:
        print("  No trending topics found")

    print()

    # Show sample JD
    if jds:
        print("💼 Sample Job Description:")
        jd = jds[0]
        print(f"  Company: {jd.company}")
        print(f"  Position: {jd.position}")
        print(f"  Keywords: {', '.join(jd.keywords[:8])}")
        print()

    # Show how this integrates into support_notes
    print("📝 Integration into support_notes:")
    print()
    print("  When generating questions, if a question involves any high-frequency")
    print("  keywords, the system will mark them as '高频技能' or '行业热点' in")
    print("  support_notes. For example:")
    print()

    if high_freq_keywords:
        top_keyword, top_freq = high_freq_keywords[0]
        print(f"  Example: 该问题涉及 {top_keyword}（高频技能，在{top_freq}个JD中出现），")
        print(f"           建议重点准备相关知识点...")

    print()


def demo_multi_agent_value(case_name: str, user_config: UserConfig):
    """Demo multi-agent architecture value"""
    print("\n" + "=" * 80)
    print("🤖 DEMO 2: Multi-Agent Architecture Benefits")
    print("=" * 80 + "\n")

    print("Generating report with multi-agent hints...")
    print()

    # Generate report
    generator = ReportGenerator()
    report = generator.generate_report(user_config)

    print(f"  ✓ Report generated successfully")
    print(f"  ✓ Total questions: {len(report.questions)}")
    print()

    # Analyze role diversity
    print("🎭 Role Perspective Analysis:")
    print()

    role_counter = Counter()
    for q in report.questions:
        role_counter[q.view_role] += 1

    for role, count in role_counter.most_common():
        percentage = (count / len(report.questions)) * 100
        bar = "█" * int(percentage / 5)
        print(f"  {role:<40} {bar} {count} questions ({percentage:.1f}%)")

    print()

    # Analyze tag diversity
    print("🏷️  Topic Coverage Analysis:")
    print()

    tag_counter = Counter()
    for q in report.questions:
        tag_counter[q.tag] += 1

    for tag, count in tag_counter.most_common(10):
        print(f"  • {tag:<30} ({count} questions)")

    print()

    # Analyze resume specificity
    print("📄 Resume Specificity Analysis:")
    print()

    resume_keywords = ['项目', '经历', '简历', '你的', '你在', '你做', '你开发']
    resume_specific_count = 0

    for q in report.questions:
        if any(kw in q.question for kw in resume_keywords):
            resume_specific_count += 1

    resume_percentage = (resume_specific_count / len(report.questions)) * 100
    print(f"  Resume-specific questions: {resume_specific_count}/{len(report.questions)} ({resume_percentage:.1f}%)")
    print()

    # Show sample question
    print("📝 Sample Question with Full Context:")
    print()

    if report.questions:
        q = report.questions[0]
        print(f"  Role: {q.view_role}")
        print(f"  Tag: {q.tag}")
        print(f"  Question: {q.question}")
        print(f"  Rationale: {q.rationale[:100]}...")
        print(f"  Support Notes: {q.support_notes[:100]}...")

    print()

    # Multi-agent benefits summary
    print("💡 Multi-Agent Architecture Benefits:")
    print()
    print(f"  ✓ Diverse Perspectives: {len(role_counter)} different role viewpoints")
    print(f"  ✓ Comprehensive Coverage: {len(tag_counter)} unique topics addressed")
    print(f"  ✓ Resume Alignment: {resume_percentage:.1f}% questions reference resume")
    print(f"  ✓ Quality Control: Advocate agent filters low-quality questions")
    print(f"  ✓ Deduplication: ForumEngine removes similar questions")

    print()


def main():
    parser = argparse.ArgumentParser(
        description="Demo GrillRadar advanced features"
    )
    parser.add_argument(
        "--case", "-c",
        type=str,
        default="job_backend",
        help="Test case to use (job_backend, job_frontend, grad_nlp)"
    )
    parser.add_argument(
        "--show-keywords", "-k",
        action="store_true",
        help="Show detailed keyword analysis"
    )

    args = parser.parse_args()

    # Banner
    print("""
╔════════════════════════════════════════════════════════════════════════╗
║                                                                        ║
║         🚀 GrillRadar Advanced Features Demo                          ║
║                                                                        ║
║  1. TrendRadar-style external information acquisition                 ║
║  2. BettaFish-style multi-agent architecture                          ║
║                                                                        ║
╚════════════════════════════════════════════════════════════════════════╝
    """)

    # Load test case
    print(f"📂 Loading test case: {args.case}")

    quality_cases_dir = project_root / "examples" / "quality_cases"
    resume_path = quality_cases_dir / f"resume_{args.case}.txt"
    config_path = quality_cases_dir / f"config_{args.case}.json"

    if not resume_path.exists() or not config_path.exists():
        print(f"❌ Test case files not found")
        sys.exit(1)

    with open(resume_path, 'r', encoding='utf-8') as f:
        resume_text = f.read()

    with open(config_path, 'r', encoding='utf-8') as f:
        config_data = json.load(f)

    domain = config_data.get("domain", "backend")

    print(f"  ✓ Loaded resume ({len(resume_text)} chars)")
    print(f"  ✓ Domain: {domain}")

    user_config = UserConfig(
        mode=config_data["mode"],
        target_desc=config_data["target_desc"],
        domain=domain,
        resume_text=resume_text,
        enable_external_info=False  # For demo purposes
    )

    # Demo 1: TrendRadar-style acquisition
    demo_trendradar_acquisition(args.case, domain)

    # Demo 2: Multi-agent value
    demo_multi_agent_value(args.case, user_config)

    print("=" * 80)
    print("✅ DEMO COMPLETE")
    print("=" * 80)
    print()
    print("💡 Key Takeaways:")
    print("  1. External data sources provide real-world context for questions")
    print("  2. Keyword frequency analysis identifies industry trends")
    print("  3. Multi-agent architecture ensures diverse perspectives")
    print("  4. Forum-style coordination improves question quality")
    print()


if __name__ == "__main__":
    main()
