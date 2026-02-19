class AppConstants {
  // 默认专注时长（分钟）
  static const int defaultFocusDuration = 25;
  
  // 默认休息时长（分钟）
  static const int defaultRestDuration = 5;
  
  // 番茄钟周期数（长休息阈值）
  static const int pomodoroCycleCount = 4;
  
  // 长休息时长（分钟）
  static const int longRestDuration = 15;
  
  // 本地存储key
  static const String tasksKey = 'tasks';
  static const String userKey = 'user';
  static const String settingsKey = 'settings';
  static const String focusHistoryKey = 'focus_history';
  
  // 任务优先级
  static const int priorityHigh = 1;
  static const int priorityMedium = 2;
  static const int priorityLow = 3;
  
  // 日期格式
  static const String dateFormat = 'yyyy-MM-dd';
  static const String timeFormat = 'HH:mm';
  static const String dateTimeFormat = 'yyyy-MM-dd HH:mm';
}
