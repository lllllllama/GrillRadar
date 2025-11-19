#!/usr/bin/env python3
"""
测试关键词过滤器
"""
import sys
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from app.sources.crawlers.keyword_filter import KeywordFilter, create_filter_from_string


def test_basic_filtering():
    """测试基本过滤功能"""
    print("=" * 80)
    print("🧪 测试1: 基本过滤功能")
    print("=" * 80)
    print()

    # 创建过滤器: 必须有"后端", 不能有"前端", 可选"Python"
    filter1 = KeywordFilter(["Python", "+后端", "!前端"])
    print(f"过滤器: {filter1}")
    print()

    test_cases = [
        ("Python后端开发工程师", True, "有Python和后端，无前端"),
        ("前端开发工程师", False, "有排除词'前端'"),
        ("Java后端工程师", True, "有必须词'后端'，虽然无Python"),
        ("全栈工程师", False, "缺少必须词'后端'"),
        ("后端架构师", True, "有必须词'后端'"),
    ]

    for text, expected, reason in test_cases:
        result = filter1.matches(text)
        status = "✅" if result == expected else "❌"
        print(f"{status} \"{text}\" => {result} ({reason})")

    print()


def test_scoring():
    """测试评分功能"""
    print("=" * 80)
    print("🧪 测试2: 评分功能")
    print("=" * 80)
    print()

    filter2 = KeywordFilter(["Python", "Django", "+后端", "!前端"])
    print(f"过滤器: {filter2}")
    print()

    test_texts = [
        "Python Django后端开发",
        "Python后端工程师",
        "后端架构师",
        "Django开发工程师",  # 缺少"后端"，应该得0分
    ]

    for text in test_texts:
        score = filter2.calculate_score(text)
        print(f"分数 {score:5.1f}: {text}")

    print()


def test_string_parsing():
    """测试字符串解析"""
    print("=" * 80)
    print("🧪 测试3: 字符串解析")
    print("=" * 80)
    print()

    test_string = "Python +后端 !前端 Django,Flask"
    print(f"输入字符串: \"{test_string}\"")
    print()

    filter3 = create_filter_from_string(test_string)
    print(f"解析结果: {filter3}")
    print()

    print(f"普通关键词: {filter3.normal_keywords}")
    print(f"必须关键词: {filter3.required_keywords}")
    print(f"排除关键词: {filter3.exclude_keywords}")
    print()


def test_filter_items():
    """测试批量过滤和排序"""
    print("=" * 80)
    print("🧪 测试4: 批量过滤和排序")
    print("=" * 80)
    print()

    items = [
        {"title": "Python后端开发工程师 - 字节跳动", "url": "http://example.com/1"},
        {"title": "前端React工程师", "url": "http://example.com/2"},
        {"title": "Python Django后端架构师", "url": "http://example.com/3"},
        {"title": "Java后端开发", "url": "http://example.com/4"},
        {"title": "全栈工程师", "url": "http://example.com/5"},
        {"title": "后端技术专家 Python", "url": "http://example.com/6"},
    ]

    filter4 = KeywordFilter(["Python", "+后端", "!前端"])
    print(f"过滤器: {filter4}")
    print(f"原始数据: {len(items)} 条")
    print()

    filtered = filter4.filter_items(items, text_field='title')
    print(f"过滤后: {len(filtered)} 条")
    print()

    print("结果（按分数排序）:")
    for i, item in enumerate(filtered, 1):
        score = item.get('relevance_score', 0)
        title = item.get('title', '')
        print(f"{i}. [{score:5.1f}分] {title}")

    print()


def test_llm_domain():
    """测试LLM领域过滤"""
    print("=" * 80)
    print("🧪 测试5: LLM领域过滤")
    print("=" * 80)
    print()

    # LLM领域：必须有AI相关，排除硬件
    filter5 = KeywordFilter(["LLM", "GPT", "ChatGPT", "+AI", "!GPU", "!芯片"])
    print(f"过滤器: {filter5}")
    print()

    test_items = [
        {"title": "TikTok 将开放用户设置，减少短视频信息流中的 AI 内容"},
        {"title": "谷歌学术测试新技能：AI 提供论文摘要"},
        {"title": "群联推出 PCIe 5.0 企业级 SSD 新品，核显 AI 推理加速方案"},  # 虽然有AI，但也有"芯片"相关内容
        {"title": "OpenAI 发布 GPT-5 模型，性能大幅提升"},
        {"title": "NVIDIA 发布新一代 GPU 芯片"},  # 有排除词"GPU"和"芯片"
    ]

    filtered = filter5.filter_items(test_items, text_field='title')
    print(f"过滤结果: {len(filtered)}/{len(test_items)} 条")
    print()

    for i, item in enumerate(filtered, 1):
        score = item.get('relevance_score', 0)
        title = item.get('title', '')
        print(f"{i}. [{score:5.1f}分] {title}")

    print()


def test_empty_filter():
    """测试空过滤器"""
    print("=" * 80)
    print("🧪 测试6: 空过滤器")
    print("=" * 80)
    print()

    filter6 = KeywordFilter([])
    print(f"过滤器: {filter6}")
    print(f"是否为空: {filter6.is_empty}")
    print()

    # 空过滤器应该匹配所有内容（没有任何限制）
    test_texts = ["任意文本", "Another text", "123"]
    for text in test_texts:
        result = filter6.matches(text)
        print(f"匹配 \"{text}\": {result}")

    print()


def run_all_tests():
    """运行所有测试"""
    test_basic_filtering()
    test_scoring()
    test_string_parsing()
    test_filter_items()
    test_llm_domain()
    test_empty_filter()

    print("=" * 80)
    print("✨ 所有测试完成！")
    print("=" * 80)
    print()
    print("💡 关键词过滤语法:")
    print("   - normal_word: 普通关键词（可选，增加相关性分数）")
    print("   - +required_word: 必须包含的关键词")
    print("   - !exclude_word: 必须排除的关键词")
    print()
    print("💡 评分规则:")
    print("   - 基础分: 10分")
    print("   - 每个必须关键词: +20分")
    print("   - 每个普通关键词: +10分")
    print("   - 最高分: 100分")
    print()


if __name__ == "__main__":
    run_all_tests()
