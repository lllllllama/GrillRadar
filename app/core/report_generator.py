"""报告生成协调器"""
import logging
from typing import Optional
from app.models.user_config import UserConfig
from app.models.report import Report, ReportMeta, QuestionItem
from app.core.prompt_builder import PromptBuilder
from app.core.llm_client import LLMClient
from app.core.logging import get_logger

logger = get_logger(__name__)


class ReportGenerator:
    """报告生成协调器 - 协调整个报告生成流程"""

    def __init__(
        self,
        llm_provider: Optional[str] = None,
        llm_model: Optional[str] = None,
        request_id: Optional[str] = None
    ):
        """
        初始化报告生成器

        Args:
            llm_provider: LLM提供商（anthropic/openai）
            llm_model: LLM模型名称
            request_id: 请求ID（用于日志追踪）
        """
        self.prompt_builder = PromptBuilder()
        self.llm_client = LLMClient(
            provider=llm_provider,
            model=llm_model,
            request_id=request_id
        )
        self.request_id = request_id or ""

    def generate_report(self, user_config: UserConfig) -> Report:
        """
        生成完整的Grilling报告

        Args:
            user_config: 用户配置（包含简历和目标等信息）

        Returns:
            完整的Report对象

        Raises:
            ValueError: 如果生成的报告不符合规范且无法降级
        """
        extra = {'request_id': self.request_id}
        logger.info(
            f"开始生成报告 - 模式: {user_config.mode}, 目标: {user_config.target_desc}",
            extra=extra
        )

        # 1. 构建Prompt
        logger.info("构建虚拟委员会Prompt...", extra=extra)
        system_prompt = self.prompt_builder.build(user_config)

        # 2. 调用LLM
        logger.info("调用LLM生成报告...", extra=extra)
        try:
            report_data = self.llm_client.call_json(system_prompt)
        except Exception as e:
            logger.error(f"LLM调用失败: {str(e)}", extra=extra, exc_info=True)
            # Try graceful degradation
            return self._create_fallback_report(user_config, error_message=str(e))

        # 3. 验证并构建Report对象
        logger.info("验证并构建Report对象...", extra=extra)
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

            logger.info(
                f"报告生成成功 - 包含{len(report.questions)}个问题",
                extra=extra
            )
            return report

        except Exception as e:
            logger.error(
                f"报告验证失败: {str(e)}",
                extra=extra,
                exc_info=True
            )
            logger.debug(f"LLM返回的数据: {report_data}", extra=extra)

            # Try to create simplified report from partial data
            return self._create_simplified_report(report_data, user_config, error_message=str(e))

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

    def _create_fallback_report(self, user_config: UserConfig, error_message: str) -> Report:
        """
        Create a fallback report when LLM call fails completely.

        This ensures the user gets SOME output rather than a complete crash.

        Args:
            user_config: User configuration
            error_message: Error message from the failure

        Returns:
            Minimal fallback report
        """
        extra = {'request_id': self.request_id}
        logger.warning(
            "Creating fallback report due to LLM failure",
            extra=extra
        )

        # Create minimal report with error information
        fallback_questions = [
            QuestionItem(
                id=1,
                question=f"⚠️ 报告生成失败",
                rationale=f"LLM调用失败: {error_message}",
                role="系统",
                baseline_answer="请检查API配置和网络连接，然后重试。",
                prompt_template="N/A",
                support_notes="如果问题持续，请查看日志文件或联系技术支持。"
            )
        ]

        return Report(
            mode=user_config.mode,
            target_desc=user_config.target_desc,
            summary=f"⚠️ 报告生成失败\n\n错误信息: {error_message}\n\n请检查配置并重试。",
            questions=fallback_questions,
            meta=ReportMeta(
                num_questions=1,
                difficulty_distribution={"error": 1},
                question_categories=["系统错误"]
            )
        )

    def _create_simplified_report(
        self,
        report_data: dict,
        user_config: UserConfig,
        error_message: str
    ) -> Report:
        """
        Create a simplified report from partial/malformed LLM output.

        This tries to salvage whatever valid data we can from the LLM response.

        Args:
            report_data: Partial/malformed report data from LLM
            user_config: User configuration
            error_message: Error message from validation failure

        Returns:
            Simplified report with available data
        """
        extra = {'request_id': self.request_id}
        logger.warning(
            "Creating simplified report from partial data",
            extra=extra
        )

        # Try to extract questions
        questions = []
        raw_questions = report_data.get('questions', [])

        for i, q_data in enumerate(raw_questions, 1):
            try:
                # Try to create QuestionItem with relaxed validation
                question = QuestionItem(
                    id=i,
                    question=q_data.get('question', f'Question {i}'),
                    rationale=q_data.get('rationale', ''),
                    role=q_data.get('role', '未知'),
                    baseline_answer=q_data.get('baseline_answer', ''),
                    prompt_template=q_data.get('prompt_template', q_data.get('question', '')),
                    support_notes=q_data.get('support_notes', '')
                )
                questions.append(question)
            except Exception as e:
                logger.debug(f"Failed to parse question {i}: {e}", extra=extra)
                # Skip malformed questions
                continue

        # If we got no questions, create a warning question
        if not questions:
            questions = [
                QuestionItem(
                    id=1,
                    question="⚠️ 报告数据解析失败",
                    rationale=f"无法从LLM输出中提取有效问题: {error_message}",
                    role="系统",
                    baseline_answer="请重试报告生成。",
                    prompt_template="N/A",
                    support_notes="检查日志获取详细错误信息。"
                )
            ]

        # Extract summary or create fallback
        summary = report_data.get('summary', '')
        if not summary:
            summary = f"⚠️ 简化报告\n\n由于数据验证失败，此报告仅包含部分信息。\n错误: {error_message}"

        return Report(
            mode=user_config.mode,
            target_desc=user_config.target_desc,
            summary=summary,
            questions=questions,
            meta=ReportMeta(
                num_questions=len(questions),
                difficulty_distribution=report_data.get('meta', {}).get('difficulty_distribution', {}),
                question_categories=report_data.get('meta', {}).get('question_categories', [])
            )
        )
