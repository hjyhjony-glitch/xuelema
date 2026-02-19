import 'dart:convert';
import 'package:shared_preferences/shared_preferences.dart';
import '../models/quiz_models.dart';

/// 自测服务
class QuizService {
  static QuizService? _instance;
  static const String _quizzesKey = 'quiz_bank';
  static const String _recordsKey = 'quiz_records';
  static const String _settingsKey = 'quiz_settings';

  QuizService._();

  factory QuizService() {
    _instance ??= QuizService._();
    return _instance!;
  }

  /// 初始化并加载默认题库
  Future<void> init() async {
    final prefs = await SharedPreferences.getInstance();
    if (!prefs.containsKey(_quizzesKey)) {
      await prefs.setString(_quizzesKey, jsonEncode(defaultQuizzes.map((e) => e.toJson()).toList()));
    }
    if (!prefs.containsKey(_settingsKey)) {
      await prefs.setString(_settingsKey, jsonEncode(defaultSettings));
    }
  }

  // ========== 题库管理 ==========

  /// 获取所有测验题库
  Future<List<QuizSet>> getAllQuizSets() async {
    final prefs = await SharedPreferences.getInstance();
    final String? data = prefs.getString(_quizzesKey);
    if (data == null) return [];
    
    final List<dynamic> jsonList = jsonDecode(data);
    return jsonList.map((json) => QuizSet.fromJson(json)).toList();
  }

  /// 按科目获取题库
  Future<List<QuizSet>> getQuizSetsBySubject(String subject) async {
    final allSets = await getAllQuizSets();
    return allSets.where((set) => set.subject == subject).toList();
  }

  /// 获取单个题库详情
  Future<QuizSet?> getQuizSet(String setId) async {
    final allSets = await getAllQuizSets();
    try {
      return allSets.firstWhere((set) => set.id == setId);
    } catch (e) {
      return null;
    }
  }

  /// 添加题库
  Future<void> addQuizSet(QuizSet quizSet) async {
    final sets = await getAllQuizSets();
    sets.add(quizSet);
    await _saveQuizSets(sets);
  }

  /// 更新题库
  Future<void> updateQuizSet(QuizSet quizSet) async {
    final sets = await getAllQuizSets();
    final index = sets.indexWhere((s) => s.id == quizSet.id);
    if (index != -1) {
      sets[index] = quizSet;
      await _saveQuizSets(sets);
    }
  }

  /// 删除题库
  Future<void> deleteQuizSet(String setId) async {
    final sets = await getAllQuizSets();
    sets.removeWhere((s) => s.id == setId);
    await _saveQuizSets(sets);
  }

  /// 批量添加题目到题库
  Future<void> addQuestionsToSet(String setId, List<QuizQuestion> questions) async {
    final sets = await getAllQuizSets();
    final index = sets.indexWhere((s) => s.id == setId);
    if (index != -1) {
      final updatedSet = sets[index].copyWith(
        questions: [...sets[index].questions, ...questions],
      );
      sets[index] = updatedSet;
      await _saveQuizSets(sets);
    }
  }

  // ========== 测验记录 ==========

  /// 获取所有测验记录
  Future<List<QuizRecord>> getAllRecords() async {
    final prefs = await SharedPreferences.getInstance();
    final String? data = prefs.getString(_recordsKey);
    if (data == null) return [];
    
    final List<dynamic> jsonList = jsonDecode(data);
    return jsonList.map((json) => QuizRecord.fromJson(json)).toList();
  }

  /// 获取某题库的测验记录
  Future<List<QuizRecord>> getRecordsBySetId(String setId) async {
    final allRecords = await getAllRecords();
    return allRecords.where((r) => r.setId == setId).toList();
  }

  /// 获取最近N条记录
  Future<List<QuizRecord>> getRecentRecords(int limit) async {
    final allRecords = await getAllRecords();
    allRecords.sort((a, b) => b.completedAt.compareTo(a.completedAt));
    return allRecords.take(limit).toList();
  }

  /// 保存测验记录
  Future<void> saveRecord(QuizRecord record) async {
    final records = await getAllRecords();
    records.add(record);
    await _saveRecords(records);
  }

  /// 获取测验统计
  Future<QuizStats> getStatistics() async {
    final records = await getAllRecords();
    final sets = await getAllQuizSets();
    
    if (records.isEmpty) {
      return QuizStats(
        totalQuizzes: 0,
        totalQuestions: 0,
        averageScore: 0,
        totalTimeSpent: 0,
        subjectStats: {},
      );
    }

    final totalQuestions = records.fold(0, (sum, r) => sum + r.totalQuestions);
    final totalScore = records.fold(0.0, (sum, r) => sum + r.score);
    final totalTime = records.fold(0, (sum, r) => sum + r.timeSpentSeconds);
    final averageScore = totalScore / records.length;

    // 按科目统计
    final Map<String, SubjectStats> subjectStats = {};
    for (final record in records) {
      if (!subjectStats.containsKey(record.subject)) {
        subjectStats[record.subject] = SubjectStats(
          subject: record.subject,
          quizCount: 0,
          totalScore: 0,
          totalTime: 0,
        );
      }
      final stats = subjectStats[record.subject]!;
      subjectStats[record.subject] = SubjectStats(
        subject: record.subject,
        quizCount: stats.quizCount + 1,
        totalScore: stats.totalScore + record.score,
        totalTime: stats.totalTime + record.timeSpentSeconds,
      );
    }

    // 计算平均分
    subjectStats.forEach((key, value) {
      subjectStats[key] = SubjectStats(
        subject: value.subject,
        quizCount: value.quizCount,
        totalScore: value.totalScore,
        averageScore: value.totalScore / value.quizCount,
        totalTime: value.totalTime,
      );
    });

    return QuizStats(
      totalQuizzes: records.length,
      totalQuestions: totalQuestions,
      averageScore: averageScore.round(),
      totalTimeSpent: totalTime,
      subjectStats: subjectStats,
    );
  }

  // ========== 测验设置 ==========

  /// 获取测验设置
  Future<QuizSettings> getSettings() async {
    final prefs = await SharedPreferences.getInstance();
    final String? data = prefs.getString(_settingsKey);
    if (data == null) return QuizSettings.defaults();
    
    return QuizSettings.fromJson(jsonDecode(data));
  }

  /// 更新测验设置
  Future<void> updateSettings(QuizSettings settings) async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.setString(_settingsKey, jsonEncode(settings.toJson()));
  }

  // ========== 辅助方法 ==========

  Future<void> _saveQuizSets(List<QuizSet> sets) async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.setString(_quizzesKey, jsonEncode(sets.map((e) => e.toJson()).toList()));
  }

  Future<void> _saveRecords(List<QuizRecord> records) async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.setString(_recordsKey, jsonEncode(records.map((e) => e.toJson()).toList()));
  }
}

/// 默认题库
final defaultQuizzes = [
  QuizSet(
    id: 'quiz_math_001',
    name: '小学数学 - 四则运算',
    subject: '数学',
    description: '测试加减乘除基本运算能力',
    difficulty: Difficulty.easy,
    questionCount: 10,
    estimatedTime: 10,
    questions: [
      QuizQuestion(
        id: 'q1',
        question: '计算: 15 + 27 = ?',
        options: ['32', '42', '52', '62'],
        correctIndex: 1,
        explanation: '15+27=42',
        difficulty: Difficulty.easy,
      ),
      QuizQuestion(
        id: 'q2',
        question: '计算: 8 × 7 = ?',
        options: ['54', '56', '64', '72'],
        correctIndex: 1,
        explanation: '8×7=56',
        difficulty: Difficulty.easy,
      ),
      QuizQuestion(
        id: 'q3',
        question: '计算: 144 ÷ 12 = ?',
        options: ['10', '11', '12', '13'],
        correctIndex: 2,
        explanation: '144÷12=12',
        difficulty: Difficulty.medium,
      ),
      QuizQuestion(
        id: 'q4',
        question: '计算: 25 × 4 = ?',
        options: ['80', '100', '120', '150'],
        correctIndex: 1,
        explanation: '25×4=100',
        difficulty: Difficulty.easy,
      ),
      QuizQuestion(
        id: 'q5',
        question: '计算: 50 - 18 = ?',
        options: ['22', '32', '42', '52'],
        correctIndex: 1,
        explanation: '50-18=32',
        difficulty: Difficulty.easy,
      ),
    ],
  ),
  QuizSet(
    id: 'quiz_chinese_001',
    name: '语文 - 成语填空',
    subject: '语文',
    description: '测试常用成语的理解和运用',
    difficulty: Difficulty.medium,
    questionCount: 5,
    estimatedTime: 8,
    questions: [
      QuizQuestion(
        id: 'c1',
        question: '"___，我们在所不惜" 填入合适的成语',
        options: ['A. 赴汤蹈火', 'B. 走马观花', 'C. 画蛇添足', 'D. 守株待兔'],
        correctIndex: 0,
        explanation: '赴汤蹈火：比喻不避艰险，勇往直前',
        difficulty: Difficulty.medium,
      ),
      QuizQuestion(
        id: 'c2',
        question: '形容做事马虎、粗心的成语是？',
        options: ['A. 专心致志', 'B. 心不在焉', 'C. 一丝不苟', 'D. 粗枝大叶'],
        correctIndex: 3,
        explanation: '粗枝大叶：比喻粗心大意，不细致',
        difficulty: Difficulty.easy,
      ),
    ],
  ),
  QuizSet(
    id: 'quiz_english_001',
    name: '英语 - 基础词汇',
    subject: '英语',
    description: '测试英语基础词汇的掌握',
    difficulty: Difficulty.easy,
    questionCount: 10,
    estimatedTime: 10,
    questions: [
      QuizQuestion(
        id: 'e1',
        question: '"Apple" 的中文意思是？',
        options: ['香蕉', '苹果', '橙子', '葡萄'],
        correctIndex: 1,
        explanation: 'Apple = 苹果',
        difficulty: Difficulty.easy,
      ),
      QuizQuestion(
        id: 'e2',
        question: '"Good morning" 的中文意思是？',
        options: ['晚上好', '下午好', '早上好', '再见'],
        correctIndex: 2,
        explanation: 'Good morning = 早上好',
        difficulty: Difficulty.easy,
      ),
    ],
  ),
];

/// 默认设置
final defaultSettings = {
  'defaultQuestionCount': 10,
  'showAnalysis': true,
  'shuffleQuestions': true,
  'showTimer': true,
  'passingScore': 60,
};
