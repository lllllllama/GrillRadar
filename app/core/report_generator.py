"""报告生成协调器"""
import logging
from typing import Optional
from app.models.user_config import UserConfig
from app.models.report import Report, ReportMeta
from app.core.prompt_builder import PromptBuilder
from app.core.llm_client import LLMClient

logger = logging.getLogger(__name__)


class ReportGenerator:
    """报告生成协调器 - 协调整个报告生成流程"""

    def __init__(
        self,
        llm_provider: Optional[str] = None,
        llm_model: Optional[str] = None
    ):
        """
        初始化报告生成器

        Args:
            llm_provider: LLM提供商（anthropic/openai）
            llm_model: LLM模型名称
        """
        self.prompt_builder = PromptBuilder()
        self.llm_client = LLMClient(provider=llm_provider, model=llm_model)

    def generate_report(self, user_config: UserConfig) -> Report:
        """
        生成完整的Grilling报告

        Args:
            user_config: 用户配置（包含简历和目标等信息）

        Returns:
            完整的Report对象

        Raises:
            ValueError: 如果生成的报告不符合规范
        """
        logger.info(f"开始生成报告 - 模式: {user_config.mode}, 目标: {user_config.target_desc}")

        # 1. 构建Prompt
        logger.info("构建虚拟委员会Prompt...")
        system_prompt = self.prompt_builder.build(user_config)

        # 2. 调用LLM
        logger.info("调用LLM生成报告...")
        try:
            report_data = self.llm_client.call_json(system_prompt)
        except Exception as e:
            logger.error(f"LLM调用失败: {str(e)}")
            raise

        # 3. 验证并构建Report对象
        logger.info("验证并构建Report对象...")
        try:
            # 确保meta字段存在
            if 'meta' not in report_data:
                report_data['meta'] = {}

            # 补充meta字段
            if 'num_questions' not in report_data['meta']:
                report_data['meta']['num_questions'] = len(report_data.get('questions', []))

            # 使用Pydantic验证
            report = Report(**report_data)

            # 额外验证
            self._validate_report(report, user_config)

            logger.info(f"报告生成成功 - 包含{len(report.questions)}个问题")
            return report

        except Exception as e:
            logger.error(f"报告验证失败: {str(e)}")
            logger.debug(f"LLM返回的数据: {report_data}")
            raise ValueError(f"生成的报告不符合规范: {str(e)}")

    def _validate_report(self, report: Report, user_config: UserConfig):
        """
        额外验证报告内容

        Args:
            report: 生成的报告
            user_config: 用户配置

        Raises:
            ValueError: 如果验证失败
        """
        # 验证问题数量
        num_questions = len(report.questions)
        if num_questions < 10:
            raise ValueError(f"问题数量不足：只有{num_questions}个，至少需要10个")
        if num_questions > 20:
            raise ValueError(f"问题数量过多：有{num_questions}个，最多20个")

        # 验证模式匹配
        if report.mode != user_config.mode:
            raise ValueError(f"报告模式({report.mode})与用户配置({user_config.mode})不匹配")

        # 对mixed模式，验证summary包含双线评估
        if user_config.mode == "mixed":
            if "【工程候选人评估】" not in report.summary or "【科研候选人评估】" not in report.summary:
                logger.warning("Mixed模式的报告缺少双线评估标记")

        # 验证问题ID连续性
        for i, question in enumerate(report.questions, 1):
            if question.id != i:
                logger.warning(f"问题ID不连续：期望{i}，实际{question.id}")

        # 验证prompt_template包含占位符
        for question in report.questions:
            if "{your_experience}" not in question.prompt_template and "{" not in question.prompt_template:
                logger.warning(f"问题{question.id}的prompt_template可能缺少占位符")

        logger.info("报告验证通过")
