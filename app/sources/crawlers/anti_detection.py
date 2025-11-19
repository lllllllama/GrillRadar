"""
反爬虫工具 - 提供更真实的浏览器请求模拟
"""
import random
from typing import Dict, List


class AntiDetectionHelper:
    """反爬虫检测助手"""

    # User-Agent池 - 使用最新的浏览器版本
    USER_AGENTS = [
        # Chrome
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',

        # Edge
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Edg/120.0.0.0',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Edg/120.0.0.0',

        # Firefox
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:121.0) Gecko/20100101 Firefox/121.0',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0',

        # Safari
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Safari/605.1.15',
    ]

    @staticmethod
    def get_random_user_agent() -> str:
        """获取随机User-Agent"""
        return random.choice(AntiDetectionHelper.USER_AGENTS)

    @staticmethod
    def get_browser_headers(
        referer: str = None,
        accept: str = "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8"
    ) -> Dict[str, str]:
        """
        获取完整的浏览器请求头

        Args:
            referer: 来源页面URL
            accept: Accept header

        Returns:
            完整的请求头字典
        """
        headers = {
            'User-Agent': AntiDetectionHelper.get_random_user_agent(),
            'Accept': accept,
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8,en-US;q=0.7',
            'Accept-Encoding': 'gzip, deflate, br',
            'DNT': '1',  # Do Not Track
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Sec-Fetch-User': '?1',
            'Cache-Control': 'max-age=0',
        }

        if referer:
            headers['Referer'] = referer

        return headers

    @staticmethod
    def get_random_delay(min_delay: float = 0.5, max_delay: float = 2.0) -> float:
        """
        获取随机延迟时间（秒）

        Args:
            min_delay: 最小延迟
            max_delay: 最大延迟

        Returns:
            随机延迟时间
        """
        return random.uniform(min_delay, max_delay)

    @staticmethod
    def get_cookies_for_site(site: str) -> Dict[str, str]:
        """
        获取特定网站的基础cookies

        Args:
            site: 网站名称 (juejin, zhihu, csdn)

        Returns:
            cookies字典
        """
        # 这里可以添加一些基础的、公开的cookies
        # 注意：不要硬编码任何敏感或个人的cookie
        cookies_map = {
            'juejin': {
                # 掘金的一些基础配置cookie（非登录态）
                '_ga': 'GA1.2.random.1234567890',
                '_gid': 'GA1.2.random.1234567890',
            },
            'zhihu': {
                # 知乎的一些基础配置cookie（非登录态）
                '_zap': str(random.randint(100000000, 999999999)),
                '_xsrf': 'random_xsrf_token',
            },
            'csdn': {},
        }

        return cookies_map.get(site, {})
