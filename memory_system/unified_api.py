"""
统一记忆 API 层
集成 SQLite、向量存储和文件存储
"""
import os
import sys

# 添加 .memory 目录到路径
_base_dir = os.path.dirname(os.path.dirname(__file__))  # E:\OpenClaw_Workspace
_memory_path = os.path.join(_base_dir, '.memory')
_vector_path = os.path.join(_base_dir, '.memory', '.memory')

# 确保路径在最前面
for path in [_memory_path, _vector_path]:
    if path not in sys.path:
        sys.path.insert(0, path)

# 导入数据库模块
from crud_api import (
    MemoryStorage, 
    get_memory_storage, 
    save_memory, 
    load_memory, 
    search_memory,
    MemoryType,
    SearchMode
)
from chromadb_storage import (
    VectorStorage,
    add_vector,
    search_vector,
    delete_vector
)

import json
from datetime import datetime
from typing import Any, Dict, List, Optional
from pathlib import Path


class UnifiedMemory:
    """
    统一记忆管理
    
    同时维护：
    - SQLite: 结构化数据存储
    - 向量存储: 语义搜索
    - 文件存储: 备份/导出
    """
    
    def __init__(self, base_path: str = None):
        self.base_path = base_path or os.path.dirname(os.path.dirname(__file__))
        self.memory_path = os.path.join(self.base_path, 'memory')
        self.memory_storage = get_memory_storage()
        
        # 确保目录存在
        os.makedirs(self.memory_path, exist_ok=True)
    
    def save(
        self,
        key: str,
        value: Any,
        memory_type: str = "custom",
        tags: List[str] = None,
        metadata: Dict = None,
        sync_file: bool = True
    ) -> str:
        """
        保存记忆（自动同步到所有存储）
        
        Args:
            key: 唯一键名
            value: 内容
            memory_type: 记忆类型
            tags: 标签
            metadata: 元数据
            sync_file: 是否同步到文件
        
        Returns:
            str: 记忆 ID
        """
        # 转换 memory_type
        mem_type = MemoryType(memory_type) if isinstance(memory_type, str) else memory_type
        
        # 保存到数据库
        memory_id = self.memory_storage.save(
            key=key,
            value=value,
            memory_type=mem_type,
            tags=tags or [],
            metadata=metadata or {}
        )
        
        # 同步到文件（备份）
        if sync_file:
            self._sync_to_file(key, value, memory_type, tags, metadata)
        
        return memory_id
    
    def load(
        self,
        key: str = None,
        memory_id: str = None,
        tags: List[str] = None,
        memory_type: str = None,
        limit: int = 100
    ) -> List[Dict]:
        """加载记忆（优先从数据库）"""
        mem_type = MemoryType(memory_type) if memory_type else None
        return self.memory_storage.load(
            key=key,
            memory_id=memory_id,
            tags=tags,
            memory_type=mem_type,
            limit=limit
        )
    
    def search(
        self,
        query: str = None,
        key: str = None,
        tags: List[str] = None,
        memory_type: str = None,
        mode: str = "hybrid",
        limit: int = 10
    ) -> List[Dict]:
        """
        搜索记忆（混合搜索）
        
        Args:
            query: 语义搜索查询
            key: 精确键名
            tags: 标签过滤
            memory_type: 类型过滤
            mode: 搜索模式 (exact/semantic/hybrid)
            limit: 返回数量
        
        Returns:
            List[Dict]: 搜索结果
        """
        search_mode = SearchMode(mode)
        mem_type = MemoryType(memory_type) if memory_type else None
        
        return self.memory_storage.search(
            query=query,
            key=key,
            tags=tags,
            memory_type=mem_type,
            mode=search_mode,
            limit=limit
        )
    
    def delete(
        self,
        key: str = None,
        memory_id: str = None,
        tags: List[str] = None,
        memory_type: str = None
    ) -> int:
        """删除记忆"""
        mem_type = MemoryType(memory_type) if memory_type else None
        count = self.memory_storage.delete(
            key=key,
            memory_id=memory_id,
            tags=tags,
            memory_type=mem_type
        )
        
        # 从文件删除（如果存在）
        if key:
            self._delete_from_file(key)
        
        return count
    
    def sync_to_file(self, memory_type: str = None) -> int:
        """
        同步所有数据到文件
        
        Args:
            memory_type: 可选，只同步特定类型
        
        Returns:
            int: 同步的记录数
        """
        count = 0
        
        # 加载所有数据
        records = self.load(memory_type=memory_type, limit=9999)
        
        for record in records:
            key = record.get('key', record.get('id', 'unknown'))
            value = record.get('value', '')
            mem_type = record.get('memory_type', 'custom')
            tags = record.get('tags', [])
            metadata = record.get('metadata', {})
            
            self._sync_to_file(key, value, mem_type, tags, metadata)
            count += 1
        
        return count
    
    def _sync_to_file(
        self,
        key: str,
        value: Any,
        memory_type: str,
        tags: List[str],
        metadata: Dict
    ):
        """同步单条记录到文件"""
        date = datetime.now().strftime('%Y-%m-%d')
        
        # 根据类型选择文件
        if memory_type == 'conversation':
            file_path = os.path.join(self.memory_path, f'{date}.md')
        elif memory_type == 'decision':
            file_path = os.path.join(self.memory_path, 'decisions.md')
        else:
            file_path = os.path.join(self.memory_path, f'{date}.md')
        
        # 追加到文件
        content = self._format_for_file(key, value, memory_type, tags, metadata)
        
        with open(file_path, 'a', encoding='utf-8') as f:
            f.write(content)
    
    def _delete_from_file(self, key: str):
        """从文件删除（简单实现：标记删除）"""
        # TODO: 实现完整的文件删除
        pass
    
    def _format_for_file(
        self,
        key: str,
        value: Any,
        memory_type: str,
        tags: List[str],
        metadata: Dict
    ) -> str:
        """格式化记录为 Markdown"""
        timestamp = datetime.now().isoformat()
        
        # 序列化 value
        if not isinstance(value, str):
            value = json.dumps(value, ensure_ascii=False, indent=2)
        
        return f"""---
date: {timestamp}
key: {key}
type: {memory_type}
tags: {', '.join(tags)}
---

## {key}

```
{value}
```

"""
    
    def stats(self) -> Dict:
        """获取统计信息"""
        db_stats = self.memory_storage.stats()
        
        # 统计文件
        file_count = len([f for f in os.listdir(self.memory_path) if f.endswith('.md')])
        
        return {
            **db_stats,
            "file_count": file_count,
            "memory_path": self.memory_path
        }
    
    def close(self):
        """关闭连接"""
        self.memory_storage.close()


# 全局实例
_unified_memory = None

def get_unified_memory(base_path: str = None) -> UnifiedMemory:
    """获取统一记忆实例"""
    global _unified_memory
    if _unified_memory is None:
        _unified_memory = UnifiedMemory(base_path)
    return _unified_memory


# 便捷函数
def save_to_memory(key: str, value: Any, **kwargs) -> str:
    """保存到记忆"""
    return get_unified_memory().save(key, value, **kwargs)

def load_from_memory(key: str = None, **kwargs) -> List[Dict]:
    """从记忆加载"""
    return get_unified_memory().load(key=key, **kwargs)

def search_memory_v2(query: str = None, **kwargs) -> List[Dict]:
    """搜索记忆"""
    return get_unified_memory().search(query=query, **kwargs)
