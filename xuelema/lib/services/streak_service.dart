import 'package:shared_preferences/shared_preferences.dart';

class StreakService {
  static const String _streakKey = 'streak_days';
  static const String _lastActivityDateKey = 'last_activity_date';
  static const String _completedDatesKey = 'completed_dates';

  /// 获取连续学习天数
  Future<int> getStreakDays() async {
    final prefs = await SharedPreferences.getInstance();
    final lastActivityStr = prefs.getString(_lastActivityDateKey);
    final savedStreak = prefs.getInt(_streakKey) ?? 0;
    
    if (lastActivityStr == null) {
      return 0;
    }

    final lastActivity = DateTime.parse(lastActivityStr);
    final today = DateTime.now();
    final todayMidnight = DateTime(today.year, today.month, today.day);
    final lastMidnight = DateTime(lastActivity.year, lastActivity.month, lastActivity.day);
    
    final daysDiff = todayMidnight.difference(lastMidnight).inDays;
    
    // 如果超过1天没有学习，重置连续天数
    if (daysDiff > 1) {
      await prefs.setInt(_streakKey, 0);
      return 0;
    }
    
    return savedStreak;
  }

  /// 记录今日完成学习
  Future<void> recordStudyDay() async {
    final prefs = await SharedPreferences.getInstance();
    final today = DateTime.now();
    final todayStr = '${today.year}-${today.month}-${today.day}';
    
    // 获取已完成的日期列表
    final completedDates = prefs.getStringList(_completedDatesKey) ?? [];
    
    // 如果今天已经记录过，不重复计算
    if (completedDates.contains(todayStr)) {
      return;
    }
    
    // 添加今天到已完成日期
    completedDates.add(todayStr);
    await prefs.setStringList(_completedDatesKey, completedDates);
    
    // 更新最后活动日期和连续天数
    final lastActivityStr = prefs.getString(_lastActivityDateKey);
    int currentStreak = prefs.getInt(_streakKey) ?? 0;
    
    if (lastActivityStr != null) {
      final lastActivity = DateTime.parse(lastActivityStr);
      final lastMidnight = DateTime(lastActivity.year, lastActivity.month, lastActivity.day);
      final todayMidnight = DateTime(today.year, today.month, today.day);
      
      final daysDiff = todayMidnight.difference(lastMidnight).inDays;
      
      if (daysDiff == 1) {
        // 连续第二天
        currentStreak++;
      } else if (daysDiff == 0) {
        // 同一天，不增加
      } else {
        // 中断了，重新开始
        currentStreak = 1;
      }
    } else {
      // 第一次
      currentStreak = 1;
    }
    
    await prefs.setString(_lastActivityDateKey, todayStr);
    await prefs.setInt(_streakKey, currentStreak);
  }

  /// 获取所有已完成日期
  Future<List<String>> getCompletedDates() async {
    final prefs = await SharedPreferences.getInstance();
    return prefs.getStringList(_completedDatesKey) ?? [];
  }

  /// 检查今日是否已完成学习
  Future<bool> isTodayCompleted() async {
    final prefs = await SharedPreferences.getInstance();
    final today = DateTime.now();
    final todayStr = '${today.year}-${today.month}-${today.day}';
    
    final completedDates = prefs.getStringList(_completedDatesKey) ?? [];
    return completedDates.contains(todayStr);
  }

  /// 重置连续天数
  Future<void> resetStreak() async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.setInt(_streakKey, 0);
    await prefs.remove(_lastActivityDateKey);
  }
}
