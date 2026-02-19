/// @author OpenClaw
/// @date 2026-02-16

/// 复盘模型
class Review {
  final String id;
  final String type; // daily, weekly, monthly
  final DateTime date;
  final String summary;
  final String whatWentWell;
  final String needsImprovement;
  final String tomorrowPlan;
  final int focusMinutes;
  final int tasksCompleted;
  final int tasksTotal;

  Review({
    required this.id,
    required this.type,
    required this.date,
    required this.summary,
    required this.whatWentWell,
    required this.needsImprovement,
    required this.tomorrowPlan,
    required this.focusMinutes,
    required this.tasksCompleted,
    required this.tasksTotal,
  });

  factory Review.fromJson(Map<String, dynamic> json) {
    return Review(
      id: json['id'] ?? '',
      type: json['type'] ?? 'daily',
      date: json['date'] != null 
          ? DateTime.parse(json['date']) 
          : DateTime.now(),
      summary: json['summary'] ?? '',
      whatWentWell: json['whatWentWell'] ?? '',
      needsImprovement: json['needsImprovement'] ?? '',
      tomorrowPlan: json['tomorrowPlan'] ?? '',
      focusMinutes: json['focusMinutes'] ?? 0,
      tasksCompleted: json['tasksCompleted'] ?? 0,
      tasksTotal: json['tasksTotal'] ?? 0,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'type': type,
      'date': date.toIso8601String(),
      'summary': summary,
      'whatWentWell': whatWentWell,
      'needsImprovement': needsImprovement,
      'tomorrowPlan': tomorrowPlan,
      'focusMinutes': focusMinutes,
      'tasksCompleted': tasksCompleted,
      'tasksTotal': tasksTotal,
    };
  }

  Review copyWith({
    String? id,
    String? type,
    DateTime? date,
    String? summary,
    String? whatWentWell,
    String? needsImprovement,
    String? tomorrowPlan,
    int? focusMinutes,
    int? tasksCompleted,
    int? tasksTotal,
  }) {
    return Review(
      id: id ?? this.id,
      type: type ?? this.type,
      date: date ?? this.date,
      summary: summary ?? this.summary,
      whatWentWell: whatWentWell ?? this.whatWentWell,
      needsImprovement: needsImprovement ?? this.needsImprovement,
      tomorrowPlan: tomorrowPlan ?? this.tomorrowPlan,
      focusMinutes: focusMinutes ?? this.focusMinutes,
      tasksCompleted: tasksCompleted ?? this.tasksCompleted,
      tasksTotal: tasksTotal ?? this.tasksTotal,
    );
  }
}

/// 复习项模型
class ReviewItem {
  final String id;
  final String subject;
  final String title;
  final DateTime nextReviewDate;
  final int reviewCount;

  ReviewItem({
    required this.id,
    required this.subject,
    required this.title,
    required this.nextReviewDate,
    this.reviewCount = 0,
  });

  factory ReviewItem.fromJson(Map<String, dynamic> json) {
    return ReviewItem(
      id: json['id'] ?? '',
      subject: json['subject'] ?? '',
      title: json['title'] ?? '',
      nextReviewDate: json['nextReviewDate'] != null 
          ? DateTime.parse(json['nextReviewDate']) 
          : DateTime.now(),
      reviewCount: json['reviewCount'] ?? 0,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'subject': subject,
      'title': title,
      'nextReviewDate': nextReviewDate.toIso8601String(),
      'reviewCount': reviewCount,
    };
  }
}
