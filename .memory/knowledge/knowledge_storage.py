"""
知识存储模块
管理知识库的结构化存储和检索
"""
import json
import os
from datetime import datetime
from typing import Any, Dict, List, Optional


class KnowledgeStorage:
    """
    知识存储
    
    支持：
    - 主题分类（个人、编程、项目）
    - 资源库（链接、文档）
    - 自动摘要生成
    - 标签和分类管理
    """
    
    def __init__(self, base_path: str = None):
        self.base_path = base_path or os.path.join(
            os.path.dirname(__file__), 'knowledge'
        )
        
        # 子目录
        self.topics_path = os.path.join(self.base_path, 'topics')
        self.resources_path = os.path.join(self.base_path, 'resources')
        self.summaries_path = os.path.join(self.base_path, 'summaries')
        
        # 确保目录存在
        os.makedirs(self.topics_path, exist_ok=True)
        os.makedirs(os.path.join(self.topics_path, 'personal'), exist_ok=True)
        os.makedirs(os.path.join(self.topics_path, 'programming'), exist_ok=True)
        os.makedirs(os.path.join(self.topics_path, 'project'), exist_ok=True)
        os.makedirs(self.resources_path, exist_ok=True)
        os.makedirs(self.summaries_path, exist_ok=True)
    
    def save_topic(
        self,
        topic: str,
        title: str,
        content: str,
        category: str = 'personal',  # personal/programming/project
        tags: List[str] = None,
        metadata: Dict = None
    ) -> str:
        """
        保存主题知识
        
        Args:
            topic: 主题名称
            title: 标题
            content: 内容
            category: 分类
            tags: 标签
            metadata: 元数据
        
        Returns:
            str: 文件路径
        """
        category_path = os.path.join(self.topics_path, category)
        os.makedirs(category_path, exist_ok=True)
        
        file_path = os.path.join(category_path, f'{topic}.json')
        
        data = {
            "topic": topic,
            "title": title,
            "content": content,
            "category": category,
            "tags": tags or [],
            "metadata": metadata or {},
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        }
        
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        return file_path
    
    def save_resource(
        self,
        title: str,
        url: str = None,
        content: str = None,
        resource_type: str = 'link',  # link/document/note
        tags: List[str] = None,
        metadata: Dict = None
    ) -> str:
        """
        保存资源
        
        Args:
            title: 标题
            url: 链接
            content: 内容
            resource_type: 类型
            tags: 标签
            metadata: 元数据
        
        Returns:
            str: 文件路径
        """
        file_path = os.path.join(self.resources_path, f'{resource_type}s.json')
        
        resource = {
            "id": f"res_{datetime.now().strftime('%Y%m%d%H%M%S')}",
            "title": title,
            "url": url,
            "content": content,
            "resource_type": resource_type,
            "tags": tags or [],
            "metadata": metadata or {},
            "created_at": datetime.now().isoformat()
        }
        
        # 追加到资源文件
        resources = []
        if os.path.exists(file_path):
            with open(file_path, 'r', encoding='utf-8') as f:
                try:
                    resources = json.load(f)
                except json.JSONDecodeError:
                    resources = []
        
        resources.append(resource)
        
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(resources, f, ensure_ascii=False, indent=2)
        
        return file_path
    
    def save_summary(
        self,
        title: str,
        summary: str,
        source: str = None,
        tags: List[str] = None,
        metadata: Dict = None
    ) -> str:
        """
        保存摘要
        
        Args:
            title: 标题
            summary: 摘要内容
            source: 来源
            tags: 标签
            metadata: 元数据
        
        Returns:
            str: 文件路径
        """
        date = datetime.now().strftime('%Y-%m')
        file_path = os.path.join(self.summaries_path, f'{date}.json')
        
        data = {
            "id": f"sum_{datetime.now().strftime('%Y%m%d%H%M%S')}",
            "title": title,
            "summary": summary,
            "source": source,
            "tags": tags or [],
            "metadata": metadata or {},
            "created_at": datetime.now().isoformat()
        }
        
        # 追加到摘要文件
        summaries = []
        if os.path.exists(file_path):
            with open(file_path, 'r', encoding='utf-8') as f:
                try:
                    summaries = json.load(f)
                except json.JSONDecodeError:
                    summaries = []
        
        summaries.insert(0, data)  # 新摘要放在前面
        
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(summaries, f, ensure_ascii=False, indent=2)
        
        return file_path
    
    def load_topic(
        self,
        topic: str,
        category: str = 'personal'
    ) -> Optional[Dict]:
        """加载指定主题"""
        file_path = os.path.join(
            self.topics_path, category, f'{topic}.json'
        )
        
        if not os.path.exists(file_path):
            return None
        
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def load_resources(
        self,
        resource_type: str = None
    ) -> List[Dict]:
        """加载资源"""
        if resource_type:
            file_path = os.path.join(self.resources_path, f'{resource_type}s.json')
            if os.path.exists(file_path):
                with open(file_path, 'r', encoding='utf-8') as f:
                    try:
                        return json.load(f)
                    except json.JSONDecodeError:
                        return []
            return []
        
        # 加载所有资源
        all_resources = []
        for file in os.listdir(self.resources_path):
            if file.endswith('.json'):
                with open(os.path.join(self.resources_path, file), 'r', encoding='utf-8') as f:
                    try:
                        all_resources.extend(json.load(f))
                    except json.JSONDecodeError:
                        pass
        
        return all_resources
    
    def search(
        self,
        query: str = None,
        category: str = None,
        tags: List[str] = None,
        limit: int = 100
    ) -> List[Dict]:
        """
        搜索知识
        
        Args:
            query: 关键词搜索
            category: 分类筛选
            tags: 标签筛选
            limit: 返回数量
        """
        results = []
        
        # 搜索主题
        for cat in [category] if category else ['personal', 'programming', 'project']:
            cat_path = os.path.join(self.topics_path, cat)
            if not os.path.exists(cat_path):
                continue
            
            for file in os.listdir(cat_path):
                if file.endswith('.json'):
                    with open(os.path.join(cat_path, file), 'r', encoding='utf-8') as f:
                        try:
                            data = json.load(f)
                            
                            # 筛选
                            if query:
                                content = json.dumps(data)
                                if query not in content:
                                    continue
                            
                            if tags:
                                if not all(t in data.get('tags', []) for t in tags):
                                    continue
                            
                            results.append(data)
                        except json.JSONDecodeError:
                            pass
        
        return results[:limit]
    
    def get_stats(self) -> Dict:
        """获取统计信息"""
        stats = {
            "topics": {
                "personal": 0,
                "programming": 0,
                "project": 0
            },
            "resources": {
                "links": 0,
                "documents": 0,
                "notes": 0
            },
            "summaries": 0
        }
        
        # 统计主题
        for cat in stats['topics']:
            cat_path = os.path.join(self.topics_path, cat)
            if os.path.exists(cat_path):
                stats['topics'][cat] = len([
                    f for f in os.listdir(cat_path) if f.endswith('.json')
                ])
        
        # 统计资源
        for rt in stats['resources']:
            file_path = os.path.join(self.resources_path, f'{rt}s.json')
            if os.path.exists(file_path):
                with open(file_path, 'r', encoding='utf-8') as f:
                    try:
                        stats['resources'][rt] = len(json.load(f))
                    except json.JSONDecodeError:
                        pass
        
        # 统计摘要
        stats['summaries'] = len([
            f for f in os.listdir(self.summaries_path) if f.endswith('.json')
        ])
        
        return stats


# 全局实例
_knowledge_storage = None

def get_knowledge_storage(base_path: str = None) -> KnowledgeStorage:
    """获取知识存储实例"""
    global _knowledge_storage
    if _knowledge_storage is None:
        _knowledge_storage = KnowledgeStorage(base_path)
    return _knowledge_storage
