#!/usr/bin/env python3
"""
GrillRadar CLI - 命令行界面

用法:
    python cli.py --config config.json --resume resume.txt --output report.md
"""
import argparse
import json
import logging
import sys
from pathlib import Path

# 添加app目录到Python路径
sys.path.insert(0, str(Path(__file__).parent))

from app.models.user_config import UserConfig
from app.core.report_generator import ReportGenerator
from app.utils.markdown import report_to_markdown

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def load_config(config_path: str) -> dict:
    """加载配置文件"""
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"加载配置文件失败: {e}")
        sys.exit(1)


def load_resume(resume_path: str) -> str:
    """加载简历文件"""
    try:
        with open(resume_path, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        logger.error(f"加载简历文件失败: {e}")
        sys.exit(1)


def save_output(output_path: str, content: str):
    """保存输出文件"""
    try:
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(content)
        logger.info(f"报告已保存到: {output_path}")
    except Exception as e:
        logger.error(f"保存报告失败: {e}")
        sys.exit(1)


def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description='GrillRadar - 面试准备报告生成工具',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
    python cli.py --config config.json --resume resume.txt --output report.md

config.json格式:
    {
        "mode": "job",
        "target_desc": "字节跳动 - 后端研发工程师",
        "domain": "backend",
        "level": "junior"
    }
        """
    )

    parser.add_argument(
        '--config',
        required=True,
        help='配置文件路径 (JSON格式)'
    )

    parser.add_argument(
        '--resume',
        required=True,
        help='简历文件路径 (纯文本或Markdown)'
    )

    parser.add_argument(
        '--output',
        default='report.md',
        help='输出文件路径 (默认: report.md)'
    )

    parser.add_argument(
        '--format',
        choices=['markdown', 'json'],
        default='markdown',
        help='输出格式 (默认: markdown)'
    )

    parser.add_argument(
        '--provider',
        choices=['anthropic', 'openai'],
        help='LLM提供商 (默认: 使用环境变量配置)'
    )

    parser.add_argument(
        '--model',
        help='LLM模型名称 (默认: 使用环境变量配置)'
    )

    args = parser.parse_args()

    # 加载配置和简历
    logger.info("正在加载配置和简历...")
    config_data = load_config(args.config)
    resume_text = load_resume(args.resume)

    # 构建UserConfig
    config_data['resume_text'] = resume_text
    try:
        user_config = UserConfig(**config_data)
    except Exception as e:
        logger.error(f"配置验证失败: {e}")
        sys.exit(1)

    # 生成报告
    logger.info("开始生成报告...")
    try:
        generator = ReportGenerator(
            llm_provider=args.provider,
            llm_model=args.model
        )
        report = generator.generate_report(user_config)
    except Exception as e:
        logger.error(f"报告生成失败: {e}")
        sys.exit(1)

    # 输出报告
    if args.format == 'markdown':
        content = report_to_markdown(report)
    else:  # json
        content = report.model_dump_json(indent=2, exclude_none=True)

    save_output(args.output, content)

    # 打印统计信息
    logger.info("=" * 60)
    logger.info(f"✅ 报告生成成功！")
    logger.info(f"📊 问题数量: {len(report.questions)}")
    logger.info(f"🎯 目标岗位: {report.target_desc}")
    logger.info(f"📁 输出文件: {args.output}")
    logger.info("=" * 60)


if __name__ == '__main__':
    main()
