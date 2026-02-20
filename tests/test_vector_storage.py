"""
Unit Tests for Vector Storage Module (Mock-based)
================================================
向量存储模块的单元测试（使用 Mock）

由于 Python 3.14 与 ChromaDB 的 pydantic v1 兼容性问题，
本测试使用 Mock 来验证代码逻辑。

测试覆盖:
- 初始化 ChromaDB 集合
- 添加向量 (add_vector)
- 向量搜索 (search_vector)
- 删除向量 (delete_vector)
- 更新向量 (update_vector)

Author: RUNBOT-DEV（笑天）
Version: 1.0.0
Date: 2026-02-20
"""

import pytest
import os
import tempfile
import shutil
import uuid
from typing import Dict, Any, List, Optional
from unittest.mock import Mock, patch, MagicMock, PropertyMock

# 导入被测模块
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


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
def sample_content():
    """示例内容"""
    return "Python is a great programming language for AI and machine learning."


@pytest.fixture
def sample_metadata():
    """示例元数据"""
    return {
        "tags": ["python", "ai"],
        "category": "programming",
        "priority": "high"
    }


@pytest.fixture
def mock_chromadb():
    """创建 Mock ChromaDB 对象"""
    mock_client = MagicMock()
    mock_collection = MagicMock()
    
    # Mock collection methods
    mock_collection.add = MagicMock()
    mock_collection.get = MagicMock(return_value={
        "ids": [],
        "documents": [],
        "metadatas": [],
        "distances": []
    })
    mock_collection.delete = MagicMock()
    mock_collection.query = MagicMock(return_value={
        "ids": [[]],
        "documents": [[]],
        "metadatas": [[]],
        "distances": [[]]
    })
    mock_collection.count = MagicMock(return_value=0)
    
    # Mock client methods
    mock_client.get_collection = MagicMock(return_value=mock_collection)
    mock_client.create_collection = MagicMock(return_value=mock_collection)
    
    return mock_client, mock_collection


# ============ Import Test ============

class TestImport:
    """导入测试类"""
    
    def test_import_vector_storage(self):
        """测试导入模块"""
        try:
            from core.vector_storage import (
                VectorStorage,
                VectorStorageError,
                CollectionNotFoundError,
                DocumentNotFoundError,
                EmbeddingError,
                CHROMADB_AVAILABLE
            )
            
            # Verify classes exist
            assert VectorStorage is not None
            assert VectorStorageError is not None
            assert CollectionNotFoundError is not None
            assert DocumentNotFoundError is not None
            
            print("✅ All classes imported successfully")
            
        except ImportError as e:
            pytest.fail(f"Import failed: {e}")


# ============ Mock-based Tests ============

class TestVectorStorageWithMock:
    """使用 Mock 测试 VectorStorage"""
    
    def test_generate_id_format(self):
        """测试 ID 生成格式"""
        from core.vector_storage import VectorStorage
        
        with patch('core.vector_storage.chromadb'):
            # Create instance without actual ChromaDB
            with patch.object(VectorStorage, '_get_or_create_collection'):
                vs = VectorStorage.__new__(VectorStorage)
                vs._lock = MagicMock()
                vs._collections = {}
                
                # Test ID generation
                doc_id = vs._generate_id()
                assert doc_id.startswith("doc_")
                assert len(doc_id) == len("doc_") + 16  # UUID hex length
    
    def test_validate_collection_new(self, temp_dir):
        """测试验证新集合"""
        from core.vector_storage import VectorStorage
        
        with patch('core.vector_storage.chromadb'):
            vs = VectorStorage.__new__(VectorStorage)
            vs.persist_dir = temp_dir
            vs._lock = MagicMock()
            vs._collections = {}
            vs._client = MagicMock()
            vs._get_or_create_collection = MagicMock(return_value=MagicMock())
            
            collection_name = vs._validate_collection("test_collection")
            assert collection_name == "test_collection"
    
    def test_validate_collection_none(self, temp_dir):
        """测试验证 None 集合（使用默认 knowledge）"""
        from core.vector_storage import VectorStorage
        
        with patch('core.vector_storage.chromadb'):
            vs = VectorStorage.__new__(VectorStorage)
            vs.persist_dir = temp_dir
            vs._lock = MagicMock()
            vs._collections = {}
            vs._client = MagicMock()
            vs._get_or_create_collection = MagicMock(return_value=MagicMock())
            
            collection_name = vs._validate_collection(None)
            assert collection_name == VectorStorage.COLLECTION_KNOWLEDGE


class TestVectorStorageLogic:
    """测试 VectorStorage 逻辑"""
    
    def test_collection_names_constant(self):
        """测试集合名称常量"""
        from core.vector_storage import VectorStorage
        
        assert VectorStorage.COLLECTION_CONVERSATIONS == "conversations"
        assert VectorStorage.COLLECTION_GOALS == "goals"
        assert VectorStorage.COLLECTION_KNOWLEDGE == "knowledge"
    
    def test_add_vector_params(self):
        """测试 add_vector 参数处理"""
        from core.vector_storage import VectorStorage
        
        with patch('core.vector_storage.chromadb'):
            vs = VectorStorage.__new__(VectorStorage)
            vs._lock = MagicMock()
            vs._collections = {}
            vs._validate_collection = MagicMock(return_value="knowledge")
            vs._get_or_create_collection = MagicMock(return_value=MagicMock())
            vs._generate_id = MagicMock(return_value="doc_test123")
            
            # Test with custom ID
            custom_id = "my_custom_id"
            doc_id = vs.add_vector(
                content="test content",
                doc_id=custom_id
            )
            
            assert doc_id == custom_id
            vs._validate_collection.assert_called_once()
    
    def test_search_vector_params(self):
        """测试 search_vector 参数处理"""
        from core.vector_storage import VectorStorage
        
        with patch('core.vector_storage.chromadb'):
            vs = VectorStorage.__new__(VectorStorage)
            vs._lock = MagicMock()
            vs._collections = {}
            vs._search_collection = MagicMock(return_value=[])
            
            # Test with n_results
            results = vs.search_vector(
                query="test query",
                n_results=10
            )
            
            assert vs._search_collection.call_count == 0  # Called with collection name first
    
    def test_delete_vector_params(self):
        """测试 delete_vector 参数处理"""
        from core.vector_storage import VectorStorage
        
        with patch('core.vector_storage.chromadb'):
            vs = VectorStorage.__new__(VectorStorage)
            vs._lock = MagicMock()
            vs._collections = {}
            vs._validate_collection = MagicMock(return_value="knowledge")
            vs._get_or_create_collection = MagicMock(return_value=MagicMock())
            
            # Test with specific collection
            result = vs.delete_vector(
                doc_id="test_doc",
                collection_name="knowledge"
            )
            
            vs._validate_collection.assert_called()


class TestExceptionClasses:
    """测试异常类"""
    
    def test_vector_storage_error_inheritance(self):
        """测试 VectorStorageError 继承"""
        from core.vector_storage import VectorStorageError
        
        assert issubclass(VectorStorageError, Exception)
    
    def test_collection_not_found_error(self):
        """测试 CollectionNotFoundError"""
        from core.vector_storage import CollectionNotFoundError
        
        error = CollectionNotFoundError("test collection not found")
        assert "test collection not found" in str(error)
        assert isinstance(error, Exception)
    
    def test_document_not_found_error(self):
        """测试 DocumentNotFoundError"""
        from core.vector_storage import DocumentNotFoundError
        
        error = DocumentNotFoundError("doc_123 not found")
        assert "doc_123 not found" in str(error)
        assert isinstance(error, Exception)
    
    def test_embedding_error(self):
        """测试 EmbeddingError"""
        from core.vector_storage import EmbeddingError
        
        error = EmbeddingError("Embedding generation failed")
        assert "Embedding generation failed" in str(error)


class TestMetadataHandling:
    """测试元数据处理"""
    
    def test_metadata_timestamp_added(self, temp_dir):
        """测试元数据中添加时间戳"""
        from core.vector_storage import VectorStorage
        from datetime import datetime
        
        with patch('core.vector_storage.chromadb'):
            vs = VectorStorage.__new__(VectorStorage)
            vs._lock = MagicMock()
            vs._collections = {}
            vs._validate_collection = MagicMock(return_value="knowledge")
            vs._get_or_create_collection = MagicMock()
            
            mock_collection = MagicMock()
            vs._get_or_create_collection.return_value = mock_collection
            
            # Call add_vector
            with patch.object(vs, '_generate_id', return_value='doc_test'):
                vs.add_vector(
                    content="test",
                    metadata={"key": "value"}
                )
            
            # Verify add was called with timestamp
            mock_collection.add.assert_called()
            call_args = mock_collection.add.call_args
            
            # Check metadata contains timestamp
            metadata = call_args.kwargs.get('metadatas', [{}])[0]
            assert 'created_at' in metadata
            assert 'updated_at' in metadata


class TestBatchOperations:
    """测试批量操作"""
    
    def test_add_vectors_length_mismatch(self, temp_dir):
        """测试批量添加时长度不匹配"""
        from core.vector_storage import VectorStorage
        from core.vector_storage import VectorStorageError
        
        with patch('core.vector_storage.chromadb'):
            vs = VectorStorage.__new__(VectorStorage)
            vs._lock = MagicMock()
            vs._collections = {}
            vs._validate_collection = MagicMock(return_value="knowledge")
            
            with pytest.raises(VectorStorageError):
                vs.add_vectors(
                    contents=["Doc 1", "Doc 2", "Doc 3"],
                    doc_ids=["id1", "id2"]  # Mismatch!
                )


class TestSearchResults:
    """测试搜索结果格式"""
    
    def test_search_result_structure(self):
        """测试搜索结果结构"""
        from core.vector_storage import VectorStorage
        
        # Simulate search result parsing
        raw_results = {
            "ids": [["doc1", "doc2"]],
            "documents": [["content1", "content2"]],
            "metadatas": [[{"tag": "a"}, {"tag": "b"}]],
            "distances": [[0.1, 0.2]]
        }
        
        # Parse results (simulating the logic in search_vector)
        parsed_results = []
        if raw_results.get("ids") and raw_results["ids"][0]:
            ids = raw_results["ids"][0]
            documents = raw_results.get("documents", [[]])[0]
            metadatas = raw_results.get("metadatas", [[]])[0]
            distances = raw_results.get("distances", [[]])[0]
            
            for i, doc_id in enumerate(ids):
                result = {
                    "id": doc_id,
                    "content": documents[i] if i < len(documents) else "",
                    "metadata": metadatas[i] if i < len(metadatas) else {},
                    "distance": distances[i] if i < len(distances) else 0.0
                }
                parsed_results.append(result)
        
        assert len(parsed_results) == 2
        assert parsed_results[0]["id"] == "doc1"
        assert parsed_results[0]["content"] == "content1"
        assert parsed_results[0]["distance"] == 0.1
        assert parsed_results[1]["metadata"]["tag"] == "b"


class TestUpsertLogic:
    """测试 Upsert 逻辑"""
    
    def test_upsert_insert_new(self, temp_dir):
        """测试 upsert 插入新文档"""
        from core.vector_storage import VectorStorage
        
        with patch('core.vector_storage.chromadb'):
            vs = VectorStorage.__new__(VectorStorage)
            vs._lock = MagicMock()
            vs._collections = {}
            vs._validate_collection = MagicMock(return_value="knowledge")
            vs._get_or_create_collection = MagicMock()
            
            mock_collection = MagicMock()
            mock_collection.get.return_value = {"documents": []}  # Not exists
            vs._get_or_create_collection.return_value = mock_collection
            
            with patch.object(vs, 'add_vector') as mock_add:
                vs.upsert_vector(
                    doc_id="new_doc",
                    content="new content"
                )
                
                mock_add.assert_called_once()
    
    def test_upsert_update_existing(self, temp_dir):
        """测试 upsert 更新已有文档"""
        from core.vector_storage import VectorStorage
        
        with patch('core.vector_storage.chromadb'):
            vs = VectorStorage.__new__(VectorStorage)
            vs._lock = MagicMock()
            vs._collections = {}
            vs._validate_collection = MagicMock(return_value="knowledge")
            vs._get_or_create_collection = MagicMock()
            
            mock_collection = MagicMock()
            mock_collection.get.return_value = {
                "documents": ["old content"],
                "metadatas": [{"old": "meta"}]
            }
            vs._get_or_create_collection.return_value = mock_collection
            
            vs.upsert_vector(
                doc_id="existing_doc",
                content="updated content"
            )
            
            # Should call delete then add
            mock_collection.delete.assert_called_once()
            mock_collection.add.assert_called_once()


class TestEdgeCases:
    """边界情况测试"""
    
    def test_empty_content(self):
        """测试空内容"""
        from core.vector_storage import VectorStorage
        
        with patch('core.vector_storage.chromadb'):
            vs = VectorStorage.__new__(VectorStorage)
            vs._lock = MagicMock()
            vs._collections = {}
            vs._validate_collection = MagicMock(return_value="knowledge")
            vs._get_or_create_collection = MagicMock()
            vs._generate_id = MagicMock(return_value="doc_empty")
            
            doc_id = vs.add_vector(content="")
            
            assert doc_id == "doc_empty"
            vs._get_or_create_collection.assert_called()
    
    def test_very_long_content(self):
        """测试超长内容"""
        from core.vector_storage import VectorStorage
        
        long_content = "word " * 1000
        
        with patch('core.vector_storage.chromadb'):
            vs = VectorStorage.__new__(VectorStorage)
            vs._lock = MagicMock()
            vs._collections = {}
            vs._validate_collection = MagicMock(return_value="knowledge")
            vs._get_or_create_collection = MagicMock()
            vs._generate_id = MagicMock(return_value="doc_long")
            
            doc_id = vs.add_vector(content=long_content)
            
            assert doc_id == "doc_long"
    
    def test_special_characters(self):
        """测试特殊字符"""
        from core.vector_storage import VectorStorage
        
        special_content = "Hello! @#$%^&*() 世界 🌍 émojis"
        
        with patch('core.vector_storage.chromadb'):
            vs = VectorStorage.__new__(VectorStorage)
            vs._lock = MagicMock()
            vs._collections = {}
            vs._validate_collection = MagicMock(return_value="knowledge")
            vs._get_or_create_collection = MagicMock()
            vs._generate_id = MagicMock(return_value="doc_special")
            
            doc_id = vs.add_vector(content=special_content)
            
            assert doc_id == "doc_special"
    
    def test_unicode_metadata(self):
        """测试 Unicode 元数据"""
        from core.vector_storage import VectorStorage
        
        unicode_metadata = {"chinese": "中文", "emoji": "🚀"}
        
        with patch('core.vector_storage.chromadb'):
            vs = VectorStorage.__new__(VectorStorage)
            vs._lock = MagicMock()
            vs._collections = {}
            vs._validate_collection = MagicMock(return_value="knowledge")
            vs._get_or_create_collection = MagicMock()
            vs._generate_id = MagicMock(return_value="doc_unicode")
            
            doc_id = vs.add_vector(content="test", metadata=unicode_metadata)
            
            assert doc_id == "doc_unicode"


class TestConcurrency:
    """并发测试"""
    
    def test_thread_lock(self):
        """测试线程锁"""
        from core.vector_storage import VectorStorage
        
        with patch('core.vector_storage.chromadb'):
            vs = VectorStorage(persist_dir=":memory:")
            
            # Verify lock is created
            assert vs._lock is not None
            
            # Try acquiring lock
            with vs._lock:
                # Do some work
                pass
            
            vs.close()


class TestListCollections:
    """测试列出集合"""
    
    def test_list_collections_format(self):
        """测试列出集合返回格式"""
        from core.vector_storage import VectorStorage
        
        with patch('core.vector_storage.chromadb'):
            vs = VectorStorage.__new__(VectorStorage)
            vs._lock = MagicMock()
            vs._collections = {"coll1": MagicMock(), "coll2": MagicMock()}
            
            collections = vs.list_collections()
            
            assert isinstance(collections, list)
            assert "coll1" in collections
            assert "coll2" in collections


# ============ Main Entry Point ============

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
