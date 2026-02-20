#!/usr/bin/env python3
"""
FeishuSync 单元测试
==================
测试 feishu_sync.py 的功能

测试覆盖:
1. 对话获取和解析
2. 自动标签功能
3. 摘要生成
4. 存储功能
5. 索引功能

作者: RUNBOT-DEV（笑天）
版本: v1.0
日期: 2026-02-20
"""

import json
import os
import sys
import tempfile
import unittest
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List

# 添加父目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from persistent_memory.feishu_sync import (
    FeishuSync,
    Message,
    Conversation,
)


class TestFeishuSync(unittest.TestCase):
    """FeishuSync 测试类"""
    
    def setUp(self):
        """测试初始化"""
        # 创建临时目录
        self.temp_dir = tempfile.mkdtemp()
        self.sync = FeishuSync(
            root_path=self.temp_dir,
            important_keywords=["重要", "紧急", "critical"],
            task_keywords=["任务", "todo", "待办"]
        )
    
    def tearDown(self):
        """测试清理"""
        # 清理临时目录
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_init(self):
        """测试初始化"""
        self.assertIsInstance(self.sync, FeishuSync)
        self.assertTrue((self.temp_dir / "conversations" / "raw").exists())
        self.assertTrue((self.temp_dir / "conversations" / "tagged").exists())
    
    def test_generate_conversation_id(self):
        """测试对话ID生成"""
        conv_id1 = self.sync._generate_conversation_id("test_channel", "2026-02-20")
        conv_id2 = self.sync._generate_conversation_id("test_channel", "2026-02-20")
        
        # 相同输入应该生成相同ID
        self.assertEqual(conv_id1, conv_id2)
        
        # 不同日期应该生成不同ID
        conv_id3 = self.sync._generate_conversation_id("test_channel", "2026-02-21")
        self.assertNotEqual(conv_id1, conv_id3)
        
        # ID 应该是12位
        self.assertEqual(len(conv_id1), 12)
    
    def test_parse_date_path(self):
        """测试日期路径解析"""
        year, month = self.sync._parse_date_path("2026-02-20")
        self.assertEqual(year, "2026")
        self.assertEqual(month, "02")
        
        # 测试无效日期
        year, month = self.sync._parse_date_path("invalid")
        self.assertEqual(year, datetime.now().strftime("%Y"))
    
    def test_build_raw_path(self):
        """测试原始对话路径构建"""
        path = self.sync._build_raw_path("2026-02-20")
        
        self.assertTrue(str(path).endswith("2026/02/2026-02-20.json"))
        self.assertTrue(path.exists())
    
    def test_message_creation(self):
        """测试消息创建"""
        msg = Message(
            id="test_msg_001",
            role="user",
            content="测试消息",
            timestamp="2026-02-20T08:00:00+08:00",
            sender_id="user_001",
            sender_name="测试用户"
        )
        
        self.assertEqual(msg.id, "test_msg_001")
        self.assertEqual(msg.role, "user")
        self.assertEqual(msg.content, "测试消息")
        self.assertEqual(msg.sender_id, "user_001")
        self.assertEqual(msg.sender_name, "测试用户")
    
    def test_conversation_creation(self):
        """测试对话创建"""
        messages = [
            Message(
                id="msg_001",
                role="user",
                content="你好",
                timestamp="2026-02-20T08:00:00+08:00"
            ),
            Message(
                id="msg_002",
                role="assistant",
                content="你好！有什么可以帮助你的？",
                timestamp="2026-02-20T08:01:00+08:00"
            )
        ]
        
        conv = Conversation(
            id="conv_001",
            channel_id="oc_test",
            messages=messages
        )
        
        self.assertEqual(conv.id, "conv_001")
        self.assertEqual(conv.channel_id, "oc_test")
        self.assertEqual(len(conv.messages), 2)
        self.assertEqual(conv.source, "feishu")
    
    def test_auto_tag_conversation(self):
        """测试自动标签"""
        # 创建带有关键词的对话
        messages = [
            Message(
                id="msg_001",
                role="user",
                content="这是一个重要的任务，需要紧急处理",
                timestamp="2026-02-20T08:00:00+08:00"
            ),
            Message(
                id="msg_002",
                role="assistant",
                content="好的，我马上处理这个重要且紧急的任务",
                timestamp="2026-02-20T08:01:00+08:00"
            )
        ]
        
        conv = Conversation(
            id="conv_001",
            channel_id="oc_test",
            messages=messages
        )
        
        tagged_conv = self.sync._auto_tag_conversation(conv)
        
        # 应该包含 important 标签
        self.assertIn("important", tagged_conv.tags)
    
    def test_generate_summary(self):
        """测试摘要生成"""
        messages = [
            Message(
                id="msg_001",
                role="user",
                content="请帮我整理一个新的 Persistent Memory 系统设计文档，这是一项重要任务",
                timestamp="2026-02-20T08:00:00+08:00"
            ),
            Message(
                id="msg_002",
                role="assistant",
                content="好的，我来整理完整的 Persistent Memory 系统设计文档。主要内容包括：1. 系统架构设计；2. 数据模型设计；3. 目录结构设计；4. 核心模块实现",
                timestamp="2026-02-20T08:01:00+08:00"
            )
        ]
        
        conv = Conversation(
            id="conv_001",
            channel_id="oc_test",
            messages=messages
        )
        
        summary_conv = self.sync._generate_summary(conv)
        
        # 应该生成摘要
        self.assertIsNotNone(summary_conv.summary)
        self.assertIn("Persistent Memory", summary_conv.summary)
        
        # 应该包含统计信息
        self.assertEqual(summary_conv.metadata["message_count"], 2)
        self.assertEqual(summary_conv.metadata["user_message_count"], 1)
    
    def test_conversation_to_dict(self):
        """测试对话转字典"""
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
            summary="测试摘要",
            tags=["test"]
        )
        
        data = self.sync._conversation_to_dict(conv)
        
        self.assertEqual(data["id"], "conv_001")
        self.assertEqual(data["channel_id"], "oc_test")
        self.assertEqual(data["summary"], "测试摘要")
        self.assertIn("test", data["tags"])
        self.assertEqual(len(data["messages"]), 1)
    
    def test_dict_to_conversation(self):
        """测试字典转对话"""
        data = {
            "type": "conversation_snapshot",
            "version": "1.0",
            "id": "conv_001",
            "channel_id": "oc_test",
            "source": "feishu",
            "messages": [
                {
                    "id": "msg_001",
                    "role": "user",
                    "content": "测试",
                    "timestamp": "2026-02-20T08:00:00+08:00",
                    "sender_id": "user_001",
                    "sender_name": "测试用户",
                    "message_type": "text",
                    "tags": []
                }
            ],
            "summary": "测试摘要",
            "tags": ["test"],
            "metadata": {}
        }
        
        conv = self.sync._dict_to_conversation(data)
        
        self.assertEqual(conv.id, "conv_001")
        self.assertEqual(conv.channel_id, "oc_test")
        self.assertEqual(conv.summary, "测试摘要")
        self.assertIn("test", conv.tags)
        self.assertEqual(len(conv.messages), 1)
    
    def test_save_conversation(self):
        """测试保存对话"""
        messages = [
            Message(
                id="msg_001",
                role="user",
                content="测试保存功能",
                timestamp="2026-02-20T08:00:00+08:00"
            )
        ]
        
        conv = Conversation(
            id="conv_001",
            channel_id="oc_test",
            messages=messages
        )
        
        # 设置日期
        conv.messages[0].timestamp = "2026-02-20T08:00:00+08:00"
        
        result = self.sync._save_conversation(conv)
        
        self.assertTrue(result)
        
        # 验证文件存在
        file_path = self.sync._build_raw_path("2026-02-20")
        self.assertTrue(file_path.exists())
        
        # 验证内容
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        self.assertEqual(data["id"], "conv_001")
    
    def test_load_conversation(self):
        """测试加载对话"""
        messages = [
            Message(
                id="msg_001",
                role="user",
                content="测试加载功能",
                timestamp="2026-02-20T08:00:00+08:00"
            )
        ]
        
        conv = Conversation(
            id="conv_001",
            channel_id="oc_test",
            messages=messages
        )
        conv.messages[0].timestamp = "2026-02-20T08:00:00+08:00"
        
        # 保存
        self.sync._save_conversation(conv)
        
        # 加载
        loaded_conv = self.sync.load_conversation("2026-02-20", "conv_001")
        
        self.assertIsNotNone(loaded_conv)
        self.assertEqual(loaded_conv.id, "conv_001")
        self.assertEqual(len(loaded_conv.messages), 1)
    
    def test_load_conversation_not_exists(self):
        """测试加载不存在的对话"""
        conv = self.sync.load_conversation("2026-02-20", "not_exists")
        self.assertIsNone(conv)
    
    def test_sync_conversations(self):
        """测试同步对话"""
        result = self.sync.sync_conversations(
            channel_id="oc_test",
            date="2026-02-20",
            auto_tag=True,
            generate_summary=True
        )
        
        self.assertEqual(len(result), 1)
        conv = result[0]
        self.assertEqual(conv.channel_id, "oc_test")
        self.assertTrue(len(conv.tags) > 0 or conv.summary is not None)
    
    def test_generate_tagged_markdown(self):
        """测试生成标记 Markdown"""
        messages = [
            Message(
                id="msg_001",
                role="user",
                content="这是一个重要且紧急的任务",
                timestamp="2026-02-20T08:00:00+08:00"
            )
        ]
        
        conv = Conversation(
            id="conv_001",
            channel_id="oc_test",
            messages=messages,
            summary="测试摘要",
            tags=["important", "urgent"]
        )
        conv.messages[0].timestamp = "2026-02-20T08:00:00+08:00"
        
        md_content = self.sync._generate_tagged_markdown(conv, "important")
        
        self.assertIn("# 对话 - IMPORTANT", md_content)
        self.assertIn("2026-02-20", md_content)
        self.assertIn("重要", md_content)
        self.assertIn("测试摘要", md_content)
    
    def test_save_tagged_conversation(self):
        """测试保存标记对话"""
        messages = [
            Message(
                id="msg_001",
                role="user",
                content="这是一个重要任务",
                timestamp="2026-02-20T08:00:00+08:00"
            )
        ]
        
        conv = Conversation(
            id="conv_001",
            channel_id="oc_test",
            messages=messages,
            tags=["important"]
        )
        conv.messages[0].timestamp = "2026-02-20T08:00:00+08:00"
        
        result = self.sync._save_tagged_conversation(conv)
        
        self.assertTrue(result)
        
        # 验证标记文件存在
        tagged_dir = self.sync.tagged_dir / "important"
        tagged_file = tagged_dir / "2026-02-20_conv_001.md"
        self.assertTrue(tagged_file.exists())
    
    def test_list_conversations(self):
        """测试列出对话"""
        # 先同步一些对话
        self.sync.sync_conversations(
            channel_id="oc_test",
            date="2026-02-20"
        )
        
        conversations = self.sync.list_conversations(
            start_date="2026-02-20",
            end_date="2026-02-20"
        )
        
        self.assertGreater(len(conversations), 0)
        self.assertEqual(conversations[0]["type"], "raw")
    
    def test_delete_conversation(self):
        """测试删除对话"""
        # 先创建对话
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
        conv.messages[0].timestamp = "2026-02-20T08:00:00+08:00"
        
        self.sync._save_conversation(conv)
        self.sync._save_tagged_conversation(conv)
        
        # 删除
        result = self.sync.delete_conversation("2026-02-20", "conv_001")
        
        self.assertTrue(result)
        
        # 验证删除
        conv = self.sync.load_conversation("2026-02-20", "conv_001")
        self.assertIsNone(conv)
        
        # 验证标记文件也删除
        tagged_file = self.sync.tagged_dir / "important" / "2026-02-20_conv_001.md"
        self.assertFalse(tagged_file.exists())


class TestFeishuSyncEdgeCases(unittest.TestCase):
    """FeishuSync 边界情况测试"""
    
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.sync = FeishuSync(root_path=self.temp_dir)
    
    def tearDown(self):
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_empty_conversation(self):
        """测试空对话"""
        messages = []
        
        conv = Conversation(
            id="conv_001",
            channel_id="oc_test",
            messages=messages
        )
        
        # 自动标签空对话
        tagged_conv = self.sync._auto_tag_conversation(conv)
        self.assertEqual(len(tagged_conv.tags), 0)
        
        # 摘要生成空对话
        summary_conv = self.sync._generate_summary(conv)
        self.assertIsNone(summary_conv.summary)
    
    def test_very_long_content(self):
        """测试超长内容"""
        long_content = "测试内容 " * 1000
        
        messages = [
            Message(
                id="msg_001",
                role="user",
                content=long_content,
                timestamp="2026-02-20T08:00:00+08:00"
            )
        ]
        
        conv = Conversation(
            id="conv_001",
            channel_id="oc_test",
            messages=messages
        )
        conv.messages[0].timestamp = "2026-02-20T08:00:00+08:00"
        
        # 应该能处理
        summary_conv = self.sync._generate_summary(conv)
        self.assertIsNotNone(summary_conv.summary)
    
    def test_special_characters(self):
        """测试特殊字符"""
        special_content = "测试<>\"'&中文日本語한국어"
        
        messages = [
            Message(
                id="msg_001",
                role="user",
                content=special_content,
                timestamp="2026-02-20T08:00:00+08:00"
            )
        ]
        
        conv = Conversation(
            id="conv_001",
            channel_id="oc_test",
            messages=messages
        )
        conv.messages[0].timestamp = "2026-02-20T08:00:00+08:00"
        
        # 保存和加载
        self.sync._save_conversation(conv)
        loaded = self.sync.load_conversation("2026-02-20", "conv_001")
        
        self.assertIsNotNone(loaded)
        self.assertEqual(loaded.messages[0].content, special_content)
    
    def test_unicode_content(self):
        """测试 Unicode 内容"""
        unicode_content = "🚀 🎉 中文测试 🤖机器学习"
        
        messages = [
            Message(
                id="msg_001",
                role="user",
                content=unicode_content,
                timestamp="2026-02-20T08:00:00+08:00"
            )
        ]
        
        conv = Conversation(
            id="conv_001",
            channel_id="oc_test",
            messages=messages
        )
        conv.messages[0].timestamp = "2026-02-20T08:00:00+08:00"
        
        # 保存和加载
        self.sync._save_conversation(conv)
        loaded = self.sync.load_conversation("2026-02-20", "conv_001")
        
        self.assertIsNotNone(loaded)
        self.assertEqual(loaded.messages[0].content, unicode_content)


if __name__ == "__main__":
    unittest.main(verbosity=2)
