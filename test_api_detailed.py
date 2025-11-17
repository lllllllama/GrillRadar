#!/usr/bin/env python3
"""
详细的API连接诊断
"""
import sys
import httpx
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from app.config.settings import settings

def test_direct_api_call():
    """直接测试API调用"""
    print("=" * 60)
    print("直接测试 BigModel API...")
    print("=" * 60)

    url = f"{settings.ANTHROPIC_BASE_URL}/v1/messages"
    headers = {
        "x-api-key": settings.ANTHROPIC_AUTH_TOKEN,
        "anthropic-version": "2023-06-01",
        "content-type": "application/json"
    }

    data = {
        "model": "claude-sonnet-4",
        "max_tokens": 1024,
        "messages": [
            {"role": "user", "content": "你好，请用一句话介绍自己。"}
        ]
    }

    print(f"URL: {url}")
    print(f"Headers: {headers}")
    print(f"Data: {data}")
    print("\n发送请求...")

    try:
        response = httpx.post(url, headers=headers, json=data, timeout=30.0)
        print(f"\n状态码: {response.status_code}")
        print(f"响应头: {response.headers}")
        print(f"响应体: {response.text[:500]}")

        if response.status_code == 200:
            print("\n✓ API调用成功！")
            return True
        else:
            print(f"\n✗ API调用失败！")
            return False

    except Exception as e:
        print(f"\n✗ 请求异常: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = test_direct_api_call()
    sys.exit(0 if success else 1)
