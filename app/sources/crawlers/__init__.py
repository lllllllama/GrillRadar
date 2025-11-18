"""
多源爬虫模块 / Multi-source Crawler Module

TrendRadar风格的信息采集和聚合系统
TrendRadar-style information acquisition and aggregation system
"""
from app.sources.crawlers.models import RawItem, CrawlerConfig
from app.sources.crawlers.base_crawler import BaseCrawler

__all__ = ['RawItem', 'CrawlerConfig', 'BaseCrawler']
