/// 本地存储服务
import 'package:shared_preferences/shared_preferences.dart';
import '../l10n/app_localizations.dart';
import '../extensions/l10n_extension.dart';

class StorageService {
  static const String _storageKey = 'app_data';

  /// 读取字符串
  Future<String?> read(String key) async {
    final prefs = await SharedPreferences.getInstance();
    return prefs.getString(key);
  }

  /// 读取字符串列表
  Future<List<String>> readList(String key) async {
    final prefs = await SharedPreferences.getInstance();
    return prefs.getStringList(key) ?? [];
  }

  /// 读取整数
  Future<int?> readInt(String key) async {
    final prefs = await SharedPreferences.getInstance();
    return prefs.getInt(key);
  }

  /// 读取布尔值
  Future<bool?> readBool(String key) async {
    final prefs = await SharedPreferences.getInstance();
    return prefs.getBool(key);
  }

  /// 写入字符串
  Future<bool> write(String key, String value) async {
    final prefs = await SharedPreferences.getInstance();
    return prefs.setString(key, value);
  }

  /// 写入字符串列表
  Future<bool> writeList(String key, List<String> value) async {
    final prefs = await SharedPreferences.getInstance();
    return prefs.setStringList(key, value);
  }

  /// 写入整数
  Future<bool> writeInt(String key, int value) async {
    final prefs = await SharedPreferences.getInstance();
    return prefs.setInt(key, value);
  }

  /// 写入布尔值
  Future<bool> writeBool(String key, bool value) async {
    final prefs = await SharedPreferences.getInstance();
    return prefs.setBool(key, value);
  }

  /// 删除
  Future<bool> delete(String key) async {
    final prefs = await SharedPreferences.getInstance();
    return prefs.remove(key);
  }

  /// 清空所有
  Future<void> clear() async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.clear();
  }

  /// 批量读取
  Future<Map<String, dynamic>> readMultiple(List<String> keys) async {
    final prefs = await SharedPreferences.getInstance();
    final result = <String, dynamic>{};
    
    for (final key in keys) {
      if (prefs.containsKey(key)) {
        final value = prefs.get(key);
        result[key] = value;
      }
    }
    
    return result;
  }
}
