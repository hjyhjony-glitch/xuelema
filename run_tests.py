"""
测试运行器 - Test Runner
========================
运行所有单元测试并生成覆盖率报告

用法:
    python run_tests.py                    # 运行所有测试
    python run_tests.py --verbose          # 详细输出
    python run_tests.py --coverage         # 生成覆盖率报告
    python run_tests.py --module sqlite    # 运行特定模块测试
    python run_tests.py --test test_save  # 运行特定测试
"""

import unittest
import sys
import os
import argparse
import subprocess
from pathlib import Path

# 项目根目录
PROJECT_ROOT = Path(__file__).parent

# 测试目录
TEST_DIRS = [
    PROJECT_ROOT / "modules",
    PROJECT_ROOT / "core",
    PROJECT_ROOT / "memory",
]

# 测试文件模式
TEST_PATTERN = "test_*.py"


def discover_tests(module_path: str = None):
    """发现测试"""
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    if module_path:
        # 运行特定模块
        module_dir = PROJECT_ROOT / module_path
        if module_dir.exists():
            suite.addTests(loader.discover(str(module_dir), pattern=TEST_PATTERN))
    else:
        # 运行所有测试
        for test_dir in TEST_DIRS:
            if test_dir.exists():
                suite.addTests(loader.discover(str(test_dir), pattern=TEST_PATTERN))
    
    return suite


def run_tests(suite: unittest.TestSuite, verbose: bool = False):
    """运行测试"""
    runner = unittest.TextTestRunner(verbosity=2 if verbose else 1)
    result = runner.run(suite)
    return result


def run_with_coverage(module: str = None):
    """使用 pytest 运行覆盖率测试"""
    cmd = [sys.executable, "-m", "pytest"]
    
    # 收集范围
    collect_args = []
    for test_dir in TEST_DIRS:
        if test_dir.exists():
            collect_args.append(str(test_dir))
    
    cmd.extend([
        "--co", "-q"  # 只收集
    ])
    
    subprocess.run(cmd)
    
    # 运行覆盖率
    cmd = [
        sys.executable, "-m", "pytest",
        "-v",
        "--tb=short",
        f"--cov={PROJECT_ROOT}",
        "--cov-report=term-missing",
        "--cov-report=html:coverage_report",
    ]
    
    if module:
        module_path = PROJECT_ROOT / module
        cmd.append(str(module_path))
    else:
        cmd.extend([str(d) for d in TEST_DIRS])
    
    result = subprocess.run(cmd)
    return result.returncode == 0


def run_quick_tests():
    """快速测试（不收集覆盖率）"""
    print("=" * 60)
    print("快速测试模式")
    print("=" * 60)
    
    suite = discover_tests()
    result = run_tests(suite, verbose=True)
    
    # 打印摘要
    print("\n" + "=" * 60)
    print(f"测试结果摘要:")
    print(f"  运行测试: {result.testsRun}")
    print(f"  成功: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"  失败: {len(result.failures)}")
    print(f"  错误: {len(result.errors)}")
    print(f"  跳过: {len(result.skipped)}")
    print("=" * 60)
    
    return result.wasSuccessful()


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="测试运行器")
    parser.add_argument("--verbose", "-v", action="store_true", help="详细输出")
    parser.add_argument("--coverage", "-c", action="store_true", help="运行覆盖率测试")
    parser.add_argument("--module", "-m", type=str, help="运行特定模块测试")
    parser.add_argument("--test", "-t", type=str, help="运行特定测试")
    parser.add_argument("--quick", "-q", action="store_true", help="快速测试模式")
    
    args = parser.parse_args()
    
    if args.quick or not args.coverage:
        # 快速测试
        if args.test:
            # 运行特定测试
            suite = unittest.TestSuite()
            loader = unittest.TestLoader()
            tests = loader.loadTestsFromName(args.test)
            suite.addTests(tests)
        elif args.module:
            suite = discover_tests(args.module)
        else:
            suite = discover_tests()
        
        result = run_tests(suite, verbose=args.verbose or args.quick)
        
        if not args.verbose and not args.quick:
            # 打印摘要
            print("\n" + "=" * 60)
            print(f"测试结果摘要:")
            print(f"  运行测试: {result.testsRun}")
            print(f"  失败: {len(result.failures)}")
            print(f"  错误: {len(result.errors)}")
            print("=" * 60)
        
        return 0 if result.wasSuccessful() else 1
    
    else:
        # 覆盖率测试
        success = run_with_coverage(args.module)
        return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
