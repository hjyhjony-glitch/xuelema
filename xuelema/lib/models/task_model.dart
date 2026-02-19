import 'package:flutter/material.dart';
import 'package:uuid/uuid.dart';
import '../l10n/app_localizations.dart';

class Task {
  final String id;
  final String title;
  final String description;
  final DateTime dueTime;
  final List<String> subtasks;
  final bool isCompleted;
  final int focusMinutes;
  final DateTime createdAt;
  final DateTime? completedAt;
  final List<String> tags;
  final int priority; // 1: 高, 2: 中, 3: 低

  Task({
    String? id,
    required this.title,
    this.description = '',
    required this.dueTime,
    this.subtasks = const [],
    this.isCompleted = false,
    this.focusMinutes = 25,
    DateTime? createdAt,
    this.completedAt,
    this.tags = const [],
    this.priority = 2,
  })  : id = id ?? const Uuid().v4(),
        createdAt = createdAt ?? DateTime.now();

  factory Task.fromJson(Map<String, dynamic> json) {
    return Task(
      id: json['id'] ?? '',
      title: json['title'] ?? '',
      description: json['description'] ?? '',
      dueTime: json['dueTime'] != null 
          ? DateTime.parse(json['dueTime']) 
          : DateTime.now(),
      subtasks: List<String>.from(json['subtasks'] ?? []),
      isCompleted: json['isCompleted'] ?? false,
      focusMinutes: json['focusMinutes'] ?? 25,
      createdAt: json['createdAt'] != null 
          ? DateTime.parse(json['createdAt']) 
          : DateTime.now(),
      completedAt: json['completedAt'] != null 
          ? DateTime.parse(json['completedAt']) 
          : null,
      tags: List<String>.from(json['tags'] ?? []),
      priority: json['priority'] ?? 2,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'title': title,
      'description': description,
      'dueTime': dueTime.toIso8601String(),
      'subtasks': subtasks,
      'isCompleted': isCompleted,
      'focusMinutes': focusMinutes,
      'createdAt': createdAt.toIso8601String(),
      'completedAt': completedAt?.toIso8601String(),
      'tags': tags,
      'priority': priority,
    };
  }

  Task copyWith({
    String? id,
    String? title,
    String? description,
    DateTime? dueTime,
    List<String>? subtasks,
    bool? isCompleted,
    int? focusMinutes,
    DateTime? createdAt,
    DateTime? completedAt,
    List<String>? tags,
    int? priority,
  }) {
    return Task(
      id: id ?? this.id,
      title: title ?? this.title,
      description: description ?? this.description,
      dueTime: dueTime ?? this.dueTime,
      subtasks: subtasks ?? this.subtasks,
      isCompleted: isCompleted ?? this.isCompleted,
      focusMinutes: focusMinutes ?? this.focusMinutes,
      createdAt: createdAt ?? this.createdAt,
      completedAt: completedAt ?? this.completedAt,
      tags: tags ?? this.tags,
      priority: priority ?? this.priority,
    );
  }

  Duration get remainingTime {
    if (isCompleted) return Duration.zero;
    return dueTime.difference(DateTime.now());
  }

  bool get isOverdue {
    return !isCompleted && dueTime.isBefore(DateTime.now());
  }

  Color get priorityColor {
    switch (priority) {
      case 1:
        return Colors.red;
      case 2:
        return Colors.orange;
      case 3:
        return Colors.green;
      default:
        return Colors.grey;
    }
  }

  String get priorityText {
    switch (priority) {
      case 1:
        return '高';
      case 2:
        return '中';
      case 3:
        return '低';
      default:
        return '中';
    }
  }
}
