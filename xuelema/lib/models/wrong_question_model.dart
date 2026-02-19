import 'package:uuid/uuid.dart';
import '../l10n/app_localizations.dart';
import '../extensions/l10n_extension.dart';

/// 错题模型
class WrongQuestion {
  final String id;
  final String subject;        // 科目
  final String title;          // 题目
  final List<String> options;  // 选项
  final String answer;         // 答案
  final String explanation;    // 解析
  final int correctCount;      // 正确次数
  final int totalCount;        // 总次数
  final DateTime lastPractice; // 最后练习
  final List<DateTime> practiceHistory; // 练习历史
  final String difficulty;     // 难度
  final DateTime createdAt;   // 创建时间
  final DateTime? nextReview;  // 下次复习时间
  final int consecutiveCorrect; // 连续正确次数
  final String questionType;   // 题目类型（单选、多选、判断等）
  final int? correctAnswerIndex; // 正确答案索引
  final int? userAnswerIndex;    // 用户答案索引

  WrongQuestion({
    String? id,
    required this.subject,
    required this.title,
    this.options = const [],
    required this.answer,
    this.explanation = '',
    this.correctCount = 0,
    this.totalCount = 0,
    DateTime? lastPractice,
    this.practiceHistory = const [],
    this.difficulty = 'medium',
    DateTime? createdAt,
    this.nextReview,
    this.consecutiveCorrect = 0,
    this.questionType = 'single_choice', // 默认单选
    this.correctAnswerIndex,
    this.userAnswerIndex,
  })  : id = id ?? const Uuid().v4(),
        lastPractice = lastPractice ?? DateTime.now(),
        createdAt = createdAt ?? DateTime.now();

  factory WrongQuestion.fromJson(Map<String, dynamic> json) {
    return WrongQuestion(
      id: json['id'] ?? '',
      subject: json['subject'] ?? '',
      title: json['title'] ?? '',
      options: List<String>.from(json['options'] ?? []),
      answer: json['answer'] ?? '',
      explanation: json['explanation'] ?? '',
      correctCount: json['correctCount'] ?? 0,
      totalCount: json['totalCount'] ?? 0,
      lastPractice: json['lastPractice'] != null 
          ? DateTime.parse(json['lastPractice']) 
          : DateTime.now(),
      practiceHistory: json['practiceHistory'] != null
          ? (json['practiceHistory'] as List)
              .map((e) => DateTime.parse(e))
              .toList()
          : [],
      difficulty: json['difficulty'] ?? 'medium',
      createdAt: json['createdAt'] != null 
          ? DateTime.parse(json['createdAt']) 
          : DateTime.now(),
      nextReview: json['nextReview'] != null 
          ? DateTime.parse(json['nextReview']) 
          : null,
      consecutiveCorrect: json['consecutiveCorrect'] ?? 0,
      questionType: json['questionType'] ?? 'single_choice',
      correctAnswerIndex: json['correctAnswerIndex'],
      userAnswerIndex: json['userAnswerIndex'],
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'subject': subject,
      'title': title,
      'options': options,
      'answer': answer,
      'explanation': explanation,
      'correctCount': correctCount,
      'totalCount': totalCount,
      'lastPractice': lastPractice.toIso8601String(),
      'practiceHistory': practiceHistory.map((e) => e.toIso8601String()).toList(),
      'difficulty': difficulty,
      'createdAt': createdAt.toIso8601String(),
      'nextReview': nextReview?.toIso8601String(),
      'consecutiveCorrect': consecutiveCorrect,
      'questionType': questionType,
      'correctAnswerIndex': correctAnswerIndex,
      'userAnswerIndex': userAnswerIndex,
    };
  }

  WrongQuestion copyWith({
    String? id,
    String? subject,
    String? title,
    List<String>? options,
    String? answer,
    String? explanation,
    int? correctCount,
    int? totalCount,
    DateTime? lastPractice,
    List<DateTime>? practiceHistory,
    String? difficulty,
    DateTime? createdAt,
    DateTime? nextReview,
    int? consecutiveCorrect,
    String? questionType,
    int? correctAnswerIndex,
    int? userAnswerIndex,
  }) {
    return WrongQuestion(
      id: id ?? this.id,
      subject: subject ?? this.subject,
      title: title ?? this.title,
      options: options ?? this.options,
      answer: answer ?? this.answer,
      explanation: explanation ?? this.explanation,
      correctCount: correctCount ?? this.correctCount,
      totalCount: totalCount ?? this.totalCount,
      lastPractice: lastPractice ?? this.lastPractice,
      practiceHistory: practiceHistory ?? this.practiceHistory,
      difficulty: difficulty ?? this.difficulty,
      createdAt: createdAt ?? this.createdAt,
      nextReview: nextReview ?? this.nextReview,
      consecutiveCorrect: consecutiveCorrect ?? this.consecutiveCorrect,
      questionType: questionType ?? this.questionType,
      correctAnswerIndex: correctAnswerIndex ?? this.correctAnswerIndex,
      userAnswerIndex: userAnswerIndex ?? this.userAnswerIndex,
    );
  }

  /// 是否需要复习
  bool needsReview() {
    if (nextReview == null) return true;
    return DateTime.now().isAfter(nextReview!);
  }

  /// 是否应该移除（连续正确3次）
  bool shouldRemove() {
    return consecutiveCorrect >= 3;
  }

  /// 掌握率
  double get masteryRate {
    if (totalCount == 0) return 0;
    return correctCount / totalCount;
  }
}

/// 科目模型
class Subject {
  final String id;
  final String name;
  final String icon;
  final int color;
  final int questionCount;

  Subject({
    String? id,
    required this.name,
    this.icon = '📖',
    this.color = 0xFF2196F3,
    this.questionCount = 0,
  }) : id = id ?? name;

  factory Subject.fromJson(Map<String, dynamic> json) {
    return Subject(
      id: json['id'] ?? json['name'] ?? '',
      name: json['name'] ?? '',
      icon: json['icon'] ?? '📖',
      color: json['color'] ?? 0xFF2196F3,
      questionCount: json['questionCount'] ?? 0,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'name': name,
      'icon': icon,
      'color': color,
      'questionCount': questionCount,
    };
  }

  Subject copyWith({
    String? id,
    String? name,
    String? icon,
    int? color,
    int? questionCount,
  }) {
    return Subject(
      id: id ?? this.id,
      name: name ?? this.name,
      icon: icon ?? this.icon,
      color: color ?? this.color,
      questionCount: questionCount ?? this.questionCount,
    );
  }
}

/// 默认科目列表
List<Subject> defaultSubjects = [
  Subject(name: '语文', icon: '📝', color: 0xFFE91E63),
  Subject(name: '数学', icon: '🔢', color: 0xFF2196F3),
  Subject(name: '英语', icon: '🔤', color: 0xFF9C27B0),
  Subject(name: '物理', icon: '⚛️', color: 0xFF00BCD4),
  Subject(name: '化学', icon: '🧪', color: 0xFF4CAF50),
  Subject(name: '生物', icon: '🧬', color: 0xFF8BC34A),
  Subject(name: '历史', icon: '📜', color: 0xFFFF9800),
  Subject(name: '地理', icon: '🌍', color: 0xFF3F51B5),
  Subject(name: '政治', icon: '⚖️', color: 0xFFF44336),
  Subject(name: '其他', icon: '📚', color: 0xFF607D8B),
];

/// 难度等级
class Difficulty {
  static const String easy = 'easy';
  static const String medium = 'medium';
  static const String hard = 'hard';

  static String getLabel(String difficulty) {
    switch (difficulty) {
      case easy:
        return '简单';
      case medium:
        return '中等';
      case hard:
        return '困难';
      default:
        return '中等';
    }
  }
}
