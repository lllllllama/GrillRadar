#!/usr/bin/env python3
"""
GrillRadar CLI - 命令行界面

用法:
    python cli.py --config config.json --resume resume.txt --output report.md

环境变量:
    GRILLRADAR_DEBUG=1  - 启用调试日志
"""
# 重要：在导入任何模块之前先加载环境变量
from dotenv import load_dotenv
load_dotenv(override=True)

import argparse
import json
import os
import sys
from pathlib import Path

# 添加app目录到Python路径
sys.path.insert(0, str(Path(__file__).parent))

from app.models import UserConfig
from app.core.pipeline import GrillRadarPipeline
from app.utils.markdown import report_to_markdown
from app.utils.document_parser import DocumentParseError
from app.config.settings import settings
from app.core.logging import configure_logging, get_logger, generate_request_id

# Configure logging (will read GRILLRADAR_DEBUG env var)
configure_logging()
logger = get_logger(__name__)


def load_config(config_path: str) -> dict:
    """加载配置文件"""
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"加载配置文件失败: {e}")
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
        help='简历文件路径 (支持: .pdf, .docx, .txt, .md)'
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

    parser.add_argument(
        '--multi-agent',
        action='store_true',
        default=None,
        help='强制启用多智能体模式'
    )

    parser.add_argument(
        '--no-multi-agent',
        action='store_true',
        help='强制禁用多智能体模式（使用单智能体fallback）'
    )

    parser.add_argument(
        '--debug-agents',
        action='store_true',
        help='启用debug模式：保存中间产物到debug/目录'
    )

    args = parser.parse_args()

    # 处理多智能体模式设置
    use_multi_agent = settings.MULTI_AGENT_ENABLED
    if args.multi_agent:
        use_multi_agent = True
        logger.info("强制启用多智能体模式 (--multi-agent)")
    elif args.no_multi_agent:
        use_multi_agent = False
        logger.info("强制禁用多智能体模式 (--no-multi-agent)")

    # 处理debug模式设置
    if args.debug_agents:
        settings.GRILLRADAR_DEBUG_AGENTS = True
        logger.info("已启用debug模式：将保存中间产物到debug/目录")

    # 加载配置
    logger.info("正在加载配置...")
    config_data = load_config(args.config)

    # 构建UserConfig (不包含resume_text，由pipeline处理)
    try:
        user_config = UserConfig(**config_data, resume_text="")  # Placeholder
    except Exception as e:
        logger.error(f"配置验证失败: {e}")
        sys.exit(1)

    # Generate request ID for tracing
    request_id = generate_request_id()
    logger.info(f"生成请求ID: {request_id}")

    # 使用Pipeline生成报告
    logger.info("开始生成报告...")
    try:
        pipeline = GrillRadarPipeline(
            llm_provider=args.provider,
            llm_model=args.model,
            enable_multi_agent=use_multi_agent,
            request_id=request_id
        )
        report = pipeline.run(
            resume_path=args.resume,
            user_config=user_config
        )
    except DocumentParseError as e:
        logger.error(f"简历文件解析失败: {e}", extra={'request_id': request_id})
        sys.exit(1)
    except Exception as e:
        logger.error(f"报告生成失败: {e}", extra={'request_id': request_id}, exc_info=True)
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
