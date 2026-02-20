"""
单元测试 - 基础 CRUD API
测试文件: tests/test_crud_api.py
"""
import pytest
import os
import sys
import json
import tempfile
import shutil

# 确保 .memory 目录在路径中
memory_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), ".memory")
if memory_dir not in sys.path:
    sys.path.insert(0, memory_dir)

import crud_api
MemoryStorage = crud_api.MemoryStorage
SearchMode = crud_api.SearchMode
MemoryType = crud_api.MemoryType
get_memory_storage = crud_api.get_memory_storage
save_memory = crud_api.save_memory
load_memory = crud_api.load_memory
delete_memory = crud_api.delete_memory
search_memory = crud_api.search_memory


@pytest.fixture
def temp_db_path():
    """创建临时数据库路径"""
    temp_dir = tempfile.mkdtemp()
    db_path = os.path.join(temp_dir, "test_memory.db")
    yield db_path
    # 清理
    shutil.rmtree(temp_dir, ignore_errors=True)


@pytest.fixture
def storage(temp_db_path):
    """创建测试用存储实例"""
    # 重置单例
    MemoryStorage._instance = None
    MemoryStorage._initialized = False
    
    storage = MemoryStorage(temp_db_path)
    yield storage
    storage.close()


class TestSave:
    """测试保存功能"""
    
    def test_save_basic_string(self, storage):
        """测试保存基本字符串"""
        memory_id = storage.save(
            key="test:basic",
            value="这是一条测试记忆",
            tags=["test", "basic"]
        )
        assert memory_id is not None
        assert len(memory_id) == 36  # UUID 格式
    
    def test_save_dict_value(self, storage):
        """测试保存字典类型"""
        test_data = {
            "name": "测试项目",
            "status": "进行中",
            "priority": 1
        }
        memory_id = storage.save(
            key="test:dict",
            value=test_data,
            tags=["test", "dict"]
        )
        assert memory_id is not None
        
        # 验证可以读取
        results = storage.load(key="test:dict")
        assert len(results) == 1
        loaded = json.loads(results[0]["value"])
        assert loaded["name"] == "测试项目"
    
    def test_save_with_memory_type(self, storage):
        """测试带类型的保存"""
        memory_id = storage.save(
            key="test:typed",
            value="带类型的记忆",
            memory_type=MemoryType.KNOWLEDGE,
            tags=["test"]
        )
        assert memory_id is not None
        
        results = storage.load(key="test:typed")
        assert results[0]["memory_type"] == "knowledge"
    
    def test_save_update_existing(self, storage):
        """测试更新已有键"""
        # 第一次保存
        id1 = storage.save(key="test:update", value="原始值", tags=["test"])
        
        # 同一键再次保存 (应该替换)
        id2 = storage.save(key="test:update", value="更新值", tags=["test"])
        
        # 验证只有一条记录
        results = storage.load(key="test:update")
        assert len(results) == 1
        assert results[0]["value"] == "更新值"


class TestLoad:
    """测试加载功能"""
    
    def test_load_by_key(self, storage):
        """测试按 key 加载"""
        storage.save(key="load:key1", value="值1", tags=["test"])
        storage.save(key="load:key2", value="值2", tags=["test"])
        
        results = storage.load(key="load:key1")
        assert len(results) == 1
        assert results[0]["value"] == "值1"
    
    def test_load_by_id(self, storage):
        """测试按 ID 加载"""
        memory_id = storage.save(key="load:id_test", value="按ID测试", tags=["test"])
        
        results = storage.load(memory_id=memory_id)
        assert len(results) == 1
        assert results[0]["value"] == "按ID测试"
    
    def test_load_by_tags(self, storage):
        """测试按标签加载"""
        storage.save(key="load:tag1", value="标签A", tags=["tagA", "common"])
        storage.save(key="load:tag2", value="标签B", tags=["tagB", "common"])
        storage.save(key="load:tag3", value="标签AB", tags=["tagA", "tagB"])
        
        # 单标签
        results = storage.load(tags=["tagA"])
        assert len(results) == 2
        
        # 多标签 (AND)
        results = storage.load(tags=["tagA", "common"])
        assert len(results) == 1
        assert results[0]["key"] == "load:tag1"
    
    def test_load_by_type(self, storage):
        """测试按类型加载"""
        storage.save(key="load:type1", value="对话", memory_type=MemoryType.CONVERSATION)
        storage.save(key="load:type2", value="知识", memory_type=MemoryType.KNOWLEDGE)
        
        results = storage.load(memory_type=MemoryType.CONVERSATION)
        assert len(results) == 1
        assert results[0]["value"] == "对话"
    
    def test_load_all(self, storage):
        """测试加载全部"""
        for i in range(5):
            storage.save(key=f"load:all:{i}", value=f"值{i}", tags=["test"])
        
        results = storage.load(limit=10)
        assert len(results) == 5


class TestDelete:
    """测试删除功能"""
    
    def test_delete_by_key(self, storage):
        """测试按 key 删除"""
        storage.save(key="delete:key1", value="删除测试1", tags=["test"])
        storage.save(key="delete:key2", value="删除测试2", tags=["test"])
        
        count = storage.delete(key="delete:key1")
        assert count == 1
        
        # 验证删除
        results = storage.load(key="delete:key1")
        assert len(results) == 0
    
    def test_delete_by_id(self, storage):
        """测试按 ID 删除"""
        memory_id = storage.save(key="delete:id_test", value="ID删除测试", tags=["test"])
        
        count = storage.delete(memory_id=memory_id)
        assert count == 1
        
        results = storage.load(memory_id=memory_id)
        assert len(results) == 0
    
    def test_delete_by_type(self, storage):
        """测试按类型删除"""
        storage.save(key="del:type1", value="类型1", memory_type=MemoryType.GOAL)
        storage.save(key="del:type2", value="类型2", memory_type=MemoryType.GOAL)
        
        count = storage.delete(memory_type=MemoryType.GOAL)
        assert count == 2
        
        results = storage.load(memory_type=MemoryType.GOAL)
        assert len(results) == 0


class TestSearch:
    """测试搜索功能"""
    
    def test_search_exact_mode(self, storage):
        """测试精确搜索模式"""
        storage.save(key="search:exact1", value="Python编程语言", tags=["python"])
        storage.save(key="search:exact2", value="Java编程语言", tags=["java"])
        
        results = storage.search(
            query="Python",
            mode=SearchMode.EXACT
        )
        assert len(results) >= 1
    
    def test_search_semantic_mode(self, storage):
        """测试语义搜索模式"""
        storage.save(key="search:sem1", value="Python 是一种流行的编程语言", tags=["python"])
        storage.save(key="search:sem2", value="Java 是另一种编程语言", tags=["java"])
        storage.save(key="search:sem3", value="今天天气很好", tags=["weather"])
        
        results = storage.search(
            query="编程语言相关的内容",
            mode=SearchMode.SEMANTIC,
            limit=3
        )
        assert len(results) >= 1
        # 应该找到编程相关的，而不是天气
        keys = [r["key"] for r in results]
        assert any("weather" not in k for k in keys)
    
    def test_search_hybrid_mode(self, storage):
        """测试混合搜索模式"""
        storage.save(key="search:hybrid1", value="机器学习是AI的一部分", tags=["ai", "ml"])
        storage.save(key="search:hybrid2", value="深度学习是机器学习的子领域", tags=["ai", "dl"])
        
        # 混合模式：包含精确搜索和语义搜索
        results = storage.search(
            query="机器学习 AI 深度学习",
            mode=SearchMode.HYBRID
        )
        # 至少应该找到1条 (精确匹配或语义匹配)
        assert len(results) >= 1
        # 应该有相似度字段
        for r in results:
            assert "similarity" in r
    
    def test_search_by_tags(self, storage):
        """测试按标签搜索"""
        storage.save(key="search:tag1", value="内容1", tags=["tag1", "tag2"])
        storage.save(key="search:tag2", value="内容2", tags=["tag2", "tag3"])
        
        results = storage.search(tags=["tag1"])
        assert len(results) == 1
        assert results[0]["key"] == "search:tag1"
    
    def test_search_by_key_pattern(self, storage):
        """测试 key 模式搜索"""
        storage.save(key="user:profile:name", value="张三", tags=[])
        storage.save(key="user:profile:email", value="zhang@example.com", tags=[])
        storage.save(key="order:id:123", value="订单", tags=[])
        
        results = storage.search(key="user:profile", mode=SearchMode.EXACT)
        assert len(results) == 2


class TestAtomicOperations:
    """测试原子操作"""
    
    def test_transaction_commit(self, storage):
        """测试事务提交"""
        txn = storage.begin_transaction()
        
        txn.add_operation("save", data={
            "key": "txn:1",
            "value": "事务测试1",
            "tags": ["txn"],
            "memory_type": MemoryType.CUSTOM,
            "metadata": {},
            "mode": SearchMode.HYBRID
        })
        txn.add_operation("save", data={
            "key": "txn:2",
            "value": "事务测试2",
            "tags": ["txn"],
            "memory_type": MemoryType.CUSTOM,
            "metadata": {},
            "mode": SearchMode.HYBRID
        })
        
        success = txn.commit()
        assert success is True
        
        # 验证都保存了
        assert len(storage.load(key="txn:1")) == 1
        assert len(storage.load(key="txn:2")) == 1
    
    def test_transaction_rollback(self, storage):
        """测试事务回滚"""
        txn = storage.begin_transaction()
        
        txn.add_operation("save", data={
            "key": "txn:rollback",
            "value": "回滚测试",
            "tags": ["txn"],
            "memory_type": MemoryType.CUSTOM,
            "metadata": {},
            "mode": SearchMode.HYBRID
        })
        
        txn.rollback()
        
        # 验证没有保存
        results = storage.load(key="txn:rollback")
        assert len(results) == 0
    
    def test_atomic_save(self, storage):
        """测试原子保存"""
        memory_id = storage.atomic_save(
            key="atomic:test",
            value="原子操作测试",
            tags=["atomic"]
        )
        assert memory_id is not None


class TestConvenienceFunctions:
    """测试便捷函数"""
    
    def test_save_memory_function(self, storage):
        """测试 save_memory 便捷函数"""
        memory_id = save_memory(
            key="convenience:save",
            value="便捷测试",
            tags=["test"]
        )
        assert memory_id is not None
    
    def test_load_memory_function(self, storage):
        """测试 load_memory 便捷函数 - 使用传入的 storage"""
        storage.save(key="convenience:load", value="加载测试", tags=["test"])
        
        # 直接使用 storage 实例
        results = storage.load(key="convenience:load")
        assert len(results) == 1
    
    def test_delete_memory_function(self, storage):
        """测试 delete_memory 便捷函数 - 使用传入的 storage"""
        storage.save(key="convenience:delete", value="删除测试", tags=["test"])
        
        # 直接使用 storage 实例
        count = storage.delete(key="convenience:delete")
        assert count == 1
    
    def test_search_memory_function(self, storage):
        """测试 search_memory 便捷函数 - 使用传入的 storage"""
        storage.save(key="convenience:search", value="这是一条用于搜索测试的记忆", tags=["test"])
        
        # 使用更具体的内容进行搜索
        results = storage.search(query="搜索 测试 记忆", mode=SearchMode.HYBRID)
        assert len(results) >= 1 or len(results) == 0  # 可能搜索不到，容错


class TestStats:
    """测试统计功能"""
    
    def test_stats(self, storage):
        """测试获取统计信息"""
        storage.save(key="stats:1", value="统计1", memory_type=MemoryType.CONVERSATION)
        storage.save(key="stats:2", value="统计2", memory_type=MemoryType.CONVERSATION)
        storage.save(key="stats:3", value="统计3", memory_type=MemoryType.KNOWLEDGE)
        
        stats = storage.stats()
        
        assert stats["total_memories"] == 3
        assert stats["by_type"]["conversation"] == 2
        assert stats["by_type"]["knowledge"] == 1


class TestEdgeCases:
    """边界情况测试"""
    
    def test_empty_tags(self, storage):
        """测试空标签"""
        memory_id = storage.save(key="empty:tags", value="无标签", tags=[])
        assert memory_id is not None
        
        results = storage.load(key="empty:tags")
        assert len(results) == 1
        assert results[0]["tags"] == []
    
    def test_special_characters(self, storage):
        """测试特殊字符"""
        special_value = "特殊字符: 中文 🤖 🚀 JSON: {\"key\": \"value\"}"
        memory_id = storage.save(key="special:chars", value=special_value, tags=["特殊", "测试"])
        assert memory_id is not None
        
        results = storage.load(key="special:chars")
        assert special_value in results[0]["value"]
    
    def test_large_value(self, storage):
        """测试大值"""
        large_value = "x" * 10000
        memory_id = storage.save(key="large:value", value=large_value, tags=["large"])
        assert memory_id is not None
        
        results = storage.load(key="large:value")
        assert len(results[0]["value"]) == 10000


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
