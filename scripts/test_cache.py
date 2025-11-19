#!/usr/bin/env python3
"""
测试缓存机制
"""
import sys
import time
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from app.sources.crawlers.cache_manager import CacheManager, get_cache_manager


def test_basic_cache():
    """测试基本缓存功能"""
    print("=" * 80)
    print("🧪 测试1: 基本缓存功能")
    print("=" * 80)
    print()

    cache = CacheManager(cache_dir=".cache/test", default_ttl=10)

    # 设置缓存
    print("设置缓存...")
    cache.set("test_key_1", {"data": "Hello World", "count": 42})
    cache.set("test_key_2", ["Python", "Go", "Rust"], ttl=5)

    # 读取缓存
    print("读取缓存...")
    value1 = cache.get("test_key_1")
    value2 = cache.get("test_key_2")

    print(f"✅ test_key_1: {value1}")
    print(f"✅ test_key_2: {value2}")

    # 读取不存在的key
    value3 = cache.get("non_existent_key", default="default_value")
    print(f"✅ non_existent_key: {value3}")

    print()


def test_cache_expiration():
    """测试缓存过期"""
    print("=" * 80)
    print("🧪 测试2: 缓存过期")
    print("=" * 80)
    print()

    cache = CacheManager(cache_dir=".cache/test", default_ttl=2)

    # 设置短TTL缓存
    print("设置 2秒 TTL 缓存...")
    cache.set("short_ttl_key", "This will expire soon", ttl=2)

    # 立即读取
    value = cache.get("short_ttl_key")
    print(f"✅ 立即读取: {value}")

    # 等待1秒后读取
    print("等待 1秒...")
    time.sleep(1)
    value = cache.get("short_ttl_key")
    print(f"✅ 1秒后读取: {value}")

    # 等待2秒后读取（应该过期）
    print("等待 2秒...")
    time.sleep(2)
    value = cache.get("short_ttl_key", default="EXPIRED")
    print(f"✅ 3秒后读取: {value}")

    print()


def test_cache_info():
    """测试缓存信息"""
    print("=" * 80)
    print("🧪 测试3: 缓存信息")
    print("=" * 80)
    print()

    cache = CacheManager(cache_dir=".cache/test", default_ttl=60)

    # 添加一些缓存
    for i in range(5):
        cache.set(f"info_key_{i}", {"index": i, "data": f"Test data {i}"})

    # 获取缓存信息
    info = cache.get_cache_info()
    print(f"缓存目录: {info['cache_dir']}")
    print(f"总文件数: {info['total_files']}")
    print(f"总大小: {info['total_size_mb']} MB")
    print(f"过期文件: {info['expired_files']}")
    print(f"活跃文件: {info['active_files']}")

    print()


def test_cache_cleanup():
    """测试缓存清理"""
    print("=" * 80)
    print("🧪 测试4: 缓存清理")
    print("=" * 80)
    print()

    cache = CacheManager(cache_dir=".cache/test", default_ttl=1)

    # 添加一些缓存
    print("添加 5 个缓存项...")
    for i in range(5):
        cache.set(f"cleanup_key_{i}", {"index": i}, ttl=1 if i < 3 else 60)

    info = cache.get_cache_info()
    print(f"添加后: {info['total_files']} 个文件")

    # 等待2秒让一些缓存过期
    print("等待 2秒...")
    time.sleep(2)

    # 清理过期缓存
    print("清理过期缓存...")
    cleaned = cache.cleanup_expired()
    print(f"✅ 清理了 {cleaned} 个过期文件")

    info = cache.get_cache_info()
    print(f"清理后: {info['total_files']} 个文件")

    print()


def test_cache_delete():
    """测试删除缓存"""
    print("=" * 80)
    print("🧪 测试5: 删除缓存")
    print("=" * 80)
    print()

    cache = CacheManager(cache_dir=".cache/test", default_ttl=60)

    # 设置缓存
    cache.set("delete_key", "This will be deleted")

    # 验证存在
    value = cache.get("delete_key")
    print(f"设置后: {value}")

    # 删除
    print("删除缓存...")
    success = cache.delete("delete_key")
    print(f"✅ 删除成功: {success}")

    # 验证已删除
    value = cache.get("delete_key", default="NOT_FOUND")
    print(f"删除后: {value}")

    print()


def test_cache_clear():
    """测试清空所有缓存"""
    print("=" * 80)
    print("🧪 测试6: 清空所有缓存")
    print("=" * 80)
    print()

    cache = CacheManager(cache_dir=".cache/test", default_ttl=60)

    # 查看当前缓存
    info = cache.get_cache_info()
    print(f"清空前: {info['total_files']} 个文件")

    # 清空所有
    print("清空所有缓存...")
    count = cache.clear()
    print(f"✅ 删除了 {count} 个文件")

    # 验证已清空
    info = cache.get_cache_info()
    print(f"清空后: {info['total_files']} 个文件")

    print()


def run_all_tests():
    """运行所有测试"""
    test_basic_cache()
    test_cache_expiration()
    test_cache_info()
    test_cache_cleanup()
    test_cache_delete()
    test_cache_clear()

    print("=" * 80)
    print("✨ 所有缓存测试完成！")
    print("=" * 80)
    print()
    print("💡 缓存机制特性:")
    print("   - 基于文件的持久化存储")
    print("   - TTL (Time To Live) 自动过期")
    print("   - 支持清理过期缓存")
    print("   - 支持删除单个缓存")
    print("   - 支持清空所有缓存")
    print("   - 提供缓存统计信息")
    print()


if __name__ == "__main__":
    run_all_tests()
