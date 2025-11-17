"""Mock数据提供者（Milestone 4 演示版）

本模块提供模拟的JD和面经数据，用于演示外部信息源集成功能。
在生产环境中，可替换为真实的爬虫或API调用。
"""
from typing import List
from datetime import datetime
from app.models.external_info import JobDescription, InterviewExperience


class MockDataProvider:
    """模拟数据提供者"""

    @staticmethod
    def get_mock_jds(company: str = None, position: str = None) -> List[JobDescription]:
        """获取模拟的JD数据"""
        mock_jds = [
            JobDescription(
                company="字节跳动",
                position="后端开发工程师",
                location="北京",
                salary_range="30k-50k",
                requirements=[
                    "本科及以上学历，计算机相关专业",
                    "3年以上后端开发经验",
                    "精通Java或Go语言，熟悉常用框架",
                    "熟悉MySQL、Redis等数据库",
                    "有分布式系统设计和开发经验",
                    "有高并发、大流量系统开发经验优先"
                ],
                responsibilities=[
                    "负责抖音推荐系统后端开发",
                    "参与核心业务系统架构设计和优化",
                    "保证系统的稳定性、可用性和性能",
                    "参与技术方案评审和代码review"
                ],
                keywords=[
                    "Java", "Go", "MySQL", "Redis", "Kafka",
                    "分布式系统", "高并发", "微服务", "Docker", "Kubernetes"
                ],
                source_url="https://job.bytedance.com/campus/position/...",
                crawled_at=datetime.utcnow()
            ),
            JobDescription(
                company="阿里巴巴",
                position="Java开发工程师",
                location="杭州",
                salary_range="25k-45k",
                requirements=[
                    "本科及以上学历",
                    "2年以上Java开发经验",
                    "精通Spring Boot、MyBatis等框架",
                    "熟悉分布式、缓存、消息队列等技术",
                    "有电商或支付系统开发经验优先"
                ],
                responsibilities=[
                    "负责淘宝核心交易系统开发",
                    "参与系统架构升级和性能优化",
                    "保障系统稳定性，快速响应线上问题"
                ],
                keywords=[
                    "Java", "Spring Boot", "MyBatis", "MySQL",
                    "Redis", "RabbitMQ", "分布式事务", "微服务"
                ],
                source_url="https://talent.alibaba.com/...",
                crawled_at=datetime.utcnow()
            ),
            JobDescription(
                company="腾讯",
                position="后端研发工程师",
                location="深圳",
                salary_range="28k-48k",
                requirements=[
                    "本科及以上学历，3年以上开发经验",
                    "精通C++、Go或Java",
                    "熟悉Linux开发环境",
                    "有大型互联网系统开发经验",
                    "良好的算法和数据结构基础"
                ],
                responsibilities=[
                    "负责微信后台系统开发",
                    "参与核心模块的设计和实现",
                    "负责系统性能优化和故障排查"
                ],
                keywords=[
                    "C++", "Go", "Linux", "高性能", "分布式",
                    "MySQL", "协议设计", "网络编程"
                ],
                source_url="https://careers.tencent.com/...",
                crawled_at=datetime.utcnow()
            )
        ]

        # 简单过滤（实际应用中会更复杂）
        if company:
            mock_jds = [jd for jd in mock_jds if company in jd.company]
        if position:
            mock_jds = [jd for jd in mock_jds if position in jd.position or "后端" in jd.position]

        return mock_jds

    @staticmethod
    def get_mock_experiences(company: str = None, position: str = None) -> List[InterviewExperience]:
        """获取模拟的面经数据"""
        mock_exps = [
            InterviewExperience(
                company="字节跳动",
                position="后端开发工程师",
                interview_type="一面（技术面）",
                questions=[
                    "自我介绍，讲一下项目经历",
                    "详细讲一下你的分布式爬虫系统是如何设计的？",
                    "如何保证分布式任务不重复、不丢失？",
                    "Redis和MySQL的数据一致性如何保证？",
                    "如果让你设计一个秒杀系统，你会怎么做？",
                    "算法题：LeetCode 146 - LRU Cache"
                ],
                difficulty="中等",
                topics=[
                    "项目经历", "分布式系统", "数据一致性",
                    "系统设计", "算法"
                ],
                tips="重点考察项目深度，要能讲清楚技术细节和遇到的坑",
                source_url="https://www.nowcoder.com/discuss/...",
                shared_at=datetime.utcnow()
            ),
            InterviewExperience(
                company="字节跳动",
                position="后端开发工程师",
                interview_type="二面（技术面）",
                questions=[
                    "讲一下你认为最复杂的项目",
                    "如何设计一个分布式锁？",
                    "CAP理论是什么？在你的项目中如何权衡？",
                    "MySQL的索引原理，B+树和哈希索引的区别",
                    "Go的GC机制了解吗？",
                    "算法题：手写快排"
                ],
                difficulty="中等偏难",
                topics=[
                    "系统设计", "分布式理论", "数据库原理",
                    "语言特性", "算法"
                ],
                tips="二面更注重深度和原理性问题",
                source_url="https://www.nowcoder.com/discuss/...",
                shared_at=datetime.utcnow()
            ),
            InterviewExperience(
                company="阿里巴巴",
                position="Java开发工程师",
                interview_type="一面（技术面）",
                questions=[
                    "介绍一下Spring Boot的核心特性",
                    "Spring的AOP和IoC原理",
                    "MySQL的事务隔离级别有哪些？",
                    "如何解决缓存穿透、缓存击穿、缓存雪崩？",
                    "讲一下你在项目中遇到的性能问题和解决方案",
                    "算法题：两数之和变种"
                ],
                difficulty="中等",
                topics=[
                    "Java框架", "数据库", "缓存", "性能优化", "算法"
                ],
                tips="阿里很注重Java基础和框架原理",
                source_url="https://www.nowcoder.com/discuss/...",
                shared_at=datetime.utcnow()
            ),
            InterviewExperience(
                company="腾讯",
                position="后端研发工程师",
                interview_type="一面（技术面）",
                questions=[
                    "C++的多态是如何实现的？",
                    "智能指针有哪些？各自的使用场景",
                    "TCP的拥塞控制算法",
                    "如何设计一个高性能的网络框架？",
                    "讲一下你对微服务的理解",
                    "算法题：链表相关"
                ],
                difficulty="中等",
                topics=[
                    "C++", "网络编程", "系统设计", "算法"
                ],
                tips="腾讯很看重C++基础和网络编程能力",
                source_url="https://www.nowcoder.com/discuss/...",
                shared_at=datetime.utcnow()
            )
        ]

        # 简单过滤
        if company:
            mock_exps = [exp for exp in mock_exps if company in exp.company]
        if position:
            mock_exps = [exp for exp in mock_exps if "后端" in exp.position or "Java" in exp.position]

        return mock_exps
