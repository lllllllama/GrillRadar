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

        # Load research configurations
        self.research_domains = self._load_research_domains()
        self.china_grad_config = self._load_china_grad_config()

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
{research_guidance}
{external_info}

Generate a report with {target_question_count} questions in JSON format.
"""

    def _load_research_domains(self) -> Dict[str, Any]:
        """Load research domains configuration"""
        project_root = Path(__file__).parent.parent.parent
        config_file = project_root / "config" / "research_domains.yaml"

        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)
            logger.debug(f"Loaded research domains from {config_file}")
            return config or {}
        except FileNotFoundError:
            logger.warning(f"Research domains config not found: {config_file}")
            return {}
        except Exception as e:
            logger.error(f"Failed to load research domains: {e}", exc_info=True)
            return {}

    def _load_china_grad_config(self) -> Dict[str, Any]:
        """Load China graduate school interview configuration"""
        project_root = Path(__file__).parent.parent.parent
        config_file = project_root / "config" / "china_grad.yaml"

        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)
            logger.debug(f"Loaded China grad config from {config_file}")
            return config or {}
        except FileNotFoundError:
            logger.warning(f"China grad config not found: {config_file}")
            return {}
        except Exception as e:
            logger.error(f"Failed to load China grad config: {e}", exc_info=True)
            return {}

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

        # Get research-specific guidance (for grad/mixed modes)
        research_guidance = self._get_research_guidance(user_config)

        # Fill template with values
        prompt = self.prompt_template.format(
            mode=user_config.mode,
            mode_description=mode_config.get('description', ''),
            target_desc=user_config.target_desc,
            domain=user_config.domain or 'Not specified',
            level=user_config.level or 'Not specified',
            resume_text=user_config.resume_text,
            domain_knowledge=domain_knowledge,
            research_guidance=research_guidance,
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

            logger.info(f"Retrieving external info using provider: {external_info_service.provider_type}")

            # 使用配置的external_info_service（支持多种provider）
            summary = external_info_service.retrieve_external_info(
                user_config=user_config,
                company=company,
                position=position,
                domain=domain,
                enable_jd=True,
                enable_interview_exp=True
            )

            if summary is None:
                logger.info("No external info found, continuing without it")
                return ""

            # 获取格式化文本
            external_text = external_info_service.get_prompt_summary(summary)

            logger.info(f"External info retrieved: {len(summary.job_descriptions) if summary else 0} JDs, "
                       f"{len(summary.interview_experiences) if summary else 0} interviews")

            return f"\n{external_text}\n"

        except Exception as e:
            logger.error(f"Failed to get external info: {e}", exc_info=True)
            return ""

    def _get_research_guidance(self, user_config: UserConfig) -> str:
        """
        Get research-specific guidance for grad/PhD interview modes

        Args:
            user_config: User configuration

        Returns:
            Formatted research guidance string
        """
        # Only inject research guidance for grad/mixed modes
        if user_config.mode not in ['grad', 'mixed']:
            return ""

        guidance_parts = []

        # Research domain knowledge
        if user_config.domain and user_config.domain in self.research_domains:
            domain_info = self.research_domains[user_config.domain]
            guidance_parts.append(self._format_research_domain(user_config.domain, domain_info))

        # China grad context (if language is Chinese)
        if user_config.language == 'zh' and self.china_grad_config:
            guidance_parts.append(self._format_china_grad_context(self.china_grad_config))

        if not guidance_parts:
            return ""

        return "\n\n" + "\n\n".join(guidance_parts)

    def _format_research_domain(self, domain_key: str, domain_info: Dict[str, Any]) -> str:
        """Format research domain information for prompt injection"""
        parts = []

        # Header
        display_name = domain_info.get('display_name', domain_key)
        parts.append(f"### 研究领域知识库: {display_name}")
        parts.append("")

        # Conferences
        if 'conferences' in domain_info:
            parts.append("**相关顶级会议/期刊:**")
            conferences = domain_info['conferences']

            if isinstance(conferences, dict):
                for tier, conf_list in conferences.items():
                    if isinstance(conf_list, list) and conf_list:
                        conf_str = ", ".join(conf_list)
                        parts.append(f"- {tier}: {conf_str}")
            elif isinstance(conferences, list):
                parts.append(f"- {', '.join(conferences)}")
            parts.append("")

        # Core topics
        if 'core_topics' in domain_info:
            topics = domain_info['core_topics']
            if topics:
                parts.append("**核心研究主题:**")
                parts.append(", ".join(topics[:10]))  # Limit to 10
                parts.append("")

        # Recommended queries
        if 'recommended_queries' in domain_info:
            queries = domain_info['recommended_queries']
            if queries:
                parts.append("**推荐文献检索关键词:**")
                for query in queries[:5]:  # Limit to 5
                    parts.append(f"- \"{query}\"")
                parts.append("")

        # Common methods
        if 'common_methods' in domain_info:
            methods = domain_info['common_methods']
            if methods:
                parts.append("**常见方法:**")
                parts.append(", ".join(methods[:8]))  # Limit to 8
                parts.append("")

        # Important instructions
        parts.append("**重要提示:**")
        parts.append("- 在`support_notes`中，应引导学生阅读相关顶会论文（仅提及会议名，不编造具体论文标题/作者）")
        parts.append("- 推荐使用上述检索关键词进行文献调研")
        parts.append("- 避免编造不存在的论文、作者或具体实验结果")
        parts.append("- 使用如'阅读近期CVPR/NeurIPS关于X的论文'、'搜索Y survey构建系统了解'等表述")

        return "\n".join(parts)

    def _format_china_grad_context(self, china_grad: Dict[str, Any]) -> str:
        """Format China grad school interview context"""
        parts = []

        parts.append("### 中国研究生面试情境知识")
        parts.append("")

        # Interview structure
        if 'interview_structure' in china_grad:
            structure = china_grad['interview_structure']
            if 'typical_components' in structure:
                parts.append("**典型面试环节:**")
                for component in structure['typical_components']:
                    name = component.get('name', '')
                    desc = component.get('description', '')
                    if name and desc:
                        parts.append(f"- {name}: {desc}")
                parts.append("")

        # Evaluation dimensions
        if 'evaluation_dimensions' in china_grad:
            dimensions = china_grad['evaluation_dimensions']
            if dimensions:
                parts.append("**核心评估维度:**")
                for dim in dimensions[:4]:  # Top 4
                    dim_name = dim.get('dimension', '')
                    desc = dim.get('description', '')
                    if dim_name and desc:
                        parts.append(f"- {dim_name}: {desc}")
                parts.append("")

        # Killer question patterns
        if 'killer_question_patterns' in china_grad:
            patterns = china_grad['killer_question_patterns']
            if patterns:
                parts.append("**高质量问题模式 (仅参考模式，不直接使用例子):**")
                for pattern in patterns[:3]:  # Top 3 patterns
                    pattern_name = pattern.get('pattern', '')
                    pattern_desc = pattern.get('description', '')
                    if pattern_name and pattern_desc:
                        parts.append(f"- {pattern_name}: {pattern_desc}")
                parts.append("")

        # Important instructions
        parts.append("**面试问题生成指导:**")
        parts.append("- 问题应符合中国研究生面试的评估维度和提问风格")
        parts.append("- 在`support_notes`中提供符合中国学术环境的准备建议")
        parts.append("- 考虑导师制、组会文化、科研产出压力等中国特色学术环境")
        parts.append("- 避免过于西化或不符合中国面试习惯的表述")

        return "\n".join(parts)
