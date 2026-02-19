import 'package:uuid/uuid.dart';

class Knowledge {
  final String id;
  final String title;
  final String content;
  final String category;
  final List<String> tags;
  final DateTime createdAt;
  final DateTime updatedAt;
  final int viewCount;
  final int likeCount;

  Knowledge({
    String? id,
    required this.title,
    required this.content,
    this.category = '未分类',
    this.tags = const [],
    DateTime? createdAt,
    DateTime? updatedAt,
    this.viewCount = 0,
    this.likeCount = 0,
  })  : id = id ?? const Uuid().v4(),
        createdAt = createdAt ?? DateTime.now(),
        updatedAt = updatedAt ?? DateTime.now();

  factory Knowledge.fromJson(Map<String, dynamic> json) {
    return Knowledge(
      id: json['id'] ?? '',
      title: json['title'] ?? '',
      content: json['content'] ?? '',
      category: json['category'] ?? '未分类',
      tags: List<String>.from(json['tags'] ?? []),
      createdAt: json['createdAt'] != null 
          ? DateTime.parse(json['createdAt']) 
          : DateTime.now(),
      updatedAt: json['updatedAt'] != null 
          ? DateTime.parse(json['updatedAt']) 
          : DateTime.now(),
      viewCount: json['viewCount'] ?? 0,
      likeCount: json['likeCount'] ?? 0,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'title': title,
      'content': content,
      'category': category,
      'tags': tags,
      'createdAt': createdAt.toIso8601String(),
      'updatedAt': updatedAt.toIso8601String(),
      'viewCount': viewCount,
      'likeCount': likeCount,
    };
  }

  Knowledge copyWith({
    String? id,
    String? title,
    String? content,
    String? category,
    List<String>? tags,
    DateTime? createdAt,
    DateTime? updatedAt,
    int? viewCount,
    int? likeCount,
  }) {
    return Knowledge(
      id: id ?? this.id,
      title: title ?? this.title,
      content: content ?? this.content,
      category: category ?? this.category,
      tags: tags ?? this.tags,
      createdAt: createdAt ?? this.createdAt,
      updatedAt: updatedAt ?? this.updatedAt,
      viewCount: viewCount ?? this.viewCount,
      likeCount: likeCount ?? this.likeCount,
    );
  }
}

class KnowledgeCategory {
  final String id;
  final String name;
  final String icon;
  final int count;

  KnowledgeCategory({
    required this.id,
    required this.name,
    this.icon = '📚',
    this.count = 0,
  });

  factory KnowledgeCategory.fromJson(Map<String, dynamic> json) {
    return KnowledgeCategory(
      id: json['id'] ?? '',
      name: json['name'] ?? '',
      icon: json['icon'] ?? '📚',
      count: json['count'] ?? 0,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'name': name,
      'icon': icon,
      'count': count,
    };
  }
}
