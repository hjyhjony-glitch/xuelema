"""
Unit Tests for Vector Storage Module (NumPy-based Mock)
================================================
向量存储模块的单元测试（使用轻量级 NumPy 实现替代 ChromaDB）

由于 Python 3.14 与 ChromaDB 的 pydantic v1 兼容性问题，
本测试使用 `.memory/chromadb_storage.py` 的轻量级 NumPy 实现。

测试覆盖:
- 初始化向量存储
- 添加向量 (add)
- 向量搜索 (search)
- 删除向量 (delete)

Author: RUNBOT-DEV（笑天）
Version: 1.0.0
Date: 2026-02-20
"""

import pytest
import os
import sys
import tempfile
import shutil

# 确保 .memory 目录在路径中
memory_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), ".memory")
if memory_dir not in sys.path:
    sys.path.insert(0, memory_dir)

# 导入轻量级 NumPy 实现
from chromadb_storage import VectorStorage, add_vector, search_vector, delete_vector


# ============ Fixtures ============

@pytest.fixture
def temp_dir():
    """创建临时目录"""
    temp_path = tempfile.mkdtemp(prefix="vector_test_")
    yield temp_path
    # 清理
    if os.path.exists(temp_path):
        shutil.rmtree(temp_path)


@pytest.fixture
def storage(temp_dir):
    """创建测试用存储实例"""
    vs = VectorStorage(persist_dir=temp_dir)
    yield vs
    vs._save()  # 确保保存


@pytest.fixture
def sample_data():
    """示例数据"""
    return [
        {"id": "doc1", "content": "Python 是一种流行的编程语言", "metadata": {"lang": "python"}},
        {"id": "doc2", "content": "机器学习是人工智能的分支", "metadata": {"field": "ml"}},
        {"id": "doc3", "content": "深度学习使用神经网络", "metadata": {"field": "dl"}},
        {"id": "doc4", "content": "自然语言处理处理文本", "metadata": {"field": "nlp"}},
        {"id": "doc5", "content": "计算机视觉处理图像", "metadata": {"field": "cv"}},
    ]


# ============ Import Test ============

class TestImport:
    """导入测试类"""
    
    def test_import_vector_storage(self):
        """测试导入模块"""
        try:
            from chromadb_storage import (
                VectorStorage,
                vector_db,
                add_vector,
                search_vector,
                delete_vector
            )
            
            # Verify classes exist
            assert VectorStorage is not None
            assert vector_db is not None
            assert callable(add_vector)
            assert callable(search_vector)
            assert callable(delete_vector)
            
            print("✅ All classes and functions imported successfully")
            
        except ImportError as e:
            pytest.fail(f"Import failed: {e}")


# ============ Core Functionality Tests ============

class TestVectorStorageInit:
    """测试初始化"""
    
    def test_init_default_directory(self, temp_dir):
        """测试默认初始化目录"""
        vs = VectorStorage(persist_dir=temp_dir)
        assert os.path.exists(temp_dir)
    
    def test_init_creates_default_collections(self, temp_dir):
        """测试初始化默认集合"""
        vs = VectorStorage(persist_dir=temp_dir)
        assert "memories" in vs.collections
        assert "conversations" in vs.collections
        assert "knowledge" in vs.collections


class TestAddVector:
    """测试添加向量"""
    
    def test_add_single_vector(self, storage):
        """测试添加单个向量"""
        storage.add(
            collection="test_coll",
            doc_id="test_doc1",
            document="测试文档内容",
            metadata={"tag": "test"}
        )
        
        coll = storage.collections["test_coll"]
        assert "test_doc1" in coll["ids"]
        assert "测试文档内容" in coll["documents"]
    
    def test_add_multiple_vectors(self, storage, sample_data):
        """测试添加多个向量"""
        for item in sample_data:
            storage.add(
                collection="test_coll",
                doc_id=item["id"],
                document=item["content"],
                metadata=item["metadata"]
            )
        
        coll = storage.collections["test_coll"]
        assert len(coll["ids"]) == 5
        assert len(coll["documents"]) == 5
    
    def test_add_unicode_content(self, storage):
        """测试添加 Unicode 内容"""
        storage.add(
            collection="test_coll",
            doc_id="unicode_doc",
            document="中文内容 🚀 émojis",
            metadata={"中文": "标签"}
        )
        
        coll = storage.collections["test_coll"]
        assert "unicode_doc" in coll["ids"]
    
    def test_add_empty_content(self, storage):
        """测试添加空内容"""
        storage.add(
            collection="test_coll",
            doc_id="empty_doc",
            document="",
            metadata={}
        )
        
        coll = storage.collections["test_coll"]
        assert "empty_doc" in coll["ids"]
    
    def test_add_creates_collection(self, storage):
        """测试添加自动创建集合"""
        storage.add(
            collection="new_collection",
            doc_id="doc1",
            document="新集合内容",
            metadata={}
        )
        
        assert "new_collection" in storage.collections


class TestSearchVector:
    """测试搜索向量"""
    
    def test_search_returns_results(self, storage, sample_data):
        """测试搜索返回结果"""
        for item in sample_data:
            storage.add(
                collection="test_coll",
                doc_id=item["id"],
                document=item["content"],
                metadata=item["metadata"]
            )
        
        results = storage.search(
            collection="test_coll",
            query="编程语言 Python",
            n_results=3
        )
        
        assert results is not None
        assert "ids" in results
        assert "documents" in results
        assert len(results["ids"]) > 0
    
    def test_search_result_order(self, storage, sample_data):
        """测试搜索结果按距离排序"""
        for item in sample_data:
            storage.add(
                collection="test_coll",
                doc_id=item["id"],
                document=item["content"],
                metadata=item["metadata"]
            )
        
        results = storage.search(
            collection="test_coll",
            query="学习 神经网络",
            n_results=5
        )
        
        if len(results["distances"]) >= 2:
            # 距离应该递增（从小到大）
            for i in range(len(results["distances"]) - 1):
                assert results["distances"][i] <= results["distances"][i + 1]
    
    def test_search_empty_collection(self, storage):
        """测试搜索空集合"""
        results = storage.search(
            collection="empty_coll",
            query="测试查询"
        )
        
        assert results is None
    
    def test_search_with_limit(self, storage, sample_data):
        """测试搜索结果数量限制"""
        for item in sample_data:
            storage.add(
                collection="test_coll",
                doc_id=item["id"],
                document=item["content"],
                metadata=item["metadata"]
            )
        
        results = storage.search(
            collection="test_coll",
            query="学习",
            n_results=2
        )
        
        assert len(results["ids"]) <= 2
    
    def test_search_returns_distances(self, storage):
        """测试搜索返回距离"""
        storage.add("test", "d1", "内容一", {})
        storage.add("test", "d2", "内容二", {})
        
        results = storage.search("test", "内容", n_results=2)
        
        assert "distances" in results
        assert len(results["distances"]) == len(results["ids"])


class TestDeleteVector:
    """测试删除向量"""
    
    def test_delete_existing_vector(self, storage):
        """测试删除存在的向量"""
        storage.add(
            collection="test_coll",
            doc_id="delete_me",
            document="将被删除的文档",
            metadata={}
        )
        
        storage.delete(collection="test_coll", doc_id="delete_me")
        
        coll = storage.collections["test_coll"]
        assert "delete_me" not in coll["ids"]
    
    def test_delete_nonexistent_vector(self, storage):
        """测试删除不存在的向量（不应报错）"""
        # 不应抛出异常
        storage.delete(collection="test_coll", doc_id="nonexistent")
    
    def test_delete_from_empty_collection(self, storage):
        """测试从空集合删除"""
        storage.delete(collection="empty_coll", doc_id="doc")


class TestPersistence:
    """测试持久化"""
    
    def test_save_and_load(self, temp_dir):
        """测试保存和加载（使用默认集合）"""
        # 创建第一个实例并添加数据到默认集合
        vs1 = VectorStorage(persist_dir=temp_dir)
        vs1.add("memories", "doc1", "内容1", {})
        vs1.add("memories", "doc2", "内容2", {})
        
        # 创建第二个实例（应该加载已有数据）
        vs2 = VectorStorage(persist_dir=temp_dir)
        
        assert "doc1" in vs2.collections["memories"]["ids"]
        assert "doc2" in vs2.collections["memories"]["ids"]
    
    def test_persistence_file_exists(self, temp_dir):
        """测试持久化文件存在"""
        vs = VectorStorage(persist_dir=temp_dir)
        vs.add("test", "doc", "内容", {})
        
        import os
        assert os.path.exists(os.path.join(temp_dir, "vectors.json"))


class TestConvenienceFunctions:
    """测试便捷函数（使用全局 vector_db 实例）"""
    
    def test_add_vector_function(self, temp_dir):
        """测试 add_vector 便捷函数"""
        # 设置全局实例的目录
        import chromadb_storage
        chromadb_storage.vector_db.persist_dir = temp_dir
        
        add_vector(
            collection="func_test",
            doc_id="func_doc",
            document="便捷函数测试",
            metadata={"source": "test"}
        )
        
        coll = chromadb_storage.vector_db.collections["func_test"]
        assert "func_doc" in coll["ids"]
    
    def test_search_vector_function(self, temp_dir):
        """测试 search_vector 便捷函数"""
        import chromadb_storage
        chromadb_storage.vector_db.persist_dir = temp_dir
        
        chromadb_storage.vector_db.add("func_test", "s_doc1", "搜索内容一", {})
        chromadb_storage.vector_db.add("func_test", "s_doc2", "搜索内容二", {})
        
        results = search_vector(
            collection="func_test",
            query="搜索内容"
        )
        
        assert results is not None
        assert len(results["ids"]) > 0
    
    def test_delete_vector_function(self, temp_dir):
        """测试 delete_vector 便捷函数"""
        import chromadb_storage
        chromadb_storage.vector_db.persist_dir = temp_dir
        
        chromadb_storage.vector_db.add("func_test", "del_doc", "将被删除", {})
        
        delete_vector(
            collection="func_test",
            doc_id="del_doc"
        )
        
        coll = chromadb_storage.vector_db.collections["func_test"]
        assert "del_doc" not in coll["ids"]


class TestEdgeCases:
    """边界情况测试"""
    
    def test_very_long_document(self, storage):
        """测试超长文档"""
        long_doc = "word " * 1000
        storage.add("test", "long_doc", long_doc, {})
        coll = storage.collections["test"]
        assert "long_doc" in coll["ids"]
    
    def test_special_characters(self, storage):
        """测试特殊字符"""
        special = "Hello! @#$%^&*() 世界 🌍 émojis"
        storage.add("test", "special", special, {})
        coll = storage.collections["test"]
        assert "special" in coll["ids"]
    
    def test_metadata_types(self, storage):
        """测试各种元数据类型"""
        metadata = {
            "string": "value",
            "number": 42,
            "float": 3.14,
            "bool": True,
            "list": [1, 2, 3],
            "none": None
        }
        storage.add("test", "meta", "内容", metadata)
    
    def test_multiple_collections(self, storage):
        """测试多个集合"""
        for i in range(3):
            storage.add(f"coll_{i}", f"doc_{i}", f"内容{i}", {})
        
        for i in range(3):
            coll = storage.collections[f"coll_{i}"]
            assert f"doc_{i}" in coll["ids"]
    
    def test_vectors_are_numpy_arrays(self, storage):
        """测试向量是 NumPy 数组"""
        import numpy as np
        
        storage.add("test", "v1", "测试内容", {})
        coll = storage.collections["test"]
        
        # 检查向量是 NumPy 数组
        assert len(coll["vectors"]) > 0
        assert isinstance(coll["vectors"][0], np.ndarray)


# ============ Main Entry Point ============

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
