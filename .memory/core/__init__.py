# -*- coding: utf-8 -*-
"""
Persistent Memory System - Core Modules
=======================================
核心模块：Storage, WAL, Backup, Archive

Version: 1.0
Date: 2026-02-20
"""

import json
import os
import shutil
import hashlib
import zipfile
import threading
from pathlib import Path
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional


class StorageModule:
    """文件存储模块 - 负责读写操作"""

    def __init__(self, root_path: str):
        self.root = Path(root_path)
        self.root.mkdir(parents=True, exist_ok=True)
        self._lock = threading.Lock()

    def save(self, relative_path: str, data: Any) -> bool:
        """
        保存数据到文件

        Args:
            relative_path: 相对路径
            data: 数据（支持 dict, list, str）

        Returns:
            bool: 是否成功
        """
        with self._lock:
            file_path = self.root / relative_path
            file_path.parent.mkdir(parents=True, exist_ok=True)

            # 自动添加元数据
            if isinstance(data, dict):
                data["_meta"] = {
                    "updated_at": datetime.now().isoformat(),
                    "checksum": self._compute_checksum(data)
                }

            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    if relative_path.endswith('.json'):
                        json.dump(data, f, ensure_ascii=False, indent=2)
                    else:
                        f.write(str(data))
                return True
            except Exception as e:
                print(f"[Storage] 保存失败: {e}")
                return False

    def load(self, relative_path: str) -> Optional[Any]:
        """加载文件数据"""
        file_path = self.root / relative_path
        if not file_path.exists():
            return None

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                if relative_path.endswith('.json'):
                    return json.load(f)
                return f.read()
        except Exception as e:
            print(f"[Storage] 加载失败: {e}")
            return None

    def delete(self, relative_path: str) -> bool:
        """删除文件"""
        with self._lock:
            file_path = self.root / relative_path
            if file_path.exists():
                file_path.unlink()
                return True
            return False

    def exists(self, relative_path: str) -> bool:
        """检查文件是否存在"""
        return (self.root / relative_path).exists()

    def list_files(self, pattern: str = "**/*") -> List[Path]:
        """列出匹配的文件"""
        return list(self.root.glob(pattern))

    def _compute_checksum(self, data: Any) -> str:
        """计算数据校验和"""
        content = json.dumps(data, sort_keys=True)
        return hashlib.sha256(content.encode()).hexdigest()[:16]


class WALHandler:
    """WAL Protocol 处理器 - 确保写入可靠性"""

    def __init__(self, wal_dir: str):
        self.wal_dir = Path(wal_dir)
        self.wal_dir.mkdir(parents=True, exist_ok=True)
        self._sequence = self._load_sequence()
        self._lock = threading.Lock()

    def _load_sequence(self) -> int:
        """加载当前序列号"""
        seq_file = self.wal_dir / "_sequence.txt"
        if seq_file.exists():
            try:
                return int(seq_file.read_text().strip())
            except:
                pass
        return 0

    def _save_sequence(self, seq: int):
        """保存序列号"""
        seq_file = self.wal_dir / "_sequence.txt"
        seq_file.write_text(str(seq))

    def log(self, operation: str, data: Dict[str, Any]):
        """
        写入 WAL 日志

        Args:
            operation: 操作类型 (CREATE, UPDATE, DELETE, TAG)
            data: 操作数据
        """
        with self._lock:
            self._sequence += 1
            seq = self._get_next_seq()

            entry = {
                "timestamp": datetime.now().isoformat(),
                "seq": seq,
                "op": operation,
                **data
            }

            # 写入日志文件
            log_path = self.wal_dir / f"{seq}.log"
            with open(log_path, 'w', encoding='utf-8') as f:
                json.dump(entry, f, ensure_ascii=False, indent=2)

            self._save_sequence(self._sequence)

    def _get_next_seq(self) -> str:
        """获取下一个序列号"""
        return datetime.now().strftime("%Y%m%d") + f"_{self._sequence:03d}"

    def replay(self, storage: 'StorageModule') -> int:
        """
        重放 WAL 日志（恢复数据）

        Returns:
            int: 重放的操作数量
        """
        count = 0
        for log_file in sorted(self.wal_dir.glob("*.log")):
            if log_file.name.startswith("_"):
                continue
            try:
                with open(log_file, 'r', encoding='utf-8') as f:
                    entry = json.load(f)
                    self._apply_operation(storage, entry)
                    count += 1
            except Exception as e:
                print(f"[WAL] 重放失败 {log_file}: {e}")

        # 清空已重放的日志
        for log_file in self.wal_dir.glob("*.log"):
            if log_file.name.startswith("_"):
                continue
            try:
                log_file.unlink()
            except:
                pass

        return count

    def _apply_operation(self, storage: StorageModule, entry: Dict):
        """应用操作"""
        op = entry.get("op")
        path = entry.get("path")
        
        if op == "CREATE" or op == "UPDATE":
            data = entry.get("data")
            if data and path:
                storage.save(path, data)
        elif op == "DELETE":
            if path:
                storage.delete(path)


class BackupManager:
    """自动备份与版本控制"""

    def __init__(self, data_dir: str, backup_dir: str):
        self.data_dir = Path(data_dir)
        self.backup_dir = Path(backup_dir)
        self.backup_dir.mkdir(parents=True, exist_ok=True)

    def create_backup(self, backup_type: str = "daily") -> str:
        """
        创建备份

        Args:
            backup_type: daily / weekly / version

        Returns:
            str: 备份文件路径
        """
        timestamp = datetime.now().strftime("%Y-%m-%d_%H%M%S")

        if backup_type == "version":
            backup_name = f"v1.0_{timestamp}"
        else:
            backup_name = f"{backup_type}_{timestamp}"

        backup_path = self.backup_dir / f"{backup_name}.zip"

        with zipfile.ZipFile(backup_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for root, dirs, files in os.walk(self.data_dir):
                for file in files:
                    file_path = Path(root) / file
                    arcname = file_path.relative_to(self.data_dir.parent)
                    zipf.write(file_path, arcname)

        return str(backup_path)

    def list_backups(self) -> List[Dict]:
        """列出所有备份"""
        backups = []
        for f in self.backup_dir.glob("*.zip"):
            stat = f.stat()
            backups.append({
                "name": f.stem,
                "path": str(f),
                "size": stat.st_size,
                "created_at": datetime.fromtimestamp(stat.st_ctime).isoformat()
            })
        return sorted(backups, key=lambda x: x["created_at"], reverse=True)

    def restore_backup(self, backup_path: str) -> bool:
        """恢复备份"""
        try:
            with zipfile.ZipFile(backup_path, 'r') as zipf:
                zipf.extractall(self.data_dir.parent)
            return True
        except Exception as e:
            print(f"[Backup] 恢复失败: {e}")
            return False


class Archiver:
    """自动化归档脚本"""

    def __init__(self, data_dir: str, archive_dir: str, config: Dict = None):
        self.data_dir = Path(data_dir)
        self.archive_dir = Path(archive_dir)
        self.config = config or {}
        self.archive_dir.mkdir(parents=True, exist_ok=True)

    def archive_old_data(self, days_threshold: int = 90) -> int:
        """
        归档旧数据

        Args:
            days_threshold: 超过多少天的数据需要归档

        Returns:
            int: 归档的文件数量
        """
        cutoff_date = datetime.now() - timedelta(days=days_threshold)
        archived_count = 0

        for category in ["conversations", "goals"]:
            category_dir = self.data_dir / category / "raw"
            if not category_dir.exists():
                continue

            for file_path in category_dir.rglob("*"):
                if file_path.is_file():
                    mtime = datetime.fromtimestamp(file_path.stat().st_mtime)
                    if mtime < cutoff_date:
                        self._archive_file(file_path)
                        archived_count += 1

        return archived_count

    def _archive_file(self, file_path: Path):
        """归档单个文件"""
        rel_path = file_path.relative_to(self.data_dir)
        archive_path = self.archive_dir / rel_path
        archive_path.parent.mkdir(parents=True, exist_ok=True)
        shutil.move(str(file_path), str(archive_path))

    def cleanup(self, max_size_gb: float = 5.0) -> Dict:
        """
        清理空间

        Args:
            max_size_gb: 最大使用空间 (GB)

        Returns:
            Dict: 清理报告
        """
        report = {
            "deleted_files": 0,
            "freed_space": 0,
            "oldest_file": None
        }

        total_size = sum(
            f.stat().st_size
            for f in self.data_dir.rglob("*")
            if f.is_file()
        )

        if total_size / (1024**3) < max_size_gb:
            return report

        conv_dir = self.data_dir / "conversations" / "raw"
        old_files = sorted(
            conv_dir.rglob("*.json"),
            key=lambda x: x.stat().st_mtime
        )

        for file in old_files:
            size = file.stat().st_size
            file.unlink()
            report["deleted_files"] += 1
            report["freed_space"] += size

            if total_size / (1024**3) < max_size_gb * 0.9:
                break

        if old_files:
            report["oldest_file"] = str(old_files[0])

        return report


class IndexerModule:
    """复合索引模块 - 维护多维度索引"""

    def __init__(self, storage: StorageModule):
        self.storage = storage
        self._tags_index: Dict[str, set] = {}
        self._keywords_index: Dict[str, set] = {}
        self._timeline_index: Dict[str, set] = {}

    def build_indexes(self):
        """重建所有索引"""
        self._build_tags_index()
        self._build_keywords_index()
        self._build_timeline_index()

    def _build_tags_index(self):
        """从所有数据构建标签索引"""
        # 扫描 conversations, goals, knowledge 目录
        for category in ["conversations", "goals", "knowledge"]:
            category_dir = self.storage.root / category
            if not category_dir.exists():
                continue
            
            for file_path in category_dir.rglob("*.json"):
                data = self.storage.load(str(file_path.relative_to(self.storage.root)))
                if data and isinstance(data, dict):
                    tags = data.get("tags", [])
                    for tag in tags:
                        if tag not in self._tags_index:
                            self._tags_index[tag] = set()
                        self._tags_index[tag].add(str(file_path))

    def _build_keywords_index(self):
        """构建关键词索引"""
        for category in ["conversations", "goals", "knowledge"]:
            category_dir = self.storage.root / category
            if not category_dir.exists():
                continue
            
            for file_path in category_dir.rglob("*.json"):
                data = self.storage.load(str(file_path.relative_to(self.storage.root)))
                if data and isinstance(data, dict):
                    content = json.dumps(data)
                    # 简单分词
                    words = content.lower().split()
                    for word in set(words):
                        if len(word) > 3:
                            if word not in self._keywords_index:
                                self._keywords_index[word] = set()
                            self._keywords_index[word].add(str(file_path))

    def _build_timeline_index(self):
        """构建时间线索引"""
        for category in ["conversations", "goals"]:
            category_dir = self.storage.root / category / "raw"
            if not category_dir.exists():
                continue
            
            for file_path in category_dir.rglob("*.json"):
                name = file_path.stem
                if name not in self._timeline_index:
                    self._timeline_index[name] = set()
                self._timeline_index[name].add(str(file_path))

    def add_tag(self, file_path: str, tag: str):
        """添加标签到索引"""
        if tag not in self._tags_index:
            self._tags_index[tag] = set()
        self._tags_index[tag].add(file_path)

    def search_by_tag(self, tag: str) -> List[str]:
        """按标签搜索"""
        return list(self._tags_index.get(tag, set()))

    def search_by_keyword(self, keyword: str) -> List[str]:
        """按关键词搜索"""
        return list(self._keywords_index.get(keyword.lower(), set()))


class SearchModule:
    """多维度搜索模块"""

    def __init__(self, storage: StorageModule, indexer: IndexerModule):
        self.storage = storage
        self.indexer = indexer

    def search(self, query: str, filters: Dict = None) -> List[Dict]:
        """
        复合搜索

        Args:
            query: 搜索关键词
            filters: 过滤条件

        Returns:
            匹配的结果列表
        """
        results = []

        # 从索引获取候选
        candidates = self.indexer.search_by_keyword(query)
        
        if not candidates:
            # 全局搜索
            candidates = [str(f.relative_to(self.storage.root)) 
                         for f in self.storage.list_files("**/*.json")]

        # 加载并过滤
        for path in candidates:
            data = self.storage.load(path)
            if data and self._matches_filters(data, filters):
                results.append({
                    "path": path,
                    "data": data,
                    "score": self._compute_relevance(query, data)
                })

        # 按相关性排序
        results.sort(key=lambda x: x["score"], reverse=True)
        return results

    def _matches_filters(self, data: Dict, filters: Dict) -> bool:
        """检查数据是否匹配过滤条件"""
        if not filters:
            return True

        if "tag" in filters:
            if filters["tag"] not in data.get("tags", []):
                return False

        if "type" in filters:
            if data.get("type") != filters["type"]:
                return False

        return True

    def _compute_relevance(self, query: str, data: Dict) -> float:
        """计算相关性分数"""
        content = json.dumps(data).lower()
        query_lower = query.lower()
        
        if query_lower in content:
            return 1.0
        return 0.0
