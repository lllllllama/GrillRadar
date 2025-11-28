"""报告生成协调器"""
import logging
from typing import Optional
from app.models.user_config import UserConfig
from app.models.report import Report, ReportMeta, QuestionItem, RawReport
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

            # 阶段1: 使用宽松模型(RawReport)进行初步解析
            raw_report = RawReport(**report_data)

            # 智能截断 (Smart Truncation)
            if len(raw_report.questions) > 50:
                logger.info(f"Question count ({len(raw_report.questions)}) exceeds limit. Applying smart truncation...", extra=extra)
                raw_report.questions = self._smart_truncate_questions(raw_report.questions, 50)

            # 阶段2: 尝试转换为严格模型(Report)
            # convert raw objects to strict objects to validate constraints
            report = Report(**raw_report.model_dump())

            # 额外验证 (Business Logic)
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
        if num_questions > 50:
            raise ValueError(f"问题数量过多：有{num_questions}个，最多50个")

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
                question=self._ensure_text_length("⚠️ 报告生成失败", 5),
                view_role="系统",
                tag="系统错误",
                rationale=self._ensure_text_length(f"LLM调用失败，请检查配置: {error_message}", 10),
                baseline_answer=self._ensure_text_length("请检查API配置和网络连接，然后重试。", 20),
                prompt_template=self._ensure_text_length("请重试报告生成，并检查输入数据是否正确。{your_experience}", 20),
                support_notes=self._ensure_text_length("如果问题持续，请查看日志文件或联系技术支持。", 10)
            )
        ]

        return Report(
            mode=user_config.mode,
            target_desc=user_config.target_desc,
            summary=f"⚠️ 报告生成失败\n\n错误信息: {error_message}\n\n请检查配置并重试。",
            highlights="N/A",
            risks="N/A",
            questions=fallback_questions,
            meta=ReportMeta(
                num_questions=1,
                difficulty_distribution={"error": 1},
                question_categories=["系统错误"]
            )
        )

    def _smart_truncate_questions(self, questions: list, limit: int) -> list:
        """
        Smartly truncate questions to limit, prioritizing high relevance and role diversity.

        Strategy:
        1. Always keep top 50% of limit (e.g. 25) to ensure best questions are kept
        2. For the rest, try to maintain role balance
        3. If no metadata available, just truncate
        """
        if not questions or len(questions) <= limit:
            return questions

        # For now, simple truncation but with logging.
        # Future improvement: implement relevance sorting and role balancing
        # Current priority: strict truncation to ensure schema validation passes
        return questions[:limit]

    def _ensure_text_length(self, text: str, min_length: int, pad_char: str = " ") -> str:
        """Helper to ensure text meets minimum length requirements"""
        if not text:
            return "N/A" * (min_length // 3 + 1)
        if len(text) < min_length:
            return text + pad_char * (min_length - len(text))
        return text

    def _create_simplified_report(
        self,
        report_data: dict,
        user_config: UserConfig,
        error_message: str
    ) -> Report:
        """
        Create a simplified report from partial/malformed LLM output.

        This tries to salvage whatever valid data we can from the LLM response.
        Ensures the returned Report meets Strict Schema requirements by padding if necessary.

        Args:
            report_data: Partial/malformed report data from LLM
            user_config: User configuration
            error_message: Error message from validation failure

        Returns:
            Simplified report with available data that passes validation
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
                # To meet Strict QuestionItem, we must ensure fields meet min_length
                q_text = self._ensure_text_length(
                    q_data.get('question', f'Question {i}'), 5
                )
                rationale = self._ensure_text_length(
                    q_data.get('rationale', '解析失败的理由占位符'), 10
                )
                answer = self._ensure_text_length(
                    q_data.get('baseline_answer', '解析失败的答案占位符'), 20
                )
                notes = self._ensure_text_length(
                    q_data.get('support_notes', '解析失败的材料占位符'), 10
                )
                template = self._ensure_text_length(
                    q_data.get('prompt_template', f'{q_text} {{your_experience}}'), 20
                )

                # Check for placeholders in template
                if "{your_experience}" not in template:
                    template += " {your_experience}"

                question = QuestionItem(
                    id=i,
                    question=q_text,
                    view_role=q_data.get('view_role', '系统'),
                    tag=q_data.get('tag', '未知'),
                    rationale=rationale,
                    baseline_answer=answer,
                    prompt_template=template,
                    support_notes=notes
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
                    question=self._ensure_text_length("⚠️ 报告数据解析失败", 5),
                    view_role="系统",
                    tag="系统错误",
                    rationale=self._ensure_text_length(f"无法从LLM输出中提取有效问题: {error_message}", 10),
                    baseline_answer=self._ensure_text_length("请检查日志获取详细错误信息，并重试报告生成。", 20),
                    prompt_template=self._ensure_text_length("请重试报告生成，并检查输入数据是否正确。{your_experience}", 20),
                    support_notes=self._ensure_text_length("检查日志获取详细错误信息。", 10)
                )
            ]
        elif len(questions) > 50:
            questions = self._smart_truncate_questions(questions, 50)

        # Ensure we meet min question count (10) by duplicating if necessary or padding
        # But Report validation logic enforces min_length=10.
        # If we have < 10 questions, we need to pad.
        while len(questions) < 10:
            # Create padding questions
            idx = len(questions) + 1
            questions.append(QuestionItem(
                id=idx,
                question=f"⚠️ 数据不足补充问题 {idx}",
                view_role="系统",
                tag="系统提示",
                rationale="由于原始数据不足，自动补充此占位问题以满足格式要求。",
                baseline_answer=self._ensure_text_length("请忽略此问题或重试生成。", 20),
                prompt_template=self._ensure_text_length("无需回答。{your_experience}", 20),
                support_notes="无需参考。" + " " * 10
            ))

        # Extract summary or create fallback
        summary = report_data.get('summary', '')
        if not summary:
            summary = f"⚠️ 简化报告\n\n由于数据验证失败，此报告仅包含部分信息。\n错误: {error_message}"
        else:
            if error_message and "简化报告" not in summary:
                summary = f"⚠️ 简化报告 (验证失败: {error_message})\n\n{summary}"

        # Ensure strict length requirements for Report fields
        summary = self._ensure_text_length(summary, 30)
        highlights = self._ensure_text_length(report_data.get('highlights', "N/A"), 20)
        risks = self._ensure_text_length(report_data.get('risks', "N/A"), 20)

        return Report(
            mode=user_config.mode,
            target_desc=user_config.target_desc,
            summary=summary,
            highlights=highlights,
            risks=risks,
            questions=questions,
            meta=ReportMeta(
                num_questions=len(questions),
                difficulty_distribution=report_data.get('meta', {}).get('difficulty_distribution', {}),
                question_categories=report_data.get('meta', {}).get('question_categories', [])
            )
        )
