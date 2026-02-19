/// 复习屏幕 - 复习计划和提醒功能
import 'package:flutter/material.dart';
import '../services/wrong_question_service.dart';
import '../services/notification_service.dart';
import '../l10n/app_localizations.dart';
import '../models/review_model.dart';
import 'practice_screen.dart';

class ReviewScreen extends StatefulWidget {
  const ReviewScreen({super.key});

  @override
  State<ReviewScreen> createState() => _ReviewScreenState();
}

class _ReviewScreenState extends State<ReviewScreen> {
  final WrongQuestionService _wrongQuestionService = WrongQuestionService();
  final NotificationService _notificationService = NotificationService();
  
  List<ReviewItem> _todayReviews = [];
  List<ReviewItem> _upcomingReviews = [];
  bool _isLoading = true;

  @override
  void initState() {
    super.initState();
    _loadReviewData();
  }

  Future<void> _loadReviewData() async {
    setState(() => _isLoading = true);
    
    // 获取错题本中的复习项
    final wrongQuestions = await _wrongQuestionService.getAllQuestions();
    final today = DateTime.now();
    
    // 生成复习计划
    final reviewItems = <ReviewItem>[];
    
    for (final q in wrongQuestions) {
      final review = ReviewItem(
        id: q.id,
        subject: q.subject,
        title: q.title,
        nextReviewDate: today,
        reviewCount: 1,
      );
      reviewItems.add(review);
    }
    
    // 筛选复习项
    _todayReviews = reviewItems;
    _upcomingReviews = [];
    
    setState(() => _isLoading = false);
  }

  Future<void> _startReview(ReviewItem item) async {
    // 获取该题目的详细信息
    final questions = await _wrongQuestionService.getAllQuestions();
    final question = questions.firstWhere((q) => q.id == item.id, orElse: () => questions.first);
    
    Navigator.push(
      context,
      MaterialPageRoute(
        builder: (context) => PracticeScreen(
          subject: item.subject,
          questions: [question],
        ),
      ),
    );
  }

  Future<void> _setupReminder() async {
    // 获取本地化字符串
    final l10n = AppLocalizations.of(context);
    
    // 设置复习提醒
    await _notificationService.scheduleDailyNotification(
      id: 4,
      title: l10n.review,
      body: l10n.dailyReview,
      time: const TimeOfDay(hour: 20, minute: 0),
      payload: 'review',
    );
    
    if (mounted) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text(l10n.dailyReminder)),
      );
    }
  }

  IconData _getSubjectIcon(String? subject) {
    switch (subject) {
      case 'Math': return Icons.calculate;
      case 'Chinese': return Icons.text_fields;
      case 'English': return Icons.translate;
      case 'Physics': return Icons.science;
      case 'Chemistry': return Icons.science;
      default: return Icons.book;
    }
  }

  @override
  Widget build(BuildContext context) {
    final l10n = AppLocalizations.of(context);
    
    return Scaffold(
      appBar: AppBar(
        title: Text(l10n.review),
        actions: [
          IconButton(
            icon: const Icon(Icons.notifications),
            onPressed: _setupReminder,
            tooltip: l10n.notifications,
          ),
        ],
      ),
      body: _isLoading
          ? const Center(child: CircularProgressIndicator())
          : RefreshIndicator(
              onRefresh: _loadReviewData,
              child: ListView(
                padding: const EdgeInsets.all(16),
                children: [
                  // 今日复习统计
                  Card(
                    child: Padding(
                      padding: const EdgeInsets.all(16),
                      child: Column(
                        children: [
                          Text(l10n.dailyReview, style: Theme.of(context).textTheme.titleLarge),
                          const SizedBox(height: 8),
                          Text('${l10n.totalQuestions(_todayReviews.length)}', 
                              style: Theme.of(context).textTheme.headlineMedium),
                        ],
                      ),
                    ),
                  ),
                  
                  const SizedBox(height: 16),
                  
                  // 复习提醒设置
                  Card(
                    child: ListTile(
                      leading: const Icon(Icons.notifications),
                      title: Text(l10n.dailyReminder),
                      subtitle: Text(l10n.dailyReminder),
                      trailing: ElevatedButton(
                        onPressed: _setupReminder,
                        child: Text(l10n.save),
                      ),
                    ),
                  ),
                  
                  const SizedBox(height: 16),
                  
                  // 今日复习列表
                  if (_todayReviews.isNotEmpty) ...[
                    Text(l10n.dailyReview, style: Theme.of(context).textTheme.titleMedium),
                    const SizedBox(height: 8),
                    ..._todayReviews.map((item) => Card(
                      child: ListTile(
                        leading: Icon(_getSubjectIcon(item.subject)),
                        title: Text(item.title),
                        subtitle: Text('${item.subject} · ${l10n.review}'),
                        trailing: ElevatedButton(
                          onPressed: () => _startReview(item),
                          child: Text(l10n.startQuiz),
                        ),
                      ),
                    )).toList(),
                  ] else ...[
                    Card(
                      child: Padding(
                        padding: const EdgeInsets.all(32),
                        child: Column(
                          children: [
                            Icon(Icons.check_circle_outline, size: 64, color: Colors.green),
                            const SizedBox(height: 16),
                            Text(l10n.noTasksToday),
                            const SizedBox(height: 8),
                            Text(l10n.restOrAddTask, 
                                style: TextStyle(color: Colors.grey[600])),
                          ],
                        ),
                      ),
                    ),
                  ],
                ],
              ),
            ),
    );
  }
}
