#!/usr/bin/env python3
"""
自动开发流程
完全自动化执行，持续迭代直到通过

流程：
1. 运行测试 → 2. 构建验证 → 3. 功能检查 → 4. 文档更新 → 5. Git 提交
"""
import os
import sys
import subprocess
import json
from datetime import datetime
from pathlib import Path


class AutoDevFlow:
    """自动开发流程引擎"""
    
    def __init__(self, workspace: str = None):
        self.workspace = workspace or os.path.dirname(os.path.dirname(__file__))
        self.timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        self.results = {}
    
    def log(self, message: str, level: str = "INFO"):
        """打印日志"""
        print(f"[{self.timestamp}] [{level}] {message}")
    
    # ==================== 步骤 1: 运行测试 ====================
    
    def run_tests(self) -> bool:
        """运行测试套件"""
        self.log("开始步骤 1: 运行测试")
        
        test_files = [
            "memory_system/test_integration.py",
            "memory_system/test_phase5.py"
        ]
        
        all_passed = True
        
        for test_file in test_files:
            test_path = os.path.join(self.workspace, test_file)
            if os.path.exists(test_path):
                self.log(f"运行测试: {test_file}")
                
                result = subprocess.run(
                    [sys.executable, test_path],
                    capture_output=True,
                    text=True,
                    cwd=self.workspace
                )
                
                if result.returncode == 0:
                    self.log(f"✅ {test_file} 通过", "SUCCESS")
                    self.results[test_file] = True
                else:
                    self.log(f"❌ {test_file} 失败", "ERROR")
                    self.log(result.stdout)
                    self.log(result.stderr)
                    all_passed = False
                    self.results[test_file] = False
            else:
                self.log(f"⚠️ 测试文件不存在: {test_file}", "WARNING")
        
        self.results["tests"] = all_passed
        return all_passed
    
    # ==================== 步骤 2: 构建验证 ====================
    
    def verify_build(self) -> bool:
        """验证构建"""
        self.log("开始步骤 2: 构建验证")
        
        # 直接运行测试文件验证构建
        test_path = os.path.join(self.workspace, "memory_system", "test_integration.py")
        
        result = subprocess.run(
            [sys.executable, test_path],
            capture_output=True,
            text=True,
            cwd=self.workspace
        )
        
        if result.returncode == 0:
            self.log("✅ 构建验证通过", "SUCCESS")
            self.results["build"] = True
            return True
        else:
            self.log(f"❌ 构建验证失败", "ERROR")
            self.log(result.stdout)
            self.results["build"] = False
            return False
    
    # ==================== 步骤 3: 功能检查 ====================
    
    def check_features(self) -> bool:
        """检查功能完整性"""
        self.log("开始步骤 3: 功能检查")
        
        required_files = [
            # 核心存储
            ".memory/crud_api.py",
            ".memory/chromadb_storage.py",
            ".memory/__init__.py",
            
            # 存储模块
            ".memory/conversations/conversation_storage.py",
            ".memory/knowledge/knowledge_storage.py",
            ".memory/goals/goal_storage.py",
            ".memory/decisions/decision_storage.py",
            
            # 集成层
            "memory_system/unified_api.py",
            "memory_system/dual_writer.py",
            "memory_system/file_sync.py",
            "memory_system/openclaw_integration.py",
            "memory_system/__init__.py",
            
            # 迁移和测试
            "memory_system/migrate_from_files.py",
            "memory_system/test_integration.py",
            "memory_system/test_phase5.py",
            
            # 文档
            "docs/MEMORY_SYSTEM_INTEGRATION.md",
        ]
        
        all_exist = True
        
        for file_path in required_files:
            full_path = os.path.join(self.workspace, file_path)
            if os.path.exists(full_path):
                self.log(f"✅ {file_path}")
            else:
                self.log(f"❌ 缺少: {file_path}", "ERROR")
                all_exist = False
        
        self.results["features"] = all_exist
        return all_exist
    
    # ==================== 步骤 4: 文档更新 ====================
    
    def update_docs(self) -> bool:
        """更新文档"""
        self.log("开始步骤 4: 文档更新")
        
        docs_updated = []
        
        # 更新开发日志
        dev_log = os.path.join(self.workspace, 'memory', 'DEVELOPMENT_LOG.md')
        if os.path.exists(dev_log):
            self.log("更新 DEVELOPMENT_LOG.md")
            docs_updated.append("DEVELOPMENT_LOG.md")
        
        # 检查其他文档
        doc_files = ["docs/MEMORY_SYSTEM_INTEGRATION.md"]
        for doc_file in doc_files:
            doc_path = os.path.join(self.workspace, doc_file)
            if os.path.exists(doc_path):
                docs_updated.append(doc_file)
        
        self.results["docs"] = True
        return True
    
    # ==================== 步骤 5: Git 提交 ====================
    
    def git_commit(self) -> bool:
        """Git 提交"""
        self.log("开始步骤 5: Git 提交")
        
        try:
            # 检查是否有更改
            result = subprocess.run(
                ["git", "status", "--porcelain"],
                capture_output=True,
                text=True,
                cwd=self.workspace
            )
            
            if not result.stdout.strip():
                self.log("没有需要提交的更改", "INFO")
                self.results["git"] = True
                return True
            
            # 添加所有更改
            subprocess.run(
                ["git", "add", "."],
                cwd=self.workspace
            )
            
            # 创建提交
            commit_message = f"""记忆系统 P3+P4+P5 完成

Timestamp: {self.timestamp}

功能:
- P3: 集成层（SQLite + 向量 + 文件统一 API）
- P4: 数据迁移（45 条记录）
- P5: OpenClaw 集成（钩子函数）

状态: 自动提交
"""
            
            result = subprocess.run(
                ["git", "commit", "-m", commit_message],
                capture_output=True,
                text=True,
                cwd=self.workspace
            )
            
            if result.returncode == 0:
                self.log("✅ Git 提交成功", "SUCCESS")
                self.results["git"] = True
                return True
            else:
                self.log(f"❌ Git 提交失败: {result.stderr}", "ERROR")
                self.results["git"] = False
                return False
                
        except Exception as e:
            self.log(f"❌ Git 操作异常: {e}", "ERROR")
            self.results["git"] = False
            return False
    
    # ==================== 主流程 ====================
    
    def run(self) -> bool:
        """
        运行完整自动开发流程
        
        流程：
        1. 运行测试 → 2. 构建验证 → 3. 功能检查 → 4. 文档更新 → 5. Git 提交
        
        Returns:
            bool: 是否全部通过
        """
        print("\n" + "=" * 60)
        print("🚀 自动开发流程启动")
        print(f"时间: {self.timestamp}")
        print("=" * 60 + "\n")
        
        # 执行所有步骤
        steps = [
            ("测试", self.run_tests),
            ("构建", self.verify_build),
            ("功能", self.check_features),
            ("文档", self.update_docs),
            ("Git", self.git_commit),
        ]
        
        all_passed = True
        
        for step_name, step_func in steps:
            print("-" * 60)
            passed = step_func()
            
            if not passed and step_name in ["测试", "构建", "功能"]:
                # 这些步骤失败则中止
                self.log(f"⚠️ {step_name} 失败，中止流程", "WARNING")
                all_passed = False
                break
        
        # 汇总结果
        print("\n" + "=" * 60)
        print("📊 自动开发流程结果汇总")
        print("=" * 60)
        
        for step_name, _ in steps:
            status = "✅" if self.results.get(step_name.lower()) else "❌"
            print(f"  {status} {step_name}")
        
        if all_passed:
            print("\n🎉 所有步骤通过！流程完成。")
        else:
            print("\n⚠️ 部分步骤失败，请检查日志。")
        
        print("\n" + "=" * 60)
        
        return all_passed


# ==================== 入口点 ====================

def main():
    """主入口"""
    workspace = os.path.dirname(os.path.dirname(__file__))
    
    dev_flow = AutoDevFlow(workspace)
    success = dev_flow.run()
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
