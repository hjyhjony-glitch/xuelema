import 'package:flutter/material.dart';
import 'package:flutter_local_notifications/flutter_local_notifications.dart';
import 'package:timezone/timezone.dart' as tz;
import 'package:timezone/data/latest.dart' as tz;

/// 通知服务 - 处理定时提醒功能
class NotificationService {
  static final NotificationService _instance = NotificationService._();
  factory NotificationService() => _instance;
  
  late FlutterLocalNotificationsPlugin _notificationsPlugin;
  
  NotificationService._() {
    _notificationsPlugin = FlutterLocalNotificationsPlugin();
  }
  
  /// 初始化通知服务
  Future<void> init() async {
    // 初始化时区
    tz.initializeTimeZones();
    
    // Android配置
    const AndroidInitializationSettings androidInitializationSettings =
        AndroidInitializationSettings('app_icon');
    
    // iOS配置
    const DarwinInitializationSettings darwinInitializationSettings =
        DarwinInitializationSettings();
    
    final InitializationSettings initializationSettings =
        InitializationSettings(
          android: androidInitializationSettings,
          iOS: darwinInitializationSettings,
        );
    
    await _notificationsPlugin.initialize(initializationSettings);
    
    // print('通知服务初始化完成');
  }
  
  /// 检查通知权限
  Future<bool> checkPermission() async {
    final result = await _notificationsPlugin
        .resolvePlatformSpecificImplementation<
            AndroidFlutterLocalNotificationsPlugin>()
        ?.requestNotificationsPermission();
    
    return result ?? false;
  }
  
  /// 发送立即通知
  Future<void> showNotification({
    required int id,
    required String title,
    required String body,
    String? payload,
  }) async {
    const AndroidNotificationDetails androidDetails = AndroidNotificationDetails(
      'xuelema_channel',
      '学了吗提醒',
      channelDescription: '学习任务和复习提醒',
      importance: Importance.high,
      priority: Priority.high,
    );
    
    const DarwinNotificationDetails iosDetails = DarwinNotificationDetails();
    
    const NotificationDetails notificationDetails = NotificationDetails(
      android: androidDetails,
      iOS: iosDetails,
    );
    
    await _notificationsPlugin.show(
      id,
      title,
      body,
      notificationDetails,
      payload: payload,
    );
  }
  
  /// 安排定时通知
  Future<void> scheduleNotification({
    required int id,
    required String title,
    required String body,
    required tz.TZDateTime scheduledDate,
    String? payload,
    String? repeatInterval,
  }) async {
    const AndroidNotificationDetails androidDetails = AndroidNotificationDetails(
      'xuelema_schedule_channel',
      '学了吗定时提醒',
      channelDescription: '定时学习任务提醒',
      importance: Importance.high,
import '../l10n/app_localizations.dart';
      priority: Priority.high,
    );
    
    const DarwinNotificationDetails iosDetails = DarwinNotificationDetails();
    
    const NotificationDetails notificationDetails = NotificationDetails(
      android: androidDetails,
      iOS: iosDetails,
    );
    
    await _notificationsPlugin.zonedSchedule(
      id,
      title,
      body,
      scheduledDate,
      notificationDetails,
      androidScheduleMode: AndroidScheduleMode.exactAllowWhileIdle,
      payload: payload,
    );
    
    // print('已安排通知: $title 在 $scheduledDate');
  }
  
  /// 安排每日提醒
  Future<void> scheduleDailyNotification({
    required int id,
    required String title,
    required String body,
    required TimeOfDay time,
    String? payload,
  }) async {
    final now = tz.TZDateTime.now(tz.local);
    final scheduledDate = tz.TZDateTime(
      tz.local,
      now.year,
      now.month,
      now.day,
      time.hour,
      time.minute,
    );
    
    // 如果时间已过今天，安排到明天
    final scheduledTime = scheduledDate.isBefore(now)
        ? scheduledDate.add(const Duration(days: 1))
        : scheduledDate;
    
    await scheduleNotification(
      id: id,
      title: title,
      body: body,
      scheduledDate: scheduledTime,
      payload: payload,
    );
  }
  
  /// 安排任务截止提醒
  Future<void> scheduleTaskReminder({
    required int taskId,
    required String taskTitle,
    required DateTime dueTime,
    int minutesBefore = 30,
  }) async {
    final reminderTime = dueTime.subtract(Duration(minutes: minutesBefore));
    
    // 如果提醒时间已过，不安排
    if (reminderTime.isBefore(DateTime.now())) {
      return;
    }
    
    final tzDateTime = tz.TZDateTime.from(reminderTime, tz.local);
    
    await scheduleNotification(
      id: 1000 + taskId.hashCode % 1000, // 生成唯一ID
      title: '任务即将截止',
      body: '任务 "$taskTitle" 还有$minutesBefore分钟截止',
      scheduledDate: tzDateTime,
      payload: 'task:$taskId',
    );
  }
  
  /// 安排复习提醒
  Future<void> scheduleReviewReminder({
    required String subject,
    required int reviewCount,
    required DateTime reviewTime,
  }) async {
    final tzDateTime = tz.TZDateTime.from(reviewTime, tz.local);
    
    await scheduleNotification(
      id: 2000 + subject.hashCode % 1000,
      title: '复习提醒',
      body: '您有$reviewCount个$subject的题目需要复习',
      scheduledDate: tzDateTime,
      payload: 'review:$subject',
    );
  }
  
  /// 安排专注完成提醒
  Future<void> scheduleFocusCompleteReminder({
    required String taskTitle,
    required Duration focusDuration,
    required DateTime completeTime,
  }) async {
    final tzDateTime = tz.TZDateTime.from(completeTime, tz.local);
    
    final minutes = focusDuration.inMinutes;
    
    await scheduleNotification(
      id: 3000,
      title: '专注完成',
      body: '您已专注"$taskTitle" $minutes分钟，休息一下吧！',
      scheduledDate: tzDateTime,
      payload: 'focus_complete',
    );
  }
  
  /// 取消特定通知
  Future<void> cancelNotification(int id) async {
    await _notificationsPlugin.cancel(id);
  }
  
  /// 取消所有通知
  Future<void> cancelAllNotifications() async {
    await _notificationsPlugin.cancelAll();
  }
  
  /// 获取所有计划的通知
  Future<List<PendingNotificationRequest>> getPendingNotifications() async {
    return await _notificationsPlugin.pendingNotificationRequests();
  }
  
  /// 设置默认每日提醒时间
  Future<void> setupDefaultReminders() async {
    // 设置早上8点的学习提醒
    await scheduleDailyNotification(
      id: 1,
      title: '学习时间到！',
      body: '新的一天，开始今天的学习计划吧！',
      time: const TimeOfDay(hour: 8, minute: 0),
      payload: 'daily_morning',
    );
    
    // 设置晚上8点的复习提醒
    await scheduleDailyNotification(
      id: 2,
      title: '复习时间',
      body: '别忘了复习今天学习的内容',
      time: const TimeOfDay(hour: 20, minute: 0),
      payload: 'daily_evening',
    );
    
    // 设置晚上10点的睡前提醒
    await scheduleDailyNotification(
      id: 3,
      title: '睡前总结',
      body: '总结今天的学习成果，计划明天的学习任务',
      time: const TimeOfDay(hour: 22, minute: 0),
      payload: 'daily_bedtime',
    );
    
    // print('默认提醒设置完成');
  }
}
