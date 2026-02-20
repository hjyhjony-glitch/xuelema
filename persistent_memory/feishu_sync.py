#!/usr/bin/env python3
"""
FeishuSync - 飞书对话同步模块
=============================
自动拉取飞书对话、标记、存储

功能:
1. 从飞书 API 拉取对话
2. 自动标记关键对话
3. 存储到 conversations/raw/
4. 生成对话摘要

作者: RUNBOT-DEV（笑天）
版本: v1.0
日期: 2026-02-20
"""

import json
import logging
import os
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
from dataclasses import dataclass, field
import hashlib

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
    role: str  # user / assistant
    content: str
    timestamp: str
    sender_id: Optional[str] = None
    sender_name: Optional[str] = None
    message_type: str = "text"
    tags: List[str] = field(default_factory=list)


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


class FeishuSync:
    """
    飞书对话同步器
    
    Attributes:
        root_path: 存储根目录
        raw_dir: 原始对话存储目录
        tagged_dir: 已标记对话存储目录
        config: 配置信息
    """
    
    # 默认存储路径
    DEFAULT_RAW_DIR = "conversations/raw"
    DEFAULT_TAGGED_DIR = "conversations/tagged"
    
    # 默认标签关键词
    DEFAULT_IMPORTANT_KEYWORDS = [
        "重要", "紧急", "关键", "决策", "决定", "必须", "应该要",
        "important", "urgent", "critical", "decision", "must", "should"
    ]
    
    # 默认任务关键词
    DEFAULT_TASK_KEYWORDS = [
        "任务", "todo", "待办", "完成", "做", "执行",
        "task", "to-do", "action", "execute"
    ]
    
    def __init__(
        self,
        root_path: str = "./.memory",
        raw_dir: str = None,
        tagged_dir: str = None,
        important_keywords: List[str] = None,
        task_keywords: List[str] = None
    ):
        """
        初始化 FeishuSync
        
        Args:
            root_path: 存储根目录
            raw_dir: 原始对话存储目录（相对于root_path）
            tagged_dir: 已标记对话存储目录（相对于root_path）
            important_keywords: 重要对话关键词
            task_keywords: 任务对话关键词
        """
        self.root_path = Path(root_path)
        self.raw_dir = self.root_path / (raw_dir or self.DEFAULT_RAW_DIR)
        self.tagged_dir = self.root_path / (tagged_dir or self.DEFAULT_TAGGED_DIR)
        
        # 标签关键词
        self.important_keywords = important_keywords or self.DEFAULT_IMPORTANT_KEYWORDS
        self.task_keywords = task_keywords or self.DEFAULT_TASK_KEYWORDS
        
        # 配置
        self.config = self._load_config()
        
        # 确保目录存在
        self._ensure_directories()
        
        logger.info(f"FeishuSync 初始化完成")
        logger.info(f"原始对话目录: {self.raw_dir}")
        logger.info(f"标记对话目录: {self.tagged_dir}")
    
    def _load_config(self) -> Dict[str, Any]:
        """加载配置文件"""
        config_path = self.root_path / "config" / "feishu_sync.yaml"
        
        if config_path.exists():
            try:
                import yaml
                with open(config_path, 'r', encoding='utf-8') as f:
                    return yaml.safe_load(f) or {}
            except Exception as e:
                logger.warning(f"加载配置文件失败: {e}")
                return {}
        return {}
    
    def _ensure_directories(self) -> None:
        """确保存储目录存在"""
        dirs = [
            self.raw_dir,
            self.raw_dir / "{year}" / "{month}",
            self.tagged_dir / "important",
            self.tagged_dir / "decision",
            self.tagged_dir / "todo",
            self.tagged_dir / "general",
        ]
        
        for dir_path in dirs:
            if isinstance(dir_path, Path):
                dir_path.mkdir(parents=True, exist_ok=True)
            else:
                Path(dir_path).mkdir(parents=True, exist_ok=True)
    
    def _generate_conversation_id(self, channel_id: str, date: str = None) -> str:
        """
        生成对话ID
        
        Args:
            channel_id: 频道ID
            date: 日期（可选）
            
        Returns:
            str: 对话ID
        """
        if date is None:
            date = datetime.now().strftime("%Y-%m-%d")
        
        unique_str = f"{channel_id}_{date}"
        return hashlib.md5(unique_str.encode()).hexdigest()[:12]
    
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
        year = datetime.now().strftime("%Y")
        month = datetime.now().strftime("%m")
        return year, month
    
    def _build_raw_path(self, date: str) -> Path:
        """
        构建原始对话文件路径
        
        Args:
            date: 日期字符串
            
        Returns:
            Path: 文件路径
        """
        year, month = self._parse_date_path(date)
        date_file = f"{date}.json"
        
        # 确保目录存在
        dir_path = self.raw_dir / year / month
        dir_path.mkdir(parents=True, exist_ok=True)
        
        return dir_path / date_file
    
    def fetch_conversations(
        self,
        channel_id: str,
        start_date: str = None,
        end_date: str = None,
        limit: int = 100
    ) -> List[Conversation]:
        """
        获取对话（模拟实现）
        
        注意：实际使用时需要根据飞书 API 实现
        这里提供无 API 版本的占位实现
        
        Args:
            channel_id: 频道ID
            start_date: 开始日期
            end_date: 结束日期
            limit: 最大消息数量
            
        Returns:
            List[Conversation]: 对话列表
        """
        logger.info(f"获取对话: channel={channel_id}, start={start_date}, end={end_date}")
        
        # 占位实现 - 实际使用时替换为真实的飞书 API 调用
        # TODO: 实现真实的飞书 API 调用
        # 参考: https://open.feishu.cn/document/server-docs/docs/im-v1/message/list
        mock_conversations = self._generate_mock_conversations(
            channel_id, start_date or datetime.now().strftime("%Y-%m-%d")
        )
        
        return mock_conversations
    
    def _generate_mock_conversations(self, channel_id: str, date: str) -> List[Conversation]:
        """
        生成模拟对话数据（用于测试）
        
        Args:
            channel_id: 频道ID
            date: 日期
            
        Returns:
            List[Conversation]: 模拟对话列表
        """
        messages = [
            Message(
                id="msg_001",
                role="user",
                content="整理一个新的 Persistent Memory 系统设计文档",
                timestamp=f"{date}T08:00:00+08:00",
                sender_id="user_001",
                sender_name="张三"
            ),
            Message(
                id="msg_002",
                role="assistant",
                content="好的，我来整理完整的 Persistent Memory 系统设计文档。\n\n主要内容包括：\n1. 系统架构设计\n2. 数据模型设计\n3. 目录结构设计\n4. 核心模块实现",
                timestamp=f"{date}T08:01:30+08:00"
            ),
            Message(
                id="msg_003",
                role="user",
                content="这个很重要，本周内需要完成",
                timestamp=f"{date}T08:02:00+08:00"
            ),
            Message(
                id="msg_004",
                role="assistant",
                content="收到，我会优先处理这个任务。",
                timestamp=f"{dateT08:02:30+08:00"
            )
        ]
        
        conversation = Conversation(
            id=self._generate_conversation_id(channel_id, date),
            channel_id=channel_id,
            source="feishu",
            messages=messages,
            metadata={
                "fetched_at": datetime.now().isoformat(),
                "status": "mock",
                "message_count": len(messages)
            }
        )
        
        return [conversation]
    
    def fetch_from_api(self, channel_id: str, start_time: int = None, 
                       end_time: int = None, limit: int = 100) -> List[Dict]:
        """
        从飞书 API 拉取真实对话数据
        
        需要配置以下环境变量:
        - FEISHU_APP_ID: 飞书应用ID
        - FEISHU_APP_SECRET: 飞书应用密钥
        - FEISHU_APP_TOKEN: 飞书应用Token
        
        Args:
            channel_id: 频道ID
            start_time: 开始时间戳
            end_time: 结束时间戳
            limit: 最大消息数量
            
        Returns:
            List[Dict]: 原始消息数据
        """
        import requests
        import time
        
        app_id = os.environ.get("FEISHU_APP_ID")
        app_secret = os.environ.get("FEISHU_APP_SECRET")
        
        if not app_id or not app_secret:
            logger.warning("飞书 API 凭证未配置，使用模拟数据")
            return self._fetch_mock_data(channel_id, start_time, end_time, limit)
        
        try:
            # 1. 获取 tenant_access_token
            url = "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal"
            headers = {"Content-Type": "application/json"}
            payload = {
                "app_id": app_id,
                "app_secret": app_secret
            }
            
            response = requests.post(url, json=payload, headers=headers)
            response.raise_for_status()
            token_data = response.json()
            
            if token_data.get("code") != 0:
                raise Exception(f"获取 token 失败: {token_data}")
            
            tenant_token = token_data["tenant_access_token"]
            
            # 2. 获取消息列表
            messages_url = "https://open.feishu.cn/open-apis/im/v1/messages"
            headers = {
                "Authorization": f"Bearer {tenant_token}",
                "Content-Type": "application/json"
            }
            
            params = {
                "container_id_type": "chat",
                "container_id": channel_id,
                "limit": min(limit, 100)
            }
            
            if start_time:
                params["start_time"] = start_time
            if end_time:
                params["end_time"] = end_time
            
            response = requests.get(messages_url, headers=headers, params=params)
            response.raise_for_status()
            
            data = response.json()
            if data.get("code") != 0:
                raise Exception(f"获取消息失败: {data}")
            
            return data.get("data", {}).get("items", [])
            
        except Exception as e:
            logger.error(f"从飞书 API 获取数据失败: {e}")
            return self._fetch_mock_data(channel_id, start_time, end_time, limit)
    
    def _fetch_mock_data(self, channel_id: str, start_time: int = None,
                         end_time: int = None, limit: int = 100) -> List[Dict]:
        """
        获取模拟数据（当 API 不可用时）
        
        Args:
            channel_id: 频道ID
            start_time: 开始时间戳
            end_time: 结束时间戳
            limit: 最大数量
            
        Returns:
            List[Dict]: 模拟消息数据
        """
        # 返回模拟数据
        mock_messages = []
        now = datetime.now()
        
        for i in range(min(limit, 10)):
            mock_messages.append({
                "message_id": f"mock_msg_{i}",
                "sender": {
                    "id": f"user_{i}",
                    "name": f"用户{i}"
                },
                "message_type": "text",
                "content": json.dumps({
                    "text": f"这是模拟消息 {i+1}"
                }, ensure_ascii=False),
                "created_at": int(now.timestamp()) - (i * 60)
            })
        
        return mock_messages
    
    def sync_conversations(
        self,
        channel_id: str,
        date: str = None,
        auto_tag: bool = True,
        generate_summary: bool = True
    ) -> List[Conversation]:
        """
        同步对话（拉取、标记、存储）
        
        Args:
            channel_id: 频道ID
            date: 日期
            auto_tag: 是否自动标记
            generate_summary: 是否生成摘要
            
        Returns:
            List[Conversation]: 同步的对话列表
        """
        if date is None:
            date = datetime.now().strftime("%Y-%m-%d")
        
        logger.info(f"开始同步对话: channel={channel_id}, date={date}")
        
        # 1. 获取对话
        conversations = self.fetch_conversations(channel_id, date, date)
        
        if not conversations:
            logger.warning(f"未获取到对话数据")
            return []
        
        # 2. 处理每个对话
        synced = []
        for conv in conversations:
            # 2.1 自动标记
            if auto_tag:
                conv = self._auto_tag_conversation(conv)
            
            # 2.2 生成摘要
            if generate_summary:
                conv = self._generate_summary(conv)
            
            # 2.3 存储对话
            if self._save_conversation(conv):
                synced.append(conv)
                logger.info(f"对话已同步: {conv.id}")
            
            # 2.4 存储标记版本
            if conv.tags:
                self._save_tagged_conversation(conv)
        
        logger.info(f"同步完成: {len(synced)}/{len(conversations)} 个对话")
        return synced
    
    def _auto_tag_conversation(self, conversation: Conversation) -> Conversation:
        """
        自动标记对话
        
        Args:
            conversation: 对话对象
            
        Returns:
            Conversation: 标记后的对话
        """
        all_content = " ".join([msg.content for msg in conversation.messages])
        all_content_lower = all_content.lower()
        
        tags = []
        
        # 检查重要关键词
        for keyword in self.important_keywords:
            if keyword.lower() in all_content_lower:
                tags.append("important")
                break
        
        # 检查任务关键词
        for keyword in self.task_keywords:
            if keyword.lower() in all_content_lower:
                tags.append("task")
                break
        
        # 检查决策关键词
        decision_keywords = ["决定", "决策", "确定", "就这么办", "同意"]
        for keyword in decision_keywords:
            if keyword in all_content:
                tags.append("decision")
                break
        
        # 检查问题关键词
        question_keywords = ["?", "？", "怎么", "如何", "为什么"]
        if any(kw in all_content for kw in question_keywords):
            tags.append("question")
        
        # 如果有标记，更新对话
        if tags:
            conversation.tags = list(set(tags))  # 去重
            logger.info(f"对话 {conversation.id} 已标记: {tags}")
            
            # 为消息添加标签
            for msg in conversation.messages:
                if any(tag in all_content_lower for tag in self.important_keywords):
                    msg.tags.append("important")
        
        return conversation
    
    def _generate_summary(self, conversation: Conversation) -> Conversation:
        """
        生成对话摘要
        
        Args:
            conversation: 对话对象
            
        Returns:
            Conversation: 带摘要的对话
        """
        # 简单实现：提取第一条用户消息作为摘要
        user_messages = [msg for msg in conversation.messages if msg.role == "user"]
        
        if user_messages:
            first_msg = user_messages[0]
            # 限制摘要长度
            summary = first_msg.content[:200]
            if len(first_msg.content) > 200:
                summary += "..."
            conversation.summary = summary
        
        # 统计信息
        conversation.metadata["message_count"] = len(conversation.messages)
        conversation.metadata["user_message_count"] = len(user_messages)
        conversation.metadata["assistant_message_count"] = len(conversation.messages) - len(user_messages)
        
        return conversation
    
    def _save_conversation(self, conversation: Conversation) -> bool:
        """
        保存对话到 raw 目录
        
        Args:
            conversation: 对话对象
            
        Returns:
            bool: 是否保存成功
        """
        try:
            # 提取日期
            date = self._extract_date(conversation)
            file_path = self._build_raw_path(date)
            
            # 转换为字典
            data = self._conversation_to_dict(conversation)
            
            # 写入文件
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            
            logger.debug(f"对话已保存: {file_path}")
            return True
            
        except Exception as e:
            logger.error(f"保存对话失败: {e}")
            return False
    
    def _save_tagged_conversation(self, conversation: Conversation) -> bool:
        """
        保存标记对话到 tagged 目录
        
        Args:
            conversation: 对话对象
            
        Returns:
            bool: 是否保存成功
        """
        try:
            date = self._extract_date(conversation)
            
            for tag in conversation.tags:
                # 创建标签子目录
                safe_tag = tag.replace("/", "_").replace(" ", "-")
                tag_dir = self.tagged_dir / safe_tag
                tag_dir.mkdir(parents=True, exist_ok=True)
                
                # 生成文件名
                filename = f"{date}_{conversation.id}.md"
                file_path = tag_dir / filename
                
                # 生成标记文件内容
                content = self._generate_tagged_markdown(conversation, tag)
                
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                
                logger.debug(f"标记对话已保存: {file_path}")
            
            return True
            
        except Exception as e:
            logger.error(f"保存标记对话失败: {e}")
            return False
    
    def _generate_tagged_markdown(self, conversation: Conversation, tag: str) -> str:
        """
        生成标记对话的 Markdown 内容
        
        Args:
            conversation: 对话对象
            tag: 标签
            
        Returns:
            str: Markdown 内容
        """
        date = self._extract_date(conversation)
        
        lines = [
            f"# 对话摘要 - {tag.upper()}",
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
            "## 摘要",
            "",
        ]
        
        if conversation.summary:
            lines.append(conversation.summary)
        else:
            lines.append("*无摘要*")
        
        lines.extend([
            "",
            "---",
            "",
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
            "## 元数据",
            "",
            f"```json",
            json.dumps(conversation.metadata, ensure_ascii=False, indent=2),
            "```",
            "",
            "## 原始数据",
            "",
            f"参见: `conversations/raw/{date[:4]}/{date[5:7]}/{date}.json`",
        ])
        
        return "\n".join(lines)
    
    def _conversation_to_dict(self, conversation: Conversation) -> Dict:
        """
        将 Conversation 对象转换为字典
        
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
                    "tags": msg.tags
                }
                for msg in conversation.messages
            ],
            "metadata": conversation.metadata
        }
    
    def _dict_to_conversation(self, data: Dict) -> Conversation:
        """
        将字典转换为 Conversation 对象
        
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
                tags=msg.get("tags", [])
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
            tags=data.get("tags", [])
        )
    
    def _extract_date(self, conversation: Conversation) -> str:
        """
        从对话中提取日期
        
        Args:
            conversation: Conversation 对象
            
        Returns:
            str: 日期字符串 YYYY-MM-DD
        """
        # 优先使用消息时间
        if conversation.messages:
            first_msg = conversation.messages[0]
            try:
                dt = datetime.fromisoformat(first_msg.timestamp.replace("+00:00", "+08:00"))
                return dt.strftime("%Y-%m-%d")
            except ValueError:
                pass
        
        # 使用创建时间
        try:
            dt = datetime.fromisoformat(conversation.created_at)
            return dt.strftime("%Y-%m-%d")
        except ValueError:
            return datetime.now().strftime("%Y-%m-%d")
    
    def load_conversation(self, date: str, conversation_id: str = None) -> Optional[Conversation]:
        """
        加载对话
        
        Args:
            date: 日期
            conversation_id: 对话ID（可选，如果提供则只加载该对话）
            
        Returns:
            Optional[Conversation]: 对话对象，不存在返回 None
        """
        file_path = self._build_raw_path(date)
        
        if not file_path.exists():
            logger.warning(f"对话文件不存在: {file_path}")
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
    
    def list_conversations(
        self,
        start_date: str = None,
        end_date: str = None,
        tag: str = None
    ) -> List[Dict[str, Any]]:
        """
        列出对话
        
        Args:
            start_date: 开始日期
            end_date: 结束日期
            tag: 标签过滤
            
        Returns:
            List[Dict]: 对话信息列表
        """
        conversations = []
        
        # 如果指定了标签，从 tagged 目录查找
        if tag:
            tag_dir = self.tagged_dir / tag
            if tag_dir.exists():
                for file_path in tag_dir.glob("*.md"):
                    date = file_path.stem.split("_")[0]
                    conversations.append({
                        "date": date,
                        "file_path": str(file_path),
                        "tag": tag,
                        "type": "tagged"
                    })
            return conversations
        
        # 否则从 raw 目录查找
        if not start_date:
            start_date = datetime.now().strftime("%Y-%m-%d")
        if not end_date:
            end_date = start_date
        
        start_dt = datetime.strptime(start_date, "%Y-%m-%d")
        end_dt = datetime.strptime(end_date, "%Y-%m-%d")
        
        # 遍历日期范围
        current_dt = start_dt
        while current_dt <= end_dt:
            date_str = current_dt.strftime("%Y-%m-%d")
            year, month = self._parse_date_path(date_str)
            
            dir_path = self.raw_dir / year / month
            if dir_path.exists():
                for file_path in dir_path.glob("*.json"):
                    conversations.append({
                        "date": date_str,
                        "file_path": str(file_path),
                        "type": "raw"
                    })
            
            current_dt += timedelta(days=1)
        
        return conversations
    
    def delete_conversation(self, date: str, conversation_id: str = None) -> bool:
        """
        删除对话
        
        Args:
            date: 日期
            conversation_id: 对话ID（可选）
            
        Returns:
            bool: 是否删除成功
        """
        file_path = self._build_raw_path(date)
        
        if not file_path.exists():
            logger.warning(f"对话文件不存在: {file_path}")
            return False
        
        try:
            file_path.unlink()
            
            # 同时删除标记文件
            if conversation_id:
                for tag_dir in self.tagged_dir.iterdir():
                    if tag_dir.is_dir():
                        tagged_file = tag_dir / f"{date}_{conversation_id}.md"
                        if tagged_file.exists():
                            tagged_file.unlink()
            
            logger.info(f"对话已删除: {file_path}")
            return True
            
        except Exception as e:
            logger.error(f"删除对话失败: {e}")
            return False


# ============ 便捷函数 ============

_default_sync: Optional[FeishuSync] = None


def get_feishu_sync(
    root_path: str = "./.memory",
    **kwargs
) -> FeishuSync:
    """
    获取 FeishuSync 实例
    
    Args:
        root_path: 存储根目录
        **kwargs: 其他参数
        
    Returns:
        FeishuSync: 实例
    """
    global _default_sync
    if _default_sync is None:
        _default_sync = FeishuSync(root_path, **kwargs)
    return _default_sync


def sync_today(channel_id: str, **kwargs) -> List[Conversation]:
    """
    同步今天的对话
    
    Args:
        channel_id: 频道ID
        **kwargs: 其他参数
        
    Returns:
        List[Conversation]: 同步的对话列表
    """
    sync = get_feishu_sync(**kwargs)
    return sync.sync_conversations(
        channel_id,
        date=datetime.now().strftime("%Y-%m-%d")
    )


# ============ CLI 入口 ============

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(
        description="FeishuSync - 飞书对话同步工具",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # 同步今天的对话
  python feishu_sync.py sync --channel-id oc_xxx
  
  # 同步指定日期的对话
  python feishu_sync.py sync --channel-id oc_xxx --date 2026-02-20
  
  # 列出对话
  python feishu_sync.py list --start-date 2026-02-19 --end-date 2026-02-20
  
  # 加载对话
  python feishu_sync.py load --date 2026-02-20
        """
    )
    
    subparsers = parser.add_subparsers(dest="command", help="可用命令")
    
    # sync 命令
    sync_parser = subparsers.add_parser("sync", help="同步对话")
    sync_parser.add_argument(
        "--channel-id", "-c",
        required=True,
        help="飞书频道ID"
    )
    sync_parser.add_argument(
        "--date", "-d",
        default=None,
        help="日期 (YYYY-MM-DD)，默认今天"
    )
    sync_parser.add_argument(
        "--no-tag",
        action="store_true",
        help="不自动标记"
    )
    sync_parser.add_argument(
        "--no-summary",
        action="store_true",
        help="不生成摘要"
    )
    sync_parser.add_argument(
        "--root-path", "-r",
        default="./.memory",
        help="存储根目录"
    )
    
    # list 命令
    list_parser = subparsers.add_parser("list", help="列出对话")
    list_parser.add_argument(
        "--start-date", "-s",
        default=None,
        help="开始日期"
    )
    list_parser.add_argument(
        "--end-date", "-e",
        default=None,
        help="结束日期"
    )
    list_parser.add_argument(
        "--tag", "-t",
        default=None,
        help="按标签过滤"
    )
    list_parser.add_argument(
        "--root-path", "-r",
        default="./.memory",
        help="存储根目录"
    )
    
    # load 命令
    load_parser = subparsers.add_parser("load", help="加载对话")
    load_parser.add_argument(
        "--date", "-d",
        required=True,
        help="日期 (YYYY-MM-DD)"
    )
    load_parser.add_argument(
        "--conversation-id", "-i",
        default=None,
        help="对话ID"
    )
    load_parser.add_argument(
        "--root-path", "-r",
        default="./.memory",
        help="存储根目录"
    )
    
    # delete 命令
    delete_parser = subparsers.add_parser("delete", help="删除对话")
    delete_parser.add_argument(
        "--date", "-d",
        required=True,
        help="日期 (YYYY-MM-DD)"
    )
    delete_parser.add_argument(
        "--conversation-id", "-i",
        default=None,
        help="对话ID"
    )
    delete_parser.add_argument(
        "--root-path", "-r",
        default="./.memory",
        help="存储根目录"
    )
    
    args = parser.parse_args()
    
    if args.command == "sync":
        sync = FeishuSync(root_path=args.root_path)
        conversations = sync.sync_conversations(
            channel_id=args.channel_id,
            date=args.date,
            auto_tag=not args.no_tag,
            generate_summary=not args.no_summary
        )
        print(f"✓ 同步完成: {len(conversations)} 个对话")
        
    elif args.command == "list":
        sync = FeishuSync(root_path=args.root_path)
        conversations = sync.list_conversations(
            start_date=args.start_date,
            end_date=args.end_date,
            tag=args.tag
        )
        print(f"找到 {len(conversations)} 个对话:")
        for conv in conversations:
            print(f"  - {conv['date']}: {conv['file_path']}")
        
    elif args.command == "load":
        sync = FeishuSync(root_path=args.root_path)
        conversation = sync.load_conversation(
            date=args.date,
            conversation_id=args.conversation_id
        )
        if conversation:
            print(json.dumps(
                sync._conversation_to_dict(conversation),
                ensure_ascii=False,
                indent=2
            ))
        else:
            print(f"未找到对话: {args.date}")
        
    elif args.command == "delete":
        sync = FeishuSync(root_path=args.root_path)
        if sync.delete_conversation(args.date, args.conversation_id):
            print(f"✓ 已删除: {args.date}")
        else:
            print(f"✗ 删除失败: {args.date}")
        
    else:
        parser.print_help()
