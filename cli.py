#!/usr/bin/env python3
"""
GrillRadar CLI - 命令行界面

用法:
    python cli.py --config config.json --resume resume.txt --output report.md
"""
# 重要：在导入任何模块之前先加载环境变量
from dotenv import load_dotenv
load_dotenv(override=True)

import argparse
import json
import logging
import sys
from pathlib import Path

# 添加app目录到Python路径
sys.path.insert(0, str(Path(__file__).parent))

from app.models.user_config import UserConfig
from app.core.report_generator import ReportGenerator
from app.core.agent_orchestrator import AgentOrchestrator
from app.core.llm_client import LLMClient
from app.utils.markdown import report_to_markdown
from app.utils.document_parser import parse_resume, is_supported_format, DocumentParseError
from app.config.settings import settings
import asyncio

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
    """
    加载简历文件（支持多种格式）

    支持的格式:
    - PDF (.pdf)
    - Word (.docx)
    - Text (.txt)
    - Markdown (.md)
    """
    try:
        # Check if file exists
        resume_path_obj = Path(resume_path)
        if not resume_path_obj.exists():
            logger.error(f"简历文件不存在: {resume_path}")
            sys.exit(1)

        # Check if format is supported
        if not is_supported_format(resume_path):
            logger.error(
                f"不支持的文件格式: {resume_path_obj.suffix}\n"
                f"支持的格式: .pdf, .docx, .txt, .md"
            )
            sys.exit(1)

        # Parse document
        logger.info(f"正在解析简历文件: {resume_path_obj.name}")
        text = parse_resume(resume_path)

        # Validate extracted text
        if not text or len(text.strip()) < 50:
            logger.error(
                f"简历内容过短或为空（{len(text.strip())} 字符）\n"
                f"请确保文件包含有效的简历内容"
            )
            sys.exit(1)

        logger.info(f"✓ 成功解析简历: {len(text)} 字符")
        return text

    except DocumentParseError as e:
        logger.error(f"简历文件解析失败: {e}")
        sys.exit(1)
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

    # 生成报告：使用多智能体模式或单智能体模式
    logger.info("开始生成报告...")
    try:
        if use_multi_agent:
            logger.info("使用多智能体模式生成报告")
            llm_client = LLMClient(provider=args.provider, model=args.model)
            orchestrator = AgentOrchestrator(llm_client)
            report = asyncio.run(orchestrator.generate_report(user_config, enable_multi_agent=True))
        else:
            logger.info("使用单智能体模式生成报告")
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
