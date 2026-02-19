#!/usr/bin/env python3
"""
批量修复所有dart文件中的硬编码中文字符串
"""

import os
import re
from pathlib import Path

PROJECT_ROOT = Path("E:/OpenClaw_Workspace/xuelema")

# 完整的中文到ARB键映射
CHINESE_TO_KEY = {
    # 基础UI
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
    '下一步': 'nextQuestion',
    '提交': 'submit',
    '跳过': 'skip',
    '查看': 'viewResults',
    
    # 任务
    '任务': 'tasks',
    '任务列表': 'taskList',
    '任务详情': 'taskDetails',
    '任务标题': 'taskTitle',
    '任务描述': 'taskDescription',
    '添加任务': 'addTask',
    '暂无任务': 'noTasks',
    '开始任务': 'start',
    '完成任务': 'completedTask',
    '未完成任务': 'notCompleted',
    '删除任务': 'delete',
    '编辑任务': 'editProfile',
    '任务状态': 'status',
    '截止时间': 'dueTime',
    
    # 优先级
    '优先级': 'priority',
    '高': 'high',
    '中': 'medium',
    '低': 'low',
    '高优先级': 'highPriority',
    
    # 专注
    '专注': 'focus',
    '专注模式': 'focusMode',
    '开始专注': 'startFocus',
    '专注时间': 'focusTime',
    '专注完成': 'focusCompleted',
    '专注锁定': 'focusLocked',
    '休息': 'rest',
    '开始休息': 'startRest',
    
    # 复习
    '复习': 'review',
    '复习计划': 'review',
    '每日复习': 'dailyReview',
    '每周复习': 'weeklyReview',
    '每月复习': 'monthlyReview',
    '复习提醒': 'dailyReminder',
    '复习统计': 'statistics',
    '今日复习': 'dailyReview',
    
    # 错题
    '错题本': 'mistakeBook',
    '错题': 'mistakes',
    '错题集': 'wrongQuestionBank',
    '错题详情': 'mistakeDetail',
    '暂无错题': 'noQuestions',
    
    # 测验
    '测验': 'quiz',
    '开始测验': 'startQuiz',
    '测验结果': 'quizResults',
    '下一题': 'nextQuestion',
    '正确答案': 'correctAnswer',
    '你的答案': 'wrongAnswer',
    '正确': 'correct',
    '错误': 'wrong',
    '得分': 'score',
    
    # 统计
    '统计': 'statistics',
    '总计时长': 'totalFocusTime',
    '完成率': 'completionRate',
    '连续学习': 'streak',
    '学习天数': 'learningDays',
    '今日任务': 'todayTasks',
    '总计': 'total',
    '已完成': 'completedTask',
    '进度': 'progress',
    
    # 个人中心
    '个人中心': 'profileCenter',
    '我的信息': 'myInfo',
    '用户名': 'username',
    '积分': 'points',
    '成就': 'achievements',
    '学习统计': 'learningStats',
    
    # 设置
    '通用设置': 'generalSettings',
    '通知设置': 'notificationSettings',
    '语言设置': 'languageSettings',
    '深色模式': 'darkMode',
    '关于': 'about',
    '版本': 'version',
    '清除缓存': 'clearCache',
    
    # 其他
    '知识库': 'knowledgeBase',
    '资源': 'resourceLibrary',
    '好友': 'friends',
    '小组': 'groups',
    '导入': 'import',
    '导出': 'export',
    '确认': 'ok',
    '提示': 'tips',
    '成功': 'success',
    '失败': 'failed',
    'loading': 'loading',
    '保存成功': 'save',
    '保存失败': 'save',
    '加载中': 'processing',
    '请稍候': 'loading',
}

def fix_file(file_path):
    """修复单个文件"""
    try:
        content = file_path.read_text(encoding='utf-8')
        original = content
        
        # 修复模式1: const Text('中文')
        for cn, key in CHINESE_TO_KEY.items():
            if f"const Text('{cn}')" in content:
                content = content.replace(f"const Text('{cn}')", f"Text(l10n.{key})")
        
        # 修复模式2: Text('中文') - 非const
        for cn, key in CHINESE_TO_KEY.items():
            if f"Text('{cn}')" in content and f"const Text('{cn}')" not in content:
                content = content.replace(f"Text('{cn}')", f"Text(l10n.{key})")
        
        # 修复模式3: title: '中文'
        for cn, key in CHINESE_TO_KEY.items():
            if f"title: '{cn}'" in content:
                content = content.replace(f"title: '{cn}'", f"title: l10n.{key}")
        
        # 修复模式4: subtitle: '中文'  
        for cn, key in CHINESE_TO_KEY.items():
            if f"subtitle: '{cn}'" in content:
                content = content.replace(f"subtitle: '{cn}'", f"subtitle: l10n.{key}")
        
        # 修复模式5: tooltip: '中文'
        for cn, key in CHINESE_TO_KEY.items():
            if f"tooltip: '{cn}'" in content:
                content = content.replace(f"tooltip: '{cn}'", f"tooltip: l10n.{key}")
        
        # 修复模式6: AppBar title
        for cn, key in CHINESE_TO_KEY.items():
            if f"AppBar(title: const Text('{cn}')" in content:
                content = content.replace(f"AppBar(title: const Text('{cn}')", f"AppBar(title: Text(l10n.{key})")
        
        if content != original:
            file_path.write_text(content, encoding='utf-8')
            return True
    except Exception as e:
        print(f"错误: {file_path} - {e}")
    return False

def main():
    print("开始批量修复...")
    
    screens_dir = PROJECT_ROOT / "lib" / "screens"
    fixed = []
    
    for file_path in screens_dir.glob("*.dart"):
        if fix_file(file_path):
            fixed.append(file_path.name)
    
    print(f"\n修复了 {len(fixed)} 个文件:")
    for f in fixed:
        print(f"  - {f}")
    
    if not fixed:
        print("没有需要修复的文件")
    
    return len(fixed)

if __name__ == "__main__":
    main()
