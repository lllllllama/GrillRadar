#!/usr/bin/env python3
"""
快速测试API连接
"""
import sys
from pathlib import Path

# 添加app目录到Python路径
sys.path.insert(0, str(Path(__file__).parent))

from app.core.llm_client import LLMClient

def test_api_connection():
    """测试API连接"""
    print("=" * 60)
    print("测试 API 连接...")
    print("=" * 60)

    try:
        # 创建LLM客户端
        client = LLMClient()
        print("✓ LLM客户端初始化成功")

        # 发送简单的测试请求
        print("\n发送测试请求...")
        response = client.call(
            system_prompt="你是一个友好的AI助手。",
            user_message="请用一句话介绍自己。"
        )

        print("\n✓ API调用成功！")
        print("-" * 60)
        print("响应内容：")
        print(response)
        print("-" * 60)

        return True

    except Exception as e:
        print(f"\n✗ API调用失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = test_api_connection()
    sys.exit(0 if success else 1)
