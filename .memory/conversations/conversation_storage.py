"""
对话存储模块
管理对话数据的持久化和检索
"""
import json
import os
from datetime import datetime
from typing import Any, Dict, List, Optional
from pathlib import Path


class ConversationStorage:
    """
    对话存储
    
    支持：
    - 原始对话存储（按日期）
    - 带标签对话（决策、重要、待办）
    - 对话检索（按标签、时间、关键词）
    """
    
    def __init__(self, base_path: str = None):
        self.base_path = base_path or os.path.join(
            os.path.dirname(__file__), 'conversations'
        )
        
        # 子目录
        self.raw_path = os.path.join(self.base_path, 'raw')
        self.tagged_path = os.path.join(self.base_path, 'tagged')
        
        # 确保目录存在
        os.makedirs(self.raw_path, exist_ok=True)
        os.makedirs(os.path.join(self.tagged_path, 'decision'), exist_ok=True)
        os.makedirs(os.path.join(self.tagged_path, 'important'), exist_ok=True)
        os.makedirs(os.path.join(self.tagged_path, 'todo'), exist_ok=True)
    
    def save_raw(
        self,
        conversation_id: str,
        messages: List[Dict],
        metadata: Dict = None
    ) -> str:
        """
        保存原始对话
        
        Args:
            conversation_id: 对话 ID
            messages: 消息列表
            metadata: 元数据
        
        Returns:
            str: 文件路径
        """
        date = datetime.now().strftime('%Y/%m')
        date_dir = os.path.join(self.raw_path, date)
        os.makedirs(date_dir, exist_ok=True)
        
        file_path = os.path.join(date_dir, f'{datetime.now().strftime("%Y-%m-%d")}.json')
        
        data = {
            "conversation_id": conversation_id,
            "messages": messages,
            "metadata": metadata or {},
            "created_at": datetime.now().isoformat()
        }
        
        with open(file_path, 'a', encoding='utf-8') as f:
            f.write(json.dumps(data, ensure_ascii=False, indent=2) + '\n')
        
        return file_path
    
    def save_tagged(
        self,
        conversation_id: str,
        messages: List[Dict],
        tag_type: str,  # decision/important/todo
        reason: str,
        metadata: Dict = None
    ) -> str:
        """
        保存带标签对话
        
        Args:
            conversation_id: 对话 ID
            messages: 消息列表
            tag_type: 标签类型
            reason: 打标签原因
            metadata: 元数据
        
        Returns:
            str: 文件路径
        """
        tag_dir = os.path.join(self.tagged_path, tag_type)
        os.makedirs(tag_dir, exist_ok=True)
        
        file_path = os.path.join(tag_dir, f'{conversation_id}.json')
        
        data = {
            "conversation_id": conversation_id,
            "messages": messages,
            "tag_type": tag_type,
            "reason": reason,
            "metadata": metadata or {},
            "created_at": datetime.now().isoformat()
        }
        
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        return file_path
    
    def load_today(self) -> List[Dict]:
        """加载今日所有对话"""
        date_str = datetime.now().strftime('%Y-%m-%d')
        date = datetime.now().strftime('%Y/%m')
        date_dir = os.path.join(self.raw_path, date)
        
        file_path = os.path.join(date_dir, f'{date_str}.json')
        
        if not os.path.exists(file_path):
            return []
        
        conversations = []
        with open(file_path, 'r', encoding='utf-8') as f:
            for line in f.strip().split('\n'):
                if line:
                    conversations.append(json.loads(line))
        
        return conversations
    
    def load_tagged(self, tag_type: str) -> List[Dict]:
        """加载指定标签的所有对话"""
        tag_dir = os.path.join(self.tagged_path, tag_type)
        
        if not os.path.exists(tag_dir):
            return []
        
        conversations = []
        for file in os.listdir(tag_dir):
            if file.endswith('.json'):
                with open(os.path.join(tag_dir, file), 'r', encoding='utf-8') as f:
                    conversations.append(json.load(f))
        
        return conversations
    
    def search(
        self,
        query: str = None,
        tag_type: str = None,
        start_date: str = None,
        end_date: str = None,
        limit: int = 100
    ) -> List[Dict]:
        """
        搜索对话
        
        Args:
            query: 关键词搜索
            tag_type: 按标签筛选
            start_date: 开始日期
            end_date: 结束日期
            limit: 返回数量
        """
        results = []
        
        # 搜索带标签的对话
        if tag_type:
            conversations = self.load_tagged(tag_type)
            for conv in conversations:
                if query:
                    # 简单关键词匹配
                    content = json.dumps(conv.get('messages', []))
                    if query in content:
                        results.append(conv)
                else:
                    results.append(conv)
        
        # 搜索原始对话
        if not tag_type or query:
            conversations = self.load_today()
            for conv in conversations:
                if query:
                    content = json.dumps(conv.get('messages', []))
                    if query in content:
                        results.append(conv)
                else:
                    results.append(conv)
        
        return results[:limit]
    
    def get_stats(self) -> Dict:
        """获取统计信息"""
        stats = {
            "today_conversations": len(self.load_today()),
            "tagged_decisions": len(self.load_tagged('decision')),
            "tagged_important": len(self.load_tagged('important')),
            "tagged_todo": len(self.load_tagged('todo'))
        }
        return stats


# 全局实例
_conversation_storage = None

def get_conversation_storage(base_path: str = None) -> ConversationStorage:
    """获取对话存储实例"""
    global _conversation_storage
    if _conversation_storage is None:
        _conversation_storage = ConversationStorage(base_path)
    return _conversation_storage
