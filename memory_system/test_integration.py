"""
记忆系统集成测试
验证 SQLite、向量存储和文件存储是否正常工作
"""
import sys
import os

# 添加项目根目录和 memory_system 目录到路径
_project_root = os.path.dirname(os.path.dirname(__file__))
_memory_system_path = os.path.join(_project_root, 'memory_system')
_memory_path = os.path.join(_project_root, '.memory')

for path in [_project_root, _memory_system_path, _memory_path]:
    if path not in sys.path:
        sys.path.insert(0, path)

from memory_system import (
    get_unified_memory,
    save_to_memory,
    load_from_memory,
    search_memory_v2,
    get_dual_writer,
    get_file_sync,
    WriteMode
)


def test_unified_memory():
    """测试统一记忆 API"""
    print("=" * 60)
    print("测试统一记忆 API")
    print("=" * 60)
    
    um = get_unified_memory()
    
    # 测试保存
    print("\n1. 保存测试...")
    test_id = um.save(
        key="test_conversation_001",
        value="这是一个测试对话内容，用于验证记忆系统集成是否正常。",
        memory_type="conversation",
        tags=["test", "integration"],
        metadata={"source": "test_script"}
    )
    print(f"   保存成功，ID: {test_id}")
    
    # 测试加载
    print("\n2. 加载测试...")
    records = um.load(key="test_conversation_001")
    print(f"   加载到 {len(records)} 条记录")
    if records:
        print(f"   内容: {records[0]['value'][:50]}...")
    
    # 测试搜索（精确）
    print("\n3. 精确搜索测试...")
    results = um.search(key="test_conversation_001")
    print(f"   找到 {len(results)} 条结果")
    
    # 测试搜索（语义）
    print("\n4. 语义搜索测试...")
    results = um.search(query="测试对话", mode="semantic")
    print(f"   找到 {len(results)} 条结果")
    
    # 测试统计
    print("\n5. 统计测试...")
    stats = um.stats()
    print(f"   总记录数: {stats.get('total_memories', 'N/A')}")
    print(f"   文件数: {stats.get('file_count', 'N/A')}")
    
    return True


def test_dual_writer():
    """测试双写引擎"""
    print("\n" + "=" * 60)
    print("测试双写引擎")
    print("=" * 60)
    
    dw = get_dual_writer(WriteMode.SYNC)
    dw.configure_backends(sqlite=True, vector=True, file=True)
    
    print("\n1. 单条写入测试...")
    dw.write(
        operation="save",
        data={
            "key": "dual_write_test_001",
            "value": "双写引擎测试数据",
            "memory_type": "test",
            "tags": ["dual", "write", "test"]
        }
    )
    print("   写入完成")
    
    # 验证数据
    um = get_unified_memory()
    records = um.load(key="dual_write_test_001")
    print(f"   验证: 找到 {len(records)} 条记录")
    
    return True


def test_file_sync():
    """测试文件同步"""
    print("\n" + "=" * 60)
    print("测试文件同步")
    print("=" * 60)
    
    fs = get_file_sync()
    
    print("\n1. 同步所有数据到文件...")
    stats = fs.sync_all()
    print(f"   总记录: {stats['total']}")
    print(f"   对话: {stats['conversations']}")
    print(f"   决策: {stats['decisions']}")
    print(f"   知识: {stats['knowledge']}")
    
    print("\n2. 导出测试...")
    export_path = fs.export_all()
    print(f"   导出路径: {export_path}")
    
    return True


def test_migration_preparation():
    """测试迁移准备"""
    print("\n" + "=" * 60)
    print("测试迁移准备")
    print("=" * 60)
    
    # 检查 MEMORY.md 是否存在
    memory_md = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'MEMORY.md')
    print(f"\n1. 检查 MEMORY.md: {'存在' if os.path.exists(memory_md) else '不存在'}")
    
    # 检查 daily notes 目录
    memory_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'memory')
    print(f"2. 检查 memory/ 目录: {'存在' if os.path.exists(memory_dir) else '不存在'}")
    
    if os.path.exists(memory_dir):
        md_files = [f for f in os.listdir(memory_dir) if f.endswith('.md')]
        print(f"   找到 {len(md_files)} 个 .md 文件")
    
    return True


def cleanup_test_data():
    """清理测试数据"""
    print("\n" + "=" * 60)
    print("清理测试数据")
    print("=" * 60)
    
    um = get_unified_memory()
    
    # 删除测试数据
    um.delete(key="test_conversation_001")
    um.delete(key="dual_write_test_001")
    
    print("   测试数据已清理")


def run_all_tests():
    """运行所有测试"""
    print("\n" + "=" * 60)
    print("记忆系统集成测试套件")
    print("=" * 60)
    
    tests = [
        ("统一记忆 API", test_unified_memory),
        ("双写引擎", test_dual_writer),
        ("文件同步", test_file_sync),
        ("迁移准备", test_migration_preparation),
    ]
    
    results = []
    for name, test_func in tests:
        try:
            test_func()
            results.append((name, "PASS"))
        except Exception as e:
            print(f"\n❌ {name} 失败: {e}")
            results.append((name, f"FAIL: {e}"))
    
    print("\n" + "=" * 60)
    print("测试结果汇总")
    print("=" * 60)
    for name, result in results:
        status = "✅" if result == "PASS" else "❌"
        print(f"  {status} {name}: {result}")
    
    # 清理
    cleanup_test_data()
    
    return all(r[1] == "PASS" for r in results)


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
