"""
虚拟委员会Prompt构建器（Refactored - prompts loaded from external files）

This module has been refactored to load prompt templates from external markdown files
in the prompts/ directory, making them easier to edit and maintain without touching Python code.
"""
import yaml
import json
import logging
from pathlib import Path
from typing import Dict, Any, Optional
from app.models.user_config import UserConfig
from app.config.settings import settings
from app.sources.external_info_service import external_info_service
from app.sources.enhanced_info_service import enhanced_info_service
from app.config.config_manager import config_manager

logger = logging.getLogger(__name__)


class PromptBuilder:
    """
    构建虚拟委员会的System Prompt

    Prompts are now loaded from external markdown files in prompts/ directory
    for easier editing and maintenance.
    """

    def __init__(self):
        """初始化，使用配置管理器（缓存）"""
        # Use singleton config manager instead of loading files
        self.config_manager = config_manager

        # Load prompt template from file
        self.prompt_template = self._load_prompt_template()

    def _load_prompt_template(self) -> str:
        """
        Load prompt template from external file

        Returns:
            Prompt template string
        """
        # Get project root (GrillRadar/)
        project_root = Path(__file__).parent.parent.parent
        prompt_file = project_root / "prompts" / "system" / "committee_zh.md"

        try:
            with open(prompt_file, 'r', encoding='utf-8') as f:
                template = f.read()
            logger.debug(f"Loaded prompt template from {prompt_file}")
            return template
        except FileNotFoundError:
            logger.warning(f"Prompt template file not found: {prompt_file}, using fallback")
            # Fallback: Return a minimal template
            return self._get_fallback_template()
        except Exception as e:
            logger.error(f"Failed to load prompt template: {e}", exc_info=True)
            return self._get_fallback_template()

    def _get_fallback_template(self) -> str:
        """Fallback template if file loading fails"""
        return """# GrillRadar System Prompt

Mode: {mode}
Target: {target_desc}
Domain: {domain}
Level: {level}

Resume:
{resume_text}

{domain_knowledge}
{external_info}

Generate a report with {target_question_count} questions in JSON format.
"""

    def build(self, user_config: UserConfig) -> str:
        """
        构建完整的System Prompt

        Args:
            user_config: 用户配置

        Returns:
            完整的System Prompt字符串
        """
        # 获取模式配置（使用缓存的配置管理器）
        mode_config = self.config_manager.modes.get(user_config.mode, {})

        # 获取领域知识（如果指定了domain）
        domain_knowledge = self._get_domain_knowledge(user_config.domain)

        # Milestone 4: 获取外部信息（如果启用）
        external_info_text = self._get_external_info(user_config)

        # Fill template with values
        prompt = self.prompt_template.format(
            mode=user_config.mode,
            mode_description=mode_config.get('description', ''),
            target_desc=user_config.target_desc,
            domain=user_config.domain or 'Not specified',
            level=user_config.level or 'Not specified',
            resume_text=user_config.resume_text,
            domain_knowledge=domain_knowledge,
            external_info=external_info_text,
            role_weights=self._format_role_weights(mode_config.get('roles', {})),
            question_distribution=self._format_question_distribution(user_config.mode, mode_config),
            mode_specific_requirements=self._get_mode_specific_requirements(user_config.mode),
            target_question_count=mode_config.get('question_count', {}).get('target', 15),
            min_questions=mode_config.get('question_count', {}).get('min', 10),
            max_questions=mode_config.get('question_count', {}).get('max', 20),
            summary_requirements=self._get_summary_requirements(user_config.mode)
        )

        return prompt

    def _get_domain_knowledge(self, domain: Optional[str]) -> str:
        """获取领域知识的格式化字符串（增强版）"""
        if not domain:
            return "未指定领域，请基于简历内容和目标岗位进行推断。"

        # 尝试从engineering或research中查找（使用缓存的配置管理器）
        for category in ['engineering', 'research']:
            if category in self.config_manager.domains and domain in self.config_manager.domains[category]:
                domain_data = self.config_manager.domains[category][domain]

                # 构建领域知识字符串
                knowledge_parts = []

                # 领域基本信息
                display_name = domain_data.get('display_name', domain)
                description = domain_data.get('description', '')
                knowledge_parts.append(f"**领域**: {display_name}")
                if description:
                    knowledge_parts.append(f"**描述**: {description}")

                # 关键词
                if 'keywords' in domain_data:
                    keywords_str = '、'.join(domain_data['keywords'][:10])  # 限制数量
                    knowledge_parts.append(f"**关键词**: {keywords_str}")

                # 常见技术栈（工程领域）
                if 'common_stacks' in domain_data:
                    stacks_str = '、'.join(domain_data['common_stacks'][:10])
                    knowledge_parts.append(f"**常见技术栈**: {stacks_str}")

                # 经典论文（研究领域）
                if 'canonical_papers' in domain_data:
                    papers_str = '、'.join(domain_data['canonical_papers'][:5])
                    knowledge_parts.append(f"**经典论文**: {papers_str}")

                # 顶级会议（研究领域）
                if 'conferences' in domain_data:
                    conferences_str = '、'.join(domain_data['conferences'])
                    knowledge_parts.append(f"**顶级会议**: {conferences_str}")

                # 典型岗位
                if 'typical_roles' in domain_data:
                    roles_str = '、'.join(domain_data['typical_roles'])
                    knowledge_parts.append(f"**典型岗位**: {roles_str}")

                # 推荐阅读
                if 'recommended_reading' in domain_data:
                    reading_str = '；'.join(domain_data['recommended_reading'][:3])
                    knowledge_parts.append(f"**推荐阅读**: {reading_str}")

                # 组合成最终字符串
                knowledge = '\n'.join(knowledge_parts)

                # 添加提示
                knowledge += "\n\n**重点**: 根据该领域的特点，生成的问题应当聚焦于相关技术栈和核心能力，避免偏离领域范围。"

                return knowledge

        return f"领域 '{domain}' 未在配置中找到，请基于简历内容进行推断。"

    def _format_role_weights(self, roles: Dict[str, float]) -> str:
        """Format role weights"""
        if not roles:
            return "Role weights not configured"

        lines = []
        role_names = {
            'technical_interviewer': 'Technical Interviewer (技术面试官)',
            'hiring_manager': 'Hiring Manager (招聘经理)',
            'hr': 'HR/Behavioral Interviewer (HR/行为面试官)',
            'advisor': 'Advisor/PI (导师/PI)',
            'reviewer': 'Academic Reviewer (学术评审)'
        }

        for role_key, weight in sorted(roles.items(), key=lambda x: x[1], reverse=True):
            role_name = role_names.get(role_key, role_key)
            percentage = int(weight * 100)
            lines.append(f"- {role_name}: {percentage}%")

        return "\n".join(lines)

    def _format_question_distribution(self, mode: str, mode_config: Dict) -> str:
        """Format question distribution requirements"""
        dist = mode_config.get('question_distribution', {})
        if not dist:
            return "Question distribution not configured"

        lines = []
        for category, ratio in dist.items():
            percentage = int(ratio * 100)
            lines.append(f"- {category}: {percentage}%")

        return "\n".join(lines)

    def _get_mode_specific_requirements(self, mode: str) -> str:
        """Get mode-specific requirements"""
        if mode == "mixed":
            return "- **IMPORTANT**: For mixed mode, ensure balanced dual perspectives (engineering questions and academic questions each ~50%)"
        elif mode == "grad":
            return "- **IMPORTANT**: For grad mode, check coverage of: research methodology, paper reading, academic standards"
        else:
            return "- Ensure coverage of: CS fundamentals, project depth, engineering practice, soft skills"

    def _get_summary_requirements(self, mode: str) -> str:
        """Get summary field requirements"""
        if mode == "mixed":
            return """- **For mixed mode, summary MUST contain two independent evaluations (in Chinese)**:
  ```
  【工程候选人评估】
  作为XX工程师候选人，你的项目经验...

  【科研候选人评估】
  作为XX方向的研究生候选人，你的XX基础...
  ```"""
        return ""

    def _get_external_info(self, user_config: UserConfig) -> str:
        """
        获取外部信息（Milestone 4 + TrendRadar增强）

        Args:
            user_config: 用户配置

        Returns:
            格式化的外部信息文本，包含关键词频率分析
        """
        # Always enable external info from JSON database for better questions
        # Users can see the TrendRadar-style intelligence in action
        try:
            # 提取公司和岗位信息
            company = user_config.target_company
            position_desc = user_config.target_desc
            domain = user_config.domain

            # 简单提取岗位关键词
            position = None
            if "后端" in position_desc or "backend" in position_desc.lower():
                position = "后端"
            elif "前端" in position_desc or "frontend" in position_desc.lower():
                position = "前端"
            elif "算法" in position_desc or "nlp" in position_desc.lower():
                position = "算法"

            logger.info(f"Retrieving TrendRadar external info for company={company}, position={position}, domain={domain}")

            # 使用增强版服务，包含关键词频率分析
            summary, high_freq_keywords = enhanced_info_service.retrieve_with_trends(
                company=company,
                position=position,
                domain=domain,
                enable_jd=True,
                enable_interview_exp=True
            )

            if summary is None and not high_freq_keywords:
                logger.info("No external info found, continuing without it")
                return ""

            # 获取格式化文本，包含关键词频率提示
            external_text = enhanced_info_service.format_for_prompt(summary, high_freq_keywords)

            logger.info(f"External info retrieved: {len(summary.job_descriptions) if summary else 0} JDs, "
                       f"{len(high_freq_keywords)} high-freq keywords")

            return f"\n{external_text}\n"

        except Exception as e:
            logger.error(f"Failed to get external info: {e}", exc_info=True)
            return ""
