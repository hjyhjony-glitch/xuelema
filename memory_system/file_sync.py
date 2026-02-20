"""
文件同步模块
将数据库数据同步到 .md 文件
"""
import os
import json
from datetime import datetime
from typing import Any, Dict, List, Optional
from pathlib import Path


class FileSync:
    """
    文件同步器
    
    将 SQLite 中的数据同步到 .md 文件：
    - 每日对话 → memory/YYYY-MM-DD.md
    - 重要决策 → memory/decisions.md
    - 长期记忆 → MEMORY.md
    - 开发日志 → memory/DEVELOPMENT_LOG.md
    """
    
    def __init__(self, base_path: str = None):
        self.base_path = base_path or os.path.dirname(os.path.dirname(__file__))
        self.memory_path = os.path.join(self.base_path, 'memory')
        self.memory_file = os.path.join(self.base_path, 'MEMORY.md')
        
        # 确保目录存在
        os.makedirs(self.memory_path, exist_ok=True)
    
    def sync_all(self, memory_type: str = None) -> Dict:
        """
        同步所有数据到文件
        
        Args:
            memory_type: 可选，只同步特定类型
        
        Returns:
            Dict: 同步统计
        """
        from memory_system.unified_api import get_unified_memory
        
        um = get_unified_memory()
        records = um.load(memory_type=memory_type, limit=9999)
        
        stats = {
            "total": len(records),
            "conversations": 0,
            "decisions": 0,
            "knowledge": 0,
            "other": 0
        }
        
        for record in records:
            mem_type = record.get('memory_type', 'custom')
            key = record.get('key', record.get('id', 'unknown'))
            value = record.get('value', '')
            tags = record.get('tags', [])
            metadata = record.get('metadata', {})
            
            if mem_type == 'conversation':
                self._sync_conversation(key, value, tags, metadata)
                stats["conversations"] += 1
            elif mem_type == 'decision':
                self._sync_decision(key, value, tags, metadata)
                stats["decisions"] += 1
            elif mem_type == 'knowledge':
                self._sync_knowledge(key, value, tags, metadata)
                stats["knowledge"] += 1
            else:
                self._sync_other(key, value, mem_type, tags, metadata)
                stats["other"] += 1
        
        return stats
    
    def _sync_conversation(
        self,
        key: str,
        value: Any,
        tags: List[str],
        metadata: Dict
    ):
        """同步对话到每日文件"""
        date = metadata.get('date', datetime.now().strftime('%Y-%m-%d'))
        file_path = os.path.join(self.memory_path, f'{date}.md')
        
        content = self._format_record(
            key=key,
            value=value,
            tags=tags,
            metadata=metadata
        )
        
        with open(file_path, 'a', encoding='utf-8') as f:
            f.write(content)
    
    def _sync_decision(
        self,
        key: str,
        value: Any,
        tags: List[str],
        metadata: Dict
    ):
        """同步决策到专门文件"""
        file_path = os.path.join(self.memory_path, 'decisions.md')
        
        # 检查文件是否存在，不存在则创建头部
        if not os.path.exists(file_path):
            self._create_header(file_path, "# 重要决策记录", "decision")
        
        content = self._format_record(
            key=key,
            value=value,
            tags=tags,
            metadata=metadata
        )
        
        with open(file_path, 'a', encoding='utf-8') as f:
            f.write(content)
    
    def _sync_knowledge(
        self,
        key: str,
        value: Any,
        tags: List[str],
        metadata: Dict
    ):
        """同步知识到知识库"""
        # 根据标签分类
        topic = metadata.get('topic', 'general')
        file_path = os.path.join(self.memory_path, 'knowledge', f'{topic}.md')
        
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        
        if not os.path.exists(file_path):
            self._create_header(file_path, f"# {topic} 知识库", "knowledge")
        
        content = self._format_record(
            key=key,
            value=value,
            tags=tags,
            metadata=metadata
        )
        
        with open(file_path, 'a', encoding='utf-8') as f:
            f.write(content)
    
    def _sync_other(
        self,
        key: str,
        value: Any,
        memory_type: str,
        tags: List[str],
        metadata: Dict
    ):
        """同步其他类型"""
        date = datetime.now().strftime('%Y-%m-%d')
        file_path = os.path.join(self.memory_path, f'{date}_{memory_type}.md')
        
        content = self._format_record(
            key=key,
            value=value,
            tags=tags,
            metadata=metadata
        )
        
        with open(file_path, 'a', encoding='utf-8') as f:
            f.write(content)
    
    def _format_record(
        self,
        key: str,
        value: Any,
        tags: List[str],
        metadata: Dict
    ) -> str:
        """格式化记录"""
        timestamp = metadata.get('created_at', datetime.now().isoformat())
        
        # 序列化 value
        if not isinstance(value, str):
            value = json.dumps(value, ensure_ascii=False, indent=2)
        
        return f"""---
timestamp: {timestamp}
key: {key}
tags: {', '.join(tags)}
---

## {key}

```
{value}
```

"""
    
    def _create_header(self, file_path: str, title: str, type_name: str):
        """创建文件头部"""
        header = f"""{title}

*自动生成，请勿手动编辑*

---
"""
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(header)
    
    def sync_to_memory_md(self, content: str):
        """
        同步长期记忆到 MEMORY.md
        
        Args:
            content: 记忆内容
        """
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        new_content = f"""---
updated: {timestamp}
---

{content}

---
*Last updated: {timestamp}*
"""
        
        with open(self.memory_file, 'w', encoding='utf-8') as f:
            f.write(new_content)
    
    def export_all(self, output_path: str = None) -> str:
        """
        导出所有数据为 JSON
        
        Args:
            output_path: 输出路径
        
        Returns:
            str: 导出文件路径
        """
        from memory_system.unified_api import get_unified_memory
        
        um = get_unified_memory()
        records = um.load(limit=9999)
        
        export_data = {
            "export_date": datetime.now().isoformat(),
            "total_records": len(records),
            "records": records
        }
        
        output_path = output_path or os.path.join(
            self.memory_path, 
            f'export_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
        )
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, ensure_ascii=False, indent=2)
        
        return output_path


# 全局实例
_file_sync = None

def get_file_sync(base_path: str = None) -> FileSync:
    """获取文件同步器实例"""
    global _file_sync
    if _file_sync is None:
        _file_sync = FileSync(base_path)
    return _file_sync
