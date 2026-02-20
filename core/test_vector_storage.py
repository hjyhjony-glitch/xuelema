#!/usr/bin/env python3
"""
Vector Storage Unit Tests - 向量存储单元测试

测试覆盖：
1. VectorStorage 初始化
2. 向量添加 (add, search, delete)
3. 持久化
4. 边界情况

注意：由于 Python 3.14 与 ChromaDB pydantic v1 兼容性问题，
本测试使用轻量级 NumPy 实现。

Author: RUNBOT-DEV（笑天）
Version: 1.0.0
Date: 2026-02-20
"""

import unittest
import os
import sys
import tempfile
import shutil

# 导入轻量级 NumPy 实现
memory_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), ".memory")
if memory_dir not in sys.path:
    sys.path.insert(0, memory_dir)

from chromadb_storage import VectorStorage


class TestVectorStorageBasic(unittest.TestCase):
    """向量存储基础功能测试"""
    
    def setUp(self):
        """测试前置"""
        self.temp_dir = tempfile.mkdtemp()
    
    def tearDown(self):
        """测试清理"""
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
    
    def test_init_creates_directory(self):
        """测试初始化创建目录"""
        vs = VectorStorage(persist_dir=self.temp_dir)
        self.assertTrue(os.path.exists(self.temp_dir))
    
    def test_add_vector(self):
        """测试添加向量"""
        vs = VectorStorage(persist_dir=self.temp_dir)
        vs.add("test", "doc1", "测试内容", {})
        
        self.assertIn("doc1", vs.collections["test"]["ids"])
    
    def test_search_vector(self):
        """测试搜索向量"""
        vs = VectorStorage(persist_dir=self.temp_dir)
        vs.add("test", "doc1", "Python 编程", {})
        vs.add("test", "doc2", "Java 开发", {})
        
        results = vs.search("test", "Python 编程", n_results=2)
        
        self.assertIsNotNone(results)
        self.assertIn("doc1", results["ids"])
    
    def test_delete_vector(self):
        """测试删除向量"""
        vs = VectorStorage(persist_dir=self.temp_dir)
        vs.add("test", "doc1", "待删除内容", {})
        vs.delete("test", "doc1")
        
        self.assertNotIn("doc1", vs.collections["test"]["ids"])
    
    def test_persistence(self):
        """测试持久化"""
        # 第一个实例
        vs1 = VectorStorage(persist_dir=self.temp_dir)
        vs1.add("memories", "doc1", "内容1", {})
        
        # 第二个实例
        vs2 = VectorStorage(persist_dir=self.temp_dir)
        
        self.assertIn("doc1", vs2.collections["memories"]["ids"])


if __name__ == "__main__":
    unittest.main()
