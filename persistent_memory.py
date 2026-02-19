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
