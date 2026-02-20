#!/usr/bin/env python3
"""
Conversation 模块单元测试
========================
测试 conversation.py 的功能

测试覆盖:
1. CRUD 操作
2. 标签操作
3. 索引操作
4. 查询操作

作者: RUNBOT-DEV（笑天）
版本: v1.0
日期: 2026-02-20
"""

import json
import os
import sys
import tempfile
import unittest
from pathlib import Path
from typing import Any, Dict, List

# 添加父目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from persistent_memory.conversation import (
    ConversationStorage,
    Message,
    Conversation,
)


class TestConversationStorage(unittest.TestCase):
    """ConversationStorage 测试类"""
    
    def setUp(self):
        """测试初始化"""
        self.temp_dir = tempfile.mkdtemp()
        self.storage = ConversationStorage(
            root_path=self.temp_dir,
            raw_dir="conversations/raw",
            tagged_dir="conversations/tagged"
        )
    
    def tearDown(self):
        """测试清理"""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_init(self):
        """测试初始化"""
        self.assertIsInstance(self.storage, ConversationStorage)
        self.assertTrue((self.temp_dir / "conversations" / "raw").exists())
        self.assertTrue((self.temp_dir / "conversations" / "tagged").exists())
    
    def test_parse_date_path(self):
        """测试日期路径解析"""
        year, month = self.storage._parse_date_path("2026-02-20")
        self.assertEqual(year, "2026")
        self.assertEqual(month, "02")
    
    def test_build_raw_path(self):
        """测试原始对话路径构建"""
        path = self.storage._build_raw_path("2026-02-20")
        
        self.assertTrue(str(path).endswith("2026/02/2026-02-20.json"))
        self.assertTrue(path.exists())
    
    def test_save_conversation(self):
        """测试保存对话"""
        messages = [
            Message(
                id="msg_001",
                role="user",
                content="测试保存",
                timestamp="2026-02-20T08:00:00+08:00"
            )
        ]
        
        conv = Conversation(
            id="conv_001",
            channel_id="oc_test",
            messages=messages
        )
        
        result = self.storage.save(conv)
        
        self.assertTrue(result)
        
        # 验证文件存在
        file_path = self.storage._build_raw_path("2026-02-20")
        self.assertTrue(file_path.exists())
    
    def test_load_conversation(self):
        """测试加载对话"""
        messages = [
            Message(
                id="msg_001",
                role="user",
                content="测试加载",
                timestamp="2026-02-20T08:00:00+08:00"
            )
        ]
        
        conv = Conversation(
            id="conv_001",
            channel_id="oc_test",
            messages=messages,
            summary="测试摘要",
            tags=["test"]
        )
        
        # 保存
        self.storage.save(conv)
        
        # 加载
        loaded = self.storage.load("2026-02-20", "conv_001")
        
        self.assertIsNotNone(loaded)
        self.assertEqual(loaded.id, "conv_001")
        self.assertEqual(loaded.summary, "测试摘要")
        self.assertIn("test", loaded.tags)
    
    def test_load_conversation_not_exists(self):
        """测试加载不存在的对话"""
        conv = self.storage.load("2026-02-20", "not_exists")
        self.assertIsNone(conv)
    
    def test_update_conversation(self):
        """测试更新对话"""
        messages = [
            Message(
                id="msg_001",
                role="user",
                content="原始内容",
                timestamp="2026-02-20T08:00:00+08:00"
            )
        ]
        
        conv = Conversation(
            id="conv_001",
            channel_id="oc_test",
            messages=messages,
            summary="原始摘要"
        )
        
        # 保存
        self.storage.save(conv)
        
        # 更新
        conv.summary = "更新后的摘要"
        conv.messages.append(
            Message(
                id="msg_002",
                role="assistant",
                content="回复内容",
                timestamp="2026-02-20T08:01:00+08:00"
            )
        )
        
        result = self.storage.update(conv)
        self.assertTrue(result)
        
        # 验证更新
        loaded = self.storage.load("2026-02-20", "conv_001")
        self.assertEqual(loaded.summary, "更新后的摘要")
        self.assertEqual(len(loaded.messages), 2)
    
    def test_update_conversation_not_exists(self):
        """测试更新不存在的对话"""
        messages = [
            Message(
                id="msg_001",
                role="user",
                content="内容",
                timestamp="2026-02-20T08:00:00+08:00"
            )
        ]
        
        conv = Conversation(
            id="not_exists",
            channel_id="oc_test",
            messages=messages
        )
        
        result = self.storage.update(conv)
        self.assertFalse(result)
    
    def test_delete_conversation(self):
        """测试删除对话"""
        messages = [
            Message(
                id="msg_001",
                role="user",
                content="测试删除",
                timestamp="2026-02-20T08:00:00+08:00"
            )
        ]
        
        conv = Conversation(
            id="conv_001",
            channel_id="oc_test",
            messages=messages,
            tags=["important"]
        )
        
        # 保存
        self.storage.save(conv)
        self.storage._save_tagged_version(conv, "important")
        
        # 删除
        result = self.storage.delete("2026-02-20", "conv_001")
        
        self.assertTrue(result)
        
        # 验证删除
        conv = self.storage.load("2026-02-20", "conv_001")
        self.assertIsNone(conv)
    
    def test_add_tags(self):
        """测试添加标签"""
        messages = [
            Message(
                id="msg_001",
                role="user",
                content="测试添加标签",
                timestamp="2026-02-20T08:00:00+08:00"
            )
        ]
        
        conv = Conversation(
            id="conv_001",
            channel_id="oc_test",
            messages=messages,
            tags=["existing"]
        )
        
        # 保存
        self.storage.save(conv)
        
        # 添加标签
        result = self.storage.add_tags("2026-02-20", "conv_001", ["new_tag", "another_tag"])
        
        self.assertTrue(result)
        
        # 验证
        loaded = self.storage.load("2026-02-20", "conv_001")
        self.assertIn("existing", loaded.tags)
        self.assertIn("new_tag", loaded.tags)
        self.assertIn("another_tag", loaded.tags)
    
    def test_remove_tags(self):
        """测试移除标签"""
        messages = [
            Message(
                id="msg_001",
                role="user",
                content="测试移除标签",
                timestamp="2026-02-20T08:00:00+08:00"
            )
        ]
        
        conv = Conversation(
            id="conv_001",
            channel_id="oc_test",
            messages=messages,
            tags=["tag1", "tag2", "tag3"]
        )
        
        # 保存
        self.storage.save(conv)
        
        # 移除标签
        result = self.storage.remove_tags("2026-02-20", "conv_001", ["tag1", "tag3"])
        
        self.assertTrue(result)
        
        # 验证
        loaded = self.storage.load("2026-02-20", "conv_001")
        self.assertIn("tag2", loaded.tags)
        self.assertNotIn("tag1", loaded.tags)
        self.assertNotIn("tag3", loaded.tags)
    
    def test_rebuild_index(self):
        """测试重建索引"""
        # 创建对话
        for i in range(3):
            messages = [
                Message(
                    id=f"msg_{i}",
                    role="user",
                    content=f"测试对话 {i}",
                    timestamp="2026-02-20T08:00:00+08:00"
                )
            ]
            
            conv = Conversation(
                id=f"conv_{i}",
                channel_id="oc_test",
                messages=messages,
                tags=["test"]
            )
            self.storage.save(conv)
        
        # 重建索引
        self.storage.rebuild_index()
        
        # 验证索引
        index = self.storage._load_index()
        self.assertEqual(len(index["conversations"]), 3)
        self.assertIn("test", index["tags"])
    
    def test_list_by_date(self):
        """测试按日期列出"""
        # 创建对话
        messages = [
            Message(
                id="msg_001",
                role="user",
                content="测试",
                timestamp="2026-02-20T08:00:00+08:00"
            )
        ]
        
        conv = Conversation(
            id="conv_001",
            channel_id="oc_test",
            messages=messages
        )
        self.storage.save(conv)
        
        # 列出
        result = self.storage.list_by_date("2026-02-20", "2026-02-20")
        
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["type"], "file")
    
    def test_list_by_tag(self):
        """测试按标签列出"""
        messages = [
            Message(
                id="msg_001",
                role="user",
                content="测试",
                timestamp="2026-02-20T08:00:00+08:00"
            )
        ]
        
        conv = Conversation(
            id="conv_001",
            channel_id="oc_test",
            messages=messages,
            tags=["important"]
        )
        self.storage.save(conv)
        
        # 列出
        result = self.storage.list_by_tag("important")
        
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["id"], "conv_001")
    
    def test_search(self):
        """测试搜索"""
        messages = [
            Message(
                id="msg_001",
                role="user",
                content="这是一个关于Python的测试",
                timestamp="2026-02-20T08:00:00+08:00"
            )
        ]
        
        conv = Conversation(
            id="conv_001",
            channel_id="oc_test",
            messages=messages
        )
        self.storage.save(conv)
        
        # 搜索
        result = self.storage.search(query="Python")
        
        self.assertGreater(len(result), 0)
        self.assertIn("Python", result[0].get("matched_content", ""))
    
    def test_search_with_filters(self):
        """测试带过滤条件的搜索"""
        messages = [
            Message(
                id="msg_001",
                role="user",
                content="测试",
                timestamp="2026-02-20T08:00:00+08:00"
            )
        ]
        
        conv = Conversation(
            id="conv_001",
            channel_id="oc_test",
            messages=messages,
            tags=["important"]
        )
        self.storage.save(conv)
        
        # 搜索
        result = self.storage.search(tags=["important"])
        
        self.assertGreater(len(result), 0)
    
    def test_get_statistics(self):
        """测试获取统计信息"""
        messages = [
            Message(
                id="msg_001",
                role="user",
                content="测试",
                timestamp="2026-02-20T08:00:00+08:00"
            )
        ]
        
        conv = Conversation(
            id="conv_001",
            channel_id="oc_test",
            messages=messages,
            tags=["test1", "test2"]
        )
        self.storage.save(conv)
        
        # 统计
        stats = self.storage.get_statistics()
        
        self.assertEqual(stats["total_conversations"], 1)
        self.assertEqual(stats["total_tags"], 2)
    
    def test_count(self):
        """测试对话计数"""
        self.assertEqual(self.storage.count(), 0)
        
        messages = [
            Message(
                id="msg_001",
                role="user",
                content="测试",
                timestamp="2026-02-20T08:00:00+08:00"
            )
        ]
        
        conv = Conversation(
            id="conv_001",
            channel_id="oc_test",
            messages=messages
        )
        self.storage.save(conv)
        
        self.assertEqual(self.storage.count(), 1)
    
    def test_exists(self):
        """测试检查存在性"""
        messages = [
            Message(
                id="msg_001",
                role="user",
                content="测试",
                timestamp="2026-02-20T08:00:00+08:00"
            )
        ]
        
        conv = Conversation(
            id="conv_001",
            channel_id="oc_test",
            messages=messages
        )
        self.storage.save(conv)
        
        self.assertTrue(self.storage.exists("2026-02-20", "conv_001"))
        self.assertFalse(self.storage.exists("2026-02-20", "not_exists"))


class TestConversationDataClasses(unittest.TestCase):
    """Conversation 数据类测试"""
    
    def test_message_creation(self):
        """测试消息创建"""
        msg = Message(
            id="test_id",
            role="user",
            content="测试内容",
            timestamp="2026-02-20T08:00:00+08:00",
            sender_id="user_001",
            sender_name="测试用户",
            message_type="text",
            metadata={"key": "value"}
        )
        
        self.assertEqual(msg.id, "test_id")
        self.assertEqual(msg.role, "user")
        self.assertEqual(msg.content, "测试内容")
        self.assertEqual(msg.sender_id, "user_001")
        self.assertEqual(msg.message_type, "text")
        self.assertEqual(msg.metadata["key"], "value")
    
    def test_conversation_creation(self):
        """测试对话创建"""
        messages = [
            Message(
                id="msg_001",
                role="user",
                content="内容",
                timestamp="2026-02-20T08:00:00+08:00"
            )
        ]
        
        conv = Conversation(
            id="conv_001",
            channel_id="oc_test",
            source="feishu",
            messages=messages,
            summary="摘要",
            tags=["test"],
            title="测试对话",
            metadata={"key": "value"}
        )
        
        self.assertEqual(conv.id, "conv_001")
        self.assertEqual(conv.source, "feishu")
        self.assertEqual(len(conv.messages), 1)
        self.assertEqual(conv.summary, "摘要")
        self.assertIn("test", conv.tags)
        self.assertEqual(conv.title, "测试对话")
        self.assertEqual(conv.metadata["key"], "value")


if __name__ == "__main__":
    unittest.main(verbosity=2)
