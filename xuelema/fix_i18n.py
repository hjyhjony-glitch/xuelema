#!/usr/bin/env python3
"""
修复学了吗APP的国际化问题和Model导入缺失问题
"""

import os
import re
from pathlib import Path

# 项目根目录
PROJECT_ROOT = Path("E:/OpenClaw_Workspace/xuelema")

# ARB文件中定义的键列表（从app_en.arb提取）
ARB_KEYS = {
    "appTitle", "features", "todayTasks", "viewAll", "addTask", "add", "taskList",
    "taskDetail", "taskTitle", "taskTitleHint", "taskDescription", "description",
    "priority", "focusDuration", "minutes", "dueTime", "startFocus", "focusMode",
    "focusTime", "restTime", "focus", "rest", "startRest", "completed", "cancel",
    "save", "delete", "ok", "overdue", "noTasksToday", "all", "today", "thisWeek",
    "completedTask", "searchTasks", "noTasks", "addFirstTask", "subtasks", "totalFocusMinutes",
    "streak", "taskStats", "createdAt", "currentTask", "focusCompleted", "focusCompletedMessage",
    "startRestMessage", "cannotExit", "lockWarning", "confirmExit", "exitWarning", "continueTimer",
    "exit", "focusLocked", "focusUnlocked", "focusLockedMessage", "taskCompleted", "taskOverdue",
    "taskInProgress", "completedAt", "confirmDelete", "deleteTaskConfirm", "knowledgeBase",
    "statistics", "settings", "quiz", "quizTitle", "startQuiz", "nextQuestion", "submit",
    "quizResult", "correct", "wrong", "score", "totalQuestions", "correctAnswers", "noQuestions",
    "mistakeBook", "mistakes", "mistakeCount", "mistakeDetail", "wrongAnswer", "correctAnswer",
    "analysis", "addToMistakes", "removeFromMistakes", "plan", "goals", "goalSetting",
    "shortTermGoal", "longTermGoal", "createGoal", "goalTitle", "goalDescription", "targetDate",
    "progress", "review", "dailyReview", "weeklyReview", "monthlyReview", "createReview",
    "reviewSummary", "whatWentWell", "needsImprovement", "tomorrowPlan", "profile", "myInfo",
    "points", "achievements", "learningStats", "totalFocusTime", "totalTasks", "learningDays",
    "editProfile", "notifications", "darkMode", "language", "about", "logout", "pointsValue",
    "hours", "days", "resourceLibrary", "resources", "resourceCategories", "download",
    "downloadResource", "uploadResource", "upload", "myUploads", "favorites", "addToFavorites",
    "removeFromFavorites", "resourceSize", "resourceType", "free", "paid", "pointsRequired",
    "friends", "addFriend", "searchFriend", "friendRequests", "accept", "reject", "pending",
    "confirmRemoveFriend", "removeFriendConfirm", "studyGroup", "groups", "createGroup",
    "joinGroup", "groupMembers", "groupName", "groupDescription", "groupOwner", "memberCount",
    "leaveGroup", "joinGroupConfirm", "parentMode", "childProgress", "viewChildTasks",
    "viewChildStats", "dailyStudyTime", "weeklyReport", "monthlyReport", "studySummary",
    "setLimits", "dailyLimit", "appRestrictions", "childAccount", "bindChild", "unbindChild",
    "confirmUnbind", "unbindConfirm", "learningStatistics", "focusTimeStats", "taskCompletionStats",
    "studyTrend", "thisMonth", "allTime", "averageDaily", "averageFocusTime", "longestStreak",
    "completionRate", "dailyStudyChart", "taskDistribution", "learningReport", "shareReport",
    "theme", "themeLight", "themeDark", "themeSystem", "languageSetting", "notificationsSetting",
    "focusReminders", "taskReminders", "dailyReminder", "clearCache", "cacheSize", "version",
    "privacyPolicy", "termsOfService", "feedback", "rateApp", "aboutUs", "noResources",
    "noFriends", "noGroups", "ocrTitle", "captureOcr", "galleryOcr", "noResult", "processing",
    "importTitle", "selectFile", "importPreview", "importSuccess", "importError", "pdfImport",
    "selectPdf", "pdfPreview", "changeFile", "extracting", "extractionResult", "pdfType",
    "pdfTypeText", "pdfTypeScanned", "pdfTypeMixed", "questionsFound", "rawTextLength",
    "confidence", "questionsPreview", "retry", "wrongQuestionBank", "planning", "import",
    "home", "tasks", "profile", "todayTasksLabel", "streakDaysLabel", "practice",
    "noQuestionsMessage", "noTasksMessage", "profileCenter", "username", "normalUser",
    "generalSettings", "notificationManagement", "privacySecurity", "quizResults", "general",
    "notificationSettings", "languageSettings", "aboutSection", "versionInfo", "helpCenter",
    "focusModeTitle", "pause", "start", "reset", "selectFileButton", "ocrRecognition",
    "chooseImageOrText", "takePhoto", "chooseImage", "paste", "pdfImportDisabled",
    "pdfImportDisabledMessage", "waitingForSDKUpgrade", "back", "taskDetails", "dueTimeLabel",
    "priorityLabel", "startFocusButton", "backButton", "continuesLearning", "total",
    "highPriority", "completeAll", "goAddTask", "restOrAddTask", "addNewTask", "enterTaskName",
    "enterTaskDescription", "high", "medium", "low", "close", "priorityText", "status",
    "notCompleted", "completedTime", "reminderSettings", "wrongQuestionBook", "viewResults",
    "goalSettings"
}

# 中文到英文键的映射（从ARB文件中提取）
CHINESE_TO_KEY = {
    "学了吗": "appTitle",
    "功能": "features",
    "今日学习任务": "todayTasks",
    "查看全部": "viewAll",
    "添加任务": "addTask",
    "添加": "add",
    "任务列表": "taskList",
    "任务详情": "taskDetail",
    "任务标题": "taskTitle",
    "请输入任务标题": "taskTitleHint",
    "任务描述": "taskDescription",
    "描述": "description",
    "优先级": "priority",
    "专注时长": "focusDuration",
    "分钟": "minutes",
    "截止时间": "dueTime",
    "开始专注": "startFocus",
    "专注模式": "focusMode",
    "专注时间": "focusTime",
    "休息时间": "restTime",
    "专注": "focus",
    "休息": "rest",
    "开始休息": "startRest",
    "已完成": "completed",
    "取消": "cancel",
    "保存": "save",
    "删除": "delete",
    "确定": "ok",
    "已过期": "overdue",
    "今日没有任务": "noTasksToday",
    "全部": "all",
    "今日": "today",
    "本周": "thisWeek",
    "已完成": "completedTask",
    "搜索任务": "searchTasks",
    "暂无任务": "noTasks",
    "点击下方按钮添加第一个任务": "addFirstTask",
    "子任务": "subtasks",
    "总计专注分钟": "totalFocusMinutes",
    "连续学习": "streak",
    "任务统计": "taskStats",
    "创建时间": "createdAt",
    "当前任务": "currentTask",
    "专注完成": "focusCompleted",
    "已专注完成": "focusCompletedMessage",
    "该休息了": "startRestMessage",
    "无法退出": "cannotExit",
    "专注锁定": "lockWarning",
    "确认退出": "confirmExit",
    "定时器仍在运行": "exitWarning",
    "继续定时器": "continueTimer",
    "退出": "exit",
    "专注已锁定": "focusLocked",
    "专注已解锁": "focusUnlocked",
    "专注已锁定，请完成任务": "focusLockedMessage",
    "任务完成": "taskCompleted",
    "任务过期": "taskOverdue",
    "任务进行中": "taskInProgress",
    "完成时间": "completedAt",
    "确认删除": "confirmDelete",
    "确定要删除此任务吗": "deleteTaskConfirm",
    "知识库": "knowledgeBase",
    "统计": "statistics",
    "设置": "settings",
    "测验": "quiz",
    "知识测验": "quizTitle",
    "开始测验": "startQuiz",
    "下一题": "nextQuestion",
    "提交": "submit",
    "测验结果": "quizResult",
    "正确": "correct",
    "错误": "wrong",
    "得分": "score",
    "题目": "totalQuestions",
    "正确回答": "correctAnswers",
    "暂无题目": "noQuestions",
    "错题本": "mistakeBook",
    "错题": "mistakes",
    "错题数量": "mistakeCount",
    "错题详情": "mistakeDetail",
    "你的回答": "wrongAnswer",
    "正确答案": "correctAnswer",
    "分析": "analysis",
    "加入错题本": "addToMistakes",
    "从错题本移除": "removeFromMistakes",
    "计划": "plan",
    "目标": "goals",
    "目标设置": "goalSetting",
    "短期目标": "shortTermGoal",
    "长期目标": "longTermGoal",
    "创建目标": "createGoal",
    "目标标题": "goalTitle",
    "目标描述": "goalDescription",
    "目标日期": "targetDate",
    "进度": "progress",
    "复习": "review",
    "每日复习": "dailyReview",
    "每周复习": "weeklyReview",
    "每月复习": "monthlyReview",
    "创建复习": "createReview",
    "复习总结": "reviewSummary",
    "做得好的": "whatWentWell",
    "需要改进": "needsImprovement",
    "明日计划": "tomorrowPlan",
    "个人中心": "profile",
    "我的信息": "myInfo",
    "积分": "points",
    "成就": "achievements",
    "学习统计": "learningStats",
    "总计专注时间": "totalFocusTime",
    "完成任务数": "totalTasks",
    "学习天数": "learningDays",
    "编辑资料": "editProfile",
    "通知": "notifications",
    "深色模式": "darkMode",
    "语言": "language",
    "关于": "about",
    "退出登录": "logout",
    "积分": "pointsValue",
    "小时": "hours",
    "天": "days",
    "资源库": "resourceLibrary",
    "学习资源": "resources",
    "分类": "resourceCategories",
    "下载": "download",
    "下载资源": "downloadResource",
    "上传资源": "uploadResource",
    "上传": "upload",
    "我的上传": "myUploads",
    "收藏": "favorites",
    "加入收藏": "addToFavorites",
    "从收藏移除": "removeFromFavorites",
    "大小": "resourceSize",
    "类型": "resourceType",
    "免费": "free",
    "付费": "paid",
    "所需积分": "pointsRequired",
    "好友": "friends",
    "添加好友": "addFriend",
    "搜索好友": "searchFriend",
    "好友请求": "friendRequests",
    "接受": "accept",
    "拒绝": "reject",
    "待处理": "pending",
    "确认移除好友": "confirmRemoveFriend",
    "确定要移除此好友吗": "removeFriendConfirm",
    "学习小组": "studyGroup",
    "我的小组": "groups",
    "创建小组": "createGroup",
    "加入小组": "joinGroup",
    "成员": "groupMembers",
    "小组名称": "groupName",
    "小组描述": "groupDescription",
    "组长": "groupOwner",
    "成员数": "memberCount",
    "离开小组": "leaveGroup",
    "确认加入小组": "joinGroupConfirm",
    "家长模式": "parentMode",
    "孩子进度": "childProgress",
    "查看孩子任务": "viewChildTasks",
    "查看统计": "viewChildStats",
    "今日学习时间": "dailyStudyTime",
    "周报": "weeklyReport",
    "月报": "monthlyReport",
    "学习总结": "studySummary",
    "设置限制": "setLimits",
    "每日学习限制": "dailyLimit",
    "应用限制": "appRestrictions",
    "孩子账户": "childAccount",
    "绑定孩子账户": "bindChild",
    "解绑": "unbindChild",
    "确认解绑": "confirmUnbind",
    "确定要解绑孩子账户吗": "unbindConfirm",
    "学习统计": "learningStatistics",
    "专注时间统计": "focusTimeStats",
    "任务完成统计": "taskCompletionStats",
    "学习趋势": "studyTrend",
    "本月": "thisMonth",
    "全部时间": "allTime",
    "日均": "averageDaily",
    "平均专注时间": "averageFocusTime",
    "最长连学": "longestStreak",
    "完成率": "completionRate",
    "每日学习图表": "dailyStudyChart",
    "任务分布": "taskDistribution",
    "学习报告": "learningReport",
    "分享报告": "shareReport",
    "主题": "theme",
    "浅色": "themeLight",
    "深色": "themeDark",
    "跟随系统": "themeSystem",
    "语言设置": "languageSetting",
    "通知设置": "notificationsSetting",
    "专注提醒": "focusReminders",
    "任务提醒": "taskReminders",
    "每日学习提醒": "dailyReminder",
    "清除缓存": "clearCache",
    "缓存大小": "cacheSize",
    "版本": "version",
    "隐私政策": "privacyPolicy",
    "服务条款": "termsOfService",
    "反馈": "feedback",
    "评价应用": "rateApp",
    "关于我们": "aboutUs",
    "暂无资源": "noResources",
    "暂无好友": "noFriends",
    "暂无小组": "noGroups",
    "文字识别": "ocrTitle",
    "拍照": "captureOcr",
    "相册": "galleryOcr",
    "无识别结果": "noResult",
    "处理中": "processing",
    "批量导入": "importTitle",
    "选择文件": "selectFile",
    "导入预览": "importPreview",
    "导入成功": "importSuccess",
    "导入失败": "importError",
    "PDF导入": "pdfImport",
    "选择PDF文件": "selectPdf",
    "PDF预览": "pdfPreview",
    "更换文件": "changeFile",
    "提取中": "extracting",
    "提取结果": "extractionResult",
    "PDF类型": "pdfType",
    "文本PDF": "pdfTypeText",
    "扫描PDF": "pdfTypeScanned",
    "混合PDF": "pdfTypeMixed",
    "找到的题目": "questionsFound",
    "原始文本长度": "rawTextLength",
    "识别置信度": "confidence",
    "题目预览": "questionsPreview",
    "重试": "retry",
    "错题集": "wrongQuestionBank",
    "规划": "planning",
    "首页": "home",
    "今日任务": "todayTasksLabel",
    "连学天数": "streakDaysLabel",
    "练习": "practice",
    "暂无题目": "noQuestionsMessage",
    "暂无任务": "noTasksMessage",
    "个人中心": "profileCenter",
    "用户名": "username",
    "普通用户": "normalUser",
    "通用设置": "generalSettings",
    "通知管理": "notificationManagement",
    "隐私安全": "privacySecurity",
    "测验结果": "quizResults",
    "通用": "general",
    "深色模式": "notificationSettings",
    "语言设置": "languageSettings",
    "关于": "aboutSection",
    "版本信息": "versionInfo",
    "帮助中心": "helpCenter",
    "专注模式": "focusModeTitle",
    "暂停": "pause",
    "开始": "start",
    "重置": "reset",
    "导入": "importTitle",
    "选择文件": "selectFileButton",
    "OCR识别": "ocrRecognition",
    "选择图片或输入文字": "chooseImageOrText",
    "拍照": "takePhoto",
    "选择图片": "chooseImage",
    "粘贴": "paste",
    "PDF导入（暂不可用）": "pdfImportDisabled",
    "PDF导入暂时不可用": "pdfImportDisabledMessage",
    "等待Flutter SDK 3.7.2+": "waitingForSDKUpgrade",
    "返回": "back",
    "任务详情": "taskDetails",
    "截止时间:": "dueTimeLabel",
    "优先级:": "priorityLabel",
    "开始专注": "startFocusButton",
    "返回": "backButton",
    "连学": "continuesLearning",
    "总计": "total",
    "高优先级": "highPriority",
    "一键完成": "completeAll",
    "去添加任务": "goAddTask",
    "刷新": "refresh",
    "今日没有任务": "noTasksToday",
    "休息一下或添加新任务": "restOrAddTask",
    "添加新任务": "addNewTask",
    "任务标题": "taskTitle",
    "请输入任务名称": "enterTaskName",
    "任务描述": "taskDescription",
    "请输入任务描述": "enterTaskDescription",
    "优先级": "priority",
    "高": "high",
    "中": "medium",
    "低": "low",
    "取消": "cancel",
    "添加": "add",
    "关闭": "close",
    "完成任务": "completedTask",
    "优先级": "priorityText",
    "截止时间": "dueTime",
    "状态": "status",
    "未完成": "notCompleted",
    "完成时间": "completedTime",
    "提醒设置": "reminderSettings",
    "错题本": "wrongQuestionBook",
    "查看结果": "viewResults",
    "目标设置": "goalSettings"
}

# 需要导入的Model映射
MODEL_IMPORTS = {
    "task_list_screen.dart": "import '../models/task_model.dart';",
    "review_screen.dart": "import '../models/review_model.dart';", 
    "mistake_screen.dart": "import '../models/mistake_model.dart';",
}

def fix_model_imports(file_path):
    """修复Model导入缺失问题"""
    content = file_path.read_text(encoding='utf-8')
    file_name = file_path.name
    
    # 检查是否已经导入了Model
    if file_name in MODEL_IMPORTS:
        import_line = MODEL_IMPORTS[file_name]
        # 如果还没有导入，则添加导入
        if import_line not in content:
            # 找到所有import语句的最后一行
            lines = content.split('\n')
            import_end_index = 0
            for i, line in enumerate(lines):
                if line.strip() and not line.strip().startswith('import'):
                    import_end_index = i
                    break
            
            # 在import部分后面插入Model导入
            lines.insert(import_end_index, import_line)
            content = '\n'.join(lines)
            file_path.write_text(content, encoding='utf-8')
            print(f"✓ 已修复 {file_name} 的Model导入")
            return True
    return False

def fix_i18n_strings(file_path):
    """修复国际化字符串问题"""
    content = file_path.read_text(encoding='utf-8')
    original_content = content
    
    # 1. 修复 const Text('中文') 模式
    pattern = r"const\s+Text\(\s*'([^']+)'\s*\)"
    
    def replace_text(match):
        chinese_text = match.group(1)
        if chinese_text in CHINESE_TO_KEY:
            key = CHINESE_TO_KEY[chinese_text]
            return f"Text(l10n.$key)"
        return match.group(0)
    
    content = re.sub(pattern, replace_text, content)
    
    # 2. 修复 Text('中文') 模式（没有const）
    pattern2 = r"(?<!const\s)Text\(\s*'([^']+)'\s*\)"
    content = re.sub(pattern2, replace_text, content)
    
    # 3. 修复 tooltip: '中文'
    pattern3 = r"tooltip:\s*'([^']+)'"
    
    def replace_tooltip(match):
        chinese_text = match.group(1)
        if chinese_text in CHINESE_TO_KEY:
            key = CHINESE_TO_KEY[chinese_text]
            return f"tooltip: l10n.{key}"
        return match.group(0)
    
    content = re.sub(pattern3, replace_tooltip, content)
    
    # 4. 修复 title: '中文'
    pattern4 = r"title:\s*'([^']+)'"
    
    def replace_title(match):
        chinese_text = match.group(1)
        if chinese_text in CHINESE_TO_KEY:
            key = CHINESE_TO_KEY[chinese_text]
            return f"title: l10n.{key}"
        return match.group(0)
    
    content = re.sub(pattern4, replace_title, content)
    
    if content != original_content:
        file_path.write_text(content, encoding='utf-8')
        print(f"✓ 已修复 {file_path.name} 的国际化字符串")
        return True
    return False

def main():
    """主函数"""
    print("开始修复学了吗APP的问题...")
    
    # 扫描screens目录
    screens_dir = PROJECT_ROOT / "lib" / "screens"
    if not screens_dir.exists():
        print(f"错误: 找不到screens目录: {screens_dir}")
        return
    
    fixed_files = []
    
    for file_path in screens_dir.glob("*.dart"):
        print(f"\n检查文件: {file_path.name}")
        
        fixed = False
        
        # 修复Model导入
        fixed |= fix_model_imports(file_path)
        
        # 修复国际化字符串
        fixed |= fix_i18n_strings(file_path)
        
        if fixed:
            fixed_files.append(file_path.name)
    
    print("\n" + "="*50)
    print("修复完成!")
    print(f"总共修复了 {len(fixed_files)} 个文件:")
    for file_name in fixed_files:
        print(f"  - {file_name}")
    
    # 检查是否还需要手动修复的文件
    print("\n需要手动检查的文件:")
    
    # 检查task_list_screen.dart
    task_list_file = screens_dir / "task_list_screen.dart"
    if task_list_file.exists():
        content = task_list_file.read_text(encoding='utf-8')
        if "'中文'" in content or '"中文"' in content:
            print(f"  - task_list_screen.dart: 可能需要额外修复")
    
    print("\n修复完成，可以提交代码并触发GitHub Actions构建。")

if __name__ == "__main__":
    main()