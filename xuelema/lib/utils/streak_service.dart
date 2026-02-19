/// 连续打卡服务（简化版）
import 'package:shared_preferences/shared_preferences.dart';

class StreakService {
  int _currentStreak = 0;
  int get currentStreak => _currentStreak;
  
  Future<void> init() async {
    final prefs = await SharedPreferences.getInstance();
    _currentStreak = prefs.getInt('streak_days') ?? 0;
  }
  
  Future<void> recordToday() async {}
  
  Future<int> getStreakDays() async {
    final prefs = await SharedPreferences.getInstance();
    return prefs.getInt('streak_days') ?? 0;
  }
}
