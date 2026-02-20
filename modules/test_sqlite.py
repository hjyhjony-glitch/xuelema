"""
SQLite Storage Layer - 测试脚本
================================
"""

import sys
import os
import tempfile
import uuid

# 添加项目根目录到 Python 路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from modules.sqlite_storage import SQLiteStorage


def run_test(test_name, test_func):
    """运行单个测试"""
    print(f"\n{'='*50}")
    print(f"测试: {test_name}")
    print("=" * 50)
    
    db_path = None
    try:
        db_path = tempfile.mktemp(suffix='.db')
        storage = SQLiteStorage(db_path)
        
        result = test_func(storage)
        
        storage.close()
        try:
            os.unlink(db_path)
        except:
            pass
        
        print(f"\n✅ {test_name} 测试通过")
        return True
        
    except Exception as e:
        print(f"\n❌ {test_name} 测试失败: {e}")
        import traceback
        traceback.print_exc()
        if db_path:
            try:
                os.unlink(db_path)
            except:
                pass
        return False


def test_crud(storage):
    """测试 CRUD"""
    # Create
    memory_id = storage.insert_memory(
        content="测试记忆内容",
        memory_type="conversation",
        metadata={"test": True}
    )
    print(f"✓ 插入记忆: {memory_id}")
    
    # Read
    memory = storage.get_memory(memory_id)
    assert memory is not None
    assert memory['content'] == "测试记忆内容"
    print(f"✓ 读取记忆: {memory['content']}")
    
    # Update
    assert storage.update_memory(memory_id, content="更新后的内容")
    memory = storage.get_memory(memory_id)
    assert memory['content'] == "更新后的内容"
    print(f"✓ 更新记忆: {memory['content']}")
    
    # Delete (soft)
    assert storage.delete_memory(memory_id, soft=True)
    memory = storage.get_memory(memory_id)
    assert memory is None
    print(f"✓ 软删除记忆")
    
    return True


def test_transactions(storage):
    """测试事务"""
    # 成功事务
    with storage.transaction() as cursor:
        cursor.execute("INSERT INTO goals (id, title, goal_type, created_at, updated_at) VALUES (?, ?, ?, ?, ?)",
                      ("goal1", "测试目标", "monthly", "2026-01-01", "2026-01-01"))
        cursor.execute("INSERT INTO goals (id, title, goal_type, created_at, updated_at) VALUES (?, ?, ?, ?, ?)",
                      ("goal2", "测试目标2", "monthly", "2026-01-01", "2026-01-01"))
    
    goal = storage.get_goal("goal1")
    assert goal is not None
    print("✓ 事务提交成功")
    
    # 回滚事务
    try:
        with storage.transaction() as cursor:
            cursor.execute("INSERT INTO goals (id, title, goal_type, created_at, updated_at) VALUES (?, ?, ?, ?, ?)",
                          ("goal3", "测试目标3", "monthly", "2026-01-01", "2026-01-01"))
            raise Exception("模拟回滚")
    except:
        pass
    
    goal = storage.get_goal("goal3")
    assert goal is None
    print("✓ 事务回滚成功")
    
    return True


def test_goals_and_milestones(storage):
    """测试目标和里程碑"""
    # 创建目标
    goal_id = storage.insert_goal(
        title="完成系统设计",
        goal_type="monthly",
        description="设计并实现 Persistent Memory 系统",
        period="2026-02"
    )
    print(f"✓ 创建目标: {goal_id}")
    
    # 添加里程碑
    m1_id = storage.add_milestone(
        goal_id=goal_id,
        title="目录结构设计",
        due_date="2026-02-20"
    )
    m2_id = storage.add_milestone(
        goal_id=goal_id,
        title="核心模块实现",
        due_date="2026-02-25"
    )
    print(f"✓ 添加里程碑: 2个")
    
    # 完成任务
    assert storage.complete_milestone(m1_id)
    print("✓ 完成里程碑")
    
    # 更新进度
    storage.update_goal_progress(goal_id, 50)
    goal = storage.get_goal(goal_id)
    assert goal['progress'] == 50
    print(f"✓ 更新进度: {goal['progress']}%")
    
    # 获取里程碑列表
    milestones = storage.get_milestones(goal_id)
    assert len(milestones) == 2
    completed = [m for m in milestones if m['status'] == 'completed']
    assert len(completed) == 1
    print(f"✓ 里程碑列表: {len(milestones)}个 ({len(completed)}个完成)")
    
    return True


def test_tags(storage):
    """测试标签系统"""
    # 创建标签
    tag_id = storage.create_tag(
        name="python",
        category="programming",
        aliases=["py", "python3"],
        description="Python 相关内容"
    )
    print(f"✓ 创建标签: {tag_id}")
    
    # 获取标签
    tag = storage.get_tag("python")
    assert tag is not None
    print(f"✓ 获取标签: {tag['name']}")
    
    # 分配标签
    memory_id = storage.insert_memory("Python 教程", "knowledge")
    storage.assign_tag(memory_id, "python")
    print(f"✓ 分配标签到记忆")
    
    # 获取记忆的标签
    tags = storage.get_memory_tags(memory_id)
    assert len(tags) == 1
    assert tags[0]['name'] == "python"
    print(f"✓ 记忆标签: {[t['name'] for t in tags]}")
    
    # 获取所有标签
    all_tags = storage.get_all_tags()
    assert len(all_tags) == 1
    print(f"✓ 所有标签: {len(all_tags)}个")
    
    # 移除标签
    assert storage.remove_tag(memory_id, "python")
    tags = storage.get_memory_tags(memory_id)
    assert len(tags) == 0
    print("✓ 移除标签")
    
    return True


def test_checkins(storage):
    """测试签到功能"""
    # 创建目标
    goal_id = storage.insert_goal("周目标", "weekly")
    
    # 签到
    checkin_id = storage.add_checkin(
        goal_id=goal_id,
        date="2026-02-20",
        progress=30,
        notes="完成目录结构设计"
    )
    print(f"✓ 添加签到: {checkin_id}")
    
    # 再次签到
    storage.add_checkin(
        goal_id=goal_id,
        date="2026-02-21",
        progress=60,
        notes="完成核心模块"
    )
    
    # 获取签到记录
    checkins = storage.get_checkins(goal_id=goal_id)
    assert len(checkins) == 2
    print(f"✓ 签到记录: {len(checkins)}条")
    
    # 按日期查询
    checkins = storage.get_checkins(date="2026-02-20")
    assert len(checkins) == 1
    print(f"✓ 按日期查询: {len(checkins)}条")
    
    return True


def test_knowledge(storage):
    """测试知识库"""
    # 插入知识
    kb_id = storage.insert_knowledge(
        title="Python 最佳实践",
        content="1. 使用类型提示\n2. 遵循 PEP 8\n3. 编写文档字符串",
        category="programming/python"
    )
    print(f"✓ 创建知识条目: {kb_id}")
    
    # 获取知识
    kb = storage.get_knowledge(kb_id)
    assert kb is not None
    assert kb['title'] == "Python 最佳实践"
    print(f"✓ 获取知识: {kb['title']}")
    
    # 更新使用次数
    storage.update_knowledge_usage(kb_id)
    kb = storage.get_knowledge(kb_id)
    assert kb['usage_count'] == 1
    print(f"✓ 使用次数: {kb['usage_count']}")
    
    # 搜索
    results = storage.search_knowledge("类型提示")
    assert len(results) >= 1
    print(f"✓ 搜索结果: {len(results)}条")
    
    return True


def test_wal_logs(storage):
    """测试 WAL 日志"""
    # 记录 WAL
    seq = storage.log_wal(
        operation="CREATE",
        table_name="goals",
        record_id="test_goal",
        data={"title": "测试目标"}
    )
    print(f"✓ 记录 WAL: {seq}")
    
    # 获取待应用日志
    logs = storage.get_pending_wal_logs()
    assert len(logs) == 1
    print(f"✓ 待应用日志: {len(logs)}条")
    
    # 标记已应用
    assert storage.mark_wal_applied(seq)
    logs = storage.get_pending_wal_logs()
    assert len(logs) == 0
    print("✓ 标记已应用")
    
    return True


def test_stats(storage):
    """测试统计信息"""
    # 创建测试数据
    for i in range(3):
        storage.insert_memory(f"内容{i}", "conversation")
    storage.insert_goal("目标", "monthly")
    storage.create_tag("测试标签")
    storage.insert_knowledge("知识", "内容")
    
    # 获取统计
    stats = storage.get_stats()
    print(f"✓ 记忆: {stats['memories']}")
    print(f"✓ 目标: {stats['goals']}")
    print(f"✓ 标签: {stats['tags']}")
    print(f"✓ 知识: {stats['knowledge']}")
    
    assert stats['memories'] == 3
    assert stats['goals'] == 1
    
    return True


if __name__ == "__main__":
    print("=" * 50)
    print("SQLite Storage Layer - 测试套件")
    print("=" * 50)
    
    tests = [
        ("CRUD 操作", test_crud),
        ("事务", test_transactions),
        ("目标与里程碑", test_goals_and_milestones),
        ("标签系统", test_tags),
        ("签到功能", test_checkins),
        ("知识库", test_knowledge),
        ("WAL 日志", test_wal_logs),
        ("统计信息", test_stats),
    ]
    
    passed = 0
    failed = 0
    
    for name, func in tests:
        if run_test(name, func):
            passed += 1
        else:
            failed += 1
    
    print("\n" + "=" * 50)
    print(f"测试结果: {passed} 通过, {failed} 失败")
    print("=" * 50)
    
    if failed == 0:
        print("\n🎉 所有测试通过!")
        exit(0)
    else:
        print(f"\n⚠️  {failed} 个测试失败")
        exit(1)
