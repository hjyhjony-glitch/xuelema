#!/usr/bin/env python3
"""
Conversation - 对话存储模块
==========================
管理对话的持久化存储

功能:
1. 对话 CRUD 操作
2. 对话索引管理
3. 对话搜索
4. 对话归档

作者: RUNBOT-DEV（笑天）
版本: v1.0
日期: 2026-02-20
"""

import json
import logging
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
from threading import Lock

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@dataclass
class Message:
    """消息数据类"""
    id: str
    role: str  # user / assistant / system
    content: str
    timestamp: str
    sender_id: Optional[str] = None
    sender_name: Optional[str] = None
    message_type: str = "text"
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class Conversation:
    """对话数据类"""
    id: str
    channel_id: str
    source: str = "feishu"
    messages: List[Message] = field(default_factory=list)
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    updated_at: str = field(default_factory=lambda: datetime.now().isoformat())
    metadata: Dict[str, Any] = field(default_factory=dict)
    summary: Optional[str] = None
    tags: List[str] = field(default_factory=list)
    title: Optional[str] = None


class ConversationStorage:
    """
    对话存储管理器
    
    Attributes:
        root_path: 存储根目录
        raw_dir: 原始对话目录
        tagged_dir: 标记对话目录
        index_file: 索引文件路径
    """
    
    def __init__(
        self,
        root_path: str = "./.memory",
        raw_dir: str = "conversations/raw",
        tagged_dir: str = "conversations/tagged"
    ):
        """
        初始化 ConversationStorage
        
        Args:
            root_path: 存储根目录
            raw_dir: 原始对话目录（相对路径）
            tagged_dir: 标记对话目录（相对路径）
        """
        self.root_path = Path(root_path)
        self.raw_dir = self.root_path / raw_dir
        self.tagged_dir = self.root_path / tagged_dir
        self.index_file = self.root_path / "conversations" / "_index.json"
        
        # 线程安全锁
        self._lock = Lock()
        
        # 确保目录存在
        self._ensure_directories()
        
        logger.info(f"ConversationStorage 初始化完成")
        logger.info(f"原始对话目录: {self.raw_dir}")
        logger.info(f"标记对话目录: {self.tagged_dir}")
    
    def _ensure_directories(self) -> None:
        """确保存储目录存在"""
        dirs = [
            self.raw_dir / "{year}" / "{month}",
            self.tagged_dir / "important",
            self.tagged_dir / "decision",
            self.tagged_dir / "todo",
            self.tagged_dir / "question",
            self.tagged_dir / "general",
        ]
        
        for dir_path in dirs:
            if isinstance(dir_path, Path):
                dir_path.mkdir(parents=True, exist_ok=True)
            else:
                Path(dir_path).mkdir(parents=True, exist_ok=True)
    
    def _parse_date_path(self, date: str) -> Tuple[str, str]:
        """
        解析日期路径
        
        Args:
            date: 日期字符串 (YYYY-MM-DD)
            
        Returns:
            Tuple[str, str]: (年份, 月份)
        """
        parts = date.split("-")
        if len(parts) >= 2:
            return parts[0], parts[1]
        return datetime.now().strftime("%Y"), datetime.now().strftime("%m")
    
    def _build_raw_path(self, date: str) -> Path:
        """
        构建原始对话文件路径
        
        Args:
            date: 日期字符串
            
        Returns:
            Path: 文件路径
        """
        year, month = self._parse_date_path(date)
        dir_path = self.raw_dir / year / month
        dir_path.mkdir(parents=True, exist_ok=True)
        return dir_path / f"{date}.json"
    
    def _build_tagged_path(self, date: str, conversation_id: str, tag: str) -> Path:
        """
        构建标记对话文件路径
        
        Args:
            date: 日期字符串
            conversation_id: 对话ID
            tag: 标签
            
        Returns:
            Path: 文件路径
        """
        safe_tag = tag.replace("/", "_").replace(" ", "-")
        tag_dir = self.tagged_dir / safe_tag
        tag_dir.mkdir(parents=True, exist_ok=True)
        return tag_dir / f"{date}_{conversation_id}.md"
    
    # ============ CRUD Operations ============
    
    def save(self, conversation: Conversation) -> bool:
        """
        保存对话
        
        Args:
            conversation: Conversation 对象
            
        Returns:
            bool: 是否保存成功
        """
        with self._lock:
            try:
                # 提取日期
                date = self._extract_date(conversation)
                file_path = self._build_raw_path(date)
                
                # 转换为字典
                data = self._conversation_to_dict(conversation)
                
                # 写入文件
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(data, f, ensure_ascii=False, indent=2)
                
                # 更新索引
                self._update_index(conversation, date)
                
                logger.debug(f"对话已保存: {conversation.id}")
                return True
                
            except Exception as e:
                logger.error(f"保存对话失败: {e}")
                return False
    
    def load(self, date: str, conversation_id: str = None) -> Optional[Conversation]:
        """
        加载对话
        
        Args:
            date: 日期字符串
            conversation_id: 对话ID（可选，如果提供则只加载该对话）
            
        Returns:
            Optional[Conversation]: 对话对象，不存在返回 None
        """
        file_path = self._build_raw_path(date)
        
        if not file_path.exists():
            logger.debug(f"对话文件不存在: {file_path}")
            return None
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            if conversation_id:
                # 过滤特定对话
                if data.get("id") == conversation_id:
                    return self._dict_to_conversation(data)
                return None
            
            return self._dict_to_conversation(data)
            
        except Exception as e:
            logger.error(f"加载对话失败: {e}")
            return None
    
    def update(self, conversation: Conversation) -> bool:
        """
        更新对话
        
        Args:
            conversation: Conversation 对象
            
        Returns:
            bool: 是否更新成功
        """
        # 验证对话是否存在
        date = self._extract_date(conversation)
        existing = self.load(date, conversation.id)
        
        if not existing:
            logger.warning(f"对话不存在: {conversation.id}")
            return False
        
        # 更新时间戳
        conversation.updated_at = datetime.now().isoformat()
        
        # 保存
        return self.save(conversation)
    
    def delete(self, date: str, conversation_id: str = None) -> bool:
        """
        删除对话
        
        Args:
            date: 日期字符串
            conversation_id: 对话ID（可选，如果提供则只删除该对话）
            
        Returns:
            bool: 是否删除成功
        """
        with self._lock:
            file_path = self._build_raw_path(date)
            
            if not file_path.exists():
                logger.warning(f"对话文件不存在: {file_path}")
                return False
            
            try:
                # 加载现有数据
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                if conversation_id:
                    # 只删除特定对话
                    if data.get("id") != conversation_id:
                        return False
                
                # 删除标记文件
                conv_id = data.get("id", conversation_id)
                for tag in data.get("tags", []):
                    tagged_file = self._build_tagged_path(date, conv_id, tag)
                    if tagged_file.exists():
                        tagged_file.unlink()
                
                # 删除原始文件
                file_path.unlink()
                
                # 更新索引
                self._remove_from_index(date, conv_id)
                
                logger.info(f"对话已删除: {conv_id}")
                return True
                
            except Exception as e:
                logger.error(f"删除对话失败: {e}")
                return False
    
    # ============ Tag Operations ============
    
    def add_tags(self, date: str, conversation_id: str, tags: List[str]) -> bool:
        """
        为对话添加标签
        
        Args:
            date: 日期字符串
            conversation_id: 对话ID
            tags: 标签列表
            
        Returns:
            bool: 是否添加成功
        """
        conversation = self.load(date, conversation_id)
        
        if not conversation:
            return False
        
        # 添加新标签（去重）
        new_tags = list(set(conversation.tags + tags))
        conversation.tags = new_tags
        
        # 保存
        success = self.save(conversation)
        
        if success:
            # 生成标记文件
            for tag in tags:
                self._save_tagged_version(conversation, tag)
        
        return success
    
    def remove_tags(self, date: str, conversation_id: str, tags: List[str]) -> bool:
        """
        为对话移除标签
        
        Args:
            date: 日期字符串
            conversation_id: 对话ID
            tags: 标签列表
            
        Returns:
            bool: 是否移除成功
        """
        conversation = self.load(date, conversation_id)
        
        if not conversation:
            return False
        
        # 移除标签
        conversation.tags = [t for t in conversation.tags if t not in tags]
        
        # 保存
        success = self.save(conversation)
        
        if success:
            # 删除标记文件
            for tag in tags:
                tagged_file = self._build_tagged_path(date, conversation_id, tag)
                if tagged_file.exists():
                    tagged_file.unlink()
        
        return success
    
    def _save_tagged_version(self, conversation: Conversation, tag: str) -> None:
        """
        保存标记版本
        
        Args:
            conversation: Conversation 对象
            tag: 标签
        """
        date = self._extract_date(conversation)
        tagged_path = self._build_tagged_path(date, conversation.id, tag)
        
        content = self._generate_tagged_markdown(conversation, tag)
        
        with open(tagged_path, 'w', encoding='utf-8') as f:
            f.write(content)
    
    def _generate_tagged_markdown(self, conversation: Conversation, tag: str) -> str:
        """
        生成标记 Markdown
        
        Args:
            conversation: Conversation 对象
            tag: 标签
            
        Returns:
            str: Markdown 内容
        """
        date = self._extract_date(conversation)
        
        lines = [
            f"# 对话 - {tag.upper()}",
            "",
            f"**日期**: {date}",
            f"**对话ID**: {conversation.id}",
            f"**频道**: {conversation.channel_id}",
            f"**来源**: {conversation.source}",
            f"**标记时间**: {datetime.now().isoformat()}",
            f"**标签**: {', '.join(conversation.tags)}",
            "",
            "---",
            "",
        ]
        
        if conversation.summary:
            lines.extend([
                "## 摘要",
                "",
                conversation.summary,
                "",
                "---",
                "",
            ])
        
        lines.extend([
            "## 消息列表",
            "",
        ])
        
        for i, msg in enumerate(conversation.messages, 1):
            lines.extend([
                f"### 消息 {i}",
                f"- **角色**: {msg.role}",
                f"- **时间**: {msg.timestamp}",
                f"- **内容**: {msg.content}",
                "",
            ])
        
        lines.extend([
            "---",
            "",
            "## 原始数据",
            "",
            f"参见: `conversations/raw/{date[:4]}/{date[5:7]}/{date}.json`",
        ])
        
        return "\n".join(lines)
    
    # ============ Index Operations ============
    
    def _load_index(self) -> Dict[str, Any]:
        """
        加载索引
        
        Returns:
            Dict: 索引数据
        """
        if self.index_file.exists():
            try:
                with open(self.index_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                logger.warning(f"加载索引失败: {e}")
                return {"conversations": {}, "tags": {}}
        return {"conversations": {}, "tags": {}}
    
    def _save_index(self, index: Dict[str, Any]) -> None:
        """
        保存索引
        
        Args:
            index: 索引数据
        """
        self.index_file.parent.mkdir(parents=True, exist_ok=True)
        with open(self.index_file, 'w', encoding='utf-8') as f:
            json.dump(index, f, ensure_ascii=False, indent=2)
    
    def _update_index(self, conversation: Conversation, date: str) -> None:
        """
        更新索引
        
        Args:
            conversation: Conversation 对象
            date: 日期字符串
        """
        index = self._load_index()
        
        # 更新对话索引
        if "conversations" not in index:
            index["conversations"] = {}
        
        index["conversations"][conversation.id] = {
            "date": date,
            "channel_id": conversation.channel_id,
            "source": conversation.source,
            "updated_at": conversation.updated_at,
            "message_count": len(conversation.messages),
            "tags": conversation.tags
        }
        
        # 更新标签索引
        if "tags" not in index:
            index["tags"] = {}
        
        for tag in conversation.tags:
            if tag not in index["tags"]:
                index["tags"][tag] = []
            if conversation.id not in index["tags"][tag]:
                index["tags"][tag].append(conversation.id)
        
        self._save_index(index)
    
    def _remove_from_index(self, date: str, conversation_id: str) -> None:
        """
        从索引移除
        
        Args:
            date: 日期字符串
            conversation_id: 对话ID
        """
        index = self._load_index()
        
        # 从对话索引移除
        if "conversations" in index and conversation_id in index["conversations"]:
            del index["conversations"][conversation_id]
        
        # 从标签索引移除
        if "tags" in index:
            for tag, conv_ids in list(index["tags"].items()):
                if conversation_id in conv_ids:
                    conv_ids.remove(conversation_id)
                    if not conv_ids:
                        del index["tags"][tag]
        
        self._save_index(index)
    
    def rebuild_index(self) -> None:
        """重建索引"""
        logger.info("开始重建索引...")
        
        index = {"conversations": {}, "tags": {}}
        
        # 遍历所有对话文件
        for json_file in self.raw_dir.rglob("*.json"):
            try:
                with open(json_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                conv_id = data.get("id")
                date = self._extract_date_from_path(json_file)
                
                if conv_id:
                    index["conversations"][conv_id] = {
                        "date": date,
                        "channel_id": data.get("channel_id"),
                        "source": data.get("source"),
                        "updated_at": data.get("updated_at"),
                        "message_count": len(data.get("messages", [])),
                        "tags": data.get("tags", [])
                    }
                    
                    for tag in data.get("tags", []):
                        if tag not in index["tags"]:
                            index["tags"][tag] = []
                        if conv_id not in index["tags"][tag]:
                            index["tags"][tag].append(conv_id)
                            
            except Exception as e:
                logger.warning(f"处理文件失败 {json_file}: {e}")
        
        self._save_index(index)
        logger.info(f"索引重建完成: {len(index['conversations'])} 个对话")
    
    def _extract_date_from_path(self, path: Path) -> str:
        """
        从文件路径提取日期
        
        Args:
            path: 文件路径
            
        Returns:
            str: 日期字符串
        """
        # 从路径中提取日期
        parts = path.stem.split("-")
        if len(parts) >= 3:
            return f"{parts[0]}-{parts[1]}-{parts[2]}"
        return datetime.now().strftime("%Y-%m-%d")
    
    # ============ Query Operations ============
    
    def list_by_date(
        self,
        start_date: str = None,
        end_date: str = None
    ) -> List[Dict[str, Any]]:
        """
        按日期列出对话
        
        Args:
            start_date: 开始日期
            end_date: 结束日期
            
        Returns:
            List[Dict]: 对话信息列表
        """
        if not start_date:
            start_date = datetime.now().strftime("%Y-%m-%d")
        if not end_date:
            end_date = start_date
        
        start_dt = datetime.strptime(start_date, "%Y-%m-%d")
        end_dt = datetime.strptime(end_date, "%Y-%m-%d")
        
        conversations = []
        current_dt = start_dt
        
        while current_dt <= end_dt:
            date_str = current_dt.strftime("%Y-%m-%d")
            file_path = self._build_raw_path(date_str)
            
            if file_path.exists():
                conversations.append({
                    "date": date_str,
                    "file_path": str(file_path),
                    "type": "file"
                })
            
            current_dt
        
        return conversations
    
    def list_by_tag(self, tag: str) -> List[Dict[str, Any]]:
        """
        按标签列出对话
        
        Args:
            tag: 标签
            
        Returns:
            List[Dict]: 对话信息列表
        """
        index = self._load_index()
        
        if "tags" not in index or tag not in index["tags"]:
            return []
        
        conversations = []
        for conv_id in index["tags"][tag]:
            if "conversations" in index and conv_id in index["conversations"]:
                conv_info = index["conversations"][conv_id]
                conversations.append({
                    "id": conv_id,
                    "date": conv_info.get("date"),
                    "channel_id": conv_info.get("channel_id"),
                    "tags": conv_info.get("tags", [])
                })
        
        return conversations
    
    def search(
        self,
        query: str = None,
        tags: List[str] = None,
        channel_id: str = None,
        start_date: str = None,
        end_date: str = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """
        搜索对话
        
        Args:
            query: 搜索关键词
            tags: 标签过滤
            channel_id: 频道过滤
            start_date: 开始日期
            end_date: 结束日期
            limit: 最大结果数
            
        Returns:
            List[Dict]: 匹配的对话列表
        """
        results = []
        
        # 从索引获取候选
        index = self._load_index()
        
        for conv_id, conv_info in index.get("conversations", {}).items():
            # 过滤条件
            if channel_id and conv_info.get("channel_id") != channel_id:
                continue
            
            if start_date and conv_info.get("date", "") < start_date:
                continue
            
            if end_date and conv_info.get("date", "") > end_date:
                continue
            
            if tags:
                conv_tags = conv_info.get("tags", [])
                if not any(t in conv_tags for t in tags):
                    continue
            
            # 如果有查询关键词，从文件加载并搜索
            if query:
                date = conv_info.get("date")
                if date:
                    conv = self.load(date, conv_id)
                    if conv:
                        # 搜索消息内容
                        content = " ".join([msg.content for msg in conv.messages])
                        if query.lower() in content.lower():
                            results.append({
                                "id": conv_id,
                                "date": date,
                                "channel_id": conv.channel_id,
                                "summary": conv.summary,
                                "matched_content": content
                            })
            else:
                results.append({
                    "id": conv_id,
                    "date": conv_info.get("date"),
                    "channel_id": conv_info.get("channel_id"),
                    "summary": conv_info.get("summary")
                })
        
        return results[:limit]
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        获取统计信息
        
        Returns:
            Dict: 统计信息
        """
        index = self._load_index()
        
        conversations = index.get("conversations", {})
        tags = index.get("tags", {})
        
        # 按月份统计
        monthly_stats = {}
        for conv_id, info in conversations.items():
            date = info.get("date", "")
            if date:
                month = date[:7]  # YYYY-MM
                if month not in monthly_stats:
                    monthly_stats[month] = 0
                monthly_stats[month] += 1
        
        return {
            "total_conversations": len(conversations),
            "total_tags": len(tags),
            "tag_distribution": {tag: len(ids) for tag, ids in tags.items()},
            "monthly_distribution": monthly_stats,
            "index_file": str(self.index_file),
            "raw_dir": str(self.raw_dir)
        }
    
    # ============ Helper Methods ============
    
    def _extract_date(self, conversation: Conversation) -> str:
        """
        从对话提取日期
        
        Args:
            conversation: Conversation 对象
            
        Returns:
            str: 日期字符串
        """
        # 优先使用消息时间
        if conversation.messages:
            first_msg = conversation.messages[0]
            try:
                dt = datetime.fromisoformat(first_msg.timestamp.replace("Z", "+00:00"))
                return dt.strftime("%Y-%m-%d")
            except ValueError:
                pass
        
        # 使用创建时间
        try:
            dt = datetime.fromisoformat(conversation.created_at)
            return dt.strftime("%Y-%m-%d")
        except ValueError:
            pass
        
        return datetime.now().strftime("%Y-%m-%d")
    
    def _conversation_to_dict(self, conversation: Conversation) -> Dict:
        """
        将 Conversation 转换为字典
        
        Args:
            conversation: Conversation 对象
            
        Returns:
            Dict: 字典数据
        """
        return {
            "type": "conversation_snapshot",
            "version": "1.0",
            "id": conversation.id,
            "channel_id": conversation.channel_id,
            "source": conversation.source,
            "title": conversation.title,
            "created_at": conversation.created_at,
            "updated_at": conversation.updated_at,
            "summary": conversation.summary,
            "tags": conversation.tags,
            "message_count": len(conversation.messages),
            "messages": [
                {
                    "id": msg.id,
                    "role": msg.role,
                    "content": msg.content,
                    "timestamp": msg.timestamp,
                    "sender_id": msg.sender_id,
                    "sender_name": msg.sender_name,
                    "message_type": msg.message_type,
                    "metadata": msg.metadata
                }
                for msg in conversation.messages
            ],
            "metadata": conversation.metadata
        }
    
    def _dict_to_conversation(self, data: Dict) -> Conversation:
        """
        将字典转换为 Conversation
        
        Args:
            data: 字典数据
            
        Returns:
            Conversation: Conversation 对象
        """
        messages = [
            Message(
                id=msg["id"],
                role=msg["role"],
                content=msg["content"],
                timestamp=msg["timestamp"],
                sender_id=msg.get("sender_id"),
                sender_name=msg.get("sender_name"),
                message_type=msg.get("message_type", "text"),
                metadata=msg.get("metadata", {})
            )
            for msg in data.get("messages", [])
        ]
        
        return Conversation(
            id=data["id"],
            channel_id=data["channel_id"],
            source=data.get("source", "feishu"),
            messages=messages,
            created_at=data.get("created_at", datetime.now().isoformat()),
            updated_at=data.get("updated_at", datetime.now().isoformat()),
            metadata=data.get("metadata", {}),
            summary=data.get("summary"),
            tags=data.get("tags", []),
            title=data.get("title")
        )
    
    def count(self) -> int:
        """
        获取对话数量
        
        Returns:
            int: 对话数量
        """
        index = self._load_index()
        return len(index.get("conversations", {}))
    
    def exists(self, date: str, conversation_id: str = None) -> bool:
        """
        检查对话是否存在
        
        Args:
            date: 日期字符串
            conversation_id: 对话ID
            
        Returns:
            bool: 是否存在
        """
        file_path = self._build_raw_path(date)
        
        if not file_path.exists():
            return False
        
        if conversation_id:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            return data.get("id") == conversation_id
        
        return True


# ============ 便捷函数 ============

_default_storage: Optional[ConversationStorage] = None


def get_conversation_storage(
    root_path: str = "./.memory",
    **kwargs
) -> ConversationStorage:
    """
    获取 ConversationStorage 实例
    
    Args:
        root_path: 存储根目录
        **kwargs: 其他参数
        
    Returns:
        ConversationStorage: 实例
    """
    global _default_storage
    if _default_storage is None:
        _default_storage = ConversationStorage(root_path, **kwargs)
    return _default_storage


def save_conversation(conv: Conversation) -> bool:
    """保存对话"""
    return get_conversation_storage().save(conv)


def load_conversation(date: str, conversation_id: str = None) -> Optional[Conversation]:
    """加载对话"""
    return get_conversation_storage().load(date, conversation_id)


def list_conversations(
    start_date: str = None,
    end_date: str = None
) -> List[Dict[str, Any]]:
    """列出对话"""
    return get_conversation_storage().list_by_date(start_date, end_date)


def search_conversations(
    query: str = None,
    tags: List[str] = None,
    **kwargs
) -> List[Dict[str, Any]]:
    """搜索对话"""
    return get_conversation_storage().search(query, tags, **kwargs)


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Conversation Storage - 对话存储管理工具"
    )
    
    subparsers = parser.add_subparsers(dest="command", help="可用命令")
    
    # list 命令
    list_parser = subparsers.add_parser("list", help="列出对话")
    list_parser.add_argument("--start-date", "-s", default=None)
    list_parser.add_argument("--end-date", "-e", default=None)
    
    # search 命令
    search_parser = subparsers.add_parser("search", help="搜索对话")
    search_parser.add_argument("--query", "-q", default=None)
    search_parser.add_argument("--tags", "-t", default=None)
    search_parser.add_argument("--limit", "-l", type=int, default=100)
    
    # stats 命令
    subparsers.add_parser("stats", help="查看统计")
    
    # rebuild 命令
    subparsers.add_parser("rebuild", help="重建索引")
    
    args = parser.parse_args()
    
    storage = ConversationStorage()
    
    if args.command == "list":
        conversations = storage.list_by_date(args.start_date, args.end_date)
        print(f"找到 {len(conversations)} 个对话:")
        for conv in conversations:
            print(f"  - {conv['date']}: {conv['file_path']}")
    
    elif args.command == "search":
        tags = args.tags.split(",") if args.tags else None
        results = storage.search(args.query, tags, limit=args.limit)
        print(f"找到 {len(results)} 个匹配:")
        for r in results:
            print(f"  - {r['id']} ({r['date']}): {r.get('summary', 'N/A')[:50]}")
    
    elif args.command == "stats":
        stats = storage.get_statistics()
        print("对话统计:")
        print(f"  总对话数: {stats['total_conversations']}")
        print(f"  总标签数: {stats['total_tags']}")
        print(f"  月度分布: {stats['monthly_distribution']}")
    
    elif args.command == "rebuild":
        storage.rebuild_index()
        print("索引已重建")
    
    else:
        parser.print_help()
