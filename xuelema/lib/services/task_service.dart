/// 任务服务 - 管理学习任务和提醒
import 'dart:convert';
import 'package:shared_preferences/shared_preferences.dart';
import '../models/task_model.dart';
import 'notification_service.dart';

class TaskService {
  static const String _tasksKey = 'user_tasks';
  static TaskService? _instance;
  final NotificationService _notificationService = NotificationService();
  
  TaskService._();
  
  factory TaskService() {
    _instance ??= TaskService._();
    return _instance!;
  }
  
  /// 获取所有任务
  Future<List<Task>> getAllTasks() async {
    final prefs = await SharedPreferences.getInstance();
    final String? data = prefs.getString(_tasksKey);
    
    if (data == null) {
      // 如果没有任务，创建一些示例任务
      return _createSampleTasks();
    }
    
    final List<dynamic> jsonList = jsonDecode(data);
    return jsonList.map((json) => Task.fromJson(json)).toList();
  }
  
  /// 获取今日任务
  Future<List<Task>> getTodayTasks() async {
    final allTasks = await getAllTasks();
    final today = DateTime.now();
    
    return allTasks.where((task) {
      final taskDate = DateTime(
        task.dueTime.year,
        task.dueTime.month,
        task.dueTime.day,
      );
      final todayDate = DateTime(today.year, today.month, today.day);
      return taskDate.isAtSameMomentAs(todayDate);
    }).toList();
  }
  
  /// 添加新任务
  Future<void> addTask(Task task) async {
    final tasks = await getAllTasks();
    tasks.add(task);
    await _saveTasks(tasks);
    
    // 安排任务截止提醒
    await _notificationService.scheduleTaskReminder(
      taskId: task.id.hashCode,
      taskTitle: task.title,
      dueTime: task.dueTime,
    );
    
    print('任务已添加: ${task.title}');
  }
  
  /// 更新任务
  Future<void> updateTask(Task task) async {
    final tasks = await getAllTasks();
    final index = tasks.indexWhere((t) => t.id == task.id);
    
    if (index != -1) {
      tasks[index] = task;
      await _saveTasks(tasks);
      
      // 重新安排提醒
      await _notificationService.cancelNotification(1000 + task.id.hashCode % 1000);
      await _notificationService.scheduleTaskReminder(
        taskId: task.id.hashCode,
        taskTitle: task.title,
        dueTime: task.dueTime,
      );
      
      print('任务已更新: ${task.title}');
    }
  }
  
  /// 删除任务
  Future<void> deleteTask(String taskId) async {
    final tasks = await getAllTasks();
    tasks.removeWhere((task) => task.id == taskId);
    await _saveTasks(tasks);
    
    // 取消相关提醒
    await _notificationService.cancelNotification(1000 + taskId.hashCode % 1000);
    
    print('任务已删除: $taskId');
  }
  
  /// 完成任务
  Future<void> completeTask(String taskId) async {
    final tasks = await getAllTasks();
    final index = tasks.indexWhere((t) => t.id == taskId);
    
    if (index != -1) {
      final task = tasks[index];
      final completedTask = task.copyWith(
        isCompleted: true,
        completedAt: DateTime.now(),
      );
      
      tasks[index] = completedTask;
      await _saveTasks(tasks);
      
      // 取消截止提醒
      await _notificationService.cancelNotification(1000 + taskId.hashCode % 1000);
      
      // 发送完成通知
      await _notificationService.showNotification(
        id: 4000,
        title: '任务完成',
        body: '恭喜完成"${task.title}"！',
        payload: 'task_completed:$taskId',
      );
      
      print('任务已完成: ${task.title}');
    }
  }
  
  /// 获取即将到期的任务
  Future<List<Task>> getUpcomingTasks({int daysAhead = 7}) async {
    final tasks = await getAllTasks();
    final now = DateTime.now();
    final deadline = now.add(Duration(days: daysAhead));
    
    return tasks.where((task) {
      return !task.isCompleted && 
             task.dueTime.isAfter(now) && 
             task.dueTime.isBefore(deadline);
    }).toList();
  }
  
  /// 获取逾期任务
  Future<List<Task>> getOverdueTasks() async {
    final tasks = await getAllTasks();
    return tasks.where((task) => task.isOverdue).toList();
  }
  
  /// 保存任务列表
  Future<void> _saveTasks(List<Task> tasks) async {
    final prefs = await SharedPreferences.getInstance();
    final jsonList = tasks.map((task) => task.toJson()).toList();
    await prefs.setString(_tasksKey, jsonEncode(jsonList));
  }
  
  /// 创建示例任务（用于演示）
  List<Task> _createSampleTasks() {
    final now = DateTime.now();
    
    final tasks = [
      Task(
        title: '数学作业 - 第一章',
        description: '完成练习题1-20',
        dueTime: DateTime(now.year, now.month, now.day, 18, 0),
        priority: 1,
        tags: ['数学', '作业'],
      ),
      Task(
        title: '英语单词背诵',
        description: 'Unit 3 单词表',
        dueTime: DateTime(now.year, now.month, now.day, 20, 0),
        priority: 2,
        tags: ['英语', '背诵'],
      ),
      Task(
        title: '物理实验报告',
        description: '整理实验数据',
        dueTime: DateTime(now.year, now.month, now.day + 1, 12, 0),
        priority: 1,
        tags: ['物理', '实验'],
      ),
      Task(
        title: '语文作文',
        description: '写一篇关于春天的作文',
        dueTime: DateTime(now.year, now.month, now.day + 2, 15, 0),
        priority: 2,
        tags: ['语文', '作文'],
      ),
      Task(
        title: '历史复习',
        description: '复习唐朝历史',
        dueTime: DateTime(now.year, now.month, now.day + 3, 10, 0),
        priority: 3,
        tags: ['历史', '复习'],
      ),
    ];
    
    // 保存示例任务
    _saveTasks(tasks);
    
    return tasks;
  }
  
  /// 清除所有任务
  Future<void> clearAllTasks() async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.remove(_tasksKey);
    
    // 取消所有任务提醒
    for (int i = 1000; i < 2000; i++) {
      await _notificationService.cancelNotification(i);
    }
    
    print('所有任务已清除');
  }
  
  /// 获取任务统计
  Future<Map<String, dynamic>> getTaskStats() async {
    final tasks = await getAllTasks();
    final today = DateTime.now();
    
    int total = tasks.length;
    int completed = tasks.where((t) => t.isCompleted).length;
    int todayCount = tasks.where((t) {
      final taskDate = DateTime(t.dueTime.year, t.dueTime.month, t.dueTime.day);
      final todayDate = DateTime(today.year, today.month, today.day);
      return taskDate.isAtSameMomentAs(todayDate);
    }).length;
    
    int overdue = tasks.where((t) => t.isOverdue).length;
    int highPriority = tasks.where((t) => t.priority == 1 && !t.isCompleted).length;
    
    return {
      'total': total,
      'completed': completed,
      'todayCount': todayCount,
      'overdue': overdue,
      'highPriority': highPriority,
      'completionRate': total > 0 ? (completed / total * 100).round() : 0,
    };
  }
}