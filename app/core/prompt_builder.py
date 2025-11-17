"""虚拟委员会Prompt构建器"""
import yaml
import json
from pathlib import Path
from typing import Dict, Any, Optional
from app.models.user_config import UserConfig
from app.config.settings import settings


class PromptBuilder:
    """构建虚拟委员会的System Prompt"""

    def __init__(self):
        """初始化，加载配置文件"""
        # 加载domains.yaml
        with open(settings.DOMAINS_CONFIG, 'r', encoding='utf-8') as f:
            self.domains = yaml.safe_load(f)

        # 加载modes.yaml
        with open(settings.MODES_CONFIG, 'r', encoding='utf-8') as f:
            self.modes = yaml.safe_load(f)

    def build(self, user_config: UserConfig) -> str:
        """
        构建完整的System Prompt

        Args:
            user_config: 用户配置

        Returns:
            完整的System Prompt字符串
        """
        # 获取模式配置
        mode_config = self.modes.get(user_config.mode, {})

        # 获取领域知识（如果指定了domain）
        domain_knowledge = self._get_domain_knowledge(user_config.domain)

        # 构建Prompt
        prompt = f"""# GrillRadar 虚拟面试委员会 System Prompt

## 你的角色
你是一个"虚拟面试/导师委员会"，由6个专业角色组成：
1. **技术面试官（Technical Interviewer）** - 考察工程技能和CS基础
2. **招聘经理（Hiring Manager）** - 考察岗位匹配和业务理解
3. **HR/行为面试官（HR Interviewer）** - 考察软技能和价值观
4. **导师/PI（Advisor）** - 考察研究能力和学术潜力
5. **学术评审（Academic Reviewer）** - 考察科研方法论和论文能力
6. **候选人守护者（Candidate Advocate）** - 过滤低质量和刁难问题

## 当前任务
用户提供了简历和目标岗位/方向，你需要生成一份"深度拷问+辅导报告"。

### 输入信息
- **模式（mode）**: {user_config.mode} - {mode_config.get('description', '')}
- **目标（target_desc）**: {user_config.target_desc}
- **领域（domain）**: {user_config.domain or '未指定'}
- **候选人级别（level）**: {user_config.level or '未指定'}
- **简历原文**:
```
{user_config.resume_text}
```

### 领域知识
{domain_knowledge}

### 角色权重（当前模式：{user_config.mode}）
{self._format_role_weights(mode_config.get('roles', {}))}

### 问题分布要求
{self._format_question_distribution(user_config.mode, mode_config)}

## 任务目标
生成一个严格符合以下JSON Schema的Report对象。

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

## 工作流程（你需要在内部模拟以下流程，但只输出最终JSON）

### 阶段1：解析输入
- 提取简历中的教育背景、项目、技能栈、实习/工作经历
- 理解目标岗位/方向的要求
- 根据mode确定各角色权重

### 阶段2：各角色提出初步问题
每个角色列出3-5个最想问的问题（附简短理由）。
**质量要求**：
- 问题必须与简历强相关
- 避免纯概念题（如"什么是TCP三次握手"），优先场景题
- 问题应有明确考察目的

### 阶段3：虚拟论坛讨论
委员会主席主持讨论：
- 合并相似问题
- 删除低质量问题（纯概念、与简历无关、过于宽泛）
- 删除过度刁难问题（人身攻击、陷阱题）
- 确保覆盖度（基础、项目、工程/研究、软技能）
{self._get_mode_specific_requirements(user_config.mode)}

### 阶段4：生成最终问题
选出{mode_config.get('question_count', {}).get('target', 15)}个问题（{mode_config.get('question_count', {}).get('min', 10)}-{mode_config.get('question_count', {}).get('max', 20)}个），为每个问题生成完整的QuestionItem：
- **view_role** - 哪个角色问的
- **tag** - 主题标签
- **question** - 具体问题，尽量引用简历内容
- **rationale** - 2-4句话，说明为什么问、考察什么、与简历/目标的关联
- **baseline_answer** - 提供回答结构："一个好的回答应包含：1)... 2)...", 但不能编造用户个人经历
- **support_notes** - 相关技术、论文、推荐阅读、搜索关键词
- **prompt_template** - 包含{{your_experience}}占位符，用户可复制练习

### 阶段5：生成报告总结
- **summary** - 总体评估，指出优势和风险，给出准备建议
{self._get_summary_requirements(user_config.mode)}
- **highlights** - 从简历推断的候选人亮点
- **risks** - 简历暴露的薄弱环节

## 输出要求

### 语言与风格
- 输出语言：简体中文
- 问题风格：略带grilling和幽默，但不能人身攻击或粗俗
- 学术内容：严谨、结构化，避免编造具体论文名（用"XXX领域的经典论文"代替）

### 质量标准（严格遵守）
- ❌ **禁止**编造用户个人经历（baseline_answer只能提供回答结构和技术要点）
- ✅ 每个问题都必须有明确的rationale
- ✅ support_notes要提供真实有用的参考资料
- ✅ prompt_template要包含清晰的占位符{{your_experience}}

### JSON格式
- 严格遵循上述Report schema
- 确保所有字符串正确转义
- questions数组包含{mode_config.get('question_count', {}).get('min', 10)}-{mode_config.get('question_count', {}).get('max', 20)}个QuestionItem对象
- 直接输出JSON，不要用markdown代码块包裹

---

**现在，请基于上述输入，直接输出完整的Report JSON（不要任何额外解释）。**
"""
        return prompt

    def _get_domain_knowledge(self, domain: Optional[str]) -> str:
        """获取领域知识的格式化字符串"""
        if not domain:
            return "未指定领域，请基于简历内容和目标岗位进行推断。"

        # 尝试从engineering或research中查找
        for category in ['engineering', 'research']:
            if category in self.domains and domain in self.domains[category]:
                domain_data = self.domains[category][domain]
                knowledge = f"领域：{domain}\n"
                if 'keywords' in domain_data:
                    knowledge += f"- 关键词：{', '.join(domain_data['keywords'])}\n"
                if 'common_stacks' in domain_data:
                    knowledge += f"- 常见技术栈：{', '.join(domain_data['common_stacks'])}\n"
                if 'canonical_papers' in domain_data:
                    knowledge += f"- 经典论文：{', '.join(domain_data['canonical_papers'])}\n"
                if 'conferences' in domain_data:
                    knowledge += f"- 顶级会议：{', '.join(domain_data['conferences'])}\n"
                return knowledge

        return f"领域 '{domain}' 未在配置中找到，请基于简历内容进行推断。"

    def _format_role_weights(self, roles: Dict[str, float]) -> str:
        """格式化角色权重"""
        if not roles:
            return "角色权重未配置"

        lines = []
        role_names = {
            'technical_interviewer': '技术面试官',
            'hiring_manager': '招聘经理',
            'hr': 'HR/行为面试官',
            'advisor': '导师/PI',
            'reviewer': '学术评审'
        }

        for role_key, weight in sorted(roles.items(), key=lambda x: x[1], reverse=True):
            role_name = role_names.get(role_key, role_key)
            percentage = int(weight * 100)
            lines.append(f"- {role_name}: {percentage}%")

        return "\n".join(lines)

    def _format_question_distribution(self, mode: str, mode_config: Dict) -> str:
        """格式化问题分布要求"""
        dist = mode_config.get('question_distribution', {})
        if not dist:
            return "问题分布未配置"

        lines = []
        for category, ratio in dist.items():
            percentage = int(ratio * 100)
            lines.append(f"- {category}: {percentage}%")

        return "\n".join(lines)

    def _get_mode_specific_requirements(self, mode: str) -> str:
        """获取特定模式的特殊要求"""
        if mode == "mixed":
            return "- **特别注意**：对mixed模式，确保双视角平衡（工程问题和学术问题各占约50%）"
        elif mode == "grad":
            return "- **特别注意**：对grad模式，检查是否覆盖：研究方法论、论文阅读、学术规范"
        else:
            return "- 确保覆盖：CS基础、项目深度、工程实践、软技能"

    def _get_summary_requirements(self, mode: str) -> str:
        """获取summary字段的特殊要求"""
        if mode == "mixed":
            return """- **对mixed模式，summary必须包含两条独立评估**：
  ```
  【工程候选人评估】
  作为XX工程师候选人，你的项目经验...

  【科研候选人评估】
  作为XX方向的研究生候选人，你的XX基础...
  ```"""
        return ""
