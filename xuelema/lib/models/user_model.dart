class User {
  final String id;
  final String name;
  final String email;
  final String avatarUrl;
  final int totalFocusMinutes;
  final int completedTasksCount;
  final DateTime createdAt;

  User({
    required this.id,
    required this.name,
    required this.email,
    this.avatarUrl = '',
    this.totalFocusMinutes = 0,
    this.completedTasksCount = 0,
    required this.createdAt,
  });

  factory User.fromJson(Map<String, dynamic> json) {
    return User(
      id: json['id'] ?? '',
      name: json['name'] ?? '',
      email: json['email'] ?? '',
      avatarUrl: json['avatarUrl'] ?? '',
      totalFocusMinutes: json['totalFocusMinutes'] ?? 0,
      completedTasksCount: json['completedTasksCount'] ?? 0,
      createdAt: json['createdAt'] != null 
          ? DateTime.parse(json['createdAt']) 
          : DateTime.now(),
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'name': name,
      'email': email,
      'avatarUrl': avatarUrl,
      'totalFocusMinutes': totalFocusMinutes,
      'completedTasksCount': completedTasksCount,
      'createdAt': createdAt.toIso8601String(),
    };
  }

  User copyWith({
    String? id,
    String? name,
    String? email,
    String? avatarUrl,
    int? totalFocusMinutes,
    int? completedTasksCount,
    DateTime? createdAt,
  }) {
    return User(
      id: id ?? this.id,
      name: name ?? this.name,
      email: email ?? this.email,
      avatarUrl: avatarUrl ?? this.avatarUrl,
      totalFocusMinutes: totalFocusMinutes ?? this.totalFocusMinutes,
      completedTasksCount: completedTasksCount ?? this.completedTasksCount,
      createdAt: createdAt ?? this.createdAt,
    );
  }
}
