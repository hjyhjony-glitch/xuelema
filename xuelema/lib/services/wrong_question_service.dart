import 'dart:convert';
import 'package:shared_preferences/shared_preferences.dart';
import '../models/wrong_question_model.dart';

/// 错题库服务
class WrongQuestionService {
  static WrongQuestionService? _instance;
  static const String _wrongQuestionsKey = 'wrong_questions';
  static const String _subjectsKey = 'subjects';

  // 艾宾浩斯复习间隔（天）
  static const List<int> ebbinghausIntervals = [1, 2, 4, 7, 15, 30];

  WrongQuestionService._();

  factory WrongQuestionService() {
    _instance ??= WrongQuestionService._();
    return _instance!;
  }

  /// 初始化
  Future<void> init() async {
    final prefs = await SharedPreferences.getInstance();
    if (!prefs.containsKey(_subjectsKey)) {
      await prefs.setString(
        _subjectsKey,
        jsonEncode(defaultSubjects.map((e) => e.toJson()).toList()),
      );
    }
  }

  /// 获取所有错题
  Future<List<WrongQuestion>> getAllQuestions() async {
    final prefs = await SharedPreferences.getInstance();
    final String? data = prefs.getString(_wrongQuestionsKey);
    if (data == null) return [];
    
    final List<dynamic> jsonList = jsonDecode(data);
    return jsonList.map((json) => WrongQuestion.fromJson(json)).toList();
  }

  /// 按科目获取错题
  Future<List<WrongQuestion>> getQuestionsBySubject(String subject) async {
    final allQuestions = await getAllQuestions();
    return allQuestions.where((q) => q.subject == subject).toList();
  }

  /// 获取需要复习的错题
  Future<List<WrongQuestion>> getQuestionsForReview() async {
    final allQuestions = await getAllQuestions();
    final now = DateTime.now();
    return allQuestions
        .where((q) => q.nextReview == null || now.isAfter(q.nextReview!))
        .toList()
      ..sort((a, b) => (a.nextReview ?? DateTime.now())
          .compareTo(b.nextReview ?? DateTime.now()));
  }

  /// 添加错题
  Future<void> addQuestion(WrongQuestion question) async {
    final questions = await getAllQuestions();
    questions.add(question);
    await _saveQuestions(questions);
  }

  /// 更新错题
  Future<void> updateQuestion(WrongQuestion question) async {
    final questions = await getAllQuestions();
    final index = questions.indexWhere((q) => q.id == question.id);
    if (index != -1) {
      questions[index] = question;
      await _saveQuestions(questions);
    }
  }

  /// 删除错题
  Future<void> deleteQuestion(String questionId) async {
    final questions = await getAllQuestions();
    questions.removeWhere((q) => q.id == questionId);
    await _saveQuestions(questions);
  }

  /// 练习错题
  Future<Map<String, dynamic>> practiceQuestion(
    String questionId,
    String userAnswer,
  ) async {
    final questions = await getAllQuestions();
    final index = questions.indexWhere((q) => q.id == questionId);
    if (index == -1) {
      return {'isCorrect': false, 'shouldRemove': false};
    }

    final question = questions[index];
    final isCorrect = userAnswer.trim().toLowerCase() == 
                      question.answer.trim().toLowerCase();

    final newHistory = List<DateTime>.from(question.practiceHistory)
      ..add(DateTime.now());
    
    int newConsecutiveCorrect = question.consecutiveCorrect;
    if (isCorrect) {
      newConsecutiveCorrect++;
    } else {
      newConsecutiveCorrect = 0;
    }

    // 计算下次复习时间
    DateTime? nextReview;
    if (!isCorrect) {
      nextReview = DateTime.now().add(const Duration(days: 1));
    } else if (newConsecutiveCorrect >= 3) {
      nextReview = DateTime.now().add(const Duration(days: 30));
    } else {
      final intervalIndex = question.correctCount.clamp(0, ebbinghausIntervals.length - 1);
      nextReview = DateTime.now().add(
        Duration(days: ebbinghausIntervals[intervalIndex]),
      );
    }

    final updatedQuestion = question.copyWith(
      totalCount: question.totalCount + 1,
      correctCount: isCorrect ? question.correctCount + 1 : question.correctCount,
      lastPractice: DateTime.now(),
      practiceHistory: newHistory,
      consecutiveCorrect: newConsecutiveCorrect,
      nextReview: nextReview,
    );

    questions[index] = updatedQuestion;
    await _saveQuestions(questions);

    return {
      'isCorrect': isCorrect, 
      'shouldRemove': updatedQuestion.shouldRemove()
    };
  }

  /// 检查并移除已掌握的错题
  Future<List<String>> checkAndRemoveMastered() async {
    final questions = await getAllQuestions();
    final removedIds = <String>[];

    questions.removeWhere((q) {
      if (q.shouldRemove()) {
        removedIds.add(q.id);
        return true;
      }
      return false;
    });

    if (removedIds.isNotEmpty) {
      await _saveQuestions(questions);
    }

    return removedIds;
  }

  /// 获取统计信息
  Future<Map<String, dynamic>> getStatistics() async {
    final questions = await getAllQuestions();
    final now = DateTime.now();
    final today = DateTime(now.year, now.month, now.day);

    final todayReview = questions.where((q) {
      if (q.nextReview == null) return true;
      final reviewDay = DateTime(
        q.nextReview!.year,
        q.nextReview!.month,
        q.nextReview!.day,
      );
      return !reviewDay.isAfter(today);
    }).length;

    final mastered = questions.where((q) => q.consecutiveCorrect >= 3).length;

    final Map<String, int> subjectCounts = {};
    for (final q in questions) {
      if (q.consecutiveCorrect < 3) {
        subjectCounts[q.subject] = (subjectCounts[q.subject] ?? 0) + 1;
      }
    }

    final totalActive = questions.where((q) => q.consecutiveCorrect < 3).length;

    return {
      'totalQuestions': questions.length,
      'totalActive': totalActive,
      'todayReview': todayReview,
      'mastered': mastered,
      'masteryRate': totalActive > 0 
          ? ((questions.length - totalActive) / questions.length * 100).round() 
          : 100,
      'subjectCounts': subjectCounts,
    };
  }

  /// 获取所有科目
  Future<List<Subject>> getSubjects() async {
    final prefs = await SharedPreferences.getInstance();
    final String? data = prefs.getString(_subjectsKey);
    if (data == null) return defaultSubjects;
    
    final List<dynamic> jsonList = jsonDecode(data);
    final subjects = jsonList.map((json) => Subject.fromJson(json)).toList();
    
    final questions = await getAllQuestions();
    final updatedSubjects = subjects.map((subject) {
      final count = questions
          .where((q) => q.subject == subject.name && q.consecutiveCorrect < 3)
          .length;
      return subject.copyWith(questionCount: count);
    }).toList();
    
    await prefs.setString(
      _subjectsKey,
      jsonEncode(updatedSubjects.map((e) => e.toJson()).toList()),
    );
    
    return updatedSubjects;
  }

  /// 添加新科目
  Future<void> addSubject(Subject subject) async {
    final subjects = await getSubjects();
    if (!subjects.any((s) => s.name == subject.name)) {
      subjects.add(subject);
      final prefs = await SharedPreferences.getInstance();
      await prefs.setString(
        _subjectsKey,
        jsonEncode(subjects.map((e) => e.toJson()).toList()),
      );
    }
  }

  /// 搜索错题
  Future<List<WrongQuestion>> searchQuestions(String query) async {
    final questions = await getAllQuestions();
    final lowerQuery = query.toLowerCase();
    return questions
        .where((q) =>
            q.title.toLowerCase().contains(lowerQuery) ||
            q.subject.toLowerCase().contains(lowerQuery) ||
            q.explanation.toLowerCase().contains(lowerQuery))
        .toList();
  }

  /// 批量添加错题
  Future<void> addQuestions(List<WrongQuestion> questions) async {
    final allQuestions = await getAllQuestions();
    allQuestions.addAll(questions);
    await _saveQuestions(allQuestions);
  }

  /// 清空所有错题
  Future<void> clearAll() async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.remove(_wrongQuestionsKey);
  }
  
  /// 清空所有错题（别名方法）
  Future<void> clearAllQuestions() async {
    await clearAll();
  }

  /// 导出错题数据
  Future<String> exportData() async {
    final questions = await getAllQuestions();
    return jsonEncode(questions.map((e) => e.toJson()).toList());
  }

  /// 导入错题数据
  Future<int> importData(String jsonData) async {
    try {
      final List<dynamic> jsonList = jsonDecode(jsonData);
      final questions = jsonList.map((e) => WrongQuestion.fromJson(e)).toList();
      await addQuestions(questions);
      return questions.length;
    } catch (e) {
      return 0;
    }
  }

  /// 保存错题列表
  Future<void> _saveQuestions(List<WrongQuestion> questions) async {
    final prefs = await SharedPreferences.getInstance();
    final jsonList = questions.map((e) => e.toJson()).toList();
    await prefs.setString(_wrongQuestionsKey, jsonEncode(jsonList));
  }
}
