"""Pytest configuration and fixtures"""

import pytest
from app.models.user_config import UserConfig


@pytest.fixture
def sample_resume():
    """Sample resume text for testing"""
    return """
姓名：张三
教育背景：清华大学 计算机科学与技术 本科

项目经历：
1. 分布式爬虫系统
   - 使用Python开发，基于Redis和RabbitMQ
   - 实现了任务去重和容错机制
   - 日均爬取数据100万条

2. 微服务后端系统
   - 使用Go开发RESTful API
   - 接入MySQL和Redis
   - 支持10000+ QPS

技能：Python, Go, Java, MySQL, Redis, Kafka, Docker
"""


@pytest.fixture
def job_config(sample_resume):
    """Job mode configuration"""
    return UserConfig(
        mode='job',
        target_desc='字节跳动后端开发工程师',
        domain='backend',
        resume_text=sample_resume
    )


@pytest.fixture
def grad_config(sample_resume):
    """Grad mode configuration"""
    return UserConfig(
        mode='grad',
        target_desc='计算机视觉方向研究生',
        domain='cv_segmentation',
        resume_text=sample_resume
    )
