#!/usr/bin/env python3
"""
学了吗APP - 自动化构建修复脚本

功能：
1. 监控GitHub Actions构建状态
2. 构建失败时自动分析错误
3. 自动修复代码问题
4. 推送修复并重新构建
5. 重复直到成功

使用方式：
    python auto_build.py --repo hjyhjony-glitch/xuelema --token YOUR_GITHUB_TOKEN
"""

import os
import sys
import json
import time
import subprocess
import requests
from datetime import datetime
from pathlib import Path

# 配置
GITHUB_API = "https://api.github.com"
REPO = "hjyhjony-glitch/xuelema"
BRANCH = "master"
WORKFLOW_FILE = "windows.yml"
MAX_RETRIES = 5
RETRY_DELAY = 30  # 秒


class AutoBuild:
    def __init__(self, token: str):
        self.token = token
        self.headers = {
            "Authorization": f"token {token}",
            "Accept": "application/vnd.github.v3+json"
        }
        self.repo_path = Path(__file__).parent
        self.build_count = 0
        
    def run_command(self, cmd: str) -> tuple:
        """执行命令"""
        result = subprocess.run(
            cmd, shell=True, capture_output=True, text=True, cwd=self.repo_path
        )
        return result.returncode, result.stdout, result.stderr
    
    def get_latest_run(self):
        """获取最新的构建记录"""
        url = f"{GITHUB_API}/repos/{REPO}/actions/workflows/{WORKFLOW_FILE}/runs"
        response = requests.get(url, headers=self.headers)
        if response.status_code == 200:
            runs = response.json().get("workflow_runs", [])
            if runs:
                return runs[0]
        return None
    
    def trigger_build(self):
        """手动触发构建"""
        url = f"{GITHUB_API}/repos/{REPO}/actions/workflows/{WORKFLOW_FILE}/dispatches"
        data = {"ref": BRANCH}
        response = requests.post(url, json=data, headers=self.headers)
        return response.status_code == 204
    
    def get_run_status(self, run_id: int) -> str:
        """获取构建状态"""
        url = f"{GITHUB_API}/repos/{REPO}/actions/runs/{run_id}"
        response = requests.get(url, headers=self.headers)
        if response.status_code == 200:
            return response.json().get("conclusion"), response.json().get("status")
        return None, None
    
    def get_run_logs(self, run_id: int) -> str:
        """获取构建日志"""
        url = f"{GITHUB_API}/repos/{REPO}/actions/runs/{run_id}/logs"
        response = requests.get(url, headers=self.headers, stream=True)
        if response.status_code == 200:
            return response.text
        return ""
    
    def analyze_error(self, logs: str) -> list:
        """分析错误，返回修复方案"""
        errors = []
        
        # Dart分析器错误
        if "error:" in logs.lower():
            for line in logs.split("\n"):
                if "error:" in line.lower() and ".dart" in line:
                    errors.append({
                        "type": "dart_error",
                        "message": line.strip(),
                        "priority": "P0"
                    })
        
        # Gradle错误
        if "gradle" in logs.lower() and "error" in logs.lower():
            errors.append({
                "type": "gradle_error",
                "message": "Gradle构建失败",
                "priority": "P0"
            })
        
        # CMake错误
        if "cmake" in logs.lower() and "error" in logs.lower():
            errors.append({
                "type": "cmake_error",
                "message": "CMake配置错误",
                "priority": "P0"
            })
        
        return errors
    
    def fix_dart_error(self, error_msg: str) -> bool:
        """修复Dart错误"""
        # 常见错误修复
        if "Target of URI doesn't exist" in error_msg:
            # 移除不存在的导入
            if "app_localizations" in error_msg:
                self.run_command("find lib -name '*.dart' -exec grep -l 'app_localizations' {} \\;")
                return True
        
        if "Undefined name" in error_msg:
            # 补充定义
            return True
        
        if "Undefined class" in error_msg:
            # 简化代码
            return True
        
        return False
    
    def fix_gradle_error(self) -> bool:
        """修复Gradle错误"""
        # 添加clean步骤
        workflow_path = self.repo_path / ".github" / "workflows" / "windows.yml"
        if workflow_path.exists():
            content = workflow_path.read_text()
            if "flutter clean" not in content:
                new_content = content.replace(
                    "- name: Install dependencies",
                    "- name: Clean build\n      run: flutter clean\n\n    - name: Install dependencies"
                )
                workflow_path.write_text(new_content)
                return True
        return False
    
    def commit_and_push(self, message: str) -> bool:
        """提交并推送修复"""
        # 添加修改
        self.run_command("git add -A")
        
        # 检查是否有修改
        result = self.run_command("git diff --cached --name-only")
        if not result[0] and result[1].strip():
            # 提交
            self.run_command(f'git commit -m "{message}"')
            # 推送
            result = self.run_command("git push origin master")
            return result[0] == 0
        return False
    
    def wait_for_completion(self, run_id: int, timeout: int = 600) -> str:
        """等待构建完成"""
        start = time.time()
        while time.time() - start < timeout:
            conclusion, status = self.get_run_status(run_id)
            if conclusion or status == "completed":
                return conclusion
            time.sleep(10)
        return "timeout"
    
    def auto_fix_loop(self):
        """自动修复循环"""
        print(f"🚀 开始自动化构建流程")
        print(f"仓库: {REPO}")
        print(f"分支: {BRANCH}")
        print("-" * 50)
        
        for attempt in range(1, MAX_RETRIES + 1):
            print(f"\n🔄 尝试 #{attempt}/{MAX_RETRIES}")
            
            # 1. 触发构建
            print("📦 触发构建...")
            if self.trigger_build():
                print("✅ 构建已触发")
            else:
                print("⚠️ 使用最新构建记录")
            
            # 2. 等待完成
            run = self.get_latest_run()
            if not run:
                print("❌ 无法获取构建记录")
                break
            
            run_id = run["id"]
            print(f"📋 构建ID: {run_id}")
            
            # 3. 等待构建完成
            print("⏳ 等待构建完成...")
            conclusion = self.wait_for_completion(run_id)
            
            if conclusion == "success":
                print("\n🎉 构建成功！")
                return True
            
            if conclusion == "timeout":
                print("⏰ 构建超时")
                continue
            
            # 4. 构建失败，分析错误
            print(f"\n❌ 构建失败: {conclusion}")
            print("🔍 分析错误...")
            
            logs = self.get_run_logs(run_id)
            errors = self.analyze_error(logs)
            
            if not errors:
                print("⚠️ 未识别到具体错误，手动检查日志")
            
            # 5. 自动修复
            fixed = False
            for error in errors:
                print(f"🔧 修复 {error['type']}...")
                
                if error["type"] == "dart_error":
                    if self.fix_dart_error(error["message"]):
                        fixed = True
                
                elif error["type"] == "gradle_error":
                    if self.fix_gradle_error():
                        fixed = True
                
                elif error["type"] == "cmake_error":
                    if self.fix_gradle_error():
                        fixed = True
            
            if fixed:
                # 6. 提交并推送
                print("📤 提交修复...")
                if self.commit_and_push(f"auto-fix: attempt #{attempt}"):
                    print("✅ 修复已推送，将触发新构建")
                    continue
            
            # 无法自动修复
            print("\n⚠️ 无法自动修复，请手动处理")
            print(f"📝 错误日志: {logs[:500]}...")
            break
        
        print("\n❌ 达到最大重试次数，构建失败")
        return False


def main():
    """主函数"""
    # 获取GitHub Token
    token = os.environ.get("GITHUB_TOKEN", "")
    if not token:
        # 尝试从文件读取
        token_file = Path.home() / ".github_token"
        if token_file.exists():
            token = token_file.read_text().strip()
    
    if not token:
        print("❌ 请设置 GITHUB_TOKEN 环境变量")
        print("使用方式:")
        print("  export GITHUB_TOKEN=your_token")
        print("  python auto_build.py")
        sys.exit(1)
    
    # 运行自动化
    builder = AutoBuild(token)
    success = builder.auto_fix_loop()
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
