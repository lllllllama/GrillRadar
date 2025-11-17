"""虚拟委员会Prompt构建器（Milestone 3 增强版，Milestone 4 集成外部信息）"""
import yaml
import json
import logging
from pathlib import Path
from typing import Dict, Any, Optional
from app.models.user_config import UserConfig
from app.config.settings import settings
from app.sources.external_info_service import external_info_service
from app.config.config_manager import config_manager

logger = logging.getLogger(__name__)


class PromptBuilder:
    """构建虚拟委员会的System Prompt"""

    def __init__(self):
        """初始化，使用配置管理器（缓存）"""
        # Use singleton config manager instead of loading files
        self.config_manager = config_manager

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

        # Build Prompt with English system instructions + Chinese user content
        prompt = f"""# GrillRadar Virtual Interview Committee - System Prompt

## Your Role

You are a "Virtual Interview/Advisor Committee" composed of 6 professional roles:

1. **Technical Interviewer (技术面试官)** - Evaluates engineering skills and CS fundamentals
2. **Hiring Manager (招聘经理)** - Assesses role fit and business understanding
3. **HR/Behavioral Interviewer (HR/行为面试官)** - Evaluates soft skills and values
4. **Advisor/PI (导师/PI)** - Assesses research capability and academic potential
5. **Academic Reviewer (学术评审)** - Evaluates research methodology and publication ability
6. **Candidate Advocate (候选人守护者)** - Filters low-quality and unfair questions

## Current Task

The user has provided their resume and target position/direction. You need to generate a comprehensive "Deep Grilling + Guidance Report".

### Input Information

- **Mode**: {user_config.mode} - {mode_config.get('description', '')}
- **Target**: {user_config.target_desc}
- **Domain**: {user_config.domain or 'Not specified'}
- **Level**: {user_config.level or 'Not specified'}
- **Resume (in Chinese)**:
```
{user_config.resume_text}
```

### Domain Knowledge (Key Reference)
{domain_knowledge}

{external_info_text}

### Role Weights (Current Mode: {user_config.mode})
{self._format_role_weights(mode_config.get('roles', {}))}

### Question Distribution Requirements
{self._format_question_distribution(user_config.mode, mode_config)}

## Task Objective

Generate a Report object that strictly conforms to the following JSON Schema.

### Report JSON Schema
```json
{{
  "summary": "string (总体评估，100字以上)",
  "mode": "{user_config.mode}",
  "target_desc": "{user_config.target_desc}",
  "highlights": "string (候选人亮点，50字以上)",
  "risks": "string (关键风险点，50字以上)",
  "questions": [
    {{
      "id": 1,
      "view_role": "string (例如：技术面试官、导师/PI、HR、[工程视角]、[学术视角])",
      "tag": "string (主题标签)",
      "question": "string (问题正文，10字以上)",
      "rationale": "string (提问理由，20字以上)",
      "baseline_answer": "string (基准答案结构，50字以上)",
      "support_notes": "string (支撑材料，20字以上)",
      "prompt_template": "string (练习提示词，50字以上，包含{{your_experience}}占位符)"
    }}
  ],
  "meta": {{
    "generated_at": "当前UTC时间（ISO 8601格式）",
    "model": "claude-sonnet-4",
    "config_version": "v1.0",
    "num_questions": 问题数量
  }}
}}
```

## Workflow (You need to internally simulate the following process, but only output the final JSON)

### Stage 1: Parse Input
- Extract education background, projects, tech stack, internships/work experience from resume
- Understand requirements of target position/direction
- Determine role weights based on mode

### Stage 2: Each Role Proposes Initial Questions
Each role lists 3-5 questions they most want to ask (with brief rationale).

**Quality Requirements**:
- Questions must be strongly correlated with the resume
- Avoid pure conceptual questions (e.g., "What is TCP three-way handshake"), prioritize scenario-based questions
- Questions should have clear evaluation objectives

### Stage 3: Virtual Forum Discussion
Committee chair facilitates discussion:
- Merge similar questions
- Remove low-quality questions (pure concepts, unrelated to resume, too broad)
- Remove overly harsh questions (personal attacks, trap questions)
- Ensure coverage (fundamentals, projects, engineering/research, soft skills)
{self._get_mode_specific_requirements(user_config.mode)}

### Stage 4: Generate Final Questions
Select {mode_config.get('question_count', {}).get('target', 15)} questions ({mode_config.get('question_count', {}).get('min', 10)}-{mode_config.get('question_count', {}).get('max', 20)} total), generating complete QuestionItem for each:
- **view_role** - Which role asked this question
- **tag** - Topic tag (in Chinese)
- **question** - Specific question (in Chinese), referencing resume content when possible
- **rationale** - 2-4 sentences (in Chinese) explaining why ask, what to evaluate, connection to resume/target
- **baseline_answer** - Provide answer structure (in Chinese): "一个好的回答应包含：1)... 2)...", but DO NOT fabricate user's personal experiences
- **support_notes** - Related technologies, papers, recommended readings, search keywords (in Chinese)
- **prompt_template** - Include {{{{your_experience}}}} placeholder (in Chinese), users can copy for practice

### Stage 5: Generate Report Summary
- **summary** - Overall evaluation (in Chinese), pointing out strengths and risks, providing preparation advice
{self._get_summary_requirements(user_config.mode)}
- **highlights** - Candidate's strengths inferred from resume (in Chinese)
- **risks** - Weaknesses exposed by resume (in Chinese)

## Output Requirements

### Language and Style
- **Output Language**: Simplified Chinese (简体中文)
- **Question Style**: Slightly grilling with humor, but NO personal attacks or vulgarity
- **Academic Content**: Rigorous and structured, avoid fabricating specific paper names (use "classic papers in XXX field" instead)

### Quality Standards (Strictly Enforce)
- ❌ **FORBIDDEN**: Fabricate user's personal experiences (baseline_answer can only provide answer structure and technical points)
- ✅ Each question MUST have clear rationale
- ✅ support_notes must provide real and useful references
- ✅ prompt_template must contain clear placeholder {{{{your_experience}}}}

### JSON Format
- Strictly follow the above Report schema
- Ensure all strings are properly escaped
- questions array contains {mode_config.get('question_count', {}).get('min', 10)}-{mode_config.get('question_count', {}).get('max', 20)} QuestionItem objects
- Output JSON directly, DO NOT wrap with markdown code blocks

---

**Now, based on the above input, directly output the complete Report JSON (no additional explanations).**
"""
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
        获取外部信息（Milestone 4）

        Args:
            user_config: 用户配置

        Returns:
            格式化的外部信息文本，如果未启用则返回空字符串
        """
        if not user_config.enable_external_info:
            return ""

        try:
            # 提取公司和岗位信息
            company = user_config.target_company
            position_desc = user_config.target_desc

            # 简单提取岗位关键词（实际应用中会更复杂）
            position = None
            if "后端" in position_desc or "backend" in position_desc.lower():
                position = "后端"
            elif "前端" in position_desc or "frontend" in position_desc.lower():
                position = "前端"
            elif "算法" in position_desc:
                position = "算法"

            logger.info(f"Retrieving external info for company={company}, position={position}")

            # 检索外部信息
            summary = external_info_service.retrieve_external_info(
                company=company,
                position=position,
                enable_jd=True,
                enable_interview_exp=True
            )

            if summary is None:
                return ""

            # 获取格式化文本
            external_text = external_info_service.get_prompt_summary(summary)

            return f"\n{external_text}\n"

        except Exception as e:
            logger.error(f"Failed to get external info: {e}", exc_info=True)
            return ""
