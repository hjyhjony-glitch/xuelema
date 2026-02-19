#!/usr/bin/env python3
"""
GitHub Actions 构建检查脚本
检查最近3次构建结果
"""

import subprocess
import json
from datetime import datetime

def get_recent_workflows():
    """获取最近的工作流运行记录"""
    try:
        result = subprocess.run(
            ["gh", "run", "list", "--limit", "3", "--json", 
             "status,conclusion,name,number,createdAt,duration"],
            capture_output=True,
            text=True,
            cwd=r"E:\OpenClaw_Workspace"
        )
        if result.returncode == 0:
            return json.loads(result.stdout)
        return []
    except Exception as e:
        print(f"获取工作流失败: {e}")
        return []

def format_duration(seconds):
    """格式化时长"""
    if not seconds:
        return "N/A"
    mins = seconds // 60
    secs = seconds % 60
    return f"{mins}m {secs}s"

def main():
    print("=" * 60)
    print("GitHub Actions 构建检查报告")
    print(f"检查时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    workflows = get_recent_workflows()
    
    if not workflows:
        print("⚠️ 无法获取构建记录")
        return
    
    for i, wf in enumerate(workflows, 1):
        status_icon = {
            "completed": "✅",
            "in_progress": "🔄",
            "queued": "⏳",
            "pending": "⏳",
            "action_required": "⚠️"
        }.get(wf.get("status"), "❓")
        
        conclusion_icon = {
            "success": "✅",
            "failure": "❌",
            "cancelled": "🚫",
            "skipped": "⏭️",
            "timed_out": "⏱️",
            "stale": "🔒"
        }.get(wf.get("conclusion"), "❓")
        
        print(f"\n构建 #{wf['number']}: {wf['name']}")
        print(f"  状态: {status_icon} {wf['status']}")
        print(f"  结果: {conclusion_icon} {wf.get('conclusion', 'N/A')}")
        print(f"  时间: {wf['createdAt']}")
        print(f"  时长: {format_duration(wf.get('duration'))}")
    
    print("\n" + "=" * 60)

if __name__ == "__main__":
    main()
