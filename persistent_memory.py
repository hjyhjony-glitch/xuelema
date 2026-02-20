#!/usr/bin/env python3
"""
Persistent Memory System - 本地持久化记忆系统
============================================
纯本地存储、轻量级、函数调用式

使用方法:
    from persistent_memory import Memory

    mem = Memory()
    mem.save("user_name", "张三")
    name = mem.load("user_name")  # "张三"
    mem.delete("user_name")
"""

import json
import os
import threading
from pathlib import Path
from typing import Any, Dict, List, Optional
from datetime import datetime


class Memory:
    """
    本地持久化记忆系统

    特性:
    - 纯本地 JSON 文件存储
    - 线程安全
    - 自动创建存储目录
    - 支持过期时间（可选）
    """

    def __init__(self, storage_path: str = "./data/memory"):
        """
        初始化记忆系统

        Args:
            storage_path: 存储目录路径（相对于工作目录或绝对路径）
        """
        self.storage_path = Path(storage_path)
        self._lock = threading.Lock()
        self._ensure_storage()

    def _ensure_storage(self) -> None:
        """确保存储目录存在"""
        self.storage_path.mkdir(parents=True, exist_ok=True)
        # 创建索引文件
        self._index_file = self.storage_path / "_index.json"

    def _get_file_path(self, key: str) -> Path:
        """获取键对应的文件路径"""
        # 使用安全的文件名（避免路径遍历）
        safe_key = key.replace("/", "_").replace("\\", "_")
        return self.storage_path / f"{safe_key}.json"

    def _load_index(self) -> Dict:
        """加载索引文件"""
        if self._index_file.exists():
            try:
                with open(self._index_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError):
                return {}
        return {}

    def _save_index(self, index: Dict) -> None:
        """保存索引文件"""
        with open(self._index_file, 'w', encoding='utf-8') as f:
            json.dump(index, f, ensure_ascii=False, indent=2)

    def save(self, key: str, value: Any, expire_seconds: Optional[int] = None) -> bool:
        """
        保存记忆

        Args:
            key: 记忆键名
            value: 记忆内容（任意可序列化类型）
            expire_seconds: 过期时间（秒），None 表示永不过期

        Returns:
            bool: 是否保存成功
        """
        with self._lock:
            try:
                file_path = self._get_file_path(key)
                data = {
                    "key": key,
                    "value": value,
                    "created_at": datetime.now().isoformat(),
                    "expire_at": None if expire_seconds is None
                        else datetime.now().timestamp() + expire_seconds
                }

                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(data, f, ensure_ascii=False, indent=2)

                # 更新索引
                index = self._load_index()
                index[key] = {
                    "file": str(file_path),
                    "saved_at": data["created_at"],
                    "expire_at": data["expire_at"]
                }
                self._save_index(index)

                return True
            except Exception as e:
                print(f"[Memory] 保存失败: {e}")
                return False

    def load(self, key: str) -> Any:
        """
        加载记忆

        Args:
            key: 记忆键名

        Returns:
            记忆值，如果不存在或已过期则返回 None
        """
        with self._lock:
            file_path = self._get_file_path(key)

            if not file_path.exists():
                return None

            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)

                # 检查是否过期
                if data.get("expire_at") is not None:
                    if datetime.now().timestamp() > data["expire_at"]:
                        # 已过期，删除并返回 None
                        self.delete(key)
                        return None

                return data.get("value")
            except Exception as e:
                print(f"[Memory] 加载失败: {e}")
                return None

    def load_with_meta(self, key: str) -> Optional[Dict]:
        """
        加载记忆（包含元数据）

        Args:
            key: 记忆键名

        Returns:
            包含 value 和 metadata 的字典，不存在返回 None
        """
        with self._lock:
            file_path = self._get_file_path(key)

            if not file_path.exists():
                return None

            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)

                # 检查是否过期
                if data.get("expire_at") is not None:
                    if datetime.now().timestamp() > data["expire_at"]:
                        self.delete(key)
                        return None

                return {
                    "value": data.get("value"),
                    "created_at": data.get("created_at"),
                    "expire_at": data.get("expire_at")
                }
            except Exception as e:
                print(f"[Memory] 加载失败: {e}")
                return None

    def delete(self, key: str) -> bool:
        """
        删除记忆

        Args:
            key: 记忆键名

        Returns:
            bool: 是否删除成功
        """
        with self._lock:
            file_path = self._get_file_path(key)

            if not file_path.exists():
                return False

            try:
                file_path.unlink()

                # 更新索引
                index = self._load_index()
                index.pop(key, None)
                self._save_index(index)

                return True
            except Exception as e:
                print(f"[Memory] 删除失败: {e}")
                return False

    def exists(self, key: str) -> bool:
        """
        检查记忆是否存在

        Args:
            key: 记忆键名

        Returns:
            bool: 是否存在
        """
        file_path = self._get_file_path(key)
        if not file_path.exists():
            return False

        # 检查是否过期
        meta = self.load_with_meta(key)
        return meta is not None

    def list_keys(self) -> List[str]:
        """
        列出所有记忆键名

        Returns:
            list: 键名列表
        """
        index = self._load_index()
        now = datetime.now().timestamp()

        # 过滤掉过期的
        valid_keys = []
        for key, info in index.items():
            if info.get("expire_at") is None or info["expire_at"] > now:
                valid_keys.append(key)

        return valid_keys

    def list_all(self) -> Dict[str, Any]:
        """
        获取所有记忆

        Returns:
            dict: {键名: 值}
        """
        result = {}
        for key in self.list_keys():
            value = self.load(key)
            if value is not None:
                result[key] = value
        return result

    def clear(self) -> int:
        """
        清空所有记忆

        Returns:
            int: 删除的记忆数量
        """
        with self._lock:
            keys = self.list_keys()
            count = 0
            for key in keys:
                if self.delete(key):
                    count += 1
            return count

    def count(self) -> int:
        """
        获取记忆数量

        Returns:
            int: 记忆数量
        """
        return len(self.list_keys())

    def cleanup_expired(self) -> int:
        """
        清理过期记忆

        Returns:
            int: 清理的记忆数量
        """
        with self._lock:
            index = self._load_index()
            now = datetime.now().timestamp()
            count = 0

            for key, info in list(index.items()):
                if info.get("expire_at") is not None and info["expire_at"] <= now:
                    file_path = Path(info["file"])
                    if file_path.exists():
                        file_path.unlink()
                    index.pop(key, None)
                    count += 1

            self._save_index(index)
            return count


# ============ 便捷函数 ============

_default_memory: Optional[Memory] = None


def _get_default() -> Memory:
    """获取默认记忆实例"""
    global _default_memory
    if _default_memory is None:
        _default_memory = Memory()
    return _default_memory


def save(key: str, value: Any, expire_seconds: Optional[int] = None) -> bool:
    """保存记忆（使用默认实例）"""
    return _get_default().save(key, value, expire_seconds)


def load(key: str) -> Any:
    """加载记忆（使用默认实例）"""
    return _get_default().load(key)


def delete(key: str) -> bool:
    """删除记忆（使用默认实例）"""
    return _get_default().delete(key)


def exists(key: str) -> bool:
    """检查记忆是否存在（使用默认实例）"""
    return _get_default().exists(key)


def list_keys() -> List[str]:
    """列出所有键（使用默认实例）"""
    return _get_default().list_keys()


def list_all() -> Dict[str, Any]:
    """获取所有记忆（使用默认实例）"""
    return _get_default().list_all()


def clear() -> int:
    """清空所有记忆（使用默认实例）"""
    return _get_default().clear()


# ============ CLI 入口 ============

# 尝试从 core 模块导入
_imported_core_modules = None
try:
    import sys
    sys.path.insert(0, str(Path(__file__).parent / ".memory"))
    _imported_core_modules = __import__('core', fromlist=[
        'StorageModule', 'WALHandler', 'BackupManager', 
        'Archiver', 'IndexerModule', 'SearchModule'
    ])
except ImportError:
    _imported_core_modules = None


class PersistentMemory:
    """统一记忆系统 API - 增强版"""

    def __init__(self, root_path: str = "./.memory"):
        self.root = Path(root_path)
        self.root.mkdir(parents=True, exist_ok=True)

        # 从导入的模块获取类
        if _imported_core_modules:
            StorageModule = _imported_core_modules.StorageModule
            WALHandler = _imported_core_modules.WALHandler
            BackupManager = _imported_core_modules.BackupManager
            Archiver = _imported_core_modules.Archiver
            IndexerModule = _imported_core_modules.IndexerModule
            SearchModule = _imported_core_modules.SearchModule

        # 初始化核心模块
        self.storage = StorageModule(str(self.root))
        self.wal = WALHandler(str(self.root / "_index" / "_wal"))
        self.backup = BackupManager(
            str(self.root),
            str(self.root / "_backup")
        )
        self.archiver = Archiver(
            str(self.root),
            str(self.root / "_archive")
        )
        self.indexer = IndexerModule(self.storage)
        self.search = SearchModule(self.storage, self.indexer)

        # 初始化目录结构
        self._init_directories()

    def _init_directories(self):
        """初始化目录结构"""
        dirs = [
            "conversations/raw",
            "conversations/tagged/important",
            "conversations/tagged/decision",
            "conversations/tagged/todo",
            "goals/annual",
            "goals/quarterly",
            "goals/monthly",
            "goals/_闭环/daily_checkin",
            "goals/_闭环/weekly_review",
            "goals/_闭环/monthly_review",
            "goals/_闭环/quarterly_review",
            "goals/_templates",
            "knowledge/topics",
            "knowledge/resources",
            "_index/_wal",
            "_backup/daily",
            "_backup/weekly",
            "_backup/versions",
            "_archive"
        ]
        for d in dirs:
            (self.root / d).mkdir(parents=True, exist_ok=True)

    # ============ Conversation API ============

    def save_conversation(self, date: str, data: Dict) -> bool:
        """保存对话快照"""
        path = f"conversations/raw/{date[:4]}/{date[5:7]}/{date}.json"
        
        # 写入 WAL
        self.wal.log("CREATE", {"path": path, "data": data})
        
        return self.storage.save(path, data)

    def get_conversation(self, date: str) -> Optional[Dict]:
        """获取对话"""
        path = f"conversations/raw/{date[:4]}/{date[5:7]}/{date}.json"
        return self.storage.load(path)

    def tag_conversation(self, date: str, tags: List[str]) -> bool:
        """标记对话"""
        for tag in tags:
            safe_tag = tag.replace("/", "_").replace(" ", "-")
            path = f"conversations/tagged/{safe_tag}/{date}.md"
            
            content = f"""# {date} - Tagged Conversations

**Tags**: {', '.join(tags)}
**Time**: {datetime.now().isoformat()}

## Summary

See: `conversations/raw/{date[:4]}/{date[5:7]}/{date}.json`

"""
            self.storage.save(path, content)
        
        return True

    # ============ Goal API ============

    def save_goal(self, goal_type: str, period: str, data: Dict) -> bool:
        """保存目标"""
        path = f"goals/{goal_type}/{period}.md"
        
        # 转换为 Markdown 格式
        content = self._goal_to_markdown(goal_type, period, data)
        
        # 写入 WAL
        self.wal.log("CREATE", {"path": path, "data": content})
        
        return self.storage.save(path, content)

    def _goal_to_markdown(self, goal_type: str, period: str, data: Dict) -> str:
        """将目标数据转换为 Markdown"""
        lines = [
            f"# {goal_type.title()} Goal: {period}",
            "",
            f"**Created**: {datetime.now().isoformat()}",
            f"**Status**: {data.get('status', 'active')}",
            "",
            "## Goals",
            ""
        ]
        
        for goal in data.get("goals", []):
            lines.append(f"### {goal.get('title', 'Untitled')}")
            lines.append(f"{goal.get('description', '')}")
            lines.append(f"- **Priority**: {goal.get('priority', 'medium')}")
            lines.append(f"- **Progress**: {goal.get('progress', 0)}%")
            lines.append("")
        
        return "\n".join(lines)

    def checkin_daily(self, date: str, progress: int, notes: str) -> bool:
        """每日签到"""
        data = {
            "date": date,
            "progress": progress,
            "notes": notes,
            "timestamp": datetime.now().isoformat()
        }
        path = f"goals/_闭环/daily_checkin/{date}.json"
        
        # 写入 WAL
        self.wal.log("CREATE", {"path": path, "data": data})
        
        return self.storage.save(path, data)

    # ============ Knowledge API ============

    def save_knowledge(self, category: str, title: str, content: str,
                       tags: List[str] = None) -> bool:
        """保存知识条目"""
        safe_title = title.replace("/", "_").replace(" ", "-").replace(":", "-")
        path = f"knowledge/topics/{category}/{safe_title}.md"

        yaml_header = f"""---
title: "{title}"
category: "{category}"
created_at: "{datetime.now().isoformat()}"
tags: {json.dumps(tags or [])}
---

"""
        full_content = yaml_header + content
        
        # 写入 WAL
        self.wal.log("CREATE", {"path": path, "data": full_content})
        
        return self.storage.save(path, full_content)

    def search_knowledge(self, query: str, filters: Dict = None) -> List[Dict]:
        """搜索知识库"""
        return self.search.search(query, filters)

    def suggest_tags(self, content: str) -> List[str]:
        """自动建议标签"""
        keywords = ["python", "memory", "design", "task", "important", "goal", "knowledge"]
        suggestions = [k for k in keywords if k in content.lower()]
        return suggestions

    # ============ Backup & Archive API ============

    def create_backup(self, backup_type: str = "daily") -> str:
        """创建备份"""
        return self.backup.create_backup(backup_type)

    def list_backups(self) -> List[Dict]:
        """列出备份"""
        return self.backup.list_backups()

    def restore_backup(self, backup_path: str) -> bool:
        """恢复备份"""
        return self.backup.restore_backup(backup_path)

    def archive_old(self, days: int = 90) -> int:
        """归档旧数据"""
        return self.archiver.archive_old_data(days)

    def cleanup(self, max_size_gb: float = 5.0) -> Dict:
        """清理空间"""
        return self.archiver.cleanup(max_size_gb)

    # ============ Index API ============

    def rebuild_indexes(self):
        """重建索引"""
        self.indexer.build_indexes()

    def search_by_tag(self, tag: str) -> List[str]:
        """按标签搜索"""
        return self.indexer.search_by_tag(tag)


# ============ 便捷函数 ============

_pm: Optional[PersistentMemory] = None


def get_pm() -> PersistentMemory:
    """获取 PersistentMemory 实例"""
    global _pm
    if _pm is None:
        _pm = PersistentMemory()
    return _pm


def save_conversation(date: str, data: Dict) -> bool:
    """保存对话"""
    return get_pm().save_conversation(date, data)


def get_conversation(date: str) -> Optional[Dict]:
    """获取对话"""
    return get_pm().get_conversation(date)


def tag_conversation(date: str, tags: List[str]) -> bool:
    """标记对话"""
    return get_pm().tag_conversation(date, tags)


def save_goal(goal_type: str, period: str, data: Dict) -> bool:
    """保存目标"""
    return get_pm().save_goal(goal_type, period, data)


def save_knowledge(category: str, title: str, content: str,
                   tags: List[str] = None) -> bool:
    """保存知识"""
    return get_pm().save_knowledge(category, title, content, tags)


def search_knowledge(query: str, filters: Dict = None) -> List[Dict]:
    """搜索知识"""
    return get_pm().search_knowledge(query, filters)


def daily_checkin(date: str, progress: int, notes: str) -> bool:
    """每日签到"""
    return get_pm().checkin_daily(date, progress, notes)


def create_backup(backup_type: str = "daily") -> str:
    """创建备份"""
    return get_pm().create_backup(backup_type)


def archive_old(days: int = 90) -> int:
    """归档旧数据"""
    return get_pm().archive_old(days)

if __name__ == "__main__":
    import sys

    def print_help():
        print("""
Persistent Memory System - CLI

用法: python persistent_memory.py <命令> [参数]

命令:
    save <key> <value>     - 保存记忆
    load <key>             - 加载记忆
    delete <key>           - 删除记忆
    exists <key>           - 检查是否存在
    list                   - 列出所有键
    list-all               - 列出所有记忆
    clear                  - 清空所有记忆
    count                  - 记忆数量
    help                   - 显示帮助

示例:
    python persistent_memory.py save user_name "张三"
    python persistent_memory.py load user_name
    python persistent_memory.py list
        """)

    if len(sys.argv) < 2:
        print_help()
        sys.exit(0)

    cmd = sys.argv[1].lower()
    mem = Memory()

    if cmd == "save" and len(sys.argv) >= 4:
        key = sys.argv[2]
        value = sys.argv[3]
        if mem.save(key, value):
            print(f"✓ 已保存: {key} = {value}")
        else:
            print(f"✗ 保存失败: {key}")

    elif cmd == "load" and len(sys.argv) >= 3:
        key = sys.argv[2]
        value = mem.load(key)
        if value is not None:
            print(value)
        else:
            print(f"未找到: {key}")

    elif cmd == "delete" and len(sys.argv) >= 3:
        key = sys.argv[2]
        if mem.delete(key):
            print(f"✓ 已删除: {key}")
        else:
            print(f"✗ 删除失败: {key}")

    elif cmd == "exists" and len(sys.argv) >= 3:
        key = sys.argv[2]
        print(f"{'是' if mem.exists(key) else '否'}")

    elif cmd == "list":
        keys = mem.list_keys()
        for k in keys:
            print(k)

    elif cmd == "list-all":
        all_mem = mem.list_all()
        for k, v in all_mem.items():
            print(f"{k} = {v}")

    elif cmd == "clear":
        count = mem.clear()
        print(f"✓ 已清空 {count} 条记忆")

    elif cmd == "count":
        print(mem.count())

    elif cmd == "help":
        print_help()

    else:
        print(f"未知命令: {cmd}")
        print_help()
