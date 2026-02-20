"""
基础 CRUD API - 记忆管理系统
统一接口：save(), load(), delete(), search()

支持：
- SQLite 持久化存储 (结构化数据)
- 向量存储 (语义搜索)
- 原子操作 (事务支持)
- 多条件搜索
"""
import json
import os
import sqlite3
import uuid
import threading
from datetime import datetime
from typing import Any, Dict, List, Optional, Union
from enum import Enum

# 导入向量存储 (处理相对/绝对导入)
try:
    from . import chromadb_storage as vector_store
except ImportError:
    import chromadb_storage as vector_store


class SearchMode(Enum):
    """搜索模式"""
    EXACT = "exact"      # 精确匹配
    SEMANTIC = "semantic"  # 语义搜索 (向量)
    HYBRID = "hybrid"    # 混合搜索


class MemoryType(Enum):
    """记忆类型"""
    CONVERSATION = "conversation"
    KNOWLEDGE = "knowledge"
    GOAL = "goal"
    TASK = "task"
    DECISION = "decision"
    CUSTOM = "custom"


class Transaction:
    """事务管理器 (线程安全)"""
    
    def __init__(self, storage: 'MemoryStorage'):
        self.storage = storage
        self.operations: List[Dict] = []
        self._lock = threading.Lock()
    
    def add_operation(self, op_type: str, **kwargs):
        """添加操作到事务"""
        self.operations.append({
            "type": op_type,
            "timestamp": datetime.now().isoformat(),
            **kwargs
        })
    
    def commit(self) -> bool:
        """提交事务"""
        with self._lock:
            try:
                for op in self.operations:
                    if op["type"] == "save":
                        self.storage._internal_save(**op["data"])
                    elif op["type"] == "delete":
                        self.storage._internal_delete(**op["data"])
                self.operations.clear()
                return True
            except Exception as e:
                self.operations.clear()
                raise e
    
    def rollback(self):
        """回滚事务"""
        self.operations.clear()


class MemoryStorage:
    """
    统一记忆存储 API
    
    同时维护：
    - SQLite: 快速键值查询、精确匹配
    - 向量存储: 语义搜索、相似度匹配
    """
    
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls, db_path: str = None):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._initialized = False
        return cls._instance
    
    def __init__(self, db_path: str = None):
        if self._initialized:
            return
        
        self.base_path = os.path.dirname(os.path.dirname(__file__))
        self.db_path = db_path or os.path.join(self.base_path, ".memory/_index/memory.db")
        self.vector_path = os.path.join(self.base_path, ".memory/.memory/vector_db")
        
        # 初始化 SQLite
        self._init_sqlite()
        
        # 初始化向量存储
        self.vector_db = vector_store.VectorStorage(self.vector_path)
        
        self._initialized = True
    
    def _init_sqlite(self):
        """初始化 SQLite 数据库"""
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        
        self.conn = sqlite3.connect(self.db_path, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        self.conn.execute("PRAGMA journal_mode=WAL")
        
        # 创建表
        self.conn.executescript("""
            CREATE TABLE IF NOT EXISTS memories (
                id TEXT PRIMARY KEY,
                key TEXT UNIQUE NOT NULL,
                value TEXT,
                memory_type TEXT DEFAULT 'custom',
                tags TEXT,
                metadata TEXT,
                created_at TEXT,
                updated_at TEXT
            );
            
            CREATE TABLE IF NOT EXISTS tags (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                memory_id TEXT,
                tag TEXT,
                FOREIGN KEY (memory_id) REFERENCES memories(id),
                UNIQUE(memory_id, tag)
            );
            
            CREATE INDEX IF NOT EXISTS idx_memories_key ON memories(key);
            CREATE INDEX IF NOT EXISTS idx_memories_type ON memories(memory_type);
            CREATE INDEX IF NOT EXISTS idx_tags_tag ON tags(tag);
        """)
        self.conn.commit()
    
    # ==================== CRUD 基础操作 ====================
    
    def save(
        self,
        key: str,
        value: Any,
        tags: List[str] = None,
        memory_type: Union[MemoryType, str] = MemoryType.CUSTOM,
        metadata: Dict = None,
        mode: SearchMode = SearchMode.HYBRID
    ) -> str:
        """
        保存记忆
        
        Args:
            key: 唯一键名
            value: 记忆内容 (任意类型，会自动 JSON 序列化)
            tags: 标签列表
            memory_type: 记忆类型
            mode: 搜索模式 (影响向量存储)
        
        Returns:
            str: 记忆 ID
        """
        return self._internal_save(
            key=key,
            value=value,
            tags=tags or [],
            memory_type=memory_type,
            metadata=metadata or {},
            mode=mode
        )
    
    def _internal_save(
        self,
        key: str,
        value: Any,
        tags: List[str],
        memory_type: Union[MemoryType, str],
        metadata: Dict,
        mode: SearchMode
    ) -> str:
        """内部保存 (用于事务)"""
        memory_id = str(uuid.uuid4())
        timestamp = datetime.now().isoformat()
        
        # 处理 memory_type
        if isinstance(memory_type, MemoryType):
            mem_type = memory_type.value
        else:
            mem_type = memory_type
        
        # 序列化 value
        if not isinstance(value, str):
            value = json.dumps(value, ensure_ascii=False, default=str)
        
        # 保存到 SQLite
        self.conn.execute("""
            INSERT OR REPLACE INTO memories (id, key, value, memory_type, tags, metadata, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            memory_id,
            key,
            value,
            mem_type,
            json.dumps(tags, ensure_ascii=False),
            json.dumps(metadata, ensure_ascii=False),
            timestamp,
            timestamp
        ))
        
        # 保存标签
        for tag in tags:
            try:
                self.conn.execute(
                    "INSERT OR IGNORE INTO tags (memory_id, tag) VALUES (?, ?)",
                    (memory_id, tag)
                )
            except Exception:
                pass
        
        self.conn.commit()
        
        # 保存到向量存储 (使用 key 和 value 作为内容)
        vector_metadata = {
            "key": key,
            "type": mem_type,
            "tags": tags,
            **metadata
        }
        self.vector_db.add(
            collection="memories",
            doc_id=memory_id,
            document=f"{key}: {value[:500]}",  # 截断避免过长
            metadata=vector_metadata
        )
        
        return memory_id
    
    def load(
        self,
        key: str = None,
        memory_id: str = None,
        tags: List[str] = None,
        memory_type: Union[MemoryType, str] = None,
        limit: int = 100
    ) -> List[Dict]:
        """
        加载记忆
        
        Args:
            key: 按键名精确查找
            memory_id: 按 ID 查找
            tags: 按标签筛选 (多标签为 AND)
            memory_type: 按类型筛选
            limit: 返回数量限制
        
        Returns:
            List[Dict]: 记忆列表
        """
        query = "SELECT * FROM memories WHERE 1=1"
        params = []
        
        if key:
            query += " AND key = ?"
            params.append(key)
        
        if memory_id:
            query += " AND id = ?"
            params.append(memory_id)
        
        if memory_type:
            if isinstance(memory_type, MemoryType):
                mem_type = memory_type.value
            else:
                mem_type = memory_type
            query += " AND memory_type = ?"
            params.append(mem_type)
        
        query += f" ORDER BY updated_at DESC LIMIT ?"
        params.append(limit)
        
        cursor = self.conn.execute(query, params)
        results = []
        
        for row in cursor.fetchall():
            memory = dict(row)
            memory["tags"] = json.loads(memory["tags"] or "[]")
            memory["metadata"] = json.loads(memory["metadata"] or "{}")
            results.append(memory)
        
        # 如果指定了 tags，进行过滤
        if tags:
            results = [r for r in results if all(t in r["tags"] for t in tags)]
        
        return results
    
    def delete(
        self,
        key: str = None,
        memory_id: str = None,
        tags: List[str] = None,
        memory_type: Union[MemoryType, str] = None
    ) -> int:
        """
        删除记忆
        
        Args:
            key: 按键名删除
            memory_id: 按 ID 删除
            tags: 按标签删除 (多标签为 AND)
            memory_type: 按类型删除
        
        Returns:
            int: 删除的记录数
        """
        return self._internal_delete(
            key=key,
            memory_id=memory_id,
            tags=tags,
            memory_type=memory_type
        )
    
    def _internal_delete(
        self,
        key: str = None,
        memory_id: str = None,
        tags: List[str] = None,
        memory_type: Union[MemoryType, str] = None
    ) -> int:
        """内部删除 (用于事务)"""
        # 先获取要删除的 ID
        query = "SELECT id, key FROM memories WHERE 1=1"
        params = []
        
        if key:
            query += " AND key = ?"
            params.append(key)
        
        if memory_id:
            query += " AND id = ?"
            params.append(memory_id)
        
        if memory_type:
            if isinstance(memory_type, MemoryType):
                mem_type = memory_type.value
            else:
                mem_type = memory_type
            query += " AND memory_type = ?"
            params.append(mem_type)
        
        cursor = self.conn.execute(query, params)
        to_delete = cursor.fetchall()
        
        if not to_delete:
            return 0
        
        ids_to_delete = [row["id"] for row in to_delete]
        
        # 从向量存储删除
        for mem_id in ids_to_delete:
            try:
                self.vector_db.delete("memories", mem_id)
            except Exception:
                pass
        
        # 从 SQLite 删除
        placeholders = ",".join("?" * len(ids_to_delete))
        self.conn.execute(f"DELETE FROM tags WHERE memory_id IN ({placeholders})", ids_to_delete)
        self.conn.execute(f"DELETE FROM memories WHERE id IN ({placeholders})", ids_to_delete)
        self.conn.commit()
        
        return len(ids_to_delete)
    
    # ==================== 搜索操作 ====================
    
    def search(
        self,
        query: str = None,
        key: str = None,
        tags: List[str] = None,
        memory_type: Union[MemoryType, str] = None,
        mode: SearchMode = SearchMode.HYBRID,
        limit: int = 10
    ) -> List[Dict]:
        """
        搜索记忆
        
        Args:
            query: 语义搜索查询 (mode 为 SEMANTIC 或 HYBRID 时使用)
            key: 按键名搜索 (支持 LIKE)
            tags: 按标签筛选
            memory_type: 按类型筛选
            mode: 搜索模式
                - EXACT: 精确匹配 (SQL LIKE)
                - SEMANTIC: 语义搜索 (向量相似度)
                - HYBRID: 混合搜索 (结合两种)
            limit: 返回数量限制
        
        Returns:
            List[Dict]: 搜索结果列表 (包含 similarity 字段)
        """
        results = []
        
        if mode == SearchMode.EXACT or (mode == SearchMode.HYBRID and query is None):
            # SQL 精确/模糊搜索
            sql_query = "SELECT * FROM memories WHERE 1=1"
            params = []
            
            if key:
                sql_query += " AND key LIKE ?"
                params.append(f"%{key}%")
            
            if query:
                sql_query += " AND (value LIKE ? OR key LIKE ?)"
                params.extend([f"%{query}%", f"%{query}%"])
            
            if memory_type:
                if isinstance(memory_type, MemoryType):
                    mem_type = memory_type.value
                else:
                    mem_type = memory_type
                sql_query += " AND memory_type = ?"
                params.append(mem_type)
            
            sql_query += " ORDER BY updated_at DESC LIMIT ?"
            params.append(limit)
            
            cursor = self.conn.execute(sql_query, params)
            for row in cursor.fetchall():
                memory = dict(row)
                memory["tags"] = json.loads(memory["tags"] or "[]")
                memory["metadata"] = json.loads(memory["metadata"] or "{}")
                memory["similarity"] = 1.0  # 精确匹配
                results.append(memory)
        
        if mode in [SearchMode.SEMANTIC, SearchMode.HYBRID] and query:
            # 向量语义搜索
            vector_results = self.vector_db.search(
                collection="memories",
                query=query,
                n_results=limit
            )
            
            if vector_results and vector_results.get("ids"):
                for i, doc_id in enumerate(vector_results["ids"]):
                    # 计算相似度 (距离转相似度)
                    distance = vector_results["distances"][i]
                    similarity = max(0, 1 - distance / 2)  # 近似转换
                    
                    # 加载完整记录
                    full_records = self.load(memory_id=doc_id, limit=1)
                    if full_records:
                        record = full_records[0]
                        record["similarity"] = similarity
                        
                        # 去重
                        if record["id"] not in [r["id"] for r in results]:
                            results.append(record)
        
        # Tag 过滤
        if tags:
            results = [r for r in results if all(t in r["tags"] for t in tags)]
        
        # 排序: 混合模式下按相似度排序
        if mode == SearchMode.HYBRID and query:
            results.sort(key=lambda x: x.get("similarity", 0), reverse=True)
        
        return results[:limit]
    
    # ==================== 原子操作 ====================
    
    def begin_transaction(self) -> Transaction:
        """开始事务"""
        return Transaction(self)
    
    def atomic_save(self, *args, **kwargs) -> str:
        """单条原子保存"""
        return self.save(*args, **kwargs)
    
    def atomic_delete(self, *args, **kwargs) -> int:
        """单条原子删除"""
        return self.delete(*args, **kwargs)
    
    # ==================== 统计信息 ====================
    
    def stats(self) -> Dict:
        """获取存储统计"""
        cursor = self.conn.execute("SELECT memory_type, COUNT(*) FROM memories GROUP BY memory_type")
        type_counts = dict(cursor.fetchall())
        
        cursor = self.conn.execute("SELECT COUNT(DISTINCT tag) FROM tags")
        tag_count = cursor.fetchone()[0]
        
        return {
            "total_memories": sum(type_counts.values()),
            "by_type": type_counts,
            "total_tags": tag_count,
            "db_path": self.db_path
        }
    
    def close(self):
        """关闭连接"""
        if self.conn:
            self.conn.close()


# 全局实例
memory_storage = None

def get_memory_storage(db_path: str = None) -> MemoryStorage:
    """获取记忆存储实例"""
    global memory_storage
    if memory_storage is None:
        memory_storage = MemoryStorage(db_path)
    # 检查连接是否有效
    elif memory_storage.conn is None or not memory_storage.conn:
        memory_storage = MemoryStorage(db_path)
        memory_storage = MemoryStorage(db_path)
    return memory_storage

# 便捷函数
def save_memory(key: str, value: Any, tags: List[str] = None, **kwargs) -> str:
    """保存记忆"""
    return get_memory_storage().save(key, value, tags, **kwargs)

def load_memory(key: str = None, memory_id: str = None, tags: List[str] = None, **kwargs) -> List[Dict]:
    """加载记忆"""
    return get_memory_storage().load(key=key, memory_id=memory_id, tags=tags, **kwargs)

def delete_memory(key: str = None, memory_id: str = None, tags: List[str] = None, **kwargs) -> int:
    """删除记忆"""
    return get_memory_storage().delete(key=key, memory_id=memory_id, tags=tags, **kwargs)

def search_memory(query: str = None, key: str = None, tags: List[str] = None, mode: str = "hybrid", **kwargs) -> List[Dict]:
    """搜索记忆"""
    search_mode = SearchMode(mode.lower()) if isinstance(mode, str) else mode
    return get_memory_storage().search(query=query, key=key, tags=tags, mode=search_mode, **kwargs)
