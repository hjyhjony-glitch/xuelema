# Persistent Memory System - 详细开发计划

> **RUNBOT-ARC（青岩）项目总监制定**
> **版本**: v1.0
> **日期**: 2026-02-20
> **状态**: 待评审

---

## 一、项目概述

### 1.1 目标
构建一个轻量级、零配置的持久化记忆系统，支持长期记忆、结构化数据存储和跨会话知识管理。

### 1.2 技术栈
- **SQLite**: 结构化数据存储（对话、目标、元数据）
- **ChromaDB**: 向量存储（语义搜索、相似度匹配）
- **文件系统**: 原始对话快照、知识库 Markdown 文件

### 1.3 依赖关系图

```
Phase 1 (基础架构)
├── 目录结构创建  ←──────────┐
├── SQLite 存储层 ←────────┐ │
├── ChromaDB 向量存储 ←──┐ │ │
├── 基础 CRUD API ←─────┐ │ │ │
├── WAL Protocol ←─────┘ │ │ │
├── 标签系统 ←──────────┘ │ │
├── 单元测试 ←─────────────┘ │
└── 集成测试 ←───────────────┘

Phase 2 (对话系统) ──→ Phase 1 完成
Phase 3 (目标追踪) ──→ Phase 1 完成
Phase 4 (知识库)   ──→ Phase 1 + Phase 2
Phase 5 (运维工具) ──→ Phase 1-4 完成
```

---

## 二、Phase 1: 基础架构 (P0)

**优先级**: 🔴 紧急  
**预计工期**: 1 周  
**负责人**: DEV

### 2.1 任务清单与工时评估

| 任务 ID | 任务名称 | 优先级 | 工时 (h) | 依赖 | 负责人 |
|---------|----------|--------|----------|------|--------|
| T1.1 | 创建 .memory/ 目录结构 | P0 | 2 | 无 | DEV |
| T1.2 | 实现 SQLite 存储层 | P0 | 8 | T1.1 | DEV |
| T1.3 | 实现 ChromaDB 向量存储 | P0 | 6 | T1.1 | DEV |
| T1.4 | 实现基础 CRUD API | P0 | 8 | T1.2, T1.3 | DEV |
| T1.5 | 实现 WAL Protocol | P0 | 4 | T1.4 | DEV |
| T1.6 | 实现标签系统 | P0 | 6 | T1.4 | DEV |
| T1.7 | 单元测试 | P0 | 8 | T1.2-T1.6 | DEV |
| T1.8 | 集成测试 | P0 | 4 | T1.7 | DEV |

**小计**: 46 工时（≈ 6 人天）

### 2.2 详细任务说明

#### T1.1: 创建 .memory/ 目录结构

**输出**: 目录结构 + init.py

```
.memory/
├── conversations/
│   ├── raw/
│   │   └── _index.json
│   └── tagged/
│       ├── important/
│       ├── decision/
│       └── todo/
├── goals/
│   ├── annual/
│   ├── quarterly/
│   ├── monthly/
│   ├── _闭环/
│   │   ├── daily_checkin/
│   │   ├── weekly_review/
│   │   ├── monthly_review/
│   │   └── quarterly_review/
│   └── _templates/
├── knowledge/
│   ├── topics/
│   ├── resources/
│   └── _index/
├── _index/
│   ├── tags.yaml
│   ├── keywords.yaml
│   ├── timelines.yaml
│   └── _wal/
├── _backup/
│   ├── daily/
│   ├── weekly/
│   └── versions/
└── _archive/
```

**验收标准**:
- [ ] 所有目录创建成功
- [ ] 目录权限正确（读写）
- [ ] init.py 可执行

**测试用例**:
```python
def test_directory_structure():
    pm = PersistentMemory('.memory')
    assert (pm.root / "conversations").exists()
    assert (pm.root / "goals").exists()
    assert (pm.root / "knowledge").exists()
```

#### T1.2: 实现 SQLite 存储层

**输出**: `core/sqlite_storage.py`

**核心功能**:
```python
class SQLiteStorage:
    def __init__(self, db_path: str):
        self.conn = sqlite3.connect(db_path)
        self._init_tables()
    
    def _init_tables(self):
        """初始化表结构"""
        # memories: 记忆主表
        # conversations: 对话表
        # goals: 目标表
        # tags: 标签表
        # wal_logs: WAL 日志表
    
    def insert_memory(self, memory_id: str, content: str, 
                      memory_type: str, metadata: dict) -> bool:
        """插入记忆"""
    
    def get_memory(self, memory_id: str) -> Optional[dict]:
        """获取记忆"""
    
    def update_memory(self, memory_id: str, content: str) -> bool:
        """更新记忆"""
    
    def delete_memory(self, memory_id: str) -> bool:
        """删除记忆"""
    
    def search_by_tag(self, tag: str) -> List[dict]:
        """按标签搜索"""
    
    def search_by_time_range(self, start: str, end: str) -> List[dict]:
        """按时间范围搜索"""
```

**验收标准**:
- [ ] 创建 5 张核心表
- [ ] CRUD 操作成功率 100%
- [ ] 支持事务
- [ ] 索引正确创建

**测试用例**:
```python
def test_sqlite_crud():
    storage = SQLiteStorage(':memory:')
    
    # Create
    assert storage.insert_memory('test_id', 'test content', 'conversation', {})
    
    # Read
    memory = storage.get_memory('test_id')
    assert memory['content'] == 'test content'
    
    # Update
    assert storage.update_memory('test_id', 'updated content')
    assert storage.get_memory('test_id')['content'] == 'updated content'
    
    # Delete
    assert storage.delete_memory('test_id')
    assert storage.get_memory('test_id') is None

def test_sqlite_transactions():
    storage = SQLiteStorage(':memory:')
    
    with storage.transaction():
        storage.insert_memory('id1', 'content1', 'goal', {})
        storage.insert_memory('id2', 'content2', 'goal', {})
        # 模拟失败
        raise Exception("rollback test")
    
    assert storage.get_memory('id1') is None
    assert storage.get_memory('id2') is None
```

#### T1.3: 实现 ChromaDB 向量存储

**输出**: `core/vector_storage.py`

**核心功能**:
```python
class VectorStorage:
    def __init__(self, persist_dir: str):
        self.client = chromadb.PersistentClient(path=persist_dir)
        self._init_collections()
    
    def _init_collections(self):
        """初始化集合"""
        # conversations: 对话向量
        # goals: 目标向量
        # knowledge: 知识向量
    
    def add_embedding(self, collection_name: str, doc_id: str, 
                      content: str, metadata: dict = None):
        """添加向量"""
    
    def search(self, query: str, collection_name: str = None, 
               n_results: int = 5) -> List[dict]:
        """语义搜索"""
    
    def delete(self, collection_name: str, doc_id: str):
        """删除向量"""
    
    def update(self, collection_name: str, doc_id: str, 
               content: str, metadata: dict = None):
        """更新向量"""
```

**验收标准**:
- [ ] 创建 3 个集合
- [ ] 向量添加/搜索正常
- [ ] 支持更新/删除
- [ ] 持久化存储

**测试用例**:
```python
def test_vector_add_and_search():
    vs = VectorStorage(':memory:')
    
    # Add
    vs.add_embedding('knowledge', 'doc1', 'Python best practices', {'tags': ['python']})
    vs.add_embedding('knowledge', 'doc2', 'SQL optimization techniques', {'tags': ['sql']})
    
    # Search
    results = vs.search('python coding', n_results=1)
    assert len(results) > 0
    assert 'python' in results[0]['content'].lower()

def test_vector_update():
    vs = VectorStorage(':memory:')
    vs.add_embedding('knowledge', 'doc1', 'Original content')
    
    vs.update('knowledge', 'doc1', 'Updated content')
    
    results = vs.search('Updated content')
    assert len(results) == 1
```

#### T1.4: 实现基础 CRUD API

**输出**: `persistent_memory.py`

**核心功能**:
```python
class PersistentMemory:
    def __init__(self, root_path: str = './.memory'):
        self.sqlite = SQLiteStorage(...)
        self.vector = VectorStorage(...)
        self.wal = WALHandler(...)
    
    # ========== Memory Operations ==========
    def save_memory(self, memory_id: str, content: str, 
                    memory_type: str, tags: List[str] = None,
                    metadata: dict = None) -> bool:
        """保存记忆（原子操作）"""
    
    def get_memory(self, memory_id: str) -> Optional[dict]:
        """获取记忆"""
    
    def update_memory(self, memory_id: str, content: str,
                      tags: List[str] = None) -> bool:
        """更新记忆"""
    
    def delete_memory(self, memory_id: str) -> bool:
        """删除记忆"""
    
    def search_memories(self, query: str = None, 
                        filters: dict = None,
                        limit: int = 10) -> List[dict]:
        """复合搜索"""
    
    # ========== Tag Operations ==========
    def add_tags(self, memory_id: str, tags: List[str]) -> bool:
        """添加标签"""
    
    def remove_tags(self, memory_id: str, tags: List[str]) -> bool:
        """移除标签"""
    
    def get_memories_by_tag(self, tag: str) -> List[dict]:
        """按标签获取记忆"""
```

**验收标准**:
- [ ] save_memory 原子性保证
- [ ] 搜索支持多条件组合
- [ ] 标签操作正确维护索引
- [ ] 错误处理完善

**测试用例**:
```python
def test_save_memory_atomic():
    pm = PersistentMemory(':memory:')
    
    # 模拟失败场景
    result = pm.save_memory('test', 'content', 'conversation', ['important'])
    assert result is True
    
    memory = pm.get_memory('test')
    assert memory['content'] == 'content'
    assert 'important' in memory['tags']

def test_search_with_filters():
    pm = PersistentMemory(':memory:')
    
    pm.save_memory('m1', 'Python tutorial', 'knowledge', ['python', 'tutorial'])
    pm.save_memory('m2', 'Java tutorial', 'knowledge', ['java', 'tutorial'])
    
    # 标签过滤
    results = pm.search_memories(filters={'tags': ['python']})
    assert len(results) == 1
    assert 'python' in results[0]['tags']
```

#### T1.5: 实现 WAL Protocol

**输出**: `core/wal.py`

**核心功能**:
```python
class WALHandler:
    """Write-Ahead Log Protocol"""
    
    def __init__(self, wal_dir: str):
        self.wal_dir = wal_dir
        self._init_wal_dir()
    
    def log(self, operation: str, data: dict):
        """记录操作日志"""
        entry = {
            'timestamp': datetime.now().isoformat(),
            'seq': self._get_next_seq(),
            'op': operation,
            **data
        }
        # 写入临时文件 → 重命名
        self._write_atomic(entry)
    
    def replay(self, storage: 'Storage') -> int:
        """重放日志恢复数据"""
        # 按序列号顺序重放
        # 成功后清理日志
        pass
    
    def checkpoint(self):
        """检查点：同步 WAL 到主存储"""
        # 批量应用日志
        # 生成检查点文件
        pass
```

**验收标准**:
- [ ] 日志按序列号排序
- [ ] 支持重放恢复
- [ ] 原子写入（先 temp 后 rename）
- [ ] 日志自动清理

**测试用例**:
```python
def test_wal_atomic_write():
    wal = WALHandler(':memory:/wal')
    
    wal.log('CREATE', {'type': 'memory', 'id': 'm1', 'content': 'test'})
    
    # 验证文件存在
    assert len(os.listdir(':memory:/wal')) == 1

def test_wal_replay():
    wal = WALHandler(':memory:/wal')
    storage = SQLiteStorage(':memory:')
    
    # 写入数据
    wal.log('CREATE', {'type': 'memory', 'id': 'm1', 'content': 'test'})
    
    # 重放
    count = wal.replay(storage)
    assert count == 1
    assert storage.get_memory('m1')['content'] == 'test'
```

#### T1.6: 实现标签系统

**输出**: `core/tag_system.py`

**核心功能**:
```python
class TagSystem:
    """标签系统"""
    
    def __init__(self, sqlite: SQLiteStorage):
        self.sqlite = sqlite
    
    def create_tag(self, tag_name: str, category: str = None,
                   aliases: List[str] = None) -> bool:
        """创建标签"""
    
    def assign_tags(self, memory_id: str, tags: List[str]) -> bool:
        """分配标签"""
    
    def remove_tags(self, memory_id: str, tags: List[str]) -> bool:
        """移除标签"""
    
    def suggest_tags(self, content: str) -> List[str]:
        """自动建议标签"""
        # 基于关键词匹配
        # 基于历史使用频率
        pass
    
    def get_tag_hierarchy(self) -> dict:
        """获取标签层级"""
    
    def search_by_tag(self, tag: str, recursive: bool = True) -> List[dict]:
        """搜索标签（含子标签）"""
```

**验收标准**:
- [ ] 标签创建/分配/移除正常
- [ ] 自动建议功能可用
- [ ] 标签别名支持
- [ ] 层级标签支持

**测试用例**:
```python
def test_tag_assignment():
    tag_sys = TagSystem(sqlite)
    
    tag_sys.create_tag('python', category='programming')
    tag_sys.create_tag('important', category='priority')
    
    tag_sys.assign_tags('m1', ['python', 'important'])
    
    memory = sqlite.get_memory('m1')
    assert 'python' in memory['tags']
    assert 'important' in memory['tags']

def test_tag_suggestions():
    tag_sys = TagSystem(sqlite)
    
    suggestions = tag_sys.suggest_tags('Learn Python programming today')
    assert 'python' in suggestions
```

#### T1.7: 单元测试

**输出**: `tests/test_*.py`

**测试覆盖**:
- SQLite 存储层（CRUD、事务、索引）
- 向量存储（添加、搜索、更新、删除）
- WAL Protocol（日志、恢复、检查点）
- 标签系统（创建、分配、建议）
- 基础 API（所有公共方法）

**测试用例清单**:

| 模块 | 测试用例数 | 关键测试 |
|------|------------|----------|
| SQLite | 15 | 事务回滚、并发插入、索引查询 |
| Vector | 12 | 向量搜索、相似度阈值、批量操作 |
| WAL | 8 | 原子写入、日志重放、序列号 |
| Tags | 10 | 层级查询、别名展开、自动建议 |
| API | 20 | 边界条件、错误处理、并发 |

**验收标准**:
- [ ] 测试覆盖率 ≥ 80%
- [ ] 所有测试用例通过
- [ ] 无内存泄漏
- [ ] CI/CD 通过

#### T1.8: 集成测试

**输出**: `tests/test_integration.py`

**测试场景**:
1. **完整工作流测试**: 保存 → 搜索 → 更新 → 删除
2. **数据一致性测试**: SQLite 与 ChromaDB 数据同步
3. **故障恢复测试**: 模拟崩溃后的数据恢复
4. **并发测试**: 多线程/进程同时读写
5. **大规模数据测试**: 1000+ 记忆的搜索性能

**验收标准**:
- [ ] 完整工作流测试通过
- [ ] 数据一致性验证通过
- [ ] 故障恢复时间 < 5 秒
- [ ] 并发测试无死锁
- [ ] 搜索响应时间 < 100ms（1000条数据）

---

## 三、Phase 2: 对话系统 (P1)

**优先级**: 🟠 重要  
**预计工期**: 1 周  
**负责人**: DEV

### 3.1 任务清单

| 任务 ID | 任务名称 | 优先级 | 工时 (h) | 依赖 |
|---------|----------|--------|----------|------|
| T2.1 | 实现对话目录结构 | P1 | 2 | T1.1 |
| T2.2 | 实现 FeishuSync 对话同步 | P1 | 8 | T2.1 |
| T2.3 | 实现对话标记功能 | P1 | 4 | T2.2 |
| T2.4 | 实现对话索引 | P1 | 4 | T2.2 |
| T2.5 | 对话系统单元测试 | P1 | 6 | T2.1-T2.4 |

### 3.2 验收标准

- [ ] 自动拉取飞书对话
- [ ] 重要对话自动标记
- [ ] 对话搜索功能
- [ ] 每日对话归档

---

## 四、Phase 3: 目标追踪 (P1)

**优先级**: 🟠 重要  
**预计工期**: 1 周  
**负责人**: DEV

### 4.1 任务清单

| 任务 ID | 任务名称 | 优先级 | 工时 (h) | 依赖 |
|---------|----------|--------|----------|------|
| T3.1 | 实现目标目录结构 | P1 | 2 | T1.1 |
| T3.2 | 实现目标 CRUD | P1 | 6 | T1.4 |
| T3.3 | 实现每日签到 | P1 | 4 | T3.2 |
| T3.4 | 实现周/月回顾模板 | P1 | 6 | T3.2 |
| T3.5 | 实现闭环统计 | P1 | 4 | T3.3 |
| T3.6 | 目标追踪单元测试 | P1 | 6 | T3.1-T3.5 |

### 4.2 验收标准

- [ ] 目标创建/更新/完成
- [ ] 每日签到记录
- [ ] 周/月回顾生成
- [ ] 进度追踪统计

---

## 五、Phase 4: 知识库 (P2)

**优先级**: 🟡 可选  
**预计工期**: 1 周  
**负责人**: DEV + ASS

### 5.1 任务清单

| 任务 ID | 任务名称 | 优先级 | 工时 (h) | 依赖 |
|---------|----------|--------|----------|------|
| T4.1 | 实现知识目录结构 | P2 | 2 | T1.1 |
| T4.2 | 实现 Markdown 知识存储 | P2 | 4 | T1.4 |
| T4.3 | 实现语义搜索 | P2 | 8 | T1.3 |
| T4.4 | 实现资源引用管理 | P2 | 4 | T4.2 |
| T4.5 | 编写知识库文档 | P2 | 8 | T4.1-T4.4 |
| T4.6 | 知识库单元测试 | P2 | 4 | T4.1-T4.4 |

### 5.2 验收标准

- [ ] 知识条目创建/编辑
- [ ] 语义搜索准确率 > 80%
- [ ] 资源链接管理
- [ ] 文档完整

---

## 六、Phase 5: 运维工具 (P2)

**优先级**: 🟡 可选  
**预计工期**: 1 周  
**负责人**: ASS

### 6.1 任务清单

| 任务 ID | 任务名称 | 优先级 | 工时 (h) | 依赖 |
|---------|----------|--------|----------|------|
| T5.1 | 实现自动备份 | P2 | 6 | T1.2 |
| T5.2 | 实现归档清理 | P2 | 6 | T1.2 |
| T5.3 | 编写 CLI 工具 | P2 | 4 | T5.1, T5.2 |
| T5.4 | 编写使用文档 | P2 | 8 | All |
| T5.5 | 部署脚本 | P2 | 2 | T5.3 |

### 6.2 验收标准

- [ ] 每日自动备份
- [ ] 旧数据自动归档
- [ ] CLI 工具可用
- [ ] 文档完整清晰

---

## 七、资源分配

### 7.1 开发资源

| 角色 | 任务分配 | 工期 |
|------|----------|------|
| DEV (编码) | T1.1-T1.8, T2.1-T2.5, T3.1-T3.6, T4.1-T4.6 | 6 周 |
| ASS (文档) | T4.5, T5.4, T5.5 | 2 周 |

### 7.2 依赖库

```txt
# requirements.txt
pyyaml>=6.0
chromadb>=0.4.0
sqlite3 (内置)
```

---

## 八、风险与缓解

| 风险 | 影响 | 缓解措施 |
|------|------|----------|
| ChromaDB 依赖问题 | 中 | 保留纯文件模式作为备选 |
| 向量搜索质量 | 中 | 定期评估并调整 embedding |
| 数据量增长 | 低 | 归档策略自动执行 |
| 并发写入冲突 | 中 | WAL + 事务保证一致性 |

---

## 九、里程碑

| 里程碑 | 日期 | 交付物 |
|--------|------|--------|
| M1: 目录就绪 | D+1 | 目录结构 + init.py |
| M2: 核心 API | D+7 | persistent_memory.py |
| M3: 对话同步 | D+14 | FeishuSync.py |
| M4: 目标追踪 | D+21 | goals/ 模板 |
| M5: 知识库 | D+28 | 语义搜索功能 |
| M6: 运维工具 | D+35 | 备份/归档脚本 |
| M7: 文档完成 | D+40 | 使用文档 |

---

## 十、审批

| 角色 | 姓名 | 日期 | 签名 |
|------|------|------|------|
| 项目总监 | RUNBOT-ARC | 2026-02-20 | 待审批 |
| 开发负责人 | ______ | ______ | ______ |
| 产品负责人 | ______ | ______ | ______ |

---

> **文档版本**: v1.0
> **最后更新**: 2026-02-20
> **维护者**: RUNBOT-ARC（青岩）
