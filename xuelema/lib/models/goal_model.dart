/// @author OpenClaw
/// @date 2026-02-16

/// 目标模型
class Goal {
  final String id;
  final String title;
  final String description;
  final DateTime targetDate;
  final int progress; // 0-100
  final bool isCompleted;
  final DateTime createdAt;
  final bool isLongTerm; // 是否是长期目标

  Goal({
    required this.id,
    required this.title,
    required this.description,
    required this.targetDate,
    required this.progress,
    this.isCompleted = false,
    required this.createdAt,
    this.isLongTerm = false,
  });

  factory Goal.fromJson(Map<String, dynamic> json) {
    return Goal(
      id: json['id'] ?? '',
      title: json['title'] ?? '',
      description: json['description'] ?? '',
      targetDate: json['targetDate'] != null 
          ? DateTime.parse(json['targetDate']) 
          : DateTime.now(),
      progress: json['progress'] ?? 0,
      isCompleted: json['isCompleted'] ?? false,
      createdAt: json['createdAt'] != null 
          ? DateTime.parse(json['createdAt']) 
          : DateTime.now(),
      isLongTerm: json['isLongTerm'] ?? false,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'title': title,
      'description': description,
      'targetDate': targetDate.toIso8601String(),
      'progress': progress,
      'isCompleted': isCompleted,
      'createdAt': createdAt.toIso8601String(),
      'isLongTerm': isLongTerm,
    };
  }

  Goal copyWith({
    String? id,
    String? title,
    String? description,
    DateTime? targetDate,
    int? progress,
    bool? isCompleted,
    DateTime? createdAt,
    bool? isLongTerm,
  }) {
    return Goal(
      id: id ?? this.id,
      title: title ?? this.title,
      description: description ?? this.description,
      targetDate: targetDate ?? this.targetDate,
      progress: progress ?? this.progress,
      isCompleted: isCompleted ?? this.isCompleted,
      createdAt: createdAt ?? this.createdAt,
      isLongTerm: isLongTerm ?? this.isLongTerm,
    );
  }
}
