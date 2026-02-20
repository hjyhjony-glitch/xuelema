# Persistent Memory System Design

> **RUNBOT-ARC（青岩）项目总监设计**
> **版本**: v1.0
> **日期**: 2026-02-20

---

## 一、设计理念

### 1.1 核心原则

```
┌─────────────────────────────────────────────────────────────┐
│                    Persistent Memory System                    │
├─────────────────────────────────────────────────────────────┤
│  1. 纯文件 + Python 脚本 (无 API 依赖)                        │
│  2. 轻量级、零配置、直接可用                                  │
│  3. 与 OpenClaw 自带系统明确分工                              │
│  4. "日-月-年" 闭环设计                                      │
└─────────────────────────────────────────────────────────────┘
```

### 1.2 系统定位

| 系统 | 职责 | 存储位置 |
|------|------|----------|
| **OpenClaw 原生系统** | 会话状态、实时上下文、临时变量 | 内存/运行时 |
| **Persistent Memory** | 长期记忆、结构化数据、跨会话知识 | 文件系统 |

---

## 二、完整目录结构

```
E:\OpenClaw_Workspace\
│
├── .memory\                          # ★ 新增：持久化记忆根目录
│   │
│   ├── conversations\                # ★ 对话上下文快照
│   │   ├── raw\                      # 原始对话数据
│   │   │   ├── 2026/
│   │   │   │   └── 02/
│   │   │   │       ├── 2026-02-19.json
│   │   │   │       └── 2026-02-20.json
│   │   │   └── _index.json          # 对话索引
│   │   │
│   │   ├── tagged\                  # 已标记的关键对话
│   │   │   ├── important\           # 重要标记
│   │   │   │   ├── 2026-02-19.md
│   │   │   │   └── 2026-02-20.md
│   │   │   ├── decision\            # 决策标记
│   │   │   └── todo\                # 待办标记
│   │   │
│   │   └── metadata.yaml            # 对话元数据
│   │
│   ├── goals\                       # ★ 长期目标与里程碑
│   │   ├── annual\                  # 年度目标
│   │   │   └── 2026.md
│   │   ├── quarterly\               # 季度目标
│   │   │   ├── Q1_2026.md
│   │   │   ├── Q2_2026.md
│   │   │   ├── Q3_2026.md
│   │   │   └── Q4_2026.md
│   │   ├── monthly\                 # 月度目标
│   │   │   ├── 2026-02.md
│   │   │   └── 2026-03.md
│   │   │
│   │   ├── _闭环\                    # 闭环追踪
│   │   │   ├── daily_checkin\       # 每日签到
│   │   │   │   ├── 2026-02-19.md
│   │   │   │   └── 2026-02-20.md
│   │   │   ├── weekly_review\      # 周回顾
│   │   │   │   └── 2026-W08.md
│   │   │   ├── monthly_review\     # 月回顾
│   │   │   │   └── 2026-02.md
│   │   │   └── quarterly_review\   # 季度回顾
│   │   │       └── 2026-Q1.md
│   │   │
│   │   └── _templates\              # 目标模板
│   │       ├── goal_template.md
│   │       └── review_template.md
│   │
│   ├── knowledge\                    # ★ 资源与知识库
│   │   ├── topics\                  # 主题分类
│   │   │   ├── programming\
│   │   │   │   ├── python\
│   │   │   │   │   └── README.md
│   │   │   │   └── ai_ml\
│   │   │   ├── project\
│   │   │   └── personal\
│   │   │
│   │   ├── resources\               # 资源引用
│   │   │   ├── links.json          # 链接收藏
│   │   │   ├── papers.json         # 论文/文档
│   │   │   └── snippets.json       # 代码片段
│   │   │
│   │   ├── _index.yaml             # 知识库索引
│   │   └── _tags.yaml              # 标签定义
│   │
│   ├── _index\                      # ★ 复合索引目录
│   │   ├── tags.yaml               # 全局标签索引
│   │   ├── keywords.yaml            # 关键词索引
│   │   ├── timelines.yaml          # 时间线索引
│   │   └── _wal\                   # WAL Protocol
│   │       ├── 2026-02-20_001.log
│   │       └── 2026-02-20_002.log
│   │
│   ├── _backup\                     # ★ 自动备份
│   │   ├── daily\                  # 每日备份
│   │   │   ├── 2026-02-19.zip
│   │   │   └── 2026-02-20.zip
│   │   ├── weekly\                 # 每周备份
│   │   │   └── 2026-W08.zip
│   │   └── versions\                # 版本快照
│   │       └── v1.0_2026-02-20
│   │
│   └── _archive\                    # ★ 归档脚本
│       ├── archive_old.py           # 旧数据归档
│       ├── cleanup.py              # 清理脚本
│       └── config.yaml             # 归档配置
│
├── memory\                          # ★ 保留：OpenClaw 原生日志
│   ├── projects\
│   ├── decisions\
│   ├── lessons\
│   ├── technical\
│   ├── *.md                        # 每日日志
│   └── heartbeat-state.json
│
├── persistent_memory.py             # ★ 核心文件：轻量 KV 存储
│
├── AGENTS.md                        # ★ 保留：工作区规范
├── USER.md                          # ★ 保留：用户偏好
├── SOUL.md                          # ★ 保留：角色定义
└── MEMORY.md                        # ★ 保留：核心原则
```

---

## 三、数据模型设计

### 3.1 核心数据结构

#### 3.1.1 对话快照 (Conversation Snapshot)

```yaml
# .memory/conversations/raw/2026/02/2026-02-20.json
---
type: conversation_snapshot
version: 1.0
date: "2026-02-20"
source: "feishu"                    # 飞书对话源
channel_id: "oc_962aed74063bf1621ebe0387d94d6c54"
messages:
  - id: "msg_001"
    role: "user"
    content: "整理一个新的 Persistent Memory 系统"
    timestamp: "2026-02-20T04:27:00+04:30"
    tags: ["重要", "任务"]

  - id: "msg_002"
    role: "assistant"
    content: "好的，我来整理设计方案..."
    timestamp: "2026-02-20T04:28:00+04:30"
    tags: ["设计"]

metadata:
  message_count: 2
  participants: ["user", "assistant"]
  keywords: ["Persistent Memory", "系统设计"]
  is_important: true
  action_items: ["整理设计方案"]
```

#### 3.1.2 目标数据 (Goal)

```yaml
# .memory/goals/monthly/2026-02.md
---
type: monthly_goal
version: 1.0
period: "2026-02"
status: "active"
created_at: "2026-02-01T00:00:00+04:30"

goals:
  - id: "goal_001"
    title: "完成 Persistent Memory 系统设计"
    description: "整合所有需求，整理完整的设计方案"
    priority: "high"
    status: "in_progress"
    progress: 50
    milestones:
      - title: "目录结构设计"
        status: "completed"
        date: "2026-02-20"
      - title: "数据模型设计"
        status: "in_progress"
        date: "2026-02-20"
      - title: "核心模块实现"
        status: "pending"
        date: "2026-02-21"

weekly_breakdown:
  W1: { completed: 2, total: 3 }
  W2: { completed: 0, total: 3 }
  W3: { completed: 0, total: 3 }
  W4: { completed: 0, total: 3 }

checkins:
  - date: "2026-02-19"
    progress: 30
    notes: "完成了目录结构设计"
```

#### 3.1.3 知识条目 (Knowledge Item)

```yaml
# .memory/knowledge/topics/programming/python/python-best-practices.md
---
type: knowledge_entry
version: 1.0
id: "kb_001"
title: "Python 最佳实践"
category: "programming/python"
subcategory: "best_practices"
created_at: "2026-02-20T04:00:00+04:30"
updated_at: "2026-02-20T04:30:00+04:30"

content: |
  ## Python 编码规范

  1. 使用类型提示
  2. 遵循 PEP 8
  3. 编写文档字符串

tags: ["python", "最佳实践", "编码规范"]
priority: "medium"
usage_count: 5
last_used: "2026-02-20"

related:
  - "kb_002"    # 关联条目
  - "kb_003"

source:
  type: "conversation"
  reference: "conversations/tagged/important/2026-02-20.md"
```

### 3.2 标签系统 (Tag System)

```yaml
# .memory/knowledge/_tags.yaml
---
version: 1.0
last_updated: "2026-02-20T04:30:00+04:30"

tag_hierarchy:
  importance:
    - "critical"      # 紧急/关键
    - "high"          # 高优先级
    - "medium"        # 中优先级
    - "low"           # 低优先级
    - "archive"       # 已归档

  domain:
    - "programming"
    - "ai_ml"
    - "project"
    - "personal"

  type:
    - "task"          # 任务
    - "goal"          # 目标
    - "knowledge"     # 知识
    - "decision"      # 决策
    - "lesson"        # 教训

auto_suggestions:
  "python": ["programming", "python", "code"]
  "memory": ["knowledge", "system_design"]
  "设计": ["important", "project"]

tag_aliases:
  "重要": "important"
  "关键": "critical"
  "任务": "task"
```

### 3.3 WAL Protocol (Write-Ahead Log)

```json
// .memory/_index/_wal/2026-02-20_001.log
{"timestamp": "2026-02-20T04:27:00+04:30", "op": "CREATE", "type": "conversation_snapshot", "path": "conversations/raw/2026/02/2026-02-20.json", "checksum": "sha256:abc123..."}
{"timestamp": "2026-02-20T04:28:00+04:30", "op": "UPDATE", "type": "goal", "path": "goals/monthly/2026-02.md", "changes": {"progress": {"old": 0, "new": 50}}}
{"timestamp": "2026-02-20T04:29:00+04:30", "op": "TAG", "type": "tag_assignment", "target": "conversations/raw/2026/02/2026-02-20.json", "tags": ["重要", "任务"]}
```

---

## 四、核心功能模块

### 4.1 模块架构

```
┌─────────────────────────────────────────────────────────────────┐
│                     Persistent Memory Core                          │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│  │   Storage    │  │   Indexer    │  │   Search     │          │
│  │   Module     │  │   Module     │  │   Module     │          │
│  └──────────────┘  └──────────────┘  └──────────────┘          │
│         │               │               │                        │
│         ▼               ▼               ▼                        │
│  ┌──────────────────────────────────────────────────────┐      │
│  │                  Unified API Layer                      │      │
│  │  save() / load() / search() / tag() / archive()       │      │
│  └──────────────────────────────────────────────────────┘      │
│         │               │               │                        │
│         ▼               ▼               ▼                        │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│  │   WAL Log    │  │  Backup Mgr  │  │  Archiver    │          │
│  │   Handler    │  │              │  │              │          │
│  └──────────────┘  └──────────────┘  └──────────────┘          │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### 4.2 核心模块说明

#### 4.2.1 存储模块 (Storage Module)

```python
# core/storage.py

from pathlib import Path
from datetime import datetime
from typing import Any, Dict, Optional
import json
import hashlib

class StorageModule:
    """文件存储模块 - 负责读写操作"""

    def __init__(self, root_path: str):
        self.root = Path(root_path)
        self.root.mkdir(parents=True, exist_ok=True)

    def save(self, relative_path: str, data: Any) -> bool:
        """
        保存数据到文件

        Args:
            relative_path: 相对路径
            data: 数据（支持 dict, list, str）

        Returns:
            bool: 是否成功
        """
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
                    f.write(data)
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
        file_path = self.root / relative_path
        if file_path.exists():
            file_path.unlink()
            return True
        return False

    def _compute_checksum(self, data: Any) -> str:
        """计算数据校验和"""
        content = json.dumps(data, sort_keys=True)
        return hashlib.sha256(content.encode()).hexdigest()[:16]
```

#### 4.2.2 索引模块 (Indexer Module)

```python
# core/indexer.py

from typing import Dict, List, Set
from collections import defaultdict

class IndexerModule:
    """复合索引模块 - 维护多维度索引"""

    def __init__(self, storage: 'StorageModule'):
        self.storage = storage
        self._tags_index: Dict[str, Set[str]] = defaultdict(set)
        self._keywords_index: Dict[str, Set[str]] = defaultdict(set)
        self._timeline_index: Dict[str, Set[str]] = defaultdict(set)

    def build_indexes(self):
        """重建所有索引"""
        self._build_tags_index()
        self._build_keywords_index()
        self._build_timeline_index()

    def _build_tags_index(self):
        """从所有数据构建标签索引"""
        # 扫描 .memory/conversations/, .memory/goals/, .memory/knowledge/
        # 提取所有标签并更新索引
        pass

    def add_tag(self, file_path: str, tag: str):
        """添加标签到索引"""
        self._tags_index[tag].add(file_path)

    def search_by_tag(self, tag: str) -> List[str]:
        """按标签搜索"""
        return list(self._tags_index.get(tag, set()))

    def search_by_keyword(self, keyword: str) -> List[str]:
        """按关键词搜索"""
        return list(self._keywords_index.get(keyword.lower(), set()))
```

#### 4.2.3 搜索模块 (Search Module)

```python
# core/search.py

from typing import List, Dict, Any

class SearchModule:
    """多维度搜索模块"""

    def __init__(self, storage, indexer):
        self.storage = storage
        self.indexer = indexer

    def search(self, query: str, filters: Dict = None) -> List[Dict[str, Any]]:
        """
        复合搜索

        Args:
            query: 搜索关键词
            filters: 过滤条件
                - tag: 按标签过滤
                - type: 按类型过滤 (conversation, goal, knowledge)
                - date_range: 时间范围

        Returns:
            匹配的结果列表
        """
        results = []

        # 1. 从索引获取候选
        candidates = self.indexer.search_by_keyword(query)

        # 2. 加载并过滤
        for path in candidates:
            data = self.storage.load(path)
            if self._matches_filters(data, filters):
                results.append({
                    "path": path,
                    "data": data,
                    "score": self._compute_relevance(query, data)
                })

        # 3. 按相关性排序
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
```

#### 4.2.4 WAL Handler (Write-Ahead Log)

```python
# core/wal.py

from datetime import datetime
from typing import Dict, Any
import json
import os

class WALHandler:
    """WAL Protocol 处理器 - 确保写入可靠性"""

    def __init__(self, wal_dir: str):
        self.wal_dir = wal_dir
        os.makedirs(wal_dir, exist_ok=True)
        self._sequence = 0

    def log(self, operation: str, data: Dict[str, Any]):
        """
        写入 WAL 日志

        Args:
            operation: 操作类型 (CREATE, UPDATE, DELETE, TAG)
            data: 操作数据
        """
        entry = {
            "timestamp": datetime.now().isoformat(),
            "seq": self._get_next_seq(),
            "op": operation,
            **data
        }

        # 写入临时文件
        temp_path = os.path.join(self.wal_dir, f"temp_{entry['seq']}.log")
        with open(temp_path, 'w', encoding='utf-8') as f:
            json.dump(entry, f, ensure_ascii=False)

        # 重命名为正式文件
        final_path = os.path.join(self.wal_dir, f"{entry['seq']}.log")
        os.rename(temp_path, final_path)

    def _get_next_seq(self) -> str:
        """获取下一个序列号"""
        self._sequence += 1
        return datetime.now().strftime("%Y%m%d") + f"_{self._sequence:03d}"

    def replay(self, storage: 'StorageModule') -> int:
        """
        重放 WAL 日志（恢复数据）

        Returns:
            int: 重放的操作数量
        """
        count = 0
        for log_file in sorted(os.listdir(self.wal_dir)):
            if log_file.endswith('.log'):
                with open(os.path.join(self.wal_dir, log_file), 'r') as f:
                    entry = json.load(f)
                    self._apply_operation(storage, entry)
                    count += 1

        # 清空已重放的日志
        for log_file in os.listdir(self.wal_dir):
            if log_file.endswith('.log'):
                os.remove(os.path.join(self.wal_dir, log_file))

        return count
```

#### 4.2.5 备份管理器 (Backup Manager)

```python
# core/backup.py

import zipfile
import os
from datetime import datetime
from pathlib import Path

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
```

#### 4.2.6 归档器 (Archiver)

```python
# core/archive.py

import os
import shutil
from datetime import datetime, timedelta
from pathlib import Path

class Archiver:
    """自动化归档脚本"""

    def __init__(self, data_dir: str, archive_dir: str, config: Dict):
        self.data_dir = Path(data_dir)
        self.archive_dir = Path(archive_dir)
        self.config = config  # 归档配置
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
        # 计算相对路径
        rel_path = file_path.relative_to(self.data_dir)
        archive_path = self.archive_dir / rel_path

        # 创建目标目录
        archive_path.parent.mkdir(parents=True, exist_ok=True)

        # 移动文件
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

        # 计算当前大小
        total_size = sum(
            f.stat().st_size
            for f in self.data_dir.rglob("*")
            if f.is_file()
        )

        if total_size / (1024**3) < max_size_gb:
            return report

        # 删除最旧的对话快照
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

            # 检查是否已释放足够空间
            if total_size / (1024**3) < max_size_gb * 0.9:
                break

        if old_files:
            report["oldest_file"] = str(old_files[0])

        return report
```

### 4.3 统一 API 层

```python
# persistent_memory.py (增强版)

"""
Persistent Memory System - 增强版
==================================
整合所有模块的统一 API
"""

from pathlib import Path
from typing import Any, Dict, List, Optional
from datetime import datetime
import json

class PersistentMemory:
    """统一记忆系统 API"""

    def __init__(self, root_path: str = "./.memory"):
        self.root = Path(root_path)
        self.root.mkdir(parents=True, exist_ok=True)

        # 初始化各模块
        self._init_directories()
        self._load_modules()

    def _init_directories(self):
        """初始化目录结构"""
        dirs = [
            "conversations/raw",
            "conversations/tagged",
            "goals/annual",
            "goals/quarterly",
            "goals/monthly",
            "goals/_闭环/daily_checkin",
            "goals/_闭环/weekly_review",
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
        return self._save(path, data)

    def get_conversations(self, date: str) -> Optional[Dict]:
        """获取对话"""
        path = f"conversations/raw/{date[:4]}/{date[5:7]}/{date}.json"
        return self._load(path)

    def tag_conversation(self, date: str, tags: List[str]) -> bool:
        """标记对话"""
        path = f"conversations/tagged/{tags[0]}/{date}.md"
        # 创建标记文件
        content = f"# {date} - Tagged Conversations\n\nTags: {', '.join(tags)}\n\n## Summary\n\n"
        return self._save(path, content, is_text=True)

    # ============ Goal API ============

    def save_goal(self, goal_type: str, period: str, data: Dict) -> bool:
        """保存目标"""
        if goal_type == "monthly":
            path = f"goals/{goal_type}/{period}.md"
        elif goal_type == "quarterly":
            path = f"goals/{goal_type}/{period}.md"
        elif goal_type == "annual":
            path = f"goals/{goal_type}/{period}.md"
        else:
            return False
        return self._save(path, self._to_yaml(data))

    def checkin_daily(self, date: str, progress: int, notes: str) -> bool:
        """每日签到"""
        data = {
            "date": date,
            "progress": progress,
            "notes": notes,
            "timestamp": datetime.now().isoformat()
        }
        path = f"goals/_闭环/daily_checkin/{date}.json"
        return self._save(path, data)

    # ============ Knowledge API ============

    def save_knowledge(self, category: str, title: str, content: str,
                       tags: List[str] = None) -> bool:
        """保存知识条目"""
        safe_title = title.replace("/", "_").replace(" ", "-")
        path = f"knowledge/topics/{category}/{safe_title}.md"

        yaml_header = f"""---
title: "{title}"
category: "{category}"
created_at: "{datetime.now().isoformat()}"
tags: {tags or []}
---

"""
        return self._save(path, yaml_header + content, is_text=True)

    def search_knowledge(self, query: str) -> List[Dict]:
        """搜索知识库"""
        results = []
        topic_dir = self.root / "knowledge" / "topics"

        for md_file in topic_dir.rglob("*.md"):
            content = md_file.read_text(encoding='utf-8')
            if query.lower() in content.lower():
                results.append({
                    "path": str(md_file.relative_to(self.root)),
                    "title": self._extract_title(content)
                })

        return results

    # ============ Tag API ============

    def suggest_tags(self, content: str) -> List[str]:
        """自动建议标签"""
        keywords = ["python", "memory", "design", "task", "important"]
        suggestions = [k for k in keywords if k in content.lower()]
        return suggestions

    # ============ Backup & Archive API ============

    def create_backup(self) -> str:
        """创建备份"""
        from core.backup import BackupManager
        bm = BackupManager(str(self.root), str(self.root / "_backup"))
        return bm.create_backup("daily")

    def archive_old(self, days: int = 90) -> int:
        """归档旧数据"""
        from core.archive import Archiver
        archiver = Archiver(
            str(self.root),
            str(self.root / "_archive"),
            {"auto_archive": True}
        )
        return archiver.archive_old_data(days)

    # ============ Internal Helpers ============

    def _save(self, relative_path: str, data: Any, is_text: bool = False) -> bool:
        """内部保存"""
        path = self.root / relative_path
        path.parent.mkdir(parents=True, exist_ok=True)

        try:
            if is_text or str(path).endswith('.md'):
                if isinstance(data, dict):
                    import yaml
                    data = yaml.dump(data)
                path.write_text(str(data), encoding='utf-8')
            else:
                with open(path, 'w', encoding='utf-8') as f:
                    json.dump(data, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            print(f"[PM] 保存失败: {e}")
            return False

    def _load(self, relative_path: str) -> Any:
        """内部加载"""
        path = self.root / relative_path
        if not path.exists():
            return None

        try:
            if str(path).endswith('.json'):
                with open(path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            return path.read_text(encoding='utf-8')
        except Exception as e:
            print(f"[PM] 加载失败: {e}")
            return None

    def _to_yaml(self, data: Dict) -> str:
        """转换为 YAML"""
        import yaml
        return yaml.dump(data, allow_unicode=True)

    def _extract_title(self, content: str) -> str:
        """提取标题"""
        for line in content.split('\n'):
            if line.startswith('# '):
                return line[2:].strip()
        return "Untitled"


# ============ 便捷函数 ============

_pm: Optional[PersistentMemory] = None

def get_pm() -> PersistentMemory:
    global _pm
    if _pm is None:
        _pm = PersistentMemory()
    return _pm

# 便捷方法
def save_conversation(date: str, data: Dict) -> bool:
    return get_pm().save_conversation(date, data)

def save_goal(goal_type: str, period: str, data: Dict) -> bool:
    return get_pm().save_goal(goal_type, period, data)

def save_knowledge(category: str, title: str, content: str,
                   tags: List[str] = None) -> bool:
    return get_pm().save_knowledge(category, title, content, tags)

def search_knowledge(query: str) -> List[Dict]:
    return get_pm().search_knowledge(query)

def daily_checkin(date: str, progress: int, notes: str) -> bool:
    return get_pm().checkin_daily(date, progress, notes)
```

---

## 五、与 OpenClaw 系统的融合方式

### 5.1 系统分工

```
┌──────────────────────────────────────────────────────────────────────┐
│                         OpenClaw 运行时                                │
├──────────────────────────────────────────────────────────────────────┤
│                                                                       │
│   ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐  │
│   │   会话状态      │    │   实时上下文    │    │   临时变量      │  │
│   │   (内存)        │    │   (上下文变量)  │    │   (运行时)      │  │
│   └────────┬────────┘    └────────┬────────┘    └────────┬────────┘  │
│            │                      │                      │             │
│            └──────────────────────┼──────────────────────┘             │
│                                   │                                    │
│                          OpenClaw 自带系统                             │
│                          (memory/ 目录)                               │
│                                                                       │
└──────────────────────────────────────────────────────────────────────┘
                                   │
                                   │ ← 数据流转
                                   ▼
┌──────────────────────────────────────────────────────────────────────┐
│                      Persistent Memory System                          │
├──────────────────────────────────────────────────────────────────────┤
│                                                                       │
│   ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐  │
│   │   长期记忆      │    │   结构化知识    │    │   目标追踪      │  │
│   │   (.memory/)    │    │   (knowledge/)  │    │   (goals/)      │  │
│   └─────────────────┘    └─────────────────┘    └─────────────────┘  │
│                                                                       │
│   ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐  │
│   │   对话快照      │    │   决策记录      │    │   经验教训      │  │
│   │   (conversations│    │   (decisions/)  │    │   (lessons/)    │  │
│   └─────────────────┘    └─────────────────┘    └─────────────────┘  │
│                                                                       │
└──────────────────────────────────────────────────────────────────────┘
```

### 5.2 数据流转机制

```python
# integration/openclaw_hook.py

"""
OpenClaw 集成钩子
================
在关键时机自动同步数据到 Persistent Memory
"""

class OpenClawIntegration:
    """OpenClaw 集成处理器"""

    def __init__(self, pm: 'PersistentMemory'):
        self.pm = pm

    def on_session_start(self, session_id: str):
        """会话开始时加载历史上下文"""
        # 加载最近7天的对话摘要
        recent_conversations = self._load_recent_conversations(days=7)
        return recent_conversations

    def on_decision_made(self, decision: Dict):
        """决策记录 - 自动保存到 decisions/"""
        self.pm.save_knowledge(
            category="decisions",
            title=f"决策: {decision.get('title', '未命名')}",
            content=decision.get("reasoning", ""),
            tags=["decision", decision.get("type", "general")]
        )

    def on_lesson_learned(self, lesson: Dict):
        """经验教训 - 自动保存到 lessons/"""
        self.pm.save_knowledge(
            category="lessons",
            title=f"教训: {lesson.get('title', '未命名')}",
            content=lesson.get("description", ""),
            tags=["lesson", lesson.get("type", "general")]
        )

    def on_goal_update(self, goal_type: str, period: str, progress: int):
        """目标更新 - 记录闭环"""
        date = datetime.now().strftime("%Y-%m-%d")
        self.pm.checkin_daily(date, progress, f"自动更新: {goal_type}")
```

### 5.3 飞书对话同步

```python
# integration/feishu_sync.py

"""
飞书对话同步脚本
================
每日自动拉取飞书对话（无 API 版本的替代方案）
"""

import json
from datetime import datetime, timedelta
from pathlib import Path

class FeishuSync:
    """飞书对话同步器（无 API 版本）"""

    def __init__(self, data_dir: str = "./.memory"):
        self.data_dir = Path(data_dir)

    def fetch_daily_conversations(self, date: str = None) -> Dict:
        """
        获取每日对话（模拟实现）

        注意：实际使用时需要根据飞书 API 实现
        这里提供无 API 版本的占位实现

        Returns:
            Dict: 对话数据
        """
        if date is None:
            date = datetime.now().strftime("%Y-%m-%d")

        # 占位数据 - 实际使用时替换为真实的飞书 API 调用
        mock_data = {
            "date": date,
            "source": "feishu",
            "messages": [],
            "metadata": {
                "fetched_at": datetime.now().isoformat(),
                "status": "mock"  # 替换为 "success" 使用真实 API
            }
        }

        return mock_data

    def save_conversation(self, date: str, data: Dict) -> bool:
        """保存对话到 .memory/conversations/raw/"""
        path = f"conversations/raw/{date[:4]}/{date[5:7]}/{date}.json"
        full_path = self.data_dir / path
        full_path.parent.mkdir(parents=True, exist_ok=True)

        with open(full_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

        return True

    def mark_important(self, date: str, tags: list):
        """标记重要对话"""
        path = f"conversations/tagged/{tags[0]}/{date}.md"
        full_path = self.data_dir / path
        full_path.parent.mkdir(parents=True, exist_ok=True)

        content = f"""# {date} - 标记对话

**标签**: {', '.join(tags)}
**时间**: {datetime.now().isoformat()}

## 原始数据

请查看: `conversations/raw/{date[:4]}/{date[5:7]}/{date}.json`

## 备注

"""
        full_path.write_text(content, encoding='utf-8')
```

---

## 六、实施路线图

### 6.1 分阶段实施计划

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        Persistent Memory 实施路线图                              │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  Phase 1: 基础架构 (第 1 周)                                                │
│  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━                                               │
│  □ 创建 .memory/ 目录结构                                                   │
│  □ 实现 StorageModule 核心读写                                              │
│  □ 实现 WAL Protocol                                                       │
│  □ 集成到 persistent_memory.py                                             │
│                                                                              │
│  Phase 2: 对话系统 (第 2 周)                                               │
│  ━━━━━━━━━━━━━━━━━━━━━━━━                                                   │
│  □ 实现 conversations/ 目录结构                                             │
│  □ 实现 FeishuSync 对话同步                                                │
│  □ 实现标签系统基础功能                                                     │
│  □ 实现 _index/tags.yaml 索引                                               │
│                                                                              │
│  Phase 3: 目标追踪 (第 3 周)                                               │
│  ━━━━━━━━━━━━━━━━━━━━━━━                                                    │
│  □ 实现 goals/ 目录结构                                                     │
│  □ 实现每日签到功能                                                        │
│  □ 实现周/月/季度回顾模板                                                   │
│  □ 实现闭环追踪系统                                                        │
│                                                                              │
│  Phase 4: 知识库 (第 4 周)                                                 │
│  ━━━━━━━━━━━━━━━━━━━━━                                                     │
│  □ 实现 knowledge/ 目录结构                                                │
│  □ 实现复合搜索功能                                                        │
│  □ 实现自动标签建议                                                        │
│  □ 实现资源引用管理                                                        │
│                                                                              │
│  Phase 5: 运维工具 (第 5 周)                                               │
│  ━━━━━━━━━━━━━━━━━━━━━                                                     │
│  □ 实现自动备份系统                                                        │
│  □ 实现归档清理脚本                                                        │
│  □ 编写使用文档                                                            │
│  □ 部署与测试                                                              │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 6.2 里程碑与验收标准

| 里程碑 | 完成标准 | 验收方式 |
|--------|----------|----------|
| **M1: 目录就绪** | `.memory/` 目录创建完成 | `ls -la .memory/` |
| **M2: 核心 API** | `save_conversation()`, `save_goal()` 可用 | Python 脚本测试 |
| **M3: 对话同步** | 自动拉取并标记对话 | 手动检查生成的文件 |
| **M4: 目标闭环** | 日/周/月回顾模板可用 | 检查 `goals/_闭环/` |
| **M5: 搜索可用** | `search_knowledge()` 返回结果 | 运行测试脚本 |
| **M6: 备份可用** | 每日自动备份成功 | 检查 `_backup/` |
| **M7: 归档可用** | 旧数据自动归档 | 等待 90 天后验证 |

### 6.3 脚本清单

```bash
#!/bin/bash
# scripts/persistent_memory.sh

# 初始化目录结构
python -c "from persistent_memory import PersistentMemory; pm = PersistentMemory('.memory')"

# 每日同步（添加到 cron）
# 0 2 * * * python /path/to/scripts/feishu_sync.py

# 每周备份（添加到 cron）
# 0 3 * * 0 python /path/to/scripts/backup.py

# 每月归档（添加到 cron）
# 0 4 1 * * python /path/to/scripts/archive.py --days=90
```

---

## 七、快速开始

### 7.1 安装与初始化

```bash
# 1. 克隆/更新工作区
git pull origin main

# 2. 确保 Python 依赖
pip install pyyaml

# 3. 初始化目录结构
python persistent_memory.py init

# 4. 验证安装
python -c "
from persistent_memory import PersistentMemory

pm = PersistentMemory('.memory')
print('✓ Persistent Memory 初始化成功')
print(f'存储目录: {pm.root}')
"
```

### 7.2 使用示例

```python
# 保存对话
from persistent_memory import save_conversation

data = {
    "messages": [
        {"role": "user", "content": "设计新功能"},
        {"role": "assistant", "content": "好的，开始设计"}
    ],
    "metadata": {"tags": ["设计", "重要"]}
}
save_conversation("2026-02-20", data)

# 保存目标
from persistent_memory import save_goal

goal = {
    "title": "完成系统设计",
    "progress": 50,
    "milestones": ["目录结构", "数据模型", "核心模块"]
}
save_goal("monthly", "2026-02", goal)

# 搜索知识
from persistent_memory import search_knowledge

results = search_knowledge("Python")
for r in results:
    print(f"- {r['title']}: {r['path']}")

# 每日签到
from persistent_memory import daily_checkin

daily_checkin("2026-02-20", 75, "完成了数据模型设计")
```

---

## 八、附录

### 8.1 文件格式规范

| 目录 | 格式 | 命名规则 |
|------|------|----------|
| `conversations/raw/` | JSON | `YYYY-MM-DD.json` |
| `conversations/tagged/` | Markdown | `YYYY-MM-DD.md` |
| `goals/monthly/` | Markdown | `YYYY-MM.md` |
| `goals/_闭环/` | JSON | `YYYY-MM-DD.json` |
| `knowledge/topics/` | Markdown | `slug-title.md` |

### 8.2 标签使用指南

| 标签 | 用途 | 示例 |
|------|------|------|
| `important` | 重要对话/决策 | `save_conversation(..., tags=["important"])` |
| `decision` | 关键决策 | `save_knowledge(..., tags=["decision"])` |
| `todo` | 待办事项 | `save_knowledge(..., tags=["todo"])` |
| `python` | Python 相关 | `save_knowledge(..., tags=["python"])` |
| `ai_ml` | AI/ML 相关 | `save_knowledge(..., tags=["ai_ml"])` |

### 8.3 故障排查

| 问题 | 解决方案 |
|------|----------|
| 目录不存在 | 运行 `python persistent_memory.py init` |
| 编码错误 | 确保使用 UTF-8 编码 |
| 权限错误 | 检查目录写入权限 |
| 磁盘空间不足 | 运行 `python scripts/cleanup.py` |

---

> **文档版本**: v1.1
> **最后更新**: 2026-02-20
> **维护者**: RUNBOT-ARC（青岩）

---

# 补充章节：数据一致性、检索策略、备份机制与 OpenClaw 集成

## 九、数据一致性与事务性

### 9.1 问题背景

SQLite 和 ChromaDB 是两个独立的存储引擎，在更新记忆时需要考虑事务一致性。

### 9.2 原子更新策略

#### 核心原则：先写 SQLite，再写 ChromaDB，失败时回滚

```python
class MemoryTransaction:
    """记忆更新事务管理器"""
    
    def __init__(self, sqlite_db, vector_db):
        self.sqlite = sqlite_db
        self.vector = vector_db
        self.operation_log = []
    
    def add_memory(self, memory_id: str, content: str, embedding: list):
        """
        原子更新：先 SQLite 后 ChromaDB
        
        步骤：
        1. 写入 SQLite（事务开始）
        2. 生成向量
        3. 写入 ChromaDB
        4. 提交事务
        """
        try:
            # Step 1: 写入 SQLite
            self.sqlite.execute(
                "INSERT INTO memories (id, content, version) VALUES (?, ?, 1)",
                (memory_id, content)
            )
            
            # Step 2: 生成向量
            vector = self.vector.embed(content)
            
            # Step 3: 写入 ChromaDB
            self.vector.add(memory_id, vector)
            
            # Step 4: 提交 SQLite 事务
            self.sqlite.commit()
            
            # 记录操作日志
            self._log_operation("add", memory_id)
            
            return True
            
        except Exception as e:
            # 失败时回滚
            self._rollback(memory_id, content)
            raise MemoryUpdateError(f"原子更新失败: {e}")
    
    def _rollback(self, memory_id: str, content: str):
        """回滚操作"""
        # 记录回滚日志
        self.operation_log.append({
            "action": "rollback",
            "memory_id": memory_id,
            "content": content,
            "timestamp": datetime.now().isoformat()
        })
        
        # 回滚 SQLite
        try:
            self.sqlite.execute(
                "DELETE FROM memories WHERE id = ?",
                (memory_id,)
            )
            self.sqlite.commit()
        except:
            pass
        
        # 清理 ChromaDB
        try:
            self.vector.delete(memory_id)
        except:
            pass
    
    def compensate(self):
        """补偿机制：定期检查并修复不一致数据"""
        # 获取最近的操作日志
        recent_ops = self._get_recent_operations()
        
        for op in recent_ops:
            # 检查 SQLite 和 ChromaDB 数据是否一致
            sqlite_exists = self.sqlite.exists(op.memory_id)
            vector_exists = self.vector.exists(op.memory_id)
            
            if sqlite_exists != vector_exists:
                # 不一致，进行补偿
                self._compensate(op)
    
    def _compensate(self, op: dict):
        """执行补偿操作"""
        if op.action == "add" and not self.vector.exists(op.memory_id):
            # 重新添加向量
            content = op.content
            vector = self.vector.embed(content)
            self.vector.add(op.memory_id, vector)
```

### 9.3 版本控制

#### 给每条记忆加版本号，便于回滚和审计

```sql
-- SQLite 记忆表（含版本号）
CREATE TABLE memories (
    id TEXT PRIMARY KEY,
    content TEXT NOT NULL,
    version INTEGER DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    checksum TEXT,  -- 内容校验和
    metadata JSON
);

-- 版本历史表
CREATE TABLE memory_versions (
    version_id TEXT PRIMARY KEY,
    memory_id TEXT,
    content TEXT NOT NULL,
    version INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    checksum TEXT
);

-- 更新时自动增加版本号
CREATE TRIGGER memory_version_update
AFTER UPDATE ON memories
FOR EACH ROW
BEGIN
    INSERT INTO memory_versions (version_id, memory_id, content, version, checksum)
    VALUES (
        'v_' || OLD.id || '_' || datetime('now'),
        OLD.id,
        OLD.content,
        OLD.version,
        OLD.checksum
    );
END;
```

### 9.4 数据一致性检查

```python
class ConsistencyChecker:
    """数据一致性检查器"""
    
    def __init__(self, sqlite_db, vector_db):
        self.sqlite = sqlite_db
        self.vector = vector_db
    
    def check_all(self) -> dict:
        """全面一致性检查"""
        results = {
            "total_count": 0,
            "consistent": 0,
            "missing_in_vector": [],
            "missing_in_sqlite": [],
            "inconsistent_versions": []
        }
        
        # 获取所有 SQLite 记录
        sqlite_ids = self.sqlite.get_all_ids()
        results["total_count"] = len(sqlite_ids)
        
        for memory_id in sqlite_ids:
            vector_exists = self.vector.exists(memory_id)
            if not vector_exists:
                results["missing_in_vector"].append(memory_id)
            else:
                results["consistent"] += 1
        
        # 检查反向
        vector_ids = self.vector.get_all_ids()
        for memory_id in vector_ids:
            if not self.sqlite.exists(memory_id):
                results["missing_in_sqlite"].append(memory_id)
        
        return results
    
    def repair(self, memory_id: str):
        """修复单条记录"""
        # 从 SQLite 恢复
        content = self.sqlite.get_content(memory_id)
        if content:
            vector = self.vector.embed(content)
            self.vector.add(memory_id, vector)
```

## 十、检索策略的优先级

### 10.1 检索类型与适用场景

| 检索类型 | 适用场景 | 推荐引擎 |
|----------|----------|----------|
| **精确匹配** | 已知具体内容，直接查找 | SQLite 标签 / 全文检索 |
| **关键词搜索** | 知道部分关键词 | SQLite FTS5 |
| **语义联想** | 查找相似概念，相关内容 | ChromaDB 向量检索 |
| **混合查询** | 需要精确 + 语义 | 组合策略 |

### 10.2 检索优先级策略

```python
class SearchStrategy:
    """检索策略选择器"""
    
    def __init__(self, sqlite_db, vector_db):
        self.sqlite = sqlite_db
        self.vector = vector_db
    
    def search(self, query: str, mode: str = "auto") -> list:
        """
        根据查询类型选择最佳检索策略
        
        Args:
            query: 搜索查询
            mode: 检索模式
                - "auto": 自动选择最佳策略
                - "exact": 精确匹配优先
                - "semantic": 语义搜索优先
                - "hybrid": 混合检索
        """
        if mode == "auto":
            return self._auto_search(query)
        elif mode == "exact":
            return self._exact_search(query)
        elif mode == "semantic":
            return self._semantic_search(query)
        elif mode == "hybrid":
            return self._hybrid_search(query)
    
    def _auto_search(self, query: str) -> list:
        """自动选择最佳策略"""
        # 判断查询类型
        if self._is_exact_query(query):
            return self._exact_search(query)
        elif self._is_semantic_query(query):
            return self._semantic_search(query)
        else:
            return self._hybrid_search(query)
    
    def _is_exact_query(self, query: str) -> bool:
        """判断是否为精确查询"""
        # 包含具体名称、ID、关键词
        exact_patterns = [
            r"^[a-zA-Z0-9_]+$",  # 纯标识符
            r"^\d{4}-\d{2}-\d{2}$",  # 日期格式
            r"^MEMORY_\d+$",  # 记忆ID
        ]
        return any(re.match(p, query) for p in exact_patterns)
    
    def _is_semantic_query(self, query: str) -> bool:
        """判断是否为语义查询"""
        # 包含自然语言描述
        semantic_patterns = [
            r"如何", r"怎么", r"是什么", r"相关",
            r"和.*相关", r"类似.*概念"
        ]
        return any(re.search(p, query) for p in semantic_patterns)
    
    def _exact_search(self, query: str) -> list:
        """精确匹配：优先用 SQLite 标签 / 全文检索"""
        # 方式1: 标签搜索
        tag_results = self.sqlite.search_by_tag(query)
        if tag_results:
            return tag_results
        
        # 方式2: FTS5 全文检索
        fts_results = self.sqlite.fts_search(query)
        return fts_results
    
    def _semantic_search(self, query: str) -> list:
        """语义联想：优先用 ChromaDB 向量检索"""
        return self.vector.semantic_search(query, n_results=10)
    
    def _hybrid_search(self, query: str) -> list:
        """混合查询：先通过标签过滤，再做向量相似度排序"""
        # Step 1: 获取所有候选
        all_candidates = self.vector.semantic_search(query, n_results=50)
        
        # Step 2: 标签过滤
        relevant_tags = self._extract_tags(query)
        if relevant_tags:
            candidates = [
                c for c in all_candidates
                if any(tag in c.tags for tag in relevant_tags)
            ]
        else:
            candidates = all_candidates
        
        # Step 3: 相似度排序
        return sorted(candidates, key=lambda x: x.similarity, reverse=True)
    
    def _extract_tags(self, query: str) -> list:
        """从查询中提取标签"""
        # 简单实现：提取 #标签 格式
        tags = re.findall(r"#(\w+)", query)
        return tags
```

### 10.3 检索性能优化

```python
class SearchOptimizer:
    """检索性能优化器"""
    
    def __init__(self, sqlite_db, vector_db):
        self.sqlite = sqlite_db
        self.vector = vector_db
        self.cache = {}  # LRU 缓存
    
    def cached_search(self, query: str) -> list:
        """带缓存的检索"""
        cache_key = hash(query)
        
        if cache_key in self.cache:
            return self.cache[cache_key]
        
        results = self.vector.semantic_search(query)
        
        # 缓存 5 分钟
        self.cache[cache_key] = results
        return results
    
    def batch_search(self, queries: list) -> dict:
        """批量检索"""
        results = {}
        for query in queries:
            results[query] = self._auto_search(query)
        return results
```

## 十一、备份与恢复机制

### 11.1 备份策略

#### 触发条件

| 触发类型 | 条件 | 说明 |
|----------|------|------|
| **时间触发** | 每日 03:00 AM | 定时自动备份 |
| **事件触发** | 重大决策后 | MEMORY.md 修改时 |
| **手动触发** | 用户执行命令 | `python backup.py --force` |

#### 备份内容

```python
class BackupManager:
    """备份管理器"""
    
    def __init__(self, backup_dir: str):
        self.backup_dir = Path(backup_dir)
        self.backup_dir.mkdir(parents=True, exist_ok=True)
    
    def create_backup(self, reason: str = "manual") -> str:
        """创建备份"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = self.backup_dir / f"backup_{timestamp}"
        backup_path.mkdir(exist_ok=True)
        
        # 1. 备份 SQLite
        self._backup_sqlite(backup_path / "memory.db")
        
        # 2. 备份 ChromaDB
        self._backup_vector_db(backup_path / "vector_db")
        
        # 3. 备份核心文件
        self._backup_core_files(backup_path / "core_files")
        
        # 4. 生成备份清单
        self._generate_manifest(backup_path, reason)
        
        return str(backup_path)
    
    def _backup_sqlite(self, target_path: Path):
        """备份 SQLite 数据库"""
        import shutil
        shutil.copy("data/memory/memory.db", target_path)
    
    def _backup_vector_db(self, target_path: Path):
        """备份 ChromaDB"""
        import shutil
        shutil.copytree("data/memory/vector_db", target_path)
    
    def _backup_core_files(self, target_path: Path):
        """备份核心配置文件"""
        core_files = ["MEMORY.md", "USER.md", "SOUL.md", "AGENTS.md"]
        for file in core_files:
            if Path(file).exists():
                shutil.copy(file, target_path / file)
    
    def _generate_manifest(self, backup_path: Path, reason: str):
        """生成备份清单"""
        manifest = {
            "backup_id": backup_path.name,
            "timestamp": datetime.now().isoformat(),
            "reason": reason,
            "files": [],
            "sha256": self._calculate_checksum(backup_path)
        }
        
        manifest_path = backup_path / "manifest.json"
        with open(manifest_path, "w", encoding="utf-8") as f:
            json.dump(manifest, f, ensure_ascii=False, indent=2)
```

### 11.2 版本管理策略

#### 保留策略

| 时间范围 | 保留数量 | 说明 |
|----------|----------|------|
| **最近 7 天** | 全部保留 | 每日 1 个 |
| **最近 4 周** | 每周 1 个 | 每周日备份 |
| **最近 12 个月** | 每月 1 个 | 每月 1 号备份 |
| **超过 12 个月** | 按年归档 | 年度汇总 |

```python
class BackupCleanup:
    """备份清理管理器"""
    
    def __init__(self, backup_dir: str, retention_days: int = 30):
        self.backup_dir = Path(backup_dir)
        self.retention_days = retention_days
    
    def cleanup(self):
        """清理过期备份"""
        backups = self._get_all_backups()
        
        for backup in backups:
            age_days = (datetime.now() - backup.date).days
            
            if age_days > self.retention_days * 4:  # 4个月
                backup.delete()
            elif age_days > self.retention_days:  # 1个月
                if not backup.is_weekly():  # 不是周备份
                    backup.delete()
    
    def _get_all_backups(self) -> list:
        """获取所有备份"""
        # 实现...
        return []
```

### 11.3 恢复流程

```python
class RestoreManager:
    """恢复管理器"""
    
    def __init__(self, backup_dir: str):
        self.backup_dir = Path(backup_dir)
    
    def list_backups(self) -> list:
        """列出所有备份"""
        backups = []
        for path in self.backup_dir.iterdir():
            if path.is_dir() and path.name.startswith("backup_"):
                manifest = path / "manifest.json"
                if manifest.exists():
                    with open(manifest) as f:
                        info = json.load(f)
                        backups.append({
                            "id": path.name,
                            "date": info["timestamp"],
                            "reason": info["reason"]
                        })
        return sorted(backups, key=lambda x: x["date"], reverse=True)
    
    def restore(self, backup_id: str, target_dir: str):
        """
        恢复指定备份
        
        确保 SQLite 和 ChromaDB 数据一致
        """
        backup_path = self.backup_dir / backup_id
        
        # 1. 备份当前状态（安全措施）
        self._backup_current_state()
        
        # 2. 恢复 SQLite
        self._restore_sqlite(backup_path / "memory.db")
        
        # 3. 恢复 ChromaDB
        self._restore_vector_db(backup_path / "vector_db")
        
        # 4. 恢复核心文件
        self._restore_core_files(backup_path / "core_files", target_dir)
        
        # 5. 验证一致性
        self._verify_consistency()
    
    def _restore_sqlite(self, db_path: Path):
        """恢复 SQLite 数据库"""
        import shutil
        shutil.copy(db_path, "data/memory/memory.db")
    
    def _restore_vector_db(self, vector_path: Path):
        """恢复 ChromaDB"""
        import shutil
        if Path("data/memory/vector_db").exists():
            shutil.rmtree("data/memory/vector_db")
        shutil.copytree(vector_path, "data/memory/vector_db")
    
    def _verify_consistency(self):
        """验证恢复后的一致性"""
        checker = ConsistencyChecker()
        results = checker.check_all()
        
        if results["missing_in_vector"] or results["missing_in_sqlite"]:
            raise RestoreError("恢复后数据不一致，请手动检查")
        
        print("✓ 恢复成功，数据一致性验证通过")
```

### 11.4 使用示例

```bash
# 创建备份
python -m persistent_memory.backup --create --reason "重大决策更新"

# 列出所有备份
python -m persistent_memory.backup --list

# 恢复最新备份
python -m persistent_memory.backup --restore --latest

# 恢复指定备份
python -m persistent_memory.backup --restore --id backup_20260220_030000

# 清理旧备份
python -m persistent_memory.backup --cleanup
```

## 十二、与 OpenClaw 现有架构的集成

### 12.1 集成架构

```
┌─────────────────────────────────────────────────────────────┐
│                    OpenClaw 架构                          │
├─────────────────────────────────────────────────────────────┤
│  Gateway                                           │
│    │                                                 │
│    ▼                                                 │
│  Agent (RUNBOT / ARC / DEV / ASS)                    │
│    │                                                 │
│    ├─────────────────────────────────────────────────┤
│    │                                                 │
│    ▼                                                 │
│  ┌─────────────────────────────────────────────┐      │
│  │        Persistent Memory System               │      │
│  │  ┌─────────────┐    ┌─────────────┐        │      │
│  │  │   SQLite    │ +  │  ChromaDB  │        │      │
│  │  └─────────────┘    └─────────────┘        │      │
│  └─────────────────────────────────────────────┘      │
│                                                     │
└─────────────────────────────────────────────────────────────┘
```

### 12.2 统一记忆 API 设计

```python
# persistent_memory/api.py
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional, List

app = FastAPI(
    title="Persistent Memory API",
    description="OpenClaw 统一记忆服务",
    version="1.0.0"
)

class MemoryCreate(BaseModel):
    key: str
    value: str
    tags: Optional[List[str]] = []
    importance: Optional[int] = 5
    metadata: Optional[dict] = None

class MemoryResponse(BaseModel):
    id: str
    key: str
    value: str
    tags: List[str]
    importance: int
    created_at: str
    version: int

@app.post("/memories", response_model=MemoryResponse)
async def create_memory(data: MemoryCreate):
    """创建记忆"""
    memory = await memory_system.add(
        key=data.key,
        value=data.value,
        tags=data.tags,
        importance=data.importance,
        metadata=data.metadata
    )
    return memory

@app.get("/memories/{memory_id}", response_model=MemoryResponse)
async def get_memory(memory_id: str):
    """获取记忆"""
    memory = await memory_system.get(memory_id)
    if not memory:
        raise HTTPException(status_code=404, detail="记忆不存在")
    return memory

@app.get("/memories/search")
async def search_memories(
    q: str,
    mode: str = "auto",  # exact, semantic, hybrid
    limit: int = 20
):
    """搜索记忆"""
    results = await memory_system.search(q, mode=mode, limit=limit)
    return {"results": results}

@app.delete("/memories/{memory_id}")
async def delete_memory(memory_id: str):
    """删除记忆"""
    await memory_system.delete(memory_id)
    return {"status": "deleted"}
```

### 12.3 与 Agent 集成

```python
# persistent_memory/agent_integration.py
class AgentMemoryIntegration:
    """Agent 与记忆系统的集成"""
    
    def __init__(self, agent_type: str):
        self.agent_type = agent_type
        self.memory = PersistentMemory()
    
    async def save_context(self, context: dict):
        """保存上下文到记忆系统"""
        await self.memory.add(
            key=f"context:{self.agent_type}:{context['session_id']}",
            value=json.dumps(context),
            tags=["context", self.agent_type],
            importance=8
        )
    
    async def load_context(self, session_id: str) -> dict:
        """加载上下文"""
        key = f"context:{self.agent_type}:{session_id}"
        result = await self.memory.get(key)
        return json.loads(result.value) if result else {}
    
    async def save_decision(self, decision: dict):
        """保存决策"""
        await self.memory.add(
            key=f"decision:{decision['id']}",
            value=json.dumps(decision),
            tags=["decision", decision.get("type", "general")],
            importance=10  # 决策最高优先级
        )
    
    async def get_relevant_knowledge(self, query: str) -> list:
        """获取相关知识"""
        return await self.memory.search(query, mode="hybrid")
```

### 12.4 与 Gateway 集成

```python
# persistent_memory/gateway_integration.py
class GatewayMemoryIntegration:
    """Gateway 与记忆系统的集成"""
    
    def __init__(self):
        self.memory = PersistentMemory()
    
    def on_session_start(self, session_id: str):
        """会话开始时加载上下文"""
        return self.memory.load_context(session_id)
    
    def on_session_end(self, session_id: str):
        """会话结束时保存状态"""
        self.memory.save_context(session_id, self._collect_session_state())
    
    def on_decision_made(self, decision: dict):
        """关键决策自动保存"""
        self.memory.save_decision(decision)
    
    def on_error(self, error: dict):
        """错误发生时的上下文保存"""
        self.memory.add(
            key=f"error:{error['timestamp']}",
            value=json.dumps(error),
            tags=["error", error.get("type")],
            importance=9
        )
```

### 12.5 事件驱动集成

```python
# persistent_memory/events.py
from enum import Enum
from typing import Callable

class MemoryEvent(Enum):
    MEMORY_CREATED = "memory.created"
    MEMORY_UPDATED = "memory.updated"
    MEMORY_DELETED = "memory.deleted"
    SESSION_START = "session.start"
    SESSION_END = "session.end"
    DECISION_MADE = "decision.made"

class EventBus:
    """事件总线"""
    
    def __init__(self):
        self.subscribers = {}
    
    def subscribe(self, event: MemoryEvent, handler: Callable):
        """订阅事件"""
        if event not in self.subscribers:
            self.subscribers[event] = []
        self.subscribers[event].append(handler)
    
    def publish(self, event: MemoryEvent, data: dict):
        """发布事件"""
        if event in self.subscribers:
            for handler in self.subscribers[event]:
                handler(data)

# 使用示例
event_bus = EventBus()

# 自动备份事件
def auto_backup_on_decision(data):
    if data.get("importance", 0) >= 9:
        backup_manager.create_backup(reason=f"重要决策: {data['id']}")

event_bus.subscribe(MemoryEvent.DECISION_MADE, auto_backup_on_decision)
```

### 12.6 集成配置

```yaml
# config/memory_integration.yaml
openclaw:
  gateway:
    enabled: true
    on_session_start: true
    on_session_end: true
    on_decision_made: true
  
  agent:
    enabled: true
    auto_save_context: true
    context_ttl: 86400  # 24小时
  
  events:
    enabled: true
    backup_on_decision: true
    backup_on_memory_change: false

backup:
  enabled: true
  schedule: "0 3 * * *"  # 每日3点
  retention_days: 30
  on_decision: true

api:
  host: "0.0.0.0"
  port: 8080
  enabled: false  # 默认关闭，按需开启
```

---

> **补充章节版本**: v1.0
> **创建日期**: 2026-02-20
> **包含**: 数据一致性、检索策略、备份机制、OpenClaw 集成
