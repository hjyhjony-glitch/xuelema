import 'dart:io';
import 'package:csv/csv.dart';
import 'package:excel/excel.dart';
import 'dart:convert';

/// 导入服务
class ImportService {
  /// 根据文件扩展名选择解析方法
  static Future<List<List<dynamic>>> parseFile(String filePath) async {
    final extension = getExtension(filePath).toLowerCase();
    
    switch (extension) {
      case 'csv':
        return parseCsv(filePath);
      case 'xlsx':
      case 'xls':
        return parseExcel(filePath);
      case 'json':
        return parseJson(filePath);
      default:
        throw Exception('不支持的文件格式: $extension');
    }
  }
  
  /// 获取文件扩展名
  static String getExtension(String filePath) {
    return filePath.split('.').last;
  }
  
  /// 解析CSV文件
  static Future<List<List<dynamic>>> parseCsv(String filePath) async {
    final file = File(filePath);
    final contents = await file.readAsString();
    const csvParser = CsvToListConverter();
    return csvParser.convert(contents);
  }
  
  /// 解析Excel文件
  static Future<List<List<dynamic>>> parseExcel(String filePath) async {
    final bytes = File(filePath).readAsBytesSync();
    final excel = Excel.decodeBytes(bytes);
    final result = <List<dynamic>>[];
    
    for (var table in excel.tables.keys) {
      for (var row in excel.tables[table]!.rows) {
        result.add(row);
      }
    }
    
    return result;
  }
  
  /// 解析JSON文件
  static Future<List<List<dynamic>>> parseJson(String filePath) async {
    final file = File(filePath);
    final contents = await file.readAsString();
    final dynamic data = jsonDecode(contents);
    
    if (data is List) {
      return data.map((item) => (item as Map).values.toList()).toList();
    } else if (data is Map) {
      return [data.values.toList()];
    }
    
    return [];
  }
  
  /// 转换为题目标准格式
  static List<Map<String, dynamic>> convertToQuestions(
    List<List<dynamic>> rows, 
    List<String> headers
  ) {
    final questions = <Map<String, dynamic>>[];
    
    for (var i = 1; i < rows.length; i++) {
      final row = rows[i];
      if (row.isEmpty) continue;
      
      final question = <String, dynamic>{};
      for (var j = 0; j < headers.length && j < row.length; j++) {
        question[headers[j]] = row[j].toString();
      }
      
      questions.add(question);
    }
    
    return questions;
  }
}
