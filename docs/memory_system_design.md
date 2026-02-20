# OpenClaw 持久化记忆系统整合方案

**项目**: OpenClaw 持久化记忆系统  
**版本**: v2.0（SQLite + ChromaDB 整合版）  
**创建日期**: 2026-02-20  
**技术栈**: SQLite + ChromaDB  
**负责人**: RUNBOT-ARC（青岩）项目总监

---

## 1. 技术架构概述

### 1.1 设计理念

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         持久化记忆系统架构                               │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  ┌─────────────────┐     ┌─────────────────────────────────────────┐   │
│  │   应用层接口     │     │           存储层（双引擎协同）           │   │
│  │                 │     │                                         │   │
│  │  Memory API     │────▶│  ┌─────────────┐    ┌──────────────┐  │   │
│  │  - save()       │     │  │   SQLite    │    │   ChromaDB    │  │   │
│  │  - load()       │     │  │             │    │              │  │   │
│  │  - search()     │     │  │ 结构化数据   │    │ 向量嵌入      │  │   │
│  │  - semantic()   │     │  │ 元数据       │    │ 语义搜索      │  │   │
│  │  - tag()        │     │  │ 标签系统     │    │ 相似度检索    │  │   │
│  │  - query()      │     │  │ 索引         │    │              │  │   │
│  └─────────────────┘     │  └─────────────┘    └──────────────┘  │   │
│                           └─────────────────────────────────────────┘   │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

### 1.2 存储分工

| 数据类型 | 存储引擎 | 用途 |
|----------|----------|------|
| **结构化数据** | SQLite | 用户信息、会话状态、配置项 |
| **元数据** | SQLite | 创建时间、更新时间、来源、版本 |
| **标签/分类** | SQLite | 标签体系、分类体系、关系映射 |
| **索引** | SQLite | 全文索引、属性索引、复合索引 |
| **向量嵌入** | ChromaDB | 语义向量、文本嵌入、特征向量 |
| **语义搜索** | ChromaDB | 相似度检索、语义查询、聚类分析 |

### 1.3 数据流转

```
┌─────────────┐     ┌─────────────────┐     ┌─────────────────┐
│   写入流程   │     │   查询流程      │     │   同步流程      │
├─────────────┤     ├─────────────────┤     ├─────────────────┤
│ 1. 接收数据  │     │ 1. 解析查询请求  │     │ 1. SQLite 写入  │
│ 2. 提取元数据│     │ 2. 结构化查询    │     │ 2. 生成向量      │
│ 3. 生成向量  │     │    (SQLite)     │     │ 3. ChromaDB 写入 │
│ 4. 双重存储  │     │ 3. 语义查询      │     │ 4. 建立关联ID   │
│ 5. 建立关联  │     │    (ChromaDB)   │     │                 │
│             │     │ 4. 合并结果      │     │                 │
└─────────────┘     └─────────────────┘     └─────────────────┘
```

---

## 2. SQLite 模块设计

### 2.1 数据库结构

```sql
-- 记忆主表
CREATE TABLE memories (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    key VARCHAR(255) UNIQUE NOT NULL,
    value TEXT,                    -- JSON 存储任意类型
    value_type VARCHAR(50),        -- 类型标识 (str, int, dict, list, etc.)
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    expire_at DATETIME,            -- 过期时间
    source VARCHAR(255),           -- 数据来源
    version INTEGER DEFAULT 1,     -- 版本号
    metadata TEXT                  -- 额外元数据 (JSON)
);

-- 标签表
CREATE TABLE tags (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(100) UNIQUE NOT NULL,
    color VARCHAR(7),              -- 十六进制颜色
    description TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- 记忆-标签关联表
CREATE TABLE memory_tags (
    memory_id INTEGER,
    tag_id INTEGER,
    PRIMARY KEY (memory_id, tag_id),
    FOREIGN KEY (memory_id) REFERENCES memories(id) ON DELETE CASCADE,
    FOREIGN KEY (tag_id) REFERENCES tags(id) ON DELETE CASCADE
);

-- 向量索引表（关联 ChromaDB）
CREATE TABLE vector_index (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    memory_id INTEGER UNIQUE NOT NULL,
    chroma_id VARCHAR(255),        -- ChromaDB 文档 ID
    embedding_model VARCHAR(100),  -- 使用的嵌入模型
    vector_dim INTEGER,            -- 向量维度
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (memory_id) REFERENCES memories(id) ON DELETE CASCADE
);

-- 全文索引表（FTS5）
CREATE VIRTUAL TABLE memories_fts USING fts5(
    key, value, content='memories', content_rowid='id'
);

-- 索引优化
CREATE INDEX idx_memories_key ON memories(key);
CREATE INDEX idx_memories_expire ON memories(expire_at);
CREATE INDEX idx_memories_source ON memories(source);
CREATE INDEX idx_tags_name ON tags(name);
CREATE INDEX idx_memory_tags_tag ON memory_tags(tag_id);
```

### 2.2 核心功能

```python
# sqlite_store.py - SQLite 存储模块

import sqlite3
import json
import threading
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple
from contextlib import contextmanager
from pathlib import Path


class SQLiteStore:
    """
    SQLite 结构化数据存储
    负责：结构化数据、元数据、标签、索引
    """

    def __init__(self, db_path: str = "./data/memory/memory.db"):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._lock = threading.Lock()
        self._init_db()

    def _init_db(self):
        """初始化数据库表结构"""
        with self._get_conn() as conn:
            conn.executescript('''
                -- 记忆主表
                CREATE TABLE IF NOT EXISTS memories (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    key VARCHAR(255) UNIQUE NOT NULL,
                    value TEXT,
                    value_type VARCHAR(50) DEFAULT 'str',
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    expire_at DATETIME,
                    source VARCHAR(255),
                    version INTEGER DEFAULT 1,
                    metadata TEXT
                );

                -- 标签表
                CREATE TABLE IF NOT EXISTS tags (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name VARCHAR(100) UNIQUE NOT NULL,
                    color VARCHAR(7),
                    description TEXT,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                );

                -- 记忆-标签关联表
                CREATE TABLE IF NOT EXISTS memory_tags (
                    memory_id INTEGER,
                    tag_id INTEGER,
                    PRIMARY KEY (memory_id, tag_id),
                    FOREIGN KEY (memory_id) REFERENCES memories(id) ON DELETE CASCADE,
                    FOREIGN KEY (tag_id) REFERENCES tags(id) ON DELETE CASCADE
                );

                -- 向量索引表
                CREATE TABLE IF NOT EXISTS vector_index (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    memory_id INTEGER UNIQUE NOT NULL,
                    chroma_id VARCHAR(255),
                    embedding_model VARCHAR(100),
                    vector_dim INTEGER,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (memory_id) REFERENCES memories(id) ON DELETE CASCADE
                );

                -- FTS5 全文索引
                CREATE VIRTUAL TABLE IF NOT EXISTS memories_fts USING fts5(
                    key, value, content='memories', content_rowid='id', tokenize='porter'
                );

                -- 触发器：自动更新 FTS
                CREATE TRIGGER IF NOT EXISTS memories_ai AFTER INSERT ON memories BEGIN
                    INSERT INTO memories_fts(rowid, key, value) VALUES (new.id, new.key, new.value);
                END;
                CREATE TRIGGER IF NOT EXISTS memories_ad AFTER DELETE ON memories BEGIN
                    INSERT INTO memories_fts(memories_fts, rowid, key, value) VALUES ('delete', old.id, old.key, old.value);
                END;

                -- 索引
                CREATE INDEX IF NOT EXISTS idx_memories_key ON memories(key);
                CREATE INDEX IF NOT EXISTS idx_memories_expire ON memories(expire_at);
                CREATE INDEX IF NOT EXISTS idx_tags_name ON tags(name);
            ''')

    @contextmanager
    def _get_conn(self):
        """获取数据库连接"""
        conn = sqlite3.connect(str(self.db_path), timeout=30)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()

    # ============ 基础 CRUD ============

    def save(self, key: str, value: Any, 
             expire_seconds: Optional[int] = None,
             source: Optional[str] = None,
             metadata: Optional[Dict] = None,
             tags: Optional[List[str]] = None) -> bool:
        """保存记忆"""
        with self._lock:
            try:
                json_value = json.dumps(value, ensure_ascii=False)
                value_type = type(value).__name__
                expire_at = None
                if expire_seconds:
                    expire_at = datetime.now().timestamp() + expire_seconds

                with self._get_conn() as conn:
                    # 检查是否存在
                    existing = conn.execute(
                        'SELECT id, version FROM memories WHERE key = ?', (key,)
                    ).fetchone()

                    if existing:
                        # 更新
                        conn.execute('''
                            UPDATE memories SET
                                value = ?, value_type = ?, updated_at = CURRENT_TIMESTAMP,
                                expire_at = ?, source = ?, version = version + 1,
                                metadata = ? WHERE key = ?
                        ''', (json_value, value_type, expire_at, source,
                              json.dumps(metadata) if metadata else None, key))
                        memory_id = existing['id']
                    else:
                        # 插入
                        cursor = conn.execute('''
                            INSERT INTO memories (key, value, value_type, expire_at, source, metadata)
                            VALUES (?, ?, ?, ?, ?, ?)
                        ''', (key, json_value, value_type, expire_at, source,
                              json.dumps(metadata) if metadata else None))
                        memory_id = cursor.lastrowid

                    # 处理标签
                    if tags:
                        self._update_tags(conn, memory_id, tags)

                    return True
            except sqlite3.IntegrityError:
                return False
            except Exception as e:
                print(f"[SQLiteStore] 保存失败: {e}")
                return False

    def load(self, key: str) -> Any:
        """加载记忆"""
        with self._get_conn() as conn:
            row = conn.execute(
                'SELECT value, expire_at FROM memories WHERE key = ?', (key,)
            ).fetchone()

            if not row:
                return None

            # 检查过期
            if row['expire_at']:
                if datetime.now().timestamp() > row['expire_at']:
                    self.delete(key)
                    return None

            try:
                return json.loads(row['value'])
            except json.JSONDecodeError:
                return row['value']

    def load_with_meta(self, key: str) -> Optional[Dict]:
        """加载记忆（含元数据）"""
        with self._get_conn() as conn:
            row = conn.execute('''
                SELECT m.*, GROUP_CONCAT(t.name) as tags
                FROM memories m
                LEFT JOIN memory_tags mt ON m.id = mt.memory_id
                LEFT JOIN tags t ON mt.tag_id = t.id
                WHERE m.key = ?
                GROUP BY m.id
            ''', (key,)).fetchone()

            if not row:
                return None

            # 检查过期
            if row['expire_at']:
                if datetime.now().timestamp() > row['expire_at']:
                    self.delete(key)
                    return None

            return {
                'key': row['key'],
                'value': json.loads(row['value']) if row['value'] else None,
                'value_type': row['value_type'],
                'created_at': row['created_at'],
                'updated_at': row['updated_at'],
                'expire_at': row['expire_at'],
                'source': row['source'],
                'version': row['version'],
                'metadata': json.loads(row['metadata']) if row['metadata'] else {},
                'tags': row['tags'].split(',') if row['tags'] else []
            }

    def delete(self, key: str) -> bool:
        """删除记忆"""
        with self._lock:
            with self._get_conn() as conn:
                result = conn.execute('DELETE FROM memories WHERE key = ?', (key,))
                return result.rowcount > 0

    def exists(self, key: str) -> bool:
        """检查存在"""
        with self._get_conn() as conn:
            row = conn.execute(
                'SELECT 1 FROM memories WHERE key = ? AND (expire_at IS NULL OR expire_at > ?)',
                (key, datetime.now().timestamp())
            ).fetchone()
            return row is not None

    # ============ 标签系统 ============

    def add_tag(self, tag_name: str, color: Optional[str] = None, 
                description: Optional[str] = None) -> bool:
        """添加标签"""
        with self._lock:
            try:
                with self._get_conn() as conn:
                    conn.execute(
                        'INSERT OR IGNORE INTO tags (name, color, description) VALUES (?, ?, ?)',
                        (tag_name, color, description)
                    )
                    return True
            except Exception as e:
                print(f"[SQLiteStore] 添加标签失败: {e}")
                return False

    def tag_memory(self, key: str, tags: List[str]) -> bool:
        """为记忆添加标签"""
        with self._lock:
            with self._get_conn() as conn:
                memory = conn.execute(
                    'SELECT id FROM memories WHERE key = ?', (key,)
                ).fetchone()
                if not memory:
                    return False

                for tag_name in tags:
                    tag = conn.execute(
                        'SELECT id FROM tags WHERE name = ?', (tag_name,)
                    ).fetchone()
                    if not tag:
                        cursor = conn.execute(
                            'INSERT INTO tags (name) VALUES (?)', (tag_name,)
                        )
                        tag_id = cursor.lastrowid
                    else:
                        tag_id = tag['id']

                    try:
                        conn.execute(
                            'INSERT OR IGNORE INTO memory_tags (memory_id, tag_id) VALUES (?, ?)',
                            (memory['id'], tag_id)
                        )
                    except Exception:
                        pass
                return True

    def get_by_tag(self, tag: str) -> List[Dict]:
        """按标签查询"""
        with self._get_conn() as conn:
            rows = conn.execute('''
                SELECT m.*, GROUP_CONCAT(t.name) as tags
                FROM memories m
                JOIN memory_tags mt ON m.id = mt.memory_id
                JOIN tags t ON mt.tag_id = t.id
                WHERE t.name = ? AND (m.expire_at IS NULL OR m.expire_at > ?)
                GROUP BY m.id
            ''', (tag, datetime.now().timestamp())).fetchall()

            return [dict(row) for row in rows]

    # ============ 全文搜索 ============

    def search_fts(self, query: str, limit: int = 10) -> List[Dict]:
        """全文搜索"""
        with self._get_conn() as conn:
            rows = conn.execute('''
                SELECT m.*, bm25(memories_fts) as rank
                FROM memories_fts JOIN memories m ON memories_fts.rowid = m.id
                WHERE memories_fts MATCH ?
                ORDER BY rank
                LIMIT ?
            ''', (query, limit)).fetchall()
            return [dict(row) for row in rows]

    # ============ 查询接口 ============

    def list_keys(self) -> List[str]:
        """列出所有键"""
        with self._get_conn() as conn:
            rows = conn.execute('''
                SELECT key FROM memories 
                WHERE expire_at IS NULL OR expire_at > ?
            ''', (datetime.now().timestamp(),)).fetchall()
            return [row['key'] for row in rows]

    def list_all(self) -> Dict[str, Any]:
        """获取所有"""
        result = {}
        for key in self.list_keys():
            value = self.load(key)
            if value is not None:
                result[key] = value
        return result

    def count(self) -> int:
        """计数"""
        with self._get_conn() as conn:
            return conn.execute('''
                SELECT COUNT(*) FROM memories 
                WHERE expire_at IS NULL OR expire_at > ?
            ''', (datetime.now().timestamp(),)).fetchone()[0]

    def cleanup_expired(self) -> int:
        """清理过期"""
        with self._lock:
            with self._get_conn() as conn:
                result = conn.execute(
                    'DELETE FROM memories WHERE expire_at IS NOT NULL AND expire_at <= ?',
                    (datetime.now().timestamp(),)
                )
                return result.rowcount

    def clear(self) -> int:
        """清空"""
        with self._lock:
            with self._get_conn() as conn:
                conn.execute('DELETE FROM memories')
                conn.execute('DELETE FROM memory_tags')
                conn.execute('DELETE FROM vector_index')
                return 0

    # ============ 辅助方法 ============

    def _update_tags(self, conn, memory_id: int, tags: List[str]):
        """更新标签关联"""
        # 清除旧标签
        conn.execute('DELETE FROM memory_tags WHERE memory_id = ?', (memory_id,))
        # 添加新标签
        for tag_name in tags:
            tag = conn.execute(
                'SELECT id FROM tags WHERE name = ?', (tag_name,)
            ).fetchone()
            if not tag:
                cursor = conn.execute(
                    'INSERT INTO tags (name) VALUES (?)', (tag_name,)
                )
                tag_id = cursor.lastrowid
            else:
                tag_id = tag['id']
            conn.execute(
                'INSERT INTO memory_tags (memory_id, tag_id) VALUES (?, ?)',
                (memory_id, tag_id)
            )

    def get_stats(self) -> Dict:
        """获取统计信息"""
        with self._get_conn() as conn:
            return {
                'total_memories': conn.execute(
                    'SELECT COUNT(*) FROM memories'
                ).fetchone()[0],
                'total_tags': conn.execute(
                    'SELECT COUNT(*) FROM tags'
                ).fetchone()[0],
                'expired_count': conn.execute(
                    'SELECT COUNT(*) FROM memories WHERE expire_at IS NOT NULL AND expire_at <= ?',
                    (datetime.now().timestamp(),)
                ).fetchone()[0]
            }
```

---

## 3. ChromaDB 模块设计

### 3.1 核心功能

```python
# vector_store.py - ChromaDB 向量存储模块

import chromadb
from chromadb.config import Settings
from chromadb.utils import embedding_functions
from typing import Any, Dict, List, Optional, Tuple
import threading
import json


class VectorStore:
    """
    ChromaDB 向量存储
    负责：向量嵌入、语义搜索、相似度检索
    """

    def __init__(self, db_path: str = "./data/memory/vector_db", 
                 embedding_model: str = "all-MiniLM-L6-v2"):
        self.db_path = db_path
        self.embedding_model = embedding_model
        
        # 初始化 ChromaDB
        self.client = chromadb.PersistentClient(
            path=db_path,
            settings=Settings(anonymized_telemetry=False)
        )
        
        # 初始化嵌入函数
        self.embedding_fn = embedding_functions.SentenceTransformerEmbeddingFunction(
            model_name=embedding_model
        )
        
        # 获取或创建集合
        self.collection = self.client.get_or_create_collection(
            name="memories",
            metadata={"description": "OpenClaw Memory Vectors"}
        )
        
        self._lock = threading.Lock()

    def add(self, memory_id: str, text: str, 
            metadata: Optional[Dict] = None) -> bool:
        """
        添加向量

        Args:
            memory_id: 记忆 ID (对应 SQLite 中的 key)
            text: 要嵌入的文本
            metadata: 额外元数据

        Returns:
            bool: 是否成功
        """
        with self._lock:
            try:
                self.collection.add(
                    documents=[text],
                    ids=[memory_id],
                    metadatas=[metadata or {}]
                )
                return True
            except Exception as e:
                print(f"[VectorStore] 添加失败: {e}")
                return False

    def search(self, query: str, n_results: int = 5,
               filters: Optional[Dict] = None) -> List[Dict]:
        """
        语义搜索

        Args:
            query: 查询文本
            n_results: 返回数量
            filters: 过滤条件 (如 {"source": "wechat"})

        Returns:
            List[Dict]: 搜索结果
        """
        try:
            where = filters if filters else None
            
            results = self.collection.query(
                query_texts=[query],
                n_results=n_results,
                where=where,
                include=['documents', 'metadatas', 'distances']
            )

            return [{
                'id': results['ids'][0][i],
                'text': results['documents'][0][i],
                'metadata': results['metadatas'][0][i] if results['metadatas'][0] else {},
                'distance': results['distances'][0][i] if results['distances'] else None,
                'similarity': 1 - results['distances'][0][i] if results['distances'] else None
            } for i in range(len(results['ids'][0]))]
            
        except Exception as e:
            print(f"[VectorStore] 搜索失败: {e}")
            return []

    def delete(self, memory_id: str) -> bool:
        """删除向量"""
        with self._lock:
            try:
                self.collection.delete(ids=[memory_id])
                return True
            except Exception as e:
                print(f"[VectorStore] 删除失败: {e}")
                return False

    def update(self, memory_id: str, text: str,
               metadata: Optional[Dict] = None) -> bool:
        """更新向量"""
        with self._lock:
            try:
                self.collection.update(
                    ids=[memory_id],
                    documents=[text],
                    metadatas=[metadata or {}]
                )
                return True
            except Exception as e:
                print(f"[VectorStore] 更新失败: {e}")
                return False

    def get_by_id(self, memory_id: str) -> Optional[Dict]:
        """按 ID 获取"""
        try:
            results = self.collection.get(
                ids=[memory_id],
                include=['documents', 'metadatas']
            )
            if results['documents']:
                return {
                    'id': memory_id,
                    'text': results['documents'][0],
                    'metadata': results['metadatas'][0] if results['metadatas'] else {}
                }
            return None
        except Exception as e:
            print(f"[VectorStore] 获取失败: {e}")
            return None

    def count(self) -> int:
        """计数"""
        return self.collection.count()

    def clear(self) -> bool:
        """清空集合"""
        with self._lock:
            try:
                self.client.delete_collection("memories")
                self.collection = self.client.get_or_create_collection(
                    name="memories",
                    metadata={"description": "OpenClaw Memory Vectors"}
                )
                return True
            except Exception as e:
                print(f"[VectorStore] 清空失败: {e}")
                return False

    def get_stats(self) -> Dict:
        """统计信息"""
        return {
            'total_vectors': self.count(),
            'embedding_model': self.embedding_model
        }
```

---

## 4. 统一接口层设计

### 4.1 整合架构

```python
# memory_system.py - 统一记忆系统接口

from .sqlite_store import SQLiteStore
from .vector_store import VectorStore
from typing import Any, Dict, List, Optional, Tuple
import threading


class MemorySystem:
    """
    统一记忆系统
    SQLite + ChromaDB 双引擎协同
    """

    def __init__(self, 
                 sqlite_path: str = "./data/memory/memory.db",
                 vector_path: str = "./data/memory/vector_db",
                 embedding_model: str = "all-MiniLM-L6-v2",
                 auto_embed: bool = True):
        """
        初始化记忆系统

        Args:
            sqlite_path: SQLite 数据库路径
            vector_path: ChromaDB 数据路径
            embedding_model: 嵌入模型名称
            auto_embed: 是否自动生成向量
        """
        self.sqlite = SQLiteStore(sqlite_path)
        self.vector = VectorStore(vector_path, embedding_model)
        self.auto_embed = auto_embed
        self._lock = threading.Lock()

    # ============ 统一 CRUD ============

    def save(self, key: str, value: Any,
             expire_seconds: Optional[int] = None,
             source: Optional[str] = None,
             metadata: Optional[Dict] = None,
             tags: Optional[List[str]] = None,
             embed_text: Optional[str] = None) -> bool:
        """
        保存记忆（自动同步到双引擎）

        Args:
            key: 记忆键名
            value: 记忆值
            expire_seconds: 过期时间
            source: 来源
            metadata: 元数据
            tags: 标签列表
            embed_text: 自定义嵌入文本（默认使用 value 的字符串形式）
        """
        with self._lock:
            # 1. 写入 SQLite
            success = self.sqlite.save(
                key=key, value=value,
                expire_seconds=expire_seconds,
                source=source, metadata=metadata,
                tags=tags
            )
            
            if not success:
                return False

            # 2. 生成并写入向量（如果需要）
            if self.auto_embed:
                text_to_embed = embed_text or self._value_to_text(value)
                if text_to_embed:
                    self.vector.add(
                        memory_id=key,
                        text=text_to_embed,
                        metadata={
                            'source': source or 'unknown',
                            'tags': ','.join(tags) if tags else ''
                        }
                    )

            return True

    def load(self, key: str) -> Any:
        """加载记忆"""
        return self.sqlite.load(key)

    def load_with_meta(self, key: str) -> Optional[Dict]:
        """加载记忆（含元数据）"""
        return self.sqlite.load_with_meta(key)

    def delete(self, key: str) -> bool:
        """删除记忆"""
        with self._lock:
            # 同时删除两个引擎
            sqlite_ok = self.sqlite.delete(key)
            vector_ok = self.vector.delete(key)
            return sqlite_ok

    # ============ 查询接口 ============

    def search(self, query: str, 
               limit: int = 5,
               mode: str = "auto") -> List[Dict]:
        """
        搜索记忆

        Args:
            query: 查询内容
            limit: 返回数量
            mode: 搜索模式
                - "auto": 自动选择最佳方式
                - "semantic": 仅语义搜索 (ChromaDB)
                - "keyword": 仅关键词搜索 (SQLite FTS)
                - "hybrid": 混合搜索并合并结果

        Returns:
            List[Dict]: 搜索结果列表
        """
        if mode == "auto":
            # 默认使用混合搜索
            mode = "hybrid"

        results = []

        if mode in ("auto", "semantic", "hybrid"):
            # 语义搜索
            semantic_results = self.vector.search(query, n_results=limit)
            if mode == "semantic":
                results = semantic_results

        if mode in ("auto", "keyword", "hybrid"):
            # 关键词搜索
            keyword_results = self.sqlite.search_fts(query, limit=limit)
            if mode == "keyword":
                results = keyword_results

        if mode == "hybrid":
            # 合并结果
            results = self._merge_search_results(
                semantic=semantic_results,
                keyword=keyword_results,
                query=query,
                limit=limit
            )

        return results

    def search_by_tag(self, tag: str) -> List[Dict]:
        """按标签搜索"""
        return self.sqlite.get_by_tag(tag)

    def list_keys(self) -> List[str]:
        """列出所有键"""
        return self.sqlite.list_keys()

    def list_all(self) -> Dict[str, Any]:
        """获取所有"""
        return self.sqlite.list_all()

    def exists(self, key: str) -> bool:
        """检查存在"""
        return self.sqlite.exists(key)

    # ============ 标签系统 ============

    def add_tag(self, tag_name: str, 
                color: Optional[str] = None,
                description: Optional[str] = None) -> bool:
        """添加标签"""
        return self.sqlite.add_tag(tag_name, color, description)

    def tag_memory(self, key: str, tags: List[str]) -> bool:
        """为记忆添加标签"""
        return self.sqlite.tag_memory(key, tags)

    def get_by_tag(self, tag: str) -> List[Dict]:
        """获取带标签的记忆"""
        return self.sqlite.get_by_tag(tag)

    # ============ 管理功能 ============

    def count(self) -> int:
        """计数"""
        return self.sqlite.count()

    def cleanup_expired(self) -> int:
        """清理过期"""
        count = self.sqlite.cleanup_expired()
        # 清理孤立向量（需要额外维护）
        return count

    def clear(self) -> int:
        """清空"""
        self.vector.clear()
        return self.sqlite.clear()

    def get_stats(self) -> Dict:
        """获取统计信息"""
        return {
            'sql': self.sqlite.get_stats(),
            'vector': self.vector.get_stats()
        }

    # ============ 辅助方法 ============

    def _value_to_text(self, value: Any) -> str:
        """将值转换为可嵌入文本"""
        import json
        if isinstance(value, str):
            return value
        elif isinstance(value, dict):
            return json.dumps(value, ensure_ascii=False)
        elif isinstance(value, list):
            return ' '.join(str(v) for v in value)
        else:
            return str(value)

    def _merge_search_results(self, semantic: List[Dict],
                              keyword: List[Dict],
                              query: str,
                              limit: int) -> List[Dict]:
        """
        混合搜索结果合并

        策略：
        1. 语义搜索权重：基于相似度分数
        2. 关键词搜索权重：基于排名
        3. 合并后重新排序
        """
        # 合并去重
        merged = {}
        
        # 添加语义结果
        for item in semantic:
            key = item['id']
            merged[key] = {
                'id': key,
                'text': item.get('text', ''),
                'metadata': item.get('metadata', {}),
                'source': 'semantic',
                'score': item.get('similarity', 0.5),
                'match_type': ['semantic']
            }
        
        # 添加关键词结果
        for item in keyword:
            key = item['key'] if 'key' in item else item['id']
            if key in merged:
                # 已有，增加匹配类型
                merged[key]['match_type'].append('keyword')
                # 取较高分数
                merged[key]['score'] = max(merged[key]['score'], 0.7)
            else:
                merged[key] = {
                    'id': key,
                    'text': item.get('value', ''),
                    'metadata': {'tags': item.get('tags', '')},
                    'source': 'keyword',
                    'score': 0.7,
                    'match_type': ['keyword']
                }

        # 按分数排序
        results = list(merged.values())
        results.sort(key=lambda x: x['score'], reverse=True)

        return results[:limit]

    # ============ 批量操作 ============

    def sync_to_vector(self, key: str) -> bool:
        """将现有记忆同步到向量库"""
        memory = self.load_with_meta(key)
        if not memory:
            return False
        
        text = self._value_to_text(memory['value'])
        return self.vector.add(
            memory_id=key,
            text=text,
            metadata={
                'source': memory.get('source', 'unknown'),
                'tags': ','.join(memory.get('tags', []))
            }
        )

    def rebuild_vector_index(self, batch_size: int = 100) -> Tuple[int, int]:
        """
        重建向量索引

        Returns:
            Tuple[success_count, fail_count]
        """
        # 清空现有向量
        self.vector.clear()

        # 批量同步
        keys = self.list_keys()
        success = 0
        fail = 0

        for i in range(0, len(keys), batch_size):
            batch = keys[i:i + batch_size]
            for key in batch:
                if self.sync_to_vector(key):
                    success += 1
                else:
                    fail += 1

        return success, fail
```

---

## 5. 便捷接口

```python
# memory便捷函数（与原 persistent_memory.py 兼容）

from .memory_system import MemorySystem

# 默认实例
_default_system: Optional[MemorySystem] = None


def _get_default() -> MemorySystem:
    """获取默认实例"""
    global _default_system
    if _default_system is None:
        _default_system = MemorySystem()
    return _default_system


def save(key: str, value: Any, expire_seconds: Optional[int] = None) -> bool:
    """保存记忆"""
    return _get_default().save(key, value, expire_seconds)


def load(key: str) -> Any:
    """加载记忆"""
    return _get_default().load(key)


def load_with_meta(key: str) -> Optional[Dict]:
    """加载记忆（含元数据）"""
    return _get_default().load_with_meta(key)


def delete(key: str) -> bool:
    """删除记忆"""
    return _get_default().delete(key)


def exists(key: str) -> bool:
    """检查存在"""
    return _get_default().exists(key)


def list_keys() -> List[str]:
    """列出所有键"""
    return _get_default().list_keys()


def list_all() -> Dict[str, Any]:
    """获取所有"""
    return _get_default().list_all()


def search(query: str, limit: int = 5, mode: str = "hybrid") -> List[Dict]:
    """搜索"""
    return _get_default().search(query, limit, mode)


def tag_memory(key: str, tags: List[str]) -> bool:
    """添加标签"""
    return _get_default().tag_memory(key, tags)


def get_by_tag(tag: str) -> List[Dict]:
    """按标签获取"""
    return _get_default().get_by_tag(tag)


def clear() -> int:
    """清空"""
    return _get_default().clear()


def get_stats() -> Dict:
    """统计"""
    return _get_default().get_stats()
```

---

## 6. 存储结构

```
data/memory/
├── memory.db              # SQLite 数据库
│                         #   - memories 表
│                         #   - tags 表
│                         #   - memory_tags 表
│                         #   - vector_index 表
│                         #   - memories_fts (FTS5)
│
└── vector_db/             # ChromaDB 数据目录
    ├── chroma.sqlite3     # ChromaDB 元数据
    └── ...
```

---

## 7. 使用示例

### 7.1 基础用法

```python
from memory_system import MemorySystem, save, load, search

# 创建系统实例
mem = MemorySystem()

# 保存
save("user_name", "张三")
save("user_prefs", {"theme": "dark", "lang": "zh"})

# 加载
name = load("user_name")  # "张三"

# 搜索
results = search("暗色主题")  # 语义搜索
```

### 7.2 带标签

```python
# 添加标签
mem.add_tag("重要", color="#FF0000")
mem.add_tag("用户", color="#00FF00")

# 标记记忆
mem.tag_memory("user_name", ["重要", "用户"])

# 按标签查询
users = mem.get_by_tag("用户")
```

### 7.3 元数据

```python
mem.save(
    key="session_001",
    value={"user": "张三", "action": "login"},
    source="web_app",
    metadata={"ip": "192.168.1.100", "browser": "Chrome"},
    tags=["重要", "会话"]
)

# 获取完整信息
info = mem.load_with_meta("session_001")
