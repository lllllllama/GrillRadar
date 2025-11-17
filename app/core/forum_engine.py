"""
Forum Engine - Multi-Agent Coordination and Consensus

Consolidates questions from multiple agents through discussion,
deduplication, and quality filtering.
"""
from typing import List, Dict, Any, Tuple
import logging
import asyncio

from app.agents.models import DraftQuestion
from app.models.question_item import QuestionItem
from app.models.user_config import UserConfig

logger = logging.getLogger(__name__)


class ForumEngine:
    """
    ForumEngine coordinates multi-agent discussions

    Phases:
    1. Deduplication - Merge similar questions
    2. Quality filtering - Remove low-quality questions
    3. Coverage validation - Ensure comprehensive coverage
    4. Enhancement - Convert draft questions to final QuestionItems
    """

    def __init__(self, llm_client):
        self.llm_client = llm_client
        self.logger = logging.getLogger(__name__)

    async def discuss(
        self,
        draft_questions_by_agent: Dict[str, List[DraftQuestion]],
        resume_text: str,
        user_config: UserConfig
    ) -> List[QuestionItem]:
        """
        Multi-round discussion to consolidate and refine questions

        Args:
            draft_questions_by_agent: Questions proposed by each agent
            resume_text: Candidate's resume
            user_config: User configuration

        Returns:
            List of final QuestionItems ready for report
        """
        self.logger.info("=" * 60)
        self.logger.info("ForumEngine: Starting multi-agent discussion")
        self.logger.info("=" * 60)

        # Flatten all drafts
        all_drafts = []
        for agent_name, drafts in draft_questions_by_agent.items():
            for draft in drafts:
                all_drafts.append((draft, agent_name))
            self.logger.info(f"Agent '{agent_name}': {len(drafts)} questions")

        self.logger.info(f"Total draft questions: {len(all_drafts)}")

        # Phase 1: Deduplication
        self.logger.info("\nPhase 1: Deduplication")
        deduped = self._deduplicate_questions(all_drafts)
        self.logger.info(f"After deduplication: {len(deduped)} questions")

        # Phase 2: Quality filtering
        self.logger.info("\nPhase 2: Quality Filtering")
        filtered = self._filter_low_quality(deduped)
        self.logger.info(f"After quality filter: {len(filtered)} questions")

        # Phase 3: Select top questions (10-20)
        self.logger.info("\nPhase 3: Selection")
        selected = self._select_final_set(filtered, user_config)
        self.logger.info(f"Final selection: {len(selected)} questions")

        # Phase 4: Enhance each question to final format
        self.logger.info("\nPhase 4: Enhancement")
        final_questions = await self._enhance_questions(selected, resume_text, user_config)
        self.logger.info(f"Enhanced questions: {len(final_questions)}")

        return final_questions

    def _deduplicate_questions(
        self,
        drafts: List[Tuple[DraftQuestion, str]]
    ) -> List[Tuple[DraftQuestion, str]]:
        """
        Remove semantically similar questions

        Uses simple heuristic: if two questions share >60% of characters,
        keep the one with higher confidence.

        Args:
            drafts: List of (DraftQuestion, agent_name) tuples

        Returns:
            Deduplicated list
        """
        if len(drafts) <= 1:
            return drafts

        deduplicated = []
        skip_indices = set()

        for i, (draft1, agent1) in enumerate(drafts):
            if i in skip_indices:
                continue

            # Find similar questions
            similar_found = False
            for j in range(i + 1, len(drafts)):
                if j in skip_indices:
                    continue

                draft2, agent2 = drafts[j]
                similarity = self._calculate_similarity(draft1.question, draft2.question)

                if similarity > 0.6:  # 60% similarity threshold
                    # Keep the one with higher confidence
                    if draft2.confidence > draft1.confidence:
                        skip_indices.add(i)
                        similar_found = True
                        self.logger.debug(f"Merging similar questions (keeping higher confidence)")
                        break
                    else:
                        skip_indices.add(j)

            if not similar_found:
                deduplicated.append((draft1, agent1))

        return deduplicated

    def _calculate_similarity(self, q1: str, q2: str) -> float:
        """
        Calculate similarity between two questions

        Simple character-based similarity for now.
        Could be enhanced with embedding-based similarity.

        Args:
            q1: First question
            q2: Second question

        Returns:
            Similarity score (0.0-1.0)
        """
        # Simple character overlap
        q1_lower = q1.lower()
        q2_lower = q2.lower()

        # Count common characters
        common = sum(1 for c in q1_lower if c in q2_lower)
        total = max(len(q1_lower), len(q2_lower))

        return common / total if total > 0 else 0.0

    def _filter_low_quality(
        self,
        drafts: List[Tuple[DraftQuestion, str]]
    ) -> List[Tuple[DraftQuestion, str]]:
        """
        Filter out low-quality questions

        Criteria:
        - Confidence score >= 0.6
        - Question length >= 15 characters
        - Rationale length >= 20 characters

        Args:
            drafts: List of draft questions

        Returns:
            Filtered list
        """
        filtered = []

        for draft, agent_name in drafts:
            # Check confidence
            if draft.confidence < 0.6:
                self.logger.debug(f"Filtered low confidence ({draft.confidence}): {draft.question[:50]}...")
                continue

            # Check question length
            if len(draft.question) < 15:
                self.logger.debug(f"Filtered short question: {draft.question}")
                continue

            # Check rationale length
            if len(draft.rationale) < 20:
                self.logger.debug(f"Filtered weak rationale for: {draft.question[:50]}...")
                continue

            filtered.append((draft, agent_name))

        return filtered

    def _select_final_set(
        self,
        drafts: List[Tuple[DraftQuestion, str]],
        user_config: UserConfig
    ) -> List[Tuple[DraftQuestion, str]]:
        """
        Select final set of 10-20 questions

        Prioritizes:
        - Higher confidence scores
        - Diversity across agents
        - Coverage of different question types

        Args:
            drafts: Filtered draft questions
            user_config: User configuration

        Returns:
            Selected questions (10-20)
        """
        # Sort by confidence (descending)
        sorted_drafts = sorted(drafts, key=lambda x: x[0].confidence, reverse=True)

        # Select top 15 (or fewer if not enough questions)
        target_count = min(15, len(sorted_drafts))
        selected = sorted_drafts[:target_count]

        # Ensure minimum diversity (at least 2 agents represented)
        agent_counts = {}
        for _, agent_name in selected:
            agent_counts[agent_name] = agent_counts.get(agent_name, 0) + 1

        if len(agent_counts) < 2 and len(sorted_drafts) > target_count:
            # Add more questions to ensure diversity
            for draft, agent in sorted_drafts[target_count:]:
                if agent not in agent_counts:
                    selected.append((draft, agent))
                    agent_counts[agent] = 1
                    if len(selected) >= 20:  # Max 20 questions
                        break

        self.logger.info(f"Agent distribution: {agent_counts}")
        return selected

    async def _enhance_questions(
        self,
        drafts: List[Tuple[DraftQuestion, str]],
        resume_text: str,
        user_config: UserConfig
    ) -> List[QuestionItem]:
        """
        Convert DraftQuestions to final QuestionItems

        For MVP, we'll use a simplified enhancement that creates
        QuestionItems directly without additional LLM calls.

        Args:
            drafts: Selected draft questions
            resume_text: Candidate's resume
            user_config: User configuration

        Returns:
            List of enhanced QuestionItems
        """
        final_items = []

        for idx, (draft, agent_name) in enumerate(drafts, 1):
            # Create QuestionItem with basic enhancement
            question_item = QuestionItem(
                id=idx,
                view_role=draft.role_display,
                tag=draft.tags[0] if draft.tags else "综合",
                question=draft.question,
                rationale=draft.rationale,
                baseline_answer=self._generate_baseline_answer(draft),
                support_notes=self._generate_support_notes(draft, user_config),
                prompt_template=self._generate_prompt_template(draft)
            )

            final_items.append(question_item)

        return final_items

    def _generate_baseline_answer(self, draft: DraftQuestion) -> str:
        """Generate baseline answer structure"""
        return f"""**回答框架：**

1. **直接回应问题核心**
   - 清晰说明{draft.tags[0] if draft.tags else '相关技术'}的具体应用

2. **提供具体例子**
   - 引用简历中的实际项目经验
   - 说明当时的背景、挑战和解决方案

3. **展示深度思考**
   - 讨论权衡取舍
   - 说明为什么选择这个方案
   - 可能的改进方向

4. **总结收获**
   - 从这个经历中学到了什么
   - 如何应用到未来工作中
"""

    def _generate_support_notes(self, draft: DraftQuestion, user_config: UserConfig) -> str:
        """Generate support materials"""
        tags_str = "、".join(draft.tags[:3]) if draft.tags else "相关技术"

        return f"""**参考方向：**

- **技术关键词**: {tags_str}
- **推荐深入**: 在面试前复习{tags_str}的核心概念和最佳实践
- **准备材料**: 准备1-2个相关的具体项目案例

**注意事项**:
- 回答要结合简历中的实际经历
- 避免纯理论，强调实践经验
- 准备应对追问：细节、数据、结果
"""

    def _generate_prompt_template(self, draft: DraftQuestion) -> str:
        """Generate practice prompt template"""
        return f"""我正在准备面试，请帮我练习回答这个问题：

**问题**: {draft.question}

**我的相关经验**: {{{{your_experience}}}}

请扮演面试官角色：
1. 评价我的回答是否充分
2. 提出2-3个追问
3. 给出改进建议

注意：我希望得到严格但有建设性的反馈。
"""
