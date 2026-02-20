"""
OpenClaw 记忆系统集成模块
替换原有的 memory_search/memory_get 函数
"""
import os
import sys
from typing import List, Dict, Optional
from datetime import datetime

# 添加路径
_base_dir = os.path.dirname(os.path.dirname(__file__))
_memory_system_path = os.path.join(_base_dir, 'memory_system')
_memory_path = os.path.join(_base_dir, '.memory')

for path in [_base_dir, _memory_system_path, _memory_path]:
    if path not in sys.path:
        sys.path.insert(0, path)

# 导入记忆系统
from memory_system import (
    get_unified_memory,
    save_to_memory,
    load_from_memory,
    search_memory_v2,
    get_dual_writer,
    get_file_sync,
    WriteMode
)

from crud_api import MemoryType


class MemoryManager:
    """
    记忆管理器
    集成到 OpenClaw 主会话
    """
    
    def __init__(self):
        self._initialized = False
    
    def initialize(self):
        """初始化记忆系统"""
        if self._initialized:
            return
        
        self.um = get_unified_memory()
        self.dw = get_dual_writer(WriteMode.SYNC)
        self.fs = get_file_sync()
        self._initialized = True
        
        print("✅ 记忆系统已初始化")
    
    # ==================== 保存接口 ====================
    
    def save(
        self,
        key: str,
        value: any,
        memory_type: str = "custom",
        tags: List[str] = None,
        metadata: Dict = None
    ) -> str:
        """
        保存记忆
        
        Args:
            key: 唯一键名
            value: 内容
            memory_type: 类型 (conversation/knowledge/goal/task/decision/custom)
            tags: 标签
            metadata: 元数据
        """
        if not self._initialized:
            self.initialize()
        
        return self.um.save(
            key=key,
            value=value,
            memory_type=memory_type,
            tags=tags or [],
            metadata=metadata or {}
        )
    
    def save_conversation(
        self,
        conversation_id: str,
        messages: List[Dict],
        metadata: Dict = None
    ) -> str:
        """保存对话"""
        return self.save(
            key=f"conv_{conversation_id}",
            value=messages,
            memory_type="conversation",
            tags=["conversation"],
            metadata=metadata
        )
    
    def save_decision(
        self,
        decision_id: str,
        title: str,
        content: str,
        tags: List[str] = None
    ) -> str:
        """保存决策"""
        return self.save(
            key=f"decision_{decision_id}",
            value={
                "title": title,
                "content": content
            },
            memory_type="decision",
            tags=tags or ["decision"]
        )
    
    def save_goal(
        self,
        goal_id: str,
        title: str,
        content: str,
        goal_type: str,  # annual/quarterly/monthly
        metadata: Dict = None
    ) -> str:
        """保存目标"""
        return self.save(
            key=f"goal_{goal_type}_{goal_id}",
            value={
                "title": title,
                "content": content
            },
            memory_type="goal",
            tags=["goal", goal_type],
            metadata=metadata
        )
    
    # ==================== 加载接口 ====================
    
    def load(
        self,
        key: str = None,
        memory_type: str = None,
        tags: List[str] = None,
        limit: int = 100
    ) -> List[Dict]:
        """
        加载记忆
        
        Args:
            key: 按键名查找
            memory_type: 按类型筛选
            tags: 按标签筛选
            limit: 返回数量
        """
        if not self._initialized:
            self.initialize()
        
        mem_type = MemoryType(memory_type) if memory_type else None
        
        return self.um.load(
            key=key,
            memory_type=mem_type,
            tags=tags,
            limit=limit
        )
    
    def load_today_conversations(self) -> List[Dict]:
        """加载今日对话"""
        return self.load(memory_type="conversation", limit=100)
    
    def load_decisions(self, status: str = None) -> List[Dict]:
        """加载决策"""
        return self.load(memory_type="decision", limit=100)
    
    # ==================== 搜索接口 ====================
    
    def search(
        self,
        query: str = None,
        key: str = None,
        memory_type: str = None,
        tags: List[str] = None,
        mode: str = "hybrid",  # exact/semantic/hybrid
        limit: int = 10
    ) -> List[Dict]:
        """
        搜索记忆
        
        Args:
            query: 语义搜索查询
            key: 精确键名
            memory_type: 类型筛选
            tags: 标签筛选
            mode: 搜索模式
            limit: 返回数量
        """
        if not self._initialized:
            self.initialize()
        
        return self.um.search(
            query=query,
            key=key,
            tags=tags,
            mode=mode,
            limit=limit
        )
    
    def semantic_search(self, query: str, limit: int = 10) -> List[Dict]:
        """语义搜索"""
        return self.search(query=query, mode="semantic", limit=limit)
    
    def exact_search(self, key: str) -> List[Dict]:
        """精确搜索"""
        return self.search(key=key, mode="exact", limit=1)
    
    # ==================== 删除接口 ====================
    
    def delete(
        self,
        key: str = None,
        memory_type: str = None,
        tags: List[str] = None
    ) -> int:
        """删除记忆"""
        if not self._initialized:
            self.initialize()
        
        mem_type = MemoryType(memory_type) if memory_type else None
        
        return self.um.delete(
            key=key,
            memory_type=mem_type,
            tags=tags
        )
    
    # ==================== 同步接口 ====================
    
    def sync_to_files(self) -> Dict:
        """同步所有数据到 .md 文件"""
        if not self._initialized:
            self.initialize()
        
        return self.um.sync_to_file()
    
    def export_all(self, output_path: str = None) -> str:
        """导出所有数据"""
        if not self._initialized:
            self.initialize()
        
        return self.fs.export_all(output_path)
    
    # ==================== 统计接口 ====================
    
    def stats(self) -> Dict:
        """获取统计信息"""
        if not self._initialized:
            self.initialize()
        
        return self.um.stats()


# 全局实例
_memory_manager = None

def get_memory_manager() -> MemoryManager:
    """获取记忆管理器实例"""
    global _memory_manager
    if _memory_manager is None:
        _memory_manager = MemoryManager()
    return _memory_manager


# ==================== OpenClaw 钩子函数 ====================

def memory_search(query: str = None, max_results: int = 10) -> List[Dict]:
    """
    OpenClaw 记忆搜索接口
    替换原有的 memory_search 函数
    
    Args:
        query: 搜索查询
        max_results: 最大返回数量
    
    Returns:
        List[Dict]: 搜索结果
    """
    mm = get_memory_manager()
    return mm.semantic_search(query, limit=max_results)


def memory_get(path: str = None, lines: int = None) -> str:
    """
    OpenClaw 记忆加载接口
    替换原有的 memory_get 函数
    
    Args:
        path: 记忆路径/键名
        lines: 返回行数
    
    Returns:
        str: 记忆内容
    """
    mm = get_memory_manager()
    results = mm.load(key=path, limit=1)
    
    if results:
        content = results[0].get('value', '')
        if lines and isinstance(content, str):
            content = '\n'.join(content.split('\n')[:lines])
        return content
    
    return ""


# ==================== 便捷函数 ====================

def remember(key: str, value: any, **kwargs) -> str:
    """保存记忆"""
    mm = get_memory_manager()
    return mm.save(key=key, value=value, **kwargs)


def recall(query: str = None, key: str = None, **kwargs) -> List[Dict]:
    """搜索记忆"""
    mm = get_memory_manager()
    return mm.search(query=query, key=key, **kwargs)


def forget(key: str = None, **kwargs) -> int:
    """删除记忆"""
    mm = get_memory_manager()
    return mm.delete(key=key, **kwargs)


def init_memory_system():
    """初始化记忆系统"""
    mm = get_memory_manager()
    mm.initialize()
    return mm
