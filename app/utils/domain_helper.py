"""领域管理辅助工具（Milestone 3）"""
import yaml
from typing import Dict, List, Optional
from pathlib import Path
from app.config.settings import settings


class DomainHelper:
    """领域配置管理辅助类"""

    def __init__(self):
        """初始化，加载domains.yaml"""
        with open(settings.DOMAINS_CONFIG, 'r', encoding='utf-8') as f:
            self.domains = yaml.safe_load(f)

    def get_all_domains(self) -> Dict:
        """
        获取所有领域的完整信息

        Returns:
            包含engineering和research两个类别的字典
        """
        return self.domains

    def get_domains_list(self) -> Dict:
        """
        获取领域列表（用于API返回）

        Returns:
            格式化的领域列表，包含display_name和description
        """
        result = {
            "engineering": [],
            "research": []
        }

        for category in ['engineering', 'research']:
            if category in self.domains:
                for domain_key, domain_data in self.domains[category].items():
                    result[category].append({
                        "value": domain_key,
                        "label": domain_data.get('display_name', domain_key),
                        "description": domain_data.get('description', '')
                    })

        return result

    def get_domain_detail(self, domain: str) -> Optional[Dict]:
        """
        获取单个领域的详细信息

        Args:
            domain: 领域key（如'backend', 'cv_segmentation'）

        Returns:
            领域详细信息，如果不存在则返回None
        """
        for category in ['engineering', 'research']:
            if category in self.domains and domain in self.domains[category]:
                domain_data = self.domains[category][domain].copy()
                domain_data['category'] = category
                return domain_data

        return None

    def validate_domain(self, domain: Optional[str]) -> bool:
        """
        验证领域是否存在

        Args:
            domain: 领域key

        Returns:
            是否存在
        """
        if not domain:
            return True  # 允许不指定领域

        for category in ['engineering', 'research']:
            if category in self.domains and domain in self.domains[category]:
                return True

        return False

    def get_domain_summary(self) -> Dict:
        """
        获取领域统计摘要

        Returns:
            包含总数和各类别数量的字典
        """
        engineering_count = len(self.domains.get('engineering', {}))
        research_count = len(self.domains.get('research', {}))

        return {
            "total": engineering_count + research_count,
            "engineering": engineering_count,
            "research": research_count
        }


# 单例实例
domain_helper = DomainHelper()
