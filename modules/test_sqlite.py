"""
SQLite Storage Layer Unit Tests - SQLite 存储层单元测试

测试覆盖：
1. 初始化
2. CRUD 操作
3. 事务
4. 目标和里程碑
5. 标签系统
6. 签到功能
7. 知识库
8. WAL 日志
9. 统计信息
10. 边界情况
"""

import unittest
import os
import tempfile
import shutil
from pathlib import Path

import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from modules.sqlite_storage import SQLiteStorage


class TestSQLiteStorageBasic(unittest.TestCase):
    """SQLite 存储基础测试"""

    def setUp(self):
        """每个测试前创建临时数据库"""
        self.temp_dir = tempfile.mkdtemp()
        self.db_path = os.path.join(self.temp_dir, "test.db")
        self.storage = SQLiteStorage(self.db_path)

    def tearDown(self):
        """每个测试后清理"""
        if hasattr(self, 'storage') and self.storage:
            self.storage.close()
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)

    def test_init_creates_database(self):
        """测试初始化创建数据库"""
        self.assertTrue(os.path.exists(self.db_path))

    def test_init_with_custom_path(self):
        """测试自定义路径初始化"""
        custom_path = os.path.join(self.temp_dir, "custom", "memory.db")
        storage = SQLiteStorage(custom_path)
        self.assertTrue(os.path.exists(custom_path))
        storage.close()

    def test_context_manager(self):
        """测试上下文管理器"""
        with SQLiteStorage(self.db_path) as storage:
            self.assertIsNotNone(storage)


class TestSQLiteStorageCRUD(unittest.TestCase):
    """CRUD 操作测试"""

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.db_path = os.path.join(self.temp_dir, "test.db")
        self.storage = SQLiteStorage(self.db_path)

    def tearDown(self):
        if hasattr(self, 'storage') and self.storage:
            self.storage.close()
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)

    def test_insert_memory(self):
        """测试插入记忆"""
        memory_id = self.storage.insert_memory(
            content="测试记忆内容",
            memory_type="conversation",
            metadata={"test": True}
        )

        self.assertIsNotNone(memory_id)
        self.assertTrue(len(memory_id) > 0)

    def test_get_memory(self):
        """测试获取记忆"""
        memory_id = self.storage.insert_memory(
            content="待获取的记忆",
            memory_type="conversation"
        )

        memory = self.storage.get_memory(memory_id)

        self.assertIsNotNone(memory)
        self.assertEqual(memory['content'], "待获取的记忆")
        self.assertEqual(memory['memory_type'], "conversation")

    def test_get_memory_not_exists(self):
        """测试获取不存在的记忆"""
        memory = self.storage.get_memory("不存在的ID")
        self.assertIsNone(memory)

    def test_update_memory_content(self):
        """测试更新记忆内容"""
        memory_id = self.storage.insert_memory(
            content="原始内容",
            memory_type="conversation"
        )

        result = self.storage.update_memory(memory_id, content="更新后的内容")

        self.assertTrue(result)

        memory = self.storage.get_memory(memory_id)
        self.assertEqual(memory['content'], "更新后的内容")

    def test_update_memory_metadata(self):
        """测试更新记忆元数据"""
        memory_id = self.storage.insert_memory(
            content="内容",
            memory_type="conversation"
        )

        result = self.storage.update_memory(memory_id, metadata={"key": "value"})

        self.assertTrue(result)

        memory = self.storage.get_memory(memory_id)
        # metadata 字段是 JSON 字符串
        import json
        self.assertEqual(json.loads(memory['metadata']), {"key": "value"})

    def test_delete_memory_soft(self):
        """测试软删除记忆"""
        memory_id = self.storage.insert_memory(
            content="待删除",
            memory_type="conversation"
        )

        result = self.storage.delete_memory(memory_id, soft=True)

        self.assertTrue(result)

        # 软删除后应该找不到
        memory = self.storage.get_memory(memory_id)
        self.assertIsNone(memory)

    def test_delete_memory_hard(self):
        """测试硬删除记忆"""
        memory_id = self.storage.insert_memory(
            content="待硬删除",
            memory_type="conversation"
        )

        result = self.storage.delete_memory(memory_id, soft=False)

        self.assertTrue(result)

    def test_search_memories(self):
        """测试搜索记忆"""
        self.storage.insert_memory(content="Python编程", memory_type="knowledge")
        self.storage.insert_memory(content="Java开发", memory_type="knowledge")
        self.storage.insert_memory(content="Python机器学习", memory_type="knowledge")

        results = self.storage.search_memories(query="Python")

        self.assertEqual(len(results), 2)

    def test_search_memories_by_type(self):
        """测试按类型搜索"""
        self.storage.insert_memory(content="对话1", memory_type="conversation")
        self.storage.insert_memory(content="对话2", memory_type="conversation")
        self.storage.insert_memory(content="知识", memory_type="knowledge")

        results = self.storage.search_memories(memory_type="conversation")

        self.assertEqual(len(results), 2)

    def test_search_memories_limit(self):
        """测试搜索限制"""
        for i in range(20):
            self.storage.insert_memory(content=f"内容{i}", memory_type="conversation")

        results = self.storage.search_memories(limit=5)

        self.assertLessEqual(len(results), 5)


class TestSQLiteStorageTransactions(unittest.TestCase):
    """事务测试"""

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.db_path = os.path.join(self.temp_dir, "test.db")
        self.storage = SQLiteStorage(self.db_path)

    def tearDown(self):
        if hasattr(self, 'storage') and self.storage:
            self.storage.close()
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)

    def test_transaction_commit(self):
        """测试事务提交"""
        with self.storage.transaction() as cursor:
            cursor.execute(
                "INSERT INTO goals (id, title, goal_type, created_at, updated_at) VALUES (?, ?, ?, ?, ?)",
                ("tx_goal1", "测试目标", "monthly", "2026-01-01", "2026-01-01")
            )

        goal = self.storage.get_goal("tx_goal1")
        self.assertIsNotNone(goal)

    def test_transaction_rollback(self):
        """测试事务回滚"""
        try:
            with self.storage.transaction() as cursor:
                cursor.execute(
                    "INSERT INTO goals (id, title, goal_type, created_at, updated_at) VALUES (?, ?, ?, ?, ?)",
                    ("tx_rollback", "测试", "monthly", "2026-01-01", "2026-01-01")
                )
                raise Exception("模拟回滚")
        except:
            pass

        goal = self.storage.get_goal("tx_rollback")
        self.assertIsNone(goal)


class TestSQLiteStorageGoals(unittest.TestCase):
    """目标测试"""

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.db_path = os.path.join(self.temp_dir, "test.db")
        self.storage = SQLiteStorage(self.db_path)

    def tearDown(self):
        if hasattr(self, 'storage') and self.storage:
            self.storage.close()
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)

    def test_insert_goal(self):
        """测试插入目标"""
        goal_id = self.storage.insert_goal(
            title="完成系统设计",
            goal_type="monthly",
            description="设计并实现系统",
            period="2026-02"
        )

        self.assertIsNotNone(goal_id)

    def test_get_goal(self):
        """测试获取目标"""
        goal_id = self.storage.insert_goal(title="测试目标", goal_type="weekly")

        goal = self.storage.get_goal(goal_id)

        self.assertIsNotNone(goal)
        self.assertEqual(goal['title'], "测试目标")

    def test_update_goal_progress(self):
        """测试更新目标进度"""
        goal_id = self.storage.insert_goal(title="进度目标", goal_type="monthly")

        result = self.storage.update_goal_progress(goal_id, 75)

        self.assertTrue(result)

        goal = self.storage.get_goal(goal_id)
        self.assertEqual(goal['progress'], 75)
        self.assertEqual(goal['status'], 'active')

    def test_update_goal_complete(self):
        """测试完成目标"""
        goal_id = self.storage.insert_goal(title="完成目标", goal_type="monthly")

        self.storage.update_goal_progress(goal_id, 100)

        goal = self.storage.get_goal(goal_id)
        self.assertEqual(goal['progress'], 100)
        self.assertEqual(goal['status'], 'completed')
        self.assertIsNotNone(goal['completed_at'])

    def test_get_goals_by_type(self):
        """测试按类型获取目标"""
        self.storage.insert_goal(title="月度1", goal_type="monthly")
        self.storage.insert_goal(title="月度2", goal_type="monthly")
        self.storage.insert_goal(title="周目标", goal_type="weekly")

        goals = self.storage.get_goals_by_type("monthly")

        self.assertEqual(len(goals), 2)


class TestSQLiteStorageMilestones(unittest.TestCase):
    """里程碑测试"""

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.db_path = os.path.join(self.temp_dir, "test.db")
        self.storage = SQLiteStorage(self.db_path)

    def tearDown(self):
        if hasattr(self, 'storage') and self.storage:
            self.storage.close()
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)

    def test_add_milestone(self):
        """测试添加里程碑"""
        goal_id = self.storage.insert_goal(title="目标", goal_type="monthly")

        milestone_id = self.storage.add_milestone(
            goal_id=goal_id,
            title="里程碑1",
            due_date="2026-02-20"
        )

        self.assertIsNotNone(milestone_id)

    def test_complete_milestone(self):
        """测试完成里程碑"""
        goal_id = self.storage.insert_goal(title="目标", goal_type="monthly")
        milestone_id = self.storage.add_milestone(goal_id=goal_id, title="里程碑")

        result = self.storage.complete_milestone(milestone_id)

        self.assertTrue(result)

        milestones = self.storage.get_milestones(goal_id)
        self.assertEqual(milestones[0]['status'], 'completed')

    def test_get_milestones(self):
        """测试获取里程碑"""
        goal_id = self.storage.insert_goal(title="目标", goal_type="monthly")
        self.storage.add_milestone(goal_id=goal_id, title="里程碑1")
        self.storage.add_milestone(goal_id=goal_id, title="里程碑2")

        milestones = self.storage.get_milestones(goal_id)

        self.assertEqual(len(milestones), 2)


class TestSQLiteStorageTags(unittest.TestCase):
    """标签测试"""

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.db_path = os.path.join(self.temp_dir, "test.db")
        self.storage = SQLiteStorage(self.db_path)

    def tearDown(self):
        if hasattr(self, 'storage') and self.storage:
            self.storage.close()
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)

    def test_create_tag(self):
        """测试创建标签"""
        tag_id = self.storage.create_tag(
            name="python",
            category="programming",
            aliases=["py", "python3"],
            description="Python相关内容"
        )

        self.assertIsNotNone(tag_id)

    def test_get_tag(self):
        """测试获取标签"""
        self.storage.create_tag(name="测试标签")

        tag = self.storage.get_tag("测试标签")

        self.assertIsNotNone(tag)
        self.assertEqual(tag['name'], "测试标签")

    def test_assign_tag(self):
        """测试分配标签"""
        memory_id = self.storage.insert_memory("内容", "knowledge")

        result = self.storage.assign_tag(memory_id, "python")

        self.assertTrue(result)

        tags = self.storage.get_memory_tags(memory_id)
        self.assertEqual(len(tags), 1)
        self.assertEqual(tags[0]['name'], "python")

    def test_assign_tag_creates_if_not_exists(self):
        """测试分配不存在的标签时自动创建"""
        memory_id = self.storage.insert_memory("内容", "knowledge")

        self.storage.assign_tag(memory_id, "新标签")

        tags = self.storage.get_memory_tags(memory_id)
        self.assertEqual(len(tags), 1)
        self.assertEqual(tags[0]['name'], "新标签")

    def test_remove_tag(self):
        """测试移除标签"""
        memory_id = self.storage.insert_memory("内容", "knowledge")
        self.storage.assign_tag(memory_id, "标签")

        result = self.storage.remove_tag(memory_id, "标签")

        self.assertTrue(result)

        tags = self.storage.get_memory_tags(memory_id)
        self.assertEqual(len(tags), 0)

    def test_get_all_tags(self):
        """测试获取所有标签"""
        self.storage.create_tag(name="标签1")
        self.storage.create_tag(name="标签2")

        tags = self.storage.get_all_tags()

        self.assertEqual(len(tags), 2)


class TestSQLiteStorageCheckins(unittest.TestCase):
    """签到测试"""

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.db_path = os.path.join(self.temp_dir, "test.db")
        self.storage = SQLiteStorage(self.db_path)

    def tearDown(self):
        if hasattr(self, 'storage') and self.storage:
            self.storage.close()
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)

    def test_add_checkin(self):
        """测试添加签到"""
        goal_id = self.storage.insert_goal(title="目标", goal_type="weekly")

        checkin_id = self.storage.add_checkin(
            goal_id=goal_id,
            date="2026-02-20",
            progress=50,
            notes="完成50%"
        )

        self.assertIsNotNone(checkin_id)

    def test_get_checkins_by_goal(self):
        """测试按目标获取签到"""
        goal_id = self.storage.insert_goal(title="目标", goal_type="weekly")
        self.storage.add_checkin(goal_id=goal_id, date="2026-02-20", progress=30)
        self.storage.add_checkin(goal_id=goal_id, date="2026-02-21", progress=60)

        checkins = self.storage.get_checkins(goal_id=goal_id)

        self.assertEqual(len(checkins), 2)

    def test_get_checkins_by_date(self):
        """测试按日期获取签到"""
        goal_id = self.storage.insert_goal(title="目标", goal_type="weekly")
        self.storage.add_checkin(goal_id=goal_id, date="2026-02-20", progress=30)

        checkins = self.storage.get_checkins(date="2026-02-20")

        self.assertEqual(len(checkins), 1)


class TestSQLiteStorageKnowledge(unittest.TestCase):
    """知识库测试"""

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.db_path = os.path.join(self.temp_dir, "test.db")
        self.storage = SQLiteStorage(self.db_path)

    def tearDown(self):
        if hasattr(self, 'storage') and self.storage:
            self.storage.close()
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)

    def test_insert_knowledge(self):
        """测试插入知识"""
        kb_id = self.storage.insert_knowledge(
            title="Python最佳实践",
            content="1. 使用类型提示\n2. 遵循PEP8",
            category="programming/python"
        )

        self.assertIsNotNone(kb_id)

    def test_get_knowledge(self):
        """测试获取知识"""
        kb_id = self.storage.insert_knowledge(title="知识", content="内容")

        kb = self.storage.get_knowledge(kb_id)

        self.assertIsNotNone(kb)
        self.assertEqual(kb['title'], "知识")

    def test_update_knowledge_usage(self):
        """测试更新知识使用次数"""
        kb_id = self.storage.insert_knowledge(title="知识", content="内容")

        self.storage.update_knowledge_usage(kb_id)
        self.storage.update_knowledge_usage(kb_id)

        kb = self.storage.get_knowledge(kb_id)
        self.assertEqual(kb['usage_count'], 2)

    def test_search_knowledge(self):
        """测试搜索知识"""
        self.storage.insert_knowledge(title="Python教程", content="Python学习", category="python")
        self.storage.insert_knowledge(title="Java教程", content="Java学习", category="java")

        results = self.storage.search_knowledge("Python")

        self.assertGreaterEqual(len(results), 1)


class TestSQLiteStorageWAL(unittest.TestCase):
    """WAL 日志测试"""

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.db_path = os.path.join(self.temp_dir, "test.db")
        self.storage = SQLiteStorage(self.db_path)

    def tearDown(self):
        if hasattr(self, 'storage') and self.storage:
            self.storage.close()
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)

    def test_log_wal(self):
        """测试记录 WAL"""
        seq = self.storage.log_wal(
            operation="CREATE",
            table_name="goals",
            record_id="test_goal",
            data={"title": "测试目标"}
        )

        self.assertIsNotNone(seq)

    def test_get_pending_wal_logs(self):
        """测试获取待应用日志"""
        self.storage.log_wal(operation="INSERT", table_name="memories", record_id="id1", data={})
        self.storage.log_wal(operation="INSERT", table_name="memories", record_id="id2", data={})

        logs = self.storage.get_pending_wal_logs()

        self.assertEqual(len(logs), 2)

    def test_mark_wal_applied(self):
        """测试标记 WAL 已应用"""
        seq = self.storage.log_wal(operation="INSERT", table_name="memories", record_id="id1", data={})

        result = self.storage.mark_wal_applied(seq)

        self.assertTrue(result)

        logs = self.storage.get_pending_wal_logs()
        self.assertEqual(len(logs), 0)


class TestSQLiteStorageConversations(unittest.TestCase):
    """对话测试"""

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.db_path = os.path.join(self.temp_dir, "test.db")
        self.storage = SQLiteStorage(self.db_path)

    def tearDown(self):
        if hasattr(self, 'storage') and self.storage:
            self.storage.close()
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)

    def test_insert_conversation(self):
        """测试插入对话"""
        conversation_id = self.storage.insert_conversation(
            channel_id="test_channel",
            message_count=10,
            participants=["user1", "user2"]
        )

        self.assertIsNotNone(conversation_id)

    def test_get_conversation(self):
        """测试获取对话"""
        conversation_id = self.storage.insert_conversation(channel_id="channel1")

        conversation = self.storage.get_conversation(conversation_id)

        self.assertIsNotNone(conversation)
        self.assertEqual(conversation['channel_id'], "channel1")

    def test_get_conversations_by_channel(self):
        """测试按频道获取对话"""
        self.storage.insert_conversation(channel_id="channel1")
        self.storage.insert_conversation(channel_id="channel1")
        self.storage.insert_conversation(channel_id="channel2")

        conversations = self.storage.get_conversations_by_channel("channel1")

        self.assertEqual(len(conversations), 2)


class TestSQLiteStorageStats(unittest.TestCase):
    """统计测试"""

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.db_path = os.path.join(self.temp_dir, "test.db")
        self.storage = SQLiteStorage(self.db_path)

    def tearDown(self):
        if hasattr(self, 'storage') and self.storage:
            self.storage.close()
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)

    def test_get_stats_empty(self):
        """测试空数据库统计"""
        stats = self.storage.get_stats()

        self.assertIn('memories', stats)
        self.assertIn('goals', stats)
        self.assertIn('tags', stats)
        self.assertEqual(stats['memories'], 0)

    def test_get_stats_with_data(self):
        """测试有数据时的统计"""
        self.storage.insert_memory("内容1", "conversation")
        self.storage.insert_memory("内容2", "conversation")
        self.storage.insert_goal(title="目标", goal_type="monthly")
        self.storage.create_tag(name="标签")
        self.storage.insert_knowledge(title="知识", content="内容")

        stats = self.storage.get_stats()

        self.assertEqual(stats['memories'], 2)
        self.assertEqual(stats['goals'], 1)
        self.assertEqual(stats['tags'], 1)
        self.assertEqual(stats['knowledge'], 1)


class TestSQLiteStorageEdgeCases(unittest.TestCase):
    """边界情况测试"""

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.db_path = os.path.join(self.temp_dir, "test.db")
        self.storage = SQLiteStorage(self.db_path)

    def tearDown(self):
        if hasattr(self, 'storage') and self.storage:
            self.storage.close()
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)

    def test_empty_content(self):
        """测试空内容"""
        memory_id = self.storage.insert_memory(content="", memory_type="conversation")
        self.assertIsNotNone(memory_id)

    def test_special_characters(self):
        """测试特殊字符"""
        content = "特殊: !@#$%^&*()[]{}|;':\",./<>?"
        memory_id = self.storage.insert_memory(content=content, memory_type="conversation")

        memory = self.storage.get_memory(memory_id)
        self.assertEqual(memory['content'], content)

    def test_unicode_content(self):
        """测试 Unicode 内容"""
        content = "中文内容 🚀 émojis"
        memory_id = self.storage.insert_memory(content=content, memory_type="conversation")

        memory = self.storage.get_memory(memory_id)
        self.assertEqual(memory['content'], content)

    def test_complex_metadata(self):
        """测试复杂元数据"""
        metadata = {
            "list": [1, 2, 3],
            "nested": {"key": "value"},
            "number": 42
        }
        memory_id = self.storage.insert_memory(content="内容", memory_type="conversation", metadata=metadata)

        memory = self.storage.get_memory(memory_id)
        # metadata 字段是 JSON 字符串
        import json
        self.assertEqual(json.loads(memory['metadata']), metadata)

    def test_update_nonexistent(self):
        """测试更新不存在的记录"""
        result = self.storage.update_memory("不存在的ID", content="内容")
        self.assertFalse(result)

    def test_delete_nonexistent(self):
        """测试删除不存在的记录"""
        result = self.storage.delete_memory("不存在的ID")
        self.assertFalse(result)


if __name__ == "__main__":
    unittest.main(verbosity=2)
