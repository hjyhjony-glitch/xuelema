import 'dart:convert';
import 'package:uuid/uuid.dart';

/// 难度等级
enum Difficulty { easy, medium, hard }

/// 题目类型
enum QuestionType { single, multiple, trueFalse, fillBlank }

/// 测验题库
class QuizSet {
  final String id;
  final String name;
  final String subject;
  final String description;
  final Difficulty difficulty;
  final int questionCount;
  final int estimatedTime; // 分钟
  final List<QuizQuestion> questions;

  QuizSet({
    String? id,
    required this.name,
    required this.subject,
    required this.description,
    required this.difficulty,
    required this.questionCount,
    required this.estimatedTime,
    required this.questions,
  }) : id = id ?? const Uuid().v4();

  factory QuizSet.fromJson(Map<String, dynamic> json) {
    return QuizSet(
      id: json['id'] ?? '',
      name: json['name'] ?? '',
      subject: json['subject'] ?? '',
      description: json['description'] ?? '',
      difficulty: Difficulty.values.firstWhere(
        (e) => e.toString() == 'Difficulty.${json['difficulty']}',
        orElse: () => Difficulty.medium,
      ),
      questionCount: json['questionCount'] ?? 0,
      estimatedTime: json['estimatedTime'] ?? 0,
      questions: (json['questions'] as List<dynamic>?)
              ?.map((e) => QuizQuestion.fromJson(e))
              .toList() ??
          [],
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'name': name,
      'subject': subject,
      'description': description,
      'difficulty': difficulty.toString().split('.').last,
      'questionCount': questionCount,
      'estimatedTime': estimatedTime,
      'questions': questions.map((e) => e.toJson()).toList(),
    };
  }

  QuizSet copyWith({
    String? id,
    String? name,
    String? subject,
    String? description,
    Difficulty? difficulty,
    int? questionCount,
    int? estimatedTime,
    List<QuizQuestion>? questions,
  }) {
    return QuizSet(
      id: id ?? this.id,
      name: name ?? this.name,
      subject: subject ?? this.subject,
      description: description ?? this.description,
      difficulty: difficulty ?? this.difficulty,
      questionCount: questionCount ?? this.questionCount,
      estimatedTime: estimatedTime ?? this.estimatedTime,
      questions: questions ?? this.questions,
    );
  }
}

/// 测验题目
class QuizQuestion {
  final String id;
  final String question;
  final List<String> options;
  final int correctIndex;
  final String explanation;
  final Difficulty difficulty;
  final QuestionType type;

  QuizQuestion({
    String? id,
    required this.question,
    required this.options,
    required this.correctIndex,
    required this.explanation,
    this.difficulty = Difficulty.medium,
    this.type = QuestionType.single,
  }) : id = id ?? const Uuid().v4();

  factory QuizQuestion.fromJson(Map<String, dynamic> json) {
    return QuizQuestion(
      id: json['id'] ?? '',
      question: json['question'] ?? '',
      options: List<String>.from(json['options'] ?? []),
      correctIndex: json['correctIndex'] ?? 0,
      explanation: json['explanation'] ?? '',
      difficulty: Difficulty.values.firstWhere(
        (e) => e.toString() == 'Difficulty.${json['difficulty']}',
        orElse: () => Difficulty.medium,
      ),
      type: QuestionType.values.firstWhere(
        (e) => e.toString() == 'QuestionType.${json['type']}',
        orElse: () => QuestionType.single,
      ),
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'question': question,
      'options': options,
      'correctIndex': correctIndex,
      'explanation': explanation,
      'difficulty': difficulty.toString().split('.').last,
      'type': type.toString().split('.').last,
    };
  }

  QuizQuestion copyWith({
    String? id,
    String? question,
    List<String>? options,
    int? correctIndex,
    String? explanation,
    Difficulty? difficulty,
    QuestionType? type,
  }) {
    return QuizQuestion(
      id: id ?? this.id,
      question: question ?? this.question,
      options: options ?? this.options,
      correctIndex: correctIndex ?? this.correctIndex,
      explanation: explanation ?? this.explanation,
      difficulty: difficulty ?? this.difficulty,
      type: type ?? this.type,
    );
  }
}

/// 测验记录
class QuizRecord {
  final String id;
  final String setId;
  final String setName;
  final String subject;
  final int totalQuestions;
  final int correctCount;
  final int wrongCount;
  final double score;
  final int timeSpentSeconds;
  final DateTime completedAt;
  final List<int> userAnswers;

  QuizRecord({
    String? id,
    required this.setId,
    required this.setName,
    required this.subject,
    required this.totalQuestions,
    required this.correctCount,
    required this.wrongCount,
    required this.score,
    required this.timeSpentSeconds,
    required this.completedAt,
    required this.userAnswers,
  }) : id = id ?? const Uuid().v4();

  factory QuizRecord.fromJson(Map<String, dynamic> json) {
    return QuizRecord(
      id: json['id'] ?? '',
      setId: json['setId'] ?? '',
      setName: json['setName'] ?? '',
      subject: json['subject'] ?? '',
      totalQuestions: json['totalQuestions'] ?? 0,
      correctCount: json['correctCount'] ?? 0,
      wrongCount: json['wrongCount'] ?? 0,
      score: (json['score'] ?? 0).toDouble(),
      timeSpentSeconds: json['timeSpentSeconds'] ?? 0,
      completedAt: json['completedAt'] != null
          ? DateTime.parse(json['completedAt'])
          : DateTime.now(),
      userAnswers: List<int>.from(json['userAnswers'] ?? []),
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'setId': setId,
      'setName': setName,
      'subject': subject,
      'totalQuestions': totalQuestions,
      'correctCount': correctCount,
      'wrongCount': wrongCount,
      'score': score,
      'timeSpentSeconds': timeSpentSeconds,
      'completedAt': completedAt.toIso8601String(),
      'userAnswers': userAnswers,
    };
  }
}

/// 测验统计
class QuizStats {
  final int totalQuizzes;
  final int totalQuestions;
  final int averageScore;
  final int totalTimeSpent; // 秒
  final Map<String, SubjectStats> subjectStats;

  QuizStats({
    required this.totalQuizzes,
    required this.totalQuestions,
    required this.averageScore,
    required this.totalTimeSpent,
    required this.subjectStats,
  });
}

/// 科目统计
class SubjectStats {
  final String subject;
  final int quizCount;
  final double totalScore;
  final double averageScore;
  final int totalTime;

  SubjectStats({
    required this.subject,
    required this.quizCount,
    required this.totalScore,
    required this.averageScore,
    required this.totalTime,
  });

  factory SubjectStats.fromJson(Map<String, dynamic> json) {
    return SubjectStats(
      subject: json['subject'] ?? '',
      quizCount: json['quizCount'] ?? 0,
      totalScore: (json['totalScore'] ?? 0).toDouble(),
      averageScore: (json['averageScore'] ?? 0).toDouble(),
      totalTime: json['totalTime'] ?? 0,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'subject': subject,
      'quizCount': quizCount,
      'totalScore': totalScore,
      'averageScore': averageScore,
      'totalTime': totalTime,
    };
  }
}

/// 测验设置
class QuizSettings {
  final int defaultQuestionCount;
  final bool showAnalysis;
  final bool shuffleQuestions;
  final bool showTimer;
  final int passingScore;

  QuizSettings({
    required this.defaultQuestionCount,
    required this.showAnalysis,
    required this.shuffleQuestions,
    required this.showTimer,
    required this.passingScore,
  });

  factory QuizSettings.defaults() {
    return QuizSettings(
      defaultQuestionCount: 10,
      showAnalysis: true,
      shuffleQuestions: true,
      showTimer: true,
      passingScore: 60,
    );
  }

  factory QuizSettings.fromJson(Map<String, dynamic> json) {
    return QuizSettings(
      defaultQuestionCount: json['defaultQuestionCount'] ?? 10,
      showAnalysis: json['showAnalysis'] ?? true,
      shuffleQuestions: json['shuffleQuestions'] ?? true,
      showTimer: json['showTimer'] ?? true,
      passingScore: json['passingScore'] ?? 60,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'defaultQuestionCount': defaultQuestionCount,
      'showAnalysis': showAnalysis,
      'shuffleQuestions': shuffleQuestions,
      'showTimer': showTimer,
      'passingScore': passingScore,
    };
  }
}
