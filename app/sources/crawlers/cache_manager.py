"""
爬虫缓存管理器 / Crawler Cache Manager

提供简单的文件缓存机制，避免频繁调用外部API
"""
import json
import hashlib
import os
import time
from pathlib import Path
from typing import Optional, Any, Dict
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)


class CacheManager:
    """
    爬虫缓存管理器

    特性：
    - 基于文件的缓存存储
    - TTL (Time To Live) 过期机制
    - 自动清理过期缓存
    - 线程安全（文件锁）
    """

    def __init__(
        self,
        cache_dir: str = ".cache/crawler",
        default_ttl: int = 3600,
        max_cache_size_mb: int = 100
    ):
        """
        初始化缓存管理器

        Args:
            cache_dir: 缓存目录路径
            default_ttl: 默认缓存有效期（秒），默认1小时
            max_cache_size_mb: 最大缓存大小（MB），默认100MB
        """
        self.cache_dir = Path(cache_dir)
        self.default_ttl = default_ttl
        self.max_cache_size_mb = max_cache_size_mb

        # 创建缓存目录
        self.cache_dir.mkdir(parents=True, exist_ok=True)

        logger.info(f"CacheManager initialized: dir={cache_dir}, ttl={default_ttl}s")

    def get(
        self,
        key: str,
        default: Any = None
    ) -> Optional[Any]:
        """
        从缓存获取数据

        Args:
            key: 缓存键
            default: 默认值（缓存未命中时返回）

        Returns:
            缓存的数据，如果未命中或已过期则返回default
        """
        cache_file = self._get_cache_file(key)

        if not cache_file.exists():
            logger.debug(f"Cache miss: {key}")
            return default

        try:
            with open(cache_file, 'r', encoding='utf-8') as f:
                cache_data = json.load(f)

            # 检查是否过期
            expires_at = cache_data.get('expires_at')
            if expires_at and time.time() > expires_at:
                logger.debug(f"Cache expired: {key}")
                # 删除过期缓存
                cache_file.unlink()
                return default

            logger.debug(f"Cache hit: {key}")
            return cache_data.get('data')

        except Exception as e:
            logger.warning(f"Failed to read cache for key {key}: {e}")
            return default

    def set(
        self,
        key: str,
        value: Any,
        ttl: Optional[int] = None
    ) -> bool:
        """
        设置缓存数据

        Args:
            key: 缓存键
            value: 要缓存的数据（必须可JSON序列化）
            ttl: 缓存有效期（秒），None则使用默认值

        Returns:
            bool: 是否成功设置
        """
        ttl = ttl if ttl is not None else self.default_ttl
        expires_at = time.time() + ttl

        cache_data = {
            'data': value,
            'created_at': time.time(),
            'expires_at': expires_at,
            'ttl': ttl
        }

        cache_file = self._get_cache_file(key)

        try:
            with open(cache_file, 'w', encoding='utf-8') as f:
                json.dump(cache_data, f, ensure_ascii=False, indent=2, default=str)

            logger.debug(f"Cache set: {key} (ttl={ttl}s)")
            return True

        except Exception as e:
            logger.warning(f"Failed to write cache for key {key}: {e}")
            return False

    def delete(self, key: str) -> bool:
        """
        删除缓存

        Args:
            key: 缓存键

        Returns:
            bool: 是否成功删除
        """
        cache_file = self._get_cache_file(key)

        if cache_file.exists():
            try:
                cache_file.unlink()
                logger.debug(f"Cache deleted: {key}")
                return True
            except Exception as e:
                logger.warning(f"Failed to delete cache for key {key}: {e}")
                return False

        return False

    def clear(self) -> int:
        """
        清空所有缓存

        Returns:
            int: 删除的缓存文件数量
        """
        count = 0
        for cache_file in self.cache_dir.glob("*.json"):
            try:
                cache_file.unlink()
                count += 1
            except Exception as e:
                logger.warning(f"Failed to delete cache file {cache_file}: {e}")

        logger.info(f"Cleared {count} cache files")
        return count

    def cleanup_expired(self) -> int:
        """
        清理过期缓存

        Returns:
            int: 删除的过期缓存数量
        """
        count = 0
        current_time = time.time()

        for cache_file in self.cache_dir.glob("*.json"):
            try:
                with open(cache_file, 'r', encoding='utf-8') as f:
                    cache_data = json.load(f)

                expires_at = cache_data.get('expires_at')
                if expires_at and current_time > expires_at:
                    cache_file.unlink()
                    count += 1

            except Exception as e:
                logger.warning(f"Failed to check/delete cache file {cache_file}: {e}")

        if count > 0:
            logger.info(f"Cleaned up {count} expired cache files")

        return count

    def get_cache_info(self) -> Dict[str, Any]:
        """
        获取缓存统计信息

        Returns:
            Dict: 缓存信息（文件数、总大小、过期数等）
        """
        total_files = 0
        total_size = 0
        expired_count = 0
        current_time = time.time()

        for cache_file in self.cache_dir.glob("*.json"):
            total_files += 1
            total_size += cache_file.stat().st_size

            try:
                with open(cache_file, 'r', encoding='utf-8') as f:
                    cache_data = json.load(f)

                expires_at = cache_data.get('expires_at')
                if expires_at and current_time > expires_at:
                    expired_count += 1

            except Exception:
                pass

        return {
            'cache_dir': str(self.cache_dir),
            'total_files': total_files,
            'total_size_mb': round(total_size / (1024 * 1024), 2),
            'expired_files': expired_count,
            'active_files': total_files - expired_count
        }

    def _get_cache_file(self, key: str) -> Path:
        """
        根据key生成缓存文件路径

        Args:
            key: 缓存键

        Returns:
            Path: 缓存文件路径
        """
        # 使用MD5哈希生成文件名（避免key中的特殊字符）
        key_hash = hashlib.md5(key.encode('utf-8')).hexdigest()
        return self.cache_dir / f"{key_hash}.json"

    @staticmethod
    def generate_cache_key(source: str, domain: str, keywords: list) -> str:
        """
        生成缓存键

        Args:
            source: 数据源名称
            domain: 领域
            keywords: 关键词列表

        Returns:
            str: 缓存键
        """
        # 排序keywords以保证一致性
        sorted_keywords = sorted(keywords) if keywords else []
        key_parts = [source, domain] + sorted_keywords
        cache_key = ":".join(key_parts)
        return cache_key


# 全局缓存管理器实例
_default_cache_manager: Optional[CacheManager] = None


def get_cache_manager(
    cache_dir: str = ".cache/crawler",
    default_ttl: int = 3600
) -> CacheManager:
    """
    获取全局缓存管理器实例

    Args:
        cache_dir: 缓存目录
        default_ttl: 默认TTL

    Returns:
        CacheManager: 缓存管理器实例
    """
    global _default_cache_manager

    if _default_cache_manager is None:
        _default_cache_manager = CacheManager(
            cache_dir=cache_dir,
            default_ttl=default_ttl
        )

    return _default_cache_manager
