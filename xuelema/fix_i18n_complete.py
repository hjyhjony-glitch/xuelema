#!/usr/bin/env python3
"""
完整修复学了吗APP的国际化问题和Model导入缺失问题
"""

import os
import re
from pathlib import Path

# 项目根目录
PROJECT_ROOT = Path("E:/OpenClaw_Workspace/xuelema")

# 中文字符串到ARB键的映射（更完整）
CHINESE_MAPPINGS = {
    # 通用字符串
    '刷新': 'refresh',
    '设置': 'settings',
    '添加': 'add',
    '保存': 'save',
    '取消': 'cancel',
    '删除': 'delete',
    '确定': 'ok',
    '开始': 'start',
    '暂停': 'pause',
    '重置': 'reset',
    '返回': 'back',
    '关闭': 'close',
    '完成': 'completed',
    '继续': 'continueTimer',
    '退出': 'exit',
    
    # 任务相关
    '任务': 'tasks',
    '今日任务': 'todayTasksLabel',
    '任务列表': 'taskList',
    '任务详情': 'taskDetails',
    '任务标题': 'taskTitle',
    '任务描述': 'taskDescription',
    '优先级': 'priority',
    '高': 'high',
    '中': 'medium',
    '低': 'low',
    '截止时间': 'dueTime',
    '开始专注': 'startFocus',
    '专注模式': 'focusMode',
    '专注': 'focus',
    '休息': 'rest',
    '开始休息': 'startRest',
    
    # 统计相关
    '连续学习': 'streak',
    '今日任务': 'todayTasks',
    '总计': 'total',
    '已完成': 'completedTask',
    '高优先级': 'highPriority',
    '完成率': 'completionRate',
    '统计': 'statistics',
    '一键完成': 'completeAll',
    '去添加任务': 'goAddTask',
    
    # 复习相关
    '复习': 'review',
    '复习计划': 'review',
    '每日复习': 'dailyReview',
    '开始复习': 'startQuiz',
    '复习提醒': 'dailyReminder',
    
    # 错题相关
    '错题本': 'mistakeBook',
    '错题': 'mistakes',
    '暂无错题': 'noQuestions',
    
    # 其他
    '暂无任务': 'noTasksToday',
    '今日没有任务': 'noTasksToday',
    '休息一下或添加新任务': 'restOrAddTask',
    '添加新任务': 'addNewTask',
    '请输入任务名称': 'enterTaskName',
    '请输入任务描述': 'enterTaskDescription',
    '状态': 'status',
    '未完成': 'notCompleted',
    '完成时间': 'completedTime',
    '提醒设置': 'reminderSettings',
    '查看结果': 'viewResults',
    '目标设置': 'goalSettings',
    '设置提醒': 'notifications',
}

def fix_chinese_strings(content, filename):
    """修复中文字符串"""
    lines = content.split('\n')
    fixed_lines = []
    
    for line in lines:
        # 修复 const Text('中文') 模式
        if "const Text('" in line or 'const Text("' in line:
            for chinese, key in CHINESE_MAPPINGS.items():
                if f"'{chinese}'" in line or f'"{chinese}"' in line:
                    line = line.replace(f"const Text('{chinese}')", f"Text(l10n.{key})")
                    line = line.replace(f'const Text("{chinese}")', f'Text(l10n.{key})')
                    break
        
        # 修复 Text('中文') 模式（没有const）
        if "Text('" in line and "const Text('" not in line:
            for chinese, key in CHINESE_MAPPINGS.items():
                if f"'{chinese}'" in line:
                    line = line.replace(f"Text('{chinese}')", f"Text(l10n.{key})")
                    break
        
        # 修复 tooltip: '中文'
        if "tooltip: '" in line:
            for chinese, key in CHINESE_MAPPINGS.items():
                if f"tooltip: '{chinese}'" in line:
                    line = line.replace(f"tooltip: '{chinese}'", f"tooltip: l10n.{key}")
                    break
        
        # 修复 title: '中文'
        if "title: '" in line:
            for chinese, key in CHINESE_MAPPINGS.items():
                if f"title: '{chinese}'" in line:
                    line = line.replace(f"title: '{chinese}'", f"title: l10n.{key}")
                    break
        
        # 修复 subtitle: '中文'
        if "subtitle: '" in line:
            for chinese, key in CHINESE_MAPPINGS.items():
                if f"subtitle: '{chinese}'" in line:
                    line = line.replace(f"subtitle: '{chinese}'", f"subtitle: l10n.{key}")
                    break
        
        # 修复 appBar title
        if "AppBar(title: const Text('" in line:
            for chinese, key in CHINESE_MAPPINGS.items():
                if f"AppBar(title: const Text('{chinese}')" in line:
                    line = line.replace(f"AppBar(title: const Text('{chinese}')", f"AppBar(title: Text(l10n.{key})")
                    break
        
        fixed_lines.append(line)
    
    return '\n'.join(fixed_lines)

def fix_home_screen():
    """修复home_screen.dart"""
    file_path = PROJECT_ROOT / "lib" / "screens" / "home_screen.dart"
    if not file_path.exists():
        return
    
    content = file_path.read_text(encoding='utf-8')
    
    # 修复统计卡片
    content = content.replace(
        "_buildStatCard('今日任务', '${_todayTasks.length}', Icons.list),",
        "_buildStatCard(l10n.todayTasksLabel, '${_todayTasks.length}', Icons.list),"
    )
    
    content = content.replace(
        "_buildStatCard('连续学习', '$_streakDays天', Icons.star),",
        "_buildStatCard(l10n.streak, '$_streakDays', Icons.star),"
    )
    
    content = content.replace(
        "_buildStatCard('完成率', '${_taskStats['completionRate']}%', Icons.check_circle),",
        "_buildStatCard(l10n.completionRate, '${_taskStats['completionRate']}%', Icons.check_circle),"
    )
    
    content = content.replace(
        "_buildStatCard('总计', '${_taskStats['total']}', Icons.stacked_bar_chart),",
        "_buildStatCard(l10n.total, '${_taskStats['total']}', Icons.stacked_bar_chart),"
    )
    
    content = content.replace(
        "_buildStatCard('已完成', '${_taskStats['completed']}', Icons.done_all),",
        "_buildStatCard(l10n.completedTask, '${_taskStats['completed']}', Icons.done_all),"
    )
    
    content = content.replace(
        "_buildStatCard('高优先级', '${_taskStats['highPriority']}', Icons.priority_high),",
        "_buildStatCard(l10n.highPriority, '${_taskStats['highPriority']}', Icons.priority_high),"
    )
    
    # 修复今日任务标题
    content = content.replace(
        "Text('今日任务 (${_todayTasks.length})',",
        "Text('${l10n.todayTasksLabel} (${_todayTasks.length})',"
    )
    
    # 修复一键完成按钮
    content = content.replace(
        "child: const Text('一键完成'),",
        "child: Text(l10n.completeAll),"
    )
    
    # 修复其他字符串
    content = content.replace(
        "const Text('今日没有任务', style: TextStyle(fontSize: 16)),",
        "Text(l10n.noTasksToday, style: const TextStyle(fontSize: 16)),"
    )
    
    content = content.replace(
        "Text('休息一下或添加新任务', style: TextStyle(fontSize: 14, color: Colors.grey[600])),",
        "Text(l10n.restOrAddTask, style: TextStyle(fontSize: 14, color: Colors.grey[600])),"
    )
    
    content = content.replace(
        "child: const Text('去添加任务'),",
        "child: Text(l10n.goAddTask),"
    )
    
    # 修复完成任务提示
    content = content.replace(
        "SnackBar(content: Text('已完成任务: ${task.title}')),",
        "SnackBar(content: Text('${l10n.taskCompleted}: ${task.title}')),"
    )
    
    file_path.write_text(content, encoding='utf-8')
    print("✓ 已修复 home_screen.dart")

def check_model_imports():
    """检查Model导入"""
    screens_dir = PROJECT_ROOT / "lib" / "screens"
    
    for file_path in screens_dir.glob("*.dart"):
        content = file_path.read_text(encoding='utf-8')
        file_name = file_path.name
        
        # 检查是否需要导入特定Model
        if 'task_model.dart' in content and not "import '../models/task_model.dart';" in content:
            print(f"⚠  {file_name}: 可能需要导入 task_model.dart")
        
        if 'review_model.dart' in content and not "import '../models/review_model.dart';" in content:
            print(f"⚠  {file_name}: 可能需要导入 review_model.dart")
        
        if 'mistake_model.dart' in content and not "import '../models/mistake_model.dart';" in content:
            print(f"⚠  {file_name}: 可能需要导入 mistake_model.dart")

def main():
    print("开始完整修复...")
    
    # 修复home_screen.dart
    fix_home_screen()
    
    # 检查所有屏幕文件
    screens_dir = PROJECT_ROOT / "lib" / "screens"
    fixed_count = 0
    
    for file_path in screens_dir.glob("*.dart"):
        content = file_path.read_text(encoding='utf-8')
        original_content = content
        
        # 修复中文字符串
        content = fix_chinese_strings(content, file_path.name)
        
        if content != original_content:
            file_path.write_text(content, encoding='utf-8')
            print(f"✓ 已修复 {file_path.name}")
            fixed_count += 1
    
    print(f"\n总共修复了 {fixed_count} 个文件")
    
    # 检查Model导入
    print("\n检查Model导入...")
    check_model_imports()
    
    print("\n修复完成!")

if __name__ == "__main__":
    main()