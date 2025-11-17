#!/usr/bin/env python3
"""
GrillRadar Demo Script - 计算机视觉研究生申请
一键生成面试准备报告 Markdown

使用方法:
    python examples/run_demo_cv.py

输出:
    examples/demo_report_cv.md
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
    print("=" * 60)
    print("🔥 GrillRadar Demo - 计算机视觉PhD申请面试准备")
    print("=" * 60)
    print()

    # 1. 读取简历文件
    resume_path = project_root / "examples" / "resume_cv_researcher.txt"
    print(f"📄 读取简历: {resume_path.name}")
    with open(resume_path, "r", encoding="utf-8") as f:
        resume_text = f.read()
    print(f"   ✓ 简历长度: {len(resume_text)} 字符")
    print()

    # 2. 读取配置文件
    config_path = project_root / "examples" / "config_demo_cv.json"
    print(f"⚙️  加载配置: {config_path.name}")
    with open(config_path, "r", encoding="utf-8") as f:
        config_data = json.load(f)
    print(f"   ✓ 模式: {config_data['mode']}")
    print(f"   ✓ 目标: {config_data['target_desc']}")
    print(f"   ✓ 领域: {config_data['domain']}")
    print(f"   ✓ 多智能体: {'启用' if config_data.get('multi_agent_enabled', False) else '禁用'}")
    print()

    # 3. 创建用户配置
    print("🔧 创建用户配置...")
    user_config = UserConfig(
        mode=config_data["mode"],
        target_desc=config_data["target_desc"],
        domain=config_data.get("domain"),
        resume_text=resume_text,
        enable_external_info=config_data.get("enable_external_info", False)
    )
    print("   ✓ 配置创建成功")
    print()

    # 4. 生成报告
    print("🤖 生成面试准备报告...")
    print("   (这可能需要 30-60 秒，请耐心等待)")
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
        print("   1. .env 文件中的 API Key 是否正确")
        print("   2. 网络连接是否正常")
        print("   3. API 配额是否充足")
        sys.exit(1)

    # 5. 转换为 Markdown
    print("📝 导出 Markdown 格式...")
    markdown_content = report_to_markdown(report)
    print("   ✓ Markdown 转换成功")
    print()

    # 6. 保存文件
    output_path = project_root / "examples" / "demo_report_cv.md"
    print(f"💾 保存报告: {output_path.name}")
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(markdown_content)
    print(f"   ✓ 文件已保存")
    print()

    # 7. 显示摘要
    print("=" * 60)
    print("✨ 演示完成！")
    print("=" * 60)
    print()
    print(f"📊 报告统计:")
    print(f"   • 模式: {report.mode}")
    print(f"   • 问题数量: {len(report.questions)}")
    print(f"   • 输出文件: {output_path.relative_to(project_root)}")
    print()
    print(f"📖 查看报告:")
    print(f"   cat {output_path.relative_to(project_root)}")
    print()
    print(f"🎯 下一步:")
    print(f"   1. 阅读生成的研究问题和论文建议")
    print(f"   2. 使用 prompt_template 深化研究理解")
    print(f"   3. 准备好与导师的深度学术交流！")
    print()


if __name__ == "__main__":
    main()
