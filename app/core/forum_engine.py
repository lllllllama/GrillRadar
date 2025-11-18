"""
Forum Engine - Multi-Agent Coordination and Consensus

Consolidates questions from multiple agents through discussion,
deduplication, and quality filtering.
"""
from typing import List, Dict, Any, Tuple, Optional, Literal
import logging
import asyncio
import yaml
from pathlib import Path
from collections import Counter

from app.agents.models import DraftQuestion
from app.models.question_item import QuestionItem
from app.models.user_config import UserConfig
from app.config.settings import settings
from app.utils.debug_dumper import get_debug_dumper

logger = logging.getLogger(__name__)


class EnrichedDraftQuestion:
    """Draft question with enhanced metadata for selection"""
    def __init__(
        self,
        draft: DraftQuestion,
        agent_name: str,
        dimension: str,
        difficulty: str,
        score: float
    ):
        self.draft = draft
        self.agent_name = agent_name
        self.dimension = dimension
        self.difficulty = difficulty
        self.score = score


class ForumEngine:
    """
    ForumEngine coordinates multi-agent discussions

    Phases:
    1. Deduplication - Merge similar questions
    2. Quality filtering - Remove low-quality questions
    3. Labeling & Scoring - Add dimension, difficulty, and relevance scores
    4. Coverage validation - Ensure comprehensive coverage per modes.yaml
    5. Advocate gatekeeper - Filter problematic questions
    6. Enhancement - Convert draft questions to final QuestionItems
    """

    def __init__(self, llm_client):
        self.llm_client = llm_client
        self.logger = logging.getLogger(__name__)
        self.modes_config = self._load_modes_config()

    def _load_modes_config(self) -> Dict:
        """Load modes configuration from YAML"""
        try:
            with open(settings.MODES_CONFIG, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f)
        except Exception as e:
            self.logger.warning(f"Failed to load modes config: {e}")
            return {}

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

        # Phase 3: Labeling & Scoring
        self.logger.info("\nPhase 3: Labeling & Scoring")
        enriched = await self._label_and_score(filtered, user_config, resume_text)
        self.logger.info(f"Labeled and scored: {len(enriched)} questions")

        # Debug: dump pre-selection candidates
        debug_dumper = get_debug_dumper()
        debug_dumper.dump_pre_selection_candidates(enriched)

        # Phase 4: Coverage-aware selection
        self.logger.info("\nPhase 4: Coverage-Aware Selection")
        selected = self._select_with_coverage(enriched, user_config)
        self.logger.info(f"Final selection: {len(selected)} questions")

        # Debug: dump selected questions
        debug_dumper.dump_selected_questions(selected)

        # Phase 5: Advocate gatekeeper (quality control)
        self.logger.info("\nPhase 5: Advocate Gatekeeper")
        before_count = len(selected)
        approved = await self._advocate_review(selected, user_config)
        after_count = len(approved)
        self.logger.info(f"After advocate review: {after_count} questions")

        # Debug: dump advocate feedback
        filtered_questions = [
            eq.draft.question for eq in selected if eq not in approved
        ]
        debug_dumper.dump_advocate_feedback(before_count, after_count, filtered_questions)

        # Phase 6: Enhance to final QuestionItems
        self.logger.info("\nPhase 6: Enhancement")
        final_questions = await self._enhance_questions(approved, resume_text, user_config)
        self.logger.info(f"Enhanced questions: {len(final_questions)}")

        return final_questions

    async def _label_and_score(
        self,
        drafts: List[Tuple[DraftQuestion, str]],
        user_config: UserConfig,
        resume_text: str
    ) -> List[EnrichedDraftQuestion]:
        """
        Label each draft question with dimension, difficulty, and score

        Args:
            drafts: Filtered draft questions
            user_config: User configuration
            resume_text: Resume text

        Returns:
            List of enriched draft questions with metadata
        """
        enriched_questions = []

        for draft, agent_name in drafts:
            # Determine dimension based on tags and agent role
            dimension = self._infer_dimension(draft, agent_name, user_config)

            # Determine difficulty based on question complexity
            difficulty = self._infer_difficulty(draft)

            # Calculate relevance score (1-5)
            score = self._calculate_relevance_score(draft, user_config, resume_text)

            enriched = EnrichedDraftQuestion(
                draft=draft,
                agent_name=agent_name,
                dimension=dimension,
                difficulty=difficulty,
                score=score
            )
            enriched_questions.append(enriched)

            self.logger.debug(
                f"Labeled question: dimension={dimension}, difficulty={difficulty}, score={score:.2f}"
            )

        return enriched_questions

    def _infer_dimension(
        self,
        draft: DraftQuestion,
        agent_name: str,
        user_config: UserConfig
    ) -> str:
        """
        Infer question dimension from tags and agent role

        Returns:
            One of: foundation, engineering, project_depth, research_method, reflection, soft_skill
        """
        # Check tags first
        tags_lower = [tag.lower() for tag in draft.tags]

        # Foundation keywords
        foundation_keywords = ['算法', '数据结构', '操作系统', '网络', '数据库', 'cs基础',
                               'algorithm', 'data structure', 'os', 'network']
        if any(kw in ' '.join(tags_lower) for kw in foundation_keywords):
            return "foundation"

        # Research method keywords (for grad mode)
        research_keywords = ['研究方法', '实验设计', '论文', '学术', '方法论',
                             'research', 'methodology', 'experiment', 'paper']
        if any(kw in ' '.join(tags_lower) for kw in research_keywords):
            return "research_method"

        # Project depth keywords
        project_keywords = ['项目', '实现', '架构', '设计', '优化',
                            'project', 'implementation', 'architecture', 'design']
        if any(kw in ' '.join(tags_lower) for kw in project_keywords):
            return "project_depth"

        # Soft skills keywords
        soft_keywords = ['团队', '协作', '沟通', '规划', '职业',
                         'team', 'collaboration', 'communication', 'planning']
        if any(kw in ' '.join(tags_lower) for kw in soft_keywords):
            return "soft_skill"

        # Reflection keywords
        reflection_keywords = ['反思', '成长', '挑战', '学习',
                               'reflection', 'growth', 'challenge', 'learning']
        if any(kw in ' '.join(tags_lower) for kw in reflection_keywords):
            return "reflection"

        # Fallback based on agent role
        if agent_name in ['technical_interviewer', 'hiring_manager']:
            return "engineering"
        elif agent_name in ['academic_advisor', 'academic_reviewer']:
            return "research_method"
        elif agent_name == 'hr_specialist':
            return "soft_skill"
        elif agent_name == 'candidate_advocate':
            return "reflection"

        return "engineering"  # Default

    def _infer_difficulty(self, draft: DraftQuestion) -> str:
        """
        Infer question difficulty based on complexity indicators

        Returns:
            One of: basic, intermediate, killer
        """
        question = draft.question.lower()
        rationale = draft.rationale.lower()

        # Killer question indicators
        killer_indicators = ['深入', '详细描述', '权衡', '优化', '为什么这样设计',
                             '底层原理', '源码', '如何处理', '最坏情况',
                             'deep dive', 'trade-off', 'optimize', 'why', 'source code']
        if any(ind in question or ind in rationale for ind in killer_indicators):
            return "killer"

        # Basic question indicators
        basic_indicators = ['是什么', '有什么', '用过', '了解', '知道',
                            'what is', 'have you used', 'familiar with', 'know']
        if any(ind in question or ind in rationale for ind in basic_indicators):
            return "basic"

        # Check question length (longer questions tend to be more complex)
        if len(draft.question) > 100:
            return "intermediate"

        # Check confidence (lower confidence might indicate tricky question)
        if draft.confidence < 0.7:
            return "killer"

        return "intermediate"  # Default

    def _calculate_relevance_score(
        self,
        draft: DraftQuestion,
        user_config: UserConfig,
        resume_text: str
    ) -> float:
        """
        Calculate relevance score (1-5) based on:
        - Resume relevance
        - Target job/program alignment
        - Domain matching
        - Information gain potential

        Args:
            draft: Draft question
            user_config: User configuration
            resume_text: Resume text

        Returns:
            Score from 1.0 to 5.0
        """
        score = 3.0  # Base score

        # Factor 1: Confidence from agent
        score += (draft.confidence - 0.7) * 5  # Scale confidence contribution

        # Factor 2: Tag relevance to domain
        if user_config.domain:
            domain_lower = user_config.domain.lower()
            tags_lower = ' '.join(draft.tags).lower()
            if domain_lower in tags_lower or any(word in tags_lower for word in domain_lower.split()):
                score += 0.5

        # Factor 3: Question specificity (longer rationale = more thought)
        if len(draft.rationale) > 100:
            score += 0.3

        # Factor 4: Metadata complexity
        if draft.metadata.get('complexity') == 'high':
            score += 0.3

        # Clamp to 1.0-5.0 range
        return max(1.0, min(5.0, score))

    def _select_with_coverage(
        self,
        enriched: List[EnrichedDraftQuestion],
        user_config: UserConfig
    ) -> List[EnrichedDraftQuestion]:
        """
        Select questions with coverage constraints from modes.yaml

        Ensures:
        - Minimum coverage across dimensions
        - Balanced difficulty distribution
        - Respects target question count from modes config

        Args:
            enriched: Enriched draft questions
            user_config: User configuration

        Returns:
            Selected questions with coverage guarantees
        """
        # Get mode config
        mode_config = self.modes_config.get(user_config.mode, {})
        target_count = mode_config.get('question_count', {}).get('target', 15)
        min_count = mode_config.get('question_count', {}).get('min', 10)
        max_count = mode_config.get('question_count', {}).get('max', 20)

        # Sort by score (descending)
        sorted_questions = sorted(enriched, key=lambda x: x.score, reverse=True)

        # Phase 1: Greedy selection for high scores
        selected = sorted_questions[:target_count]

        # Phase 2: Ensure dimension coverage
        selected = self._ensure_dimension_coverage(selected, sorted_questions, user_config)

        # Phase 3: Balance difficulty (avoid all killers or all basics)
        selected = self._balance_difficulty(selected, sorted_questions)

        # Phase 4: Final count adjustment
        if len(selected) < min_count:
            # Add more questions to meet minimum
            remaining = [q for q in sorted_questions if q not in selected]
            selected.extend(remaining[:min_count - len(selected)])
        elif len(selected) > max_count:
            # Trim to max count, preserving high scores
            selected = sorted(selected, key=lambda x: x.score, reverse=True)[:max_count]

        self.logger.info(f"Coverage-aware selection: {len(selected)} questions")
        self._log_coverage_stats(selected)

        return selected

    def _ensure_dimension_coverage(
        self,
        selected: List[EnrichedDraftQuestion],
        all_questions: List[EnrichedDraftQuestion],
        user_config: UserConfig
    ) -> List[EnrichedDraftQuestion]:
        """
        Ensure minimum coverage across dimensions

        For job mode: require at least 1 foundation, 1 project_depth, 1 soft_skill
        For grad mode: require at least 1 research_method, 1 foundation
        For mixed: require both engineering and research dimensions
        """
        dimension_counts = Counter(q.dimension for q in selected)

        # Define minimum requirements per mode
        if user_config.mode == "job":
            requirements = {"foundation": 2, "project_depth": 2, "soft_skill": 1}
        elif user_config.mode == "grad":
            requirements = {"research_method": 2, "foundation": 1}
        else:  # mixed
            requirements = {"foundation": 1, "project_depth": 1, "research_method": 1, "soft_skill": 1}

        # Check and fill gaps
        for dimension, min_count in requirements.items():
            current_count = dimension_counts.get(dimension, 0)
            if current_count < min_count:
                # Find questions with this dimension not already selected
                candidates = [q for q in all_questions
                              if q.dimension == dimension and q not in selected]
                # Sort by score and add top ones
                candidates.sort(key=lambda x: x.score, reverse=True)
                to_add = candidates[:min_count - current_count]
                selected.extend(to_add)
                self.logger.info(f"Added {len(to_add)} questions for dimension '{dimension}'")

        return selected

    def _balance_difficulty(
        self,
        selected: List[EnrichedDraftQuestion],
        all_questions: List[EnrichedDraftQuestion]
    ) -> List[EnrichedDraftQuestion]:
        """
        Balance difficulty distribution

        Aim for roughly:
        - 30% basic
        - 50% intermediate
        - 20% killer
        """
        difficulty_counts = Counter(q.difficulty for q in selected)
        total = len(selected)

        # Calculate target counts
        targets = {
            "basic": int(total * 0.3),
            "intermediate": int(total * 0.5),
            "killer": int(total * 0.2)
        }

        # Check if adjustment needed
        needs_adjustment = False
        for diff, target in targets.items():
            current = difficulty_counts.get(diff, 0)
            if abs(current - target) > 2:  # Allow some tolerance
                needs_adjustment = True
                break

        if not needs_adjustment:
            return selected

        # Rebuild selection with balanced difficulty
        balanced = []
        remaining = [q for q in all_questions]

        for difficulty, target_count in targets.items():
            candidates = [q for q in remaining if q.difficulty == difficulty]
            candidates.sort(key=lambda x: x.score, reverse=True)
            balanced.extend(candidates[:target_count])
            # Remove selected from remaining
            for q in balanced:
                if q in remaining:
                    remaining.remove(q)

        # Fill remaining slots with highest scores
        if len(balanced) < total:
            remaining.sort(key=lambda x: x.score, reverse=True)
            balanced.extend(remaining[:total - len(balanced)])

        return balanced[:total]

    def _log_coverage_stats(self, selected: List[EnrichedDraftQuestion]):
        """Log coverage statistics for debugging"""
        dimension_counts = Counter(q.dimension for q in selected)
        difficulty_counts = Counter(q.difficulty for q in selected)

        self.logger.info("Dimension coverage:")
        for dim, count in dimension_counts.items():
            self.logger.info(f"  {dim}: {count}")

        self.logger.info("Difficulty distribution:")
        for diff, count in difficulty_counts.items():
            self.logger.info(f"  {diff}: {count}")

    async def _advocate_review(
        self,
        selected: List[EnrichedDraftQuestion],
        user_config: UserConfig
    ) -> List[EnrichedDraftQuestion]:
        """
        Advocate agent as gatekeeper - review and filter problematic questions

        The advocate agent reviews the selected questions and flags:
        - Offensive or unfair questions
        - Extremely low information gain
        - Problematic tone or bias

        For MVP, we use simple heuristic checks. In production, this could
        call an LLM for more sophisticated review.

        Args:
            selected: Selected questions
            user_config: User configuration

        Returns:
            Approved questions (filtered)
        """
        approved = []

        for enriched in selected:
            # Simple heuristic checks
            question = enriched.draft.question.lower()

            # Flag 1: Check for offensive keywords (basic filter)
            offensive_keywords = ['愚蠢', '笨', '傻', 'stupid', 'dumb', 'idiot']
            if any(kw in question for kw in offensive_keywords):
                self.logger.warning(f"Advocate blocked offensive question: {enriched.draft.question[:50]}...")
                continue

            # Flag 2: Check for trick questions (too vague or impossible to answer)
            trick_indicators = ['猜', '运气', 'guess', 'luck']
            if any(ind in question for ind in trick_indicators):
                self.logger.warning(f"Advocate blocked trick question: {enriched.draft.question[:50]}...")
                continue

            # Flag 3: Minimum information gain (avoid pure textbook questions)
            if enriched.score < 2.0:
                self.logger.warning(f"Advocate blocked low-value question (score={enriched.score:.2f})")
                continue

            # Approved
            approved.append(enriched)

        self.logger.info(f"Advocate review: {len(selected)} -> {len(approved)} (filtered {len(selected) - len(approved)})")

        return approved

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
        enriched_drafts: List[EnrichedDraftQuestion],
        resume_text: str,
        user_config: UserConfig
    ) -> List[QuestionItem]:
        """
        Convert EnrichedDraftQuestions to final QuestionItems

        For MVP, we'll use a simplified enhancement that creates
        QuestionItems directly without additional LLM calls.

        Args:
            enriched_drafts: Selected enriched draft questions
            resume_text: Candidate's resume
            user_config: User configuration

        Returns:
            List of enhanced QuestionItems with all metadata
        """
        final_items = []

        for idx, enriched in enumerate(enriched_drafts, 1):
            draft = enriched.draft

            # Create QuestionItem with full metadata
            question_item = QuestionItem(
                id=idx,
                view_role=draft.role_display,
                tag=draft.tags[0] if draft.tags else "综合",
                question=draft.question,
                rationale=draft.rationale,
                baseline_answer=self._generate_baseline_answer(draft),
                support_notes=self._generate_support_notes(draft, user_config),
                prompt_template=self._generate_prompt_template(draft),
                # Multi-agent enhanced fields
                dimension=enriched.dimension,
                difficulty=enriched.difficulty,
                relevance_score=enriched.score
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
