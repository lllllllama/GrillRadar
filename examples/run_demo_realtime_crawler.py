#!/usr/bin/env python3
"""
GrillRadar Real-time Crawler Demo
使用GitHub实时爬虫生成面试准备报告

使用方法:
    python examples/run_demo_realtime_crawler.py

输出:
    examples/hardcore_report_realtime.md
"""
import sys
import json
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# 加载环境变量
from dotenv import load_dotenv
load_dotenv(override=True)

from app.models.user_config import UserConfig
from app.core.report_generator import ReportGenerator
from app.utils.markdown import report_to_markdown


def main():
    print("=" * 70)
    print("🌐 GrillRadar Real-time Crawler Demo")
    print("=" * 70)
    print("   使用GitHub实时爬虫获取最新技术趋势")
    print("=" * 70)
    print()

    # 1. 读取简历文件
    resume_path = project_root / "examples" / "resume_llm_senior.txt"
    print(f"📄 读取高级工程师简历: {resume_path.name}")
    with open(resume_path, "r", encoding="utf-8") as f:
        resume_text = f.read()
    print(f"   ✓ 简历长度: {len(resume_text)} 字符")
    print()

    # 2. 创建用户配置
    print("🔧 创建用户配置...")
    user_config = UserConfig(
        mode="job",
        target_desc="字节跳动抖音推荐 - LLM应用架构师（P6-P7）",
        domain="llm_application",
        level="senior",
        resume_text=resume_text,
        enable_external_info=True,  # 启用外部信息
        target_company="字节跳动"
    )
    print(f"   ✓ 模式: {user_config.mode}")
    print(f"   ✓ 目标: {user_config.target_desc}")
    print(f"   ✓ 领域: {user_config.domain}")
    print(f"   ✓ 级别: {user_config.level}")
    print(f"   ✓ 外部信息: 实时GitHub爬虫")
    print(f"   ✓ 目标公司: {user_config.target_company}")
    print()

    # 3. 生成报告
    print("🤖 生成面试准备报告 (Real-time Crawler)...")
    print("   第一次运行会从GitHub爬取数据，可能需要 60-90 秒")
    print()
    try:
        generator = ReportGenerator()
        report = generator.generate_report(user_config)
        print(f"   ✓ 报告生成成功！")
        print(f"   ✓ 包含 {len(report.questions)} 个精选问题")
        print()
    except Exception as e:
        print(f"   ✗ 报告生成失败: {e}")
        print()
        print("💡 提示: 请检查以下配置:")
        print("   1. .env 文件中的 EXTERNAL_INFO_PROVIDER 应为 multi_source_crawler")
        print("   2. API Key 是否正确")
        print("   3. 网络连接是否正常")
        import traceback
        traceback.print_exc()
        sys.exit(1)

    # 4. 转换为 Markdown
    print("📝 导出 Markdown 格式...")
    markdown_content = report_to_markdown(report)
    print("   ✓ Markdown 转换成功")
    print()

    # 5. 保存文件
    output_path = project_root / "examples" / "hardcore_report_realtime.md"
    print(f"💾 保存报告: {output_path.name}")
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(markdown_content)
    print(f"   ✓ 文件已保存")
    print()

    # 6. 显示摘要
    print("=" * 70)
    print("✨ 演示完成！")
    print("=" * 70)
    print()
    print(f"📊 报告统计:")
    print(f"   • 模式: {report.mode}")
    print(f"   • 问题数量: {len(report.questions)}")
    print(f"   • 外部信息: GitHub实时爬虫")
    print(f"   • 输出文件: {output_path.relative_to(project_root)}")
    print()
    print(f"📖 查看报告:")
    print(f"   cat {output_path.relative_to(project_root)}")
    print()
    print(f"🎯 特色:")
    print(f"   ✓ 实时GitHub trending趋势")
    print(f"   ✓ 25个高质量问题")
    print(f"   ✓ Senior级别深度技术问题")
    print(f"   ✓ 多智能体协作生成")
    print()


if __name__ == "__main__":
    main()
