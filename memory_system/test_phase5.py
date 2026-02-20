"""
Phase 5 集成测试
验证 OpenClaw 集成模块是否正常工作
"""
import sys
import os

# 添加项目根目录到路径
_project_root = os.path.dirname(os.path.dirname(__file__))
_memory_system_path = os.path.join(_project_root, 'memory_system')
_memory_path = os.path.join(_project_root, '.memory')

for path in [_project_root, _memory_system_path, _memory_path]:
    if path not in sys.path:
        sys.path.insert(0, path)

from memory_system.openclaw_integration import (
    get_memory_manager,
    memory_search,
    memory_get,
    remember,
    recall,
    init_memory_system
)


def test_memory_manager():
    """测试记忆管理器"""
    print("\n" + "=" * 60)
    print("测试记忆管理器")
    print("=" * 60)
    
    mm = get_memory_manager()
    
    # 测试保存
    print("\n1. 保存测试...")
    test_id = mm.save(
        key="integration_test_001",
        value="这是一个集成测试数据，用于验证 OpenClaw 集成是否正常。",
        memory_type="knowledge",
        tags=["test", "integration", "phase5"]
    )
    print(f"   保存成功，ID: {test_id}")
    
    # 测试加载
    print("\n2. 加载测试...")
    results = mm.load(key="integration_test_001")
    print(f"   加载到 {len(results)} 条记录")
    
    # 测试搜索
    print("\n3. 搜索测试...")
    results = mm.search(query="集成测试")
    print(f"   语义搜索: 找到 {len(results)} 条")
    
    results = mm.exact_search(key="integration_test_001")
    print(f"   精确搜索: 找到 {len(results)} 条")
    
    return True


def test_openclaw_hooks():
    """测试 OpenClaw 钩子函数"""
    print("\n" + "=" * 60)
    print("测试 OpenClaw 钩子函数")
    print("=" * 60)
    
    # 测试 memory_search
    print("\n1. memory_search 测试...")
    results = memory_search(query="集成测试")
    print(f"   找到 {len(results)} 条结果")
    
    # 测试 memory_get
    print("\n2. memory_get 测试...")
    content = memory_get(path="integration_test_001")
    print(f"   内容: {content[:50] if content else 'Empty'}...")
    
    # 测试 remember/recall
    print("\n3. remember/recall 测试...")
    remember("hook_test_001", "钩子函数测试数据", memory_type="knowledge")
    results = recall(query="钩子函数")
    print(f"   找到 {len(results)} 条结果")
    
    return True


def test_stats():
    """测试统计信息"""
    print("\n" + "=" * 60)
    print("测试统计信息")
    print("=" * 60)
    
    mm = get_memory_manager()
    stats = mm.stats()
    
    print(f"\n统计信息:")
    for key, value in stats.items():
        print(f"   {key}: {value}")
    
    return True


def cleanup():
    """清理测试数据"""
    print("\n" + "=" * 60)
    print("清理测试数据")
    print("=" * 60)
    
    mm = get_memory_manager()
    mm.delete(key="integration_test_001")
    mm.delete(key="hook_test_001")
    
    print("   测试数据已清理")


def run_all_tests():
    """运行所有测试"""
    print("\n" + "=" * 60)
    print("Phase 5 集成测试")
    print("=" * 60)
    
    tests = [
        ("记忆管理器", test_memory_manager),
        ("OpenClaw 钩子", test_openclaw_hooks),
        ("统计信息", test_stats),
    ]
    
    results = []
    for name, test_func in tests:
        try:
            test_func()
            results.append((name, "PASS"))
        except Exception as e:
            print(f"\n❌ {name} 失败: {e}")
            import traceback
            traceback.print_exc()
            results.append((name, f"FAIL: {e}"))
    
    # 清理
    cleanup()
    
    print("\n" + "=" * 60)
    print("测试结果汇总")
    print("=" * 60)
    for name, result in results:
        status = "✅" if result == "PASS" else "❌"
        print(f"  {status} {name}: {result}")
    
    return all(r[1] == "PASS" for r in results)


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
