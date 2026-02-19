import 'package:flutter/material.dart';

/// @author OpenClaw
/// @date 2026-02-16

/// 错题模型
class MistakeQuestion {
  final String id;
  final String question;
  final List<String> options;
  final int correctIndex;
  final int userAnswerIndex;
  final String analysis;
  final DateTime createdAt;
  final String category;
  final int wrongCount;

  MistakeQuestion({
    required this.id,
    required this.question,
    required this.options,
    required this.correctIndex,
    required this.userAnswerIndex,
    required this.analysis,
    required this.createdAt,
    required this.category,
    this.wrongCount = 1,
  });

  factory MistakeQuestion.fromJson(Map<String, dynamic> json) {
    return MistakeQuestion(
      id: json['id'] ?? '',
      question: json['question'] ?? '',
      options: List<String>.from(json['options'] ?? []),
      correctIndex: json['correctIndex'] ?? 0,
      userAnswerIndex: json['userAnswerIndex'] ?? 0,
      analysis: json['analysis'] ?? '',
      createdAt: json['createdAt'] != null 
          ? DateTime.parse(json['createdAt']) 
          : DateTime.now(),
      category: json['category'] ?? '未分类',
      wrongCount: json['wrongCount'] ?? 1,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'question': question,
      'options': options,
      'correctIndex': correctIndex,
      'userAnswerIndex': userAnswerIndex,
      'analysis': analysis,
      'createdAt': createdAt.toIso8601String(),
      'category': category,
      'wrongCount': wrongCount,
    };
  }

  MistakeQuestion copyWith({
    String? id,
    String? question,
    List<String>? options,
    int? correctIndex,
    int? userAnswerIndex,
    String? analysis,
    DateTime? createdAt,
    String? category,
    int? wrongCount,
  }) {
    return MistakeQuestion(
      id: id ?? this.id,
      question: question ?? this.question,
      options: options ?? this.options,
      correctIndex: correctIndex ?? this.correctIndex,
      userAnswerIndex: userAnswerIndex ?? this.userAnswerIndex,
      analysis: analysis ?? this.analysis,
      createdAt: createdAt ?? this.createdAt,
      category: category ?? this.category,
      wrongCount: wrongCount ?? this.wrongCount,
    );
  }
}
