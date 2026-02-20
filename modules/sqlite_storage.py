"""
SQLite Storage Layer - SQLite 存储层
====================================
实现结构化数据存储：对话、目标、标签、元数据
"""

import sqlite3
import json
import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple
from contextlib import contextmanager
from pathlib import Path


class SQLiteStorage:
    """
    SQLite 存储层
    
    核心表结构：
    - memories: 记忆主表
    - conversations: 对话表
    - goals: 目标表
    - tags: 标签表
    - wal_logs: WAL 日志表
    """
    
    def __init__(self, db_path: str = ".memory/memory.db"):
        """
        初始化 SQLite 存储
        
        Args:
            db_path: 数据库文件路径
        """
        self.db_path = db_path
        self._ensure_db_dir()
        self.conn = sqlite3.connect(db_path, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        self._init_tables()
        self._create_indexes()
    
    def _ensure_db_dir(self):
        """确保数据库目录存在"""
        Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)
    
    @contextmanager
    def transaction(self):
        """事务上下文管理器"""
        try:
            yield self.conn.cursor()
            self.conn.commit()
        except Exception as e:
            self.conn.rollback()
            raise e
    
    def _init_tables(self):
        """初始化所有表"""
        cursor = self.conn.cursor()
        
        # 1. memories: 记忆主表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS memories (
                id TEXT PRIMARY KEY,
                content TEXT NOT NULL,
                memory_type TEXT NOT NULL,
                metadata TEXT,
                version INTEGER DEFAULT 1,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                is_archived INTEGER DEFAULT 0
            )
        """)
        
        # 2. conversations: 对话表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS conversations (
                id TEXT PRIMARY KEY,
                memory_id TEXT,
                channel_id TEXT,
                message_count INTEGER DEFAULT 0,
                participants TEXT,
                keywords TEXT,
                is_important INTEGER DEFAULT 0,
                created_at TEXT NOT NULL,
                metadata TEXT,
                FOREIGN KEY (memory_id) REFERENCES memories(id)
            )
        """)
        
        # 3. goals: 目标表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS goals (
                id TEXT PRIMARY KEY,
                title TEXT NOT NULL,
                description TEXT,
                goal_type TEXT NOT NULL,
                period TEXT,
                priority TEXT DEFAULT 'medium',
                status TEXT DEFAULT 'active',
                progress REAL DEFAULT 0.0,
                parent_goal_id TEXT,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                completed_at TEXT,
                metadata TEXT,
                FOREIGN KEY (parent_goal_id) REFERENCES goals(id)
            )
        """)
        
        # 4. goal_milestones: 目标里程碑表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS goal_milestones (
                id TEXT PRIMARY KEY,
                goal_id TEXT NOT NULL,
                title TEXT NOT NULL,
                description TEXT,
                due_date TEXT,
                completed_at TEXT,
                status TEXT DEFAULT 'pending',
                created_at TEXT NOT NULL,
                FOREIGN KEY (goal_id) REFERENCES goals(id)
            )
        """)
        
        # 5. tags: 标签表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS tags (
                id TEXT PRIMARY KEY,
                name TEXT UNIQUE NOT NULL,
                category TEXT,
                aliases TEXT,
                description TEXT,
                color TEXT,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
        """)
        
        # 6. memory_tags: 记忆-标签关联表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS memory_tags (
                memory_id TEXT NOT NULL,
                tag_id TEXT NOT NULL,
                created_at TEXT NOT NULL,
                PRIMARY KEY (memory_id, tag_id),
                FOREIGN KEY (memory_id) REFERENCES memories(id),
                FOREIGN KEY (tag_id) REFERENCES tags(id)
            )
        """)
        
        # 7. checkins: 签到记录表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS checkins (
                id TEXT PRIMARY KEY,
                goal_id TEXT,
                date TEXT NOT NULL,
                progress REAL,
                notes TEXT,
                created_at TEXT NOT NULL,
                FOREIGN KEY (goal_id) REFERENCES goals(id)
            )
        """)
        
        # 8. wal_logs: WAL 日志表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS wal_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                seq TEXT UNIQUE NOT NULL,
                operation TEXT NOT NULL,
                table_name TEXT,
                record_id TEXT,
                data TEXT,
                timestamp TEXT NOT NULL,
                applied INTEGER DEFAULT 0
            )
        """)
        
        # 9. knowledge: 知识条目表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS knowledge (
                id TEXT PRIMARY KEY,
                memory_id TEXT,
                title TEXT NOT NULL,
                category TEXT,
                content TEXT NOT NULL,
                priority TEXT DEFAULT 'medium',
                usage_count INTEGER DEFAULT 0,
                last_used TEXT,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                metadata TEXT,
                FOREIGN KEY (memory_id) REFERENCES memories(id)
            )
        """)
        
        # 10. knowledge_references: 知识引用表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS knowledge_references (
                id TEXT PRIMARY KEY,
                knowledge_id TEXT NOT NULL,
                ref_type TEXT NOT NULL,
                ref_value TEXT NOT NULL,
                created_at TEXT NOT NULL,
                FOREIGN KEY (knowledge_id) REFERENCES knowledge(id)
            )
        """)
        
        self.conn.commit()
        print("✓ 所有表初始化完成")
    
    def _create_indexes(self):
        """创建索引"""
        cursor = self.conn.cursor()
        
        indexes = [
            # memories 索引
            ("idx_memories_type", "memories", "memory_type"),
            ("idx_memories_created", "memories", "created_at"),
            ("idx_memories_archived", "memories", "is_archived"),
            
            # conversations 索引
            ("idx_conversations_channel", "conversations", "channel_id"),
            ("idx_conversations_important", "conversations", "is_important"),
            
            # goals 索引
            ("idx_goals_type", "goals", "goal_type"),
            ("idx_goals_status", "goals", "status"),
            ("idx_goals_priority", "goals", "priority"),
            ("idx_goals_period", "goals", "period"),
            
            # tags 索引
            ("idx_tags_category", "tags", "category"),
            
            # memory_tags 索引
            ("idx_memory_tags_tag", "memory_tags", "tag_id"),
            
            # checkins 索引
            ("idx_checkins_date", "checkins", "date"),
            ("idx_checkins_goal", "checkins", "goal_id"),
            
            # knowledge 索引
            ("idx_knowledge_category", "knowledge", "category"),
            ("idx_knowledge_usage", "knowledge", "usage_count"),
            
            # wal_logs 索引
            ("idx_wal_logs_seq", "wal_logs", "seq"),
            ("idx_wal_logs_applied", "wal_logs", "applied"),
        ]
        
        for idx_name, table, col in indexes:
            try:
                cursor.execute(f"CREATE INDEX IF NOT EXISTS {idx_name} ON {table}({col})")
            except sqlite3.OperationalError:
                pass  # 索引已存在
        
        self.conn.commit()
        print("✓ 索引创建完成")
    
    # ==================== CRUD Operations ====================
    
    # ---------- Memories ----------
    
    def insert_memory(self, content: str, memory_type: str, 
                      metadata: Dict = None) -> str:
        """
        插入记忆
        
        Args:
            content: 记忆内容
            memory_type: 记忆类型 (conversation, goal, knowledge)
            metadata: 元数据
            
        Returns:
            str: 记忆 ID
        """
        memory_id = str(uuid.uuid4())
        now = datetime.now().isoformat()
        
        self.conn.execute(
            """INSERT INTO memories (id, content, memory_type, metadata, created_at, updated_at)
               VALUES (?, ?, ?, ?, ?, ?)""",
            (memory_id, content, memory_type, json.dumps(metadata or {}), now, now)
        )
        self.conn.commit()
        
        return memory_id
    
    def get_memory(self, memory_id: str) -> Optional[Dict]:
        """获取记忆"""
        cursor = self.conn.execute(
            "SELECT * FROM memories WHERE id = ? AND is_archived = 0",
            (memory_id,)
        )
        row = cursor.fetchone()
        if row:
            return dict(row)
        return None
    
    def update_memory(self, memory_id: str, content: str = None, 
                     metadata: Dict = None) -> bool:
        """
        更新记忆
        
        Args:
            memory_id: 记忆 ID
            content: 新内容
            metadata: 新元数据
            
        Returns:
            bool: 是否成功
        """
        now = datetime.now().isoformat()
        
        if content and metadata:
            self.conn.execute(
                """UPDATE memories 
                   SET content = ?, metadata = ?, version = version + 1, updated_at = ?
                   WHERE id = ?""",
                (content, json.dumps(metadata), now, memory_id)
            )
        elif content:
            self.conn.execute(
                """UPDATE memories 
                   SET content = ?, version = version + 1, updated_at = ?
                   WHERE id = ?""",
                (content, now, memory_id)
            )
        elif metadata:
            self.conn.execute(
                """UPDATE memories 
                   SET metadata = ?, version = version + 1, updated_at = ?
                   WHERE id = ?""",
                (json.dumps(metadata), now, memory_id)
            )
        
        self.conn.commit()
        return self.conn.total_changes > 0
    
    def delete_memory(self, memory_id: str, soft: bool = True) -> bool:
        """
        删除记忆
        
        Args:
            memory_id: 记忆 ID
            soft: 软删除（归档）还是硬删除
            
        Returns:
            bool: 是否成功
        """
        if soft:
            self.conn.execute(
                "UPDATE memories SET is_archived = 1, updated_at = ? WHERE id = ?",
                (datetime.now().isoformat(), memory_id)
            )
        else:
            self.conn.execute("DELETE FROM memories WHERE id = ?", (memory_id,))
        
        self.conn.commit()
        return self.conn.total_changes > 0
    
    def search_memories(self, query: str = None, memory_type: str = None,
                       limit: int = 100, offset: int = 0) -> List[Dict]:
        """
        搜索记忆
        
        Args:
            query: 关键词搜索
            memory_type: 按类型过滤
            limit: 结果数量限制
            offset: 偏移量
            
        Returns:
            List[Dict]: 记忆列表
        """
        sql = "SELECT * FROM memories WHERE is_archived = 0"
        params = []
        
        if memory_type:
            sql += " AND memory_type = ?"
            params.append(memory_type)
        
        if query:
            sql += " AND content LIKE ?"
            params.append(f"%{query}%")
        
        sql += " ORDER BY created_at DESC LIMIT ? OFFSET ?"
        params.extend([limit, offset])
        
        cursor = self.conn.execute(sql, params)
        return [dict(row) for row in cursor.fetchall()]
    
    # ---------- Conversations ----------
    
    def insert_conversation(self, channel_id: str, message_count: int = 0,
                           participants: List[str] = None, 
                           keywords: List[str] = None) -> str:
        """
        插入对话
        
        Returns:
            str: 对话 ID
        """
        conversation_id = str(uuid.uuid4())
        now = datetime.now().isoformat()
        
        self.conn.execute(
            """INSERT INTO conversations (id, channel_id, message_count, participants, keywords, created_at)
               VALUES (?, ?, ?, ?, ?, ?)""",
            (conversation_id, channel_id, message_count, 
             json.dumps(participants or []), json.dumps(keywords or []), now)
        )
        self.conn.commit()
        
        return conversation_id
    
    def get_conversation(self, conversation_id: str) -> Optional[Dict]:
        """获取对话"""
        cursor = self.conn.execute(
            "SELECT * FROM conversations WHERE id = ?",
            (conversation_id,)
        )
        row = cursor.fetchone()
        return dict(row) if row else None
    
    def get_conversations_by_channel(self, channel_id: str, 
                                    limit: int = 100) -> List[Dict]:
        """获取指定频道的对话"""
        cursor = self.conn.execute(
            "SELECT * FROM conversations WHERE channel_id = ? ORDER BY created_at DESC LIMIT ?",
            (channel_id, limit)
        )
        return [dict(row) for row in cursor.fetchall()]
    
    # ---------- Goals ----------
    
    def insert_goal(self, title: str, goal_type: str, description: str = None,
                   period: str = None, priority: str = 'medium',
                   parent_goal_id: str = None) -> str:
        """
        插入目标
        
        Returns:
            str: 目标 ID
        """
        goal_id = str(uuid.uuid4())
        now = datetime.now().isoformat()
        
        self.conn.execute(
            """INSERT INTO goals (id, title, description, goal_type, period, priority, parent_goal_id, created_at, updated_at)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (goal_id, title, description, goal_type, period, priority, parent_goal_id, now, now)
        )
        self.conn.commit()
        
        return goal_id
    
    def get_goal(self, goal_id: str) -> Optional[Dict]:
        """获取目标"""
        cursor = self.conn.execute("SELECT * FROM goals WHERE id = ?", (goal_id,))
        row = cursor.fetchone()
        return dict(row) if row else None
    
    def update_goal_progress(self, goal_id: str, progress: float) -> bool:
        """
        更新目标进度
        
        Args:
            goal_id: 目标 ID
            progress: 新进度 (0-100)
            
        Returns:
            bool: 是否成功
        """
        now = datetime.now().isoformat()
        completed_at = now if progress >= 100 else None
        status = 'completed' if progress >= 100 else 'active'
        
        self.conn.execute(
            """UPDATE goals 
               SET progress = ?, status = ?, completed_at = ?, updated_at = ?
               WHERE id = ?""",
            (progress, status, completed_at, now, goal_id)
        )
        self.conn.commit()
        
        return self.conn.total_changes > 0
    
    def get_goals_by_type(self, goal_type: str, status: str = None) -> List[Dict]:
        """
        获取指定类型的目标
        
        Args:
            goal_type: 目标类型 (annual, quarterly, monthly)
            status: 状态过滤
            
        Returns:
            List[Dict]: 目标列表
        """
        sql = "SELECT * FROM goals WHERE goal_type = ?"
        params = [goal_type]
        
        if status:
            sql += " AND status = ?"
            params.append(status)
        
        sql += " ORDER BY created_at DESC"
        
        cursor = self.conn.execute(sql, params)
        return [dict(row) for row in cursor.fetchall()]
    
    # ---------- Milestones ----------
    
    def add_milestone(self, goal_id: str, title: str, 
                     description: str = None, due_date: str = None) -> str:
        """
        添加里程碑
        
        Returns:
            str: 里程碑 ID
        """
        milestone_id = str(uuid.uuid4())
        now = datetime.now().isoformat()
        
        self.conn.execute(
            """INSERT INTO goal_milestones (id, goal_id, title, description, due_date, created_at)
               VALUES (?, ?, ?, ?, ?, ?)""",
            (milestone_id, goal_id, title, description, due_date, now)
        )
        self.conn.commit()
        
        return milestone_id
    
    def complete_milestone(self, milestone_id: str) -> bool:
        """完成里程碑"""
        now = datetime.now().isoformat()
        
        self.conn.execute(
            """UPDATE goal_milestones 
               SET status = 'completed', completed_at = ?
               WHERE id = ?""",
            (now, milestone_id)
        )
        self.conn.commit()
        
        return self.conn.total_changes > 0
    
    def get_milestones(self, goal_id: str) -> List[Dict]:
        """获取目标的所有里程碑"""
        cursor = self.conn.execute(
            "SELECT * FROM goal_milestones WHERE goal_id = ? ORDER BY created_at",
            (goal_id,)
        )
        return [dict(row) for row in cursor.fetchall()]
    
    # ---------- Checkins ----------
    
    def add_checkin(self, goal_id: str, date: str, progress: float, 
                   notes: str = None) -> str:
        """
        添加签到记录
        
        Returns:
            str: 签到 ID
        """
        checkin_id = str(uuid.uuid4())
        now = datetime.now().isoformat()
        
        self.conn.execute(
            """INSERT INTO checkins (id, goal_id, date, progress, notes, created_at)
               VALUES (?, ?, ?, ?, ?, ?)""",
            (checkin_id, goal_id, date, progress, notes, now)
        )
        self.conn.commit()
        
        return checkin_id
    
    def get_checkins(self, goal_id: str = None, date: str = None,
                    limit: int = 100) -> List[Dict]:
        """
        获取签到记录
        
        Args:
            goal_id: 目标 ID 过滤
            date: 日期过滤
            limit: 结果限制
            
        Returns:
            List[Dict]: 签到记录列表
        """
        sql = "SELECT * FROM checkins WHERE 1=1"
        params = []
        
        if goal_id:
            sql += " AND goal_id = ?"
            params.append(goal_id)
        
        if date:
            sql += " AND date = ?"
            params.append(date)
        
        sql += " ORDER BY created_at DESC LIMIT ?"
        params.append(limit)
        
        cursor = self.conn.execute(sql, params)
        return [dict(row) for row in cursor.fetchall()]
    
    # ---------- Tags ----------
    
    def create_tag(self, name: str, category: str = None,
                  aliases: List[str] = None, description: str = None) -> str:
        """
        创建标签
        
        Returns:
            str: 标签 ID
        """
        tag_id = str(uuid.uuid4())
        now = datetime.now().isoformat()
        
        self.conn.execute(
            """INSERT INTO tags (id, name, category, aliases, description, created_at, updated_at)
               VALUES (?, ?, ?, ?, ?, ?, ?)""",
            (tag_id, name, category, json.dumps(aliases or []), description, now, now)
        )
        self.conn.commit()
        
        return tag_id
    
    def get_tag(self, name: str) -> Optional[Dict]:
        """获取标签"""
        cursor = self.conn.execute(
            "SELECT * FROM tags WHERE name = ?",
            (name,)
        )
        row = cursor.fetchone()
        return dict(row) if row else None
    
    def assign_tag(self, memory_id: str, tag_name: str) -> bool:
        """
        分配标签到记忆
        
        Args:
            memory_id: 记忆 ID
            tag_name: 标签名称
            
        Returns:
            bool: 是否成功
        """
        # 获取或创建标签
        tag = self.get_tag(tag_name)
        if not tag:
            tag_id = self.create_tag(tag_name)
        else:
            tag_id = tag['id']
        
        # 检查是否已分配
        cursor = self.conn.execute(
            "SELECT 1 FROM memory_tags WHERE memory_id = ? AND tag_id = ?",
            (memory_id, tag_id)
        )
        if cursor.fetchone():
            return True  # 已存在
        
        # 分配标签
        now = datetime.now().isoformat()
        self.conn.execute(
            "INSERT INTO memory_tags (memory_id, tag_id, created_at) VALUES (?, ?, ?)",
            (memory_id, tag_id, now)
        )
        self.conn.commit()
        
        return True
    
    def remove_tag(self, memory_id: str, tag_name: str) -> bool:
        """移除标签"""
        tag = self.get_tag(tag_name)
        if not tag:
            return False
        
        self.conn.execute(
            "DELETE FROM memory_tags WHERE memory_id = ? AND tag_id = ?",
            (memory_id, tag['id'])
        )
        self.conn.commit()
        
        return self.conn.total_changes > 0
    
    def get_memory_tags(self, memory_id: str) -> List[Dict]:
        """获取记忆的所有标签"""
        cursor = self.conn.execute(
            """SELECT t.* FROM tags t
               JOIN memory_tags mt ON t.id = mt.tag_id
               WHERE mt.memory_id = ?""",
            (memory_id,)
        )
        return [dict(row) for row in cursor.fetchall()]
    
    def get_all_tags(self) -> List[Dict]:
        """获取所有标签"""
        cursor = self.conn.execute("SELECT * FROM tags ORDER BY category, name")
        return [dict(row) for row in cursor.fetchall()]
    
    # ---------- Knowledge ----------
    
    def insert_knowledge(self, title: str, content: str, 
                        category: str = None, priority: str = 'medium') -> str:
        """
        插入知识条目
        
        Returns:
            str: 知识 ID
        """
        knowledge_id = str(uuid.uuid4())
        now = datetime.now().isoformat()
        
        self.conn.execute(
            """INSERT INTO knowledge (id, title, category, content, priority, created_at, updated_at)
               VALUES (?, ?, ?, ?, ?, ?, ?)""",
            (knowledge_id, title, category, content, priority, now, now)
        )
        self.conn.commit()
        
        return knowledge_id
    
    def get_knowledge(self, knowledge_id: str) -> Optional[Dict]:
        """获取知识条目"""
        cursor = self.conn.execute(
            "SELECT * FROM knowledge WHERE id = ?",
            (knowledge_id,)
        )
        row = cursor.fetchone()
        return dict(row) if row else None
    
    def update_knowledge_usage(self, knowledge_id: str) -> bool:
        """更新知识使用次数"""
        self.conn.execute(
            """UPDATE knowledge 
               SET usage_count = usage_count + 1, last_used = ?
               WHERE id = ?""",
            (datetime.now().isoformat(), knowledge_id)
        )
        self.conn.commit()
        
        return self.conn.total_changes > 0
    
    def search_knowledge(self, query: str, category: str = None,
                        limit: int = 100) -> List[Dict]:
        """
        搜索知识条目
        
        Args:
            query: 搜索关键词
            category: 分类过滤
            limit: 结果限制
            
        Returns:
            List[Dict]: 知识条目列表
        """
        sql = "SELECT * FROM knowledge WHERE 1=1"
        params = []
        
        if category:
            sql += " AND category = ?"
            params.append(category)
        
        sql += " AND (title LIKE ? OR content LIKE ?)"
        params.extend([f"%{query}%", f"%{query}%"])
        
        sql += " ORDER BY usage_count DESC, created_at DESC LIMIT ?"
        params.append(limit)
        
        cursor = self.conn.execute(sql, params)
        return [dict(row) for row in cursor.fetchall()]
    
    # ---------- WAL Logs ----------
    
    def log_wal(self, operation: str, table_name: str, 
               record_id: str, data: Dict) -> int:
        """
        记录 WAL 日志
        
        Returns:
            int: 日志序列号
        """
        seq = datetime.now().strftime("%Y%m%d_%H%M%S") + f"_{uuid.uuid4().hex[:8]}"
        timestamp = datetime.now().isoformat()
        
        self.conn.execute(
            """INSERT INTO wal_logs (seq, operation, table_name, record_id, data, timestamp)
               VALUES (?, ?, ?, ?, ?, ?)""",
            (seq, operation, table_name, record_id, json.dumps(data), timestamp)
        )
        self.conn.commit()
        
        return seq
    
    def get_pending_wal_logs(self) -> List[Dict]:
        """获取待应用的 WAL 日志"""
        cursor = self.conn.execute(
            "SELECT * FROM wal_logs WHERE applied = 0 ORDER BY timestamp"
        )
        return [dict(row) for row in cursor.fetchall()]
    
    def mark_wal_applied(self, seq: str) -> bool:
        """标记 WAL 日志已应用"""
        self.conn.execute(
            "UPDATE wal_logs SET applied = 1 WHERE seq = ?",
            (seq,)
        )
        self.conn.commit()
        
        return self.conn.total_changes > 0
    
    # ==================== Utility Methods ====================
    
    def get_stats(self) -> Dict:
        """获取统计信息"""
        stats = {}
        
        tables = ['memories', 'conversations', 'goals', 'tags', 'knowledge']
        for table in tables:
            cursor = self.conn.execute(f"SELECT COUNT(*) as cnt FROM {table}")
            stats[table] = cursor.fetchone()['cnt']
        
        return stats
    
    def close(self):
        """关闭数据库连接"""
        if self.conn:
            self.conn.close()
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
        return False


# ==================== Factory Function ====================

def create_storage(db_path: str = ".memory/memory.db") -> SQLiteStorage:
    """
    创建存储实例
    
    Args:
        db_path: 数据库路径
        
    Returns:
        SQLiteStorage: 存储实例
    """
    return SQLiteStorage(db_path)
