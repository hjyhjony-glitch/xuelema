/// 测验结果屏幕 - 完整的学习成果展示
import 'package:flutter/material.dart';
import '../l10n/app_localizations.dart';

class QuizResultScreen extends StatefulWidget {
  final int totalQuestions;
  final int correctCount;
  final int? wrongCount;
  final int? timeSpentSeconds;
  final VoidCallback? onRetry;
  final VoidCallback? onReview;
  final VoidCallback? onContinue;

  const QuizResultScreen({
    super.key,
    required this.totalQuestions,
    required this.correctCount,
    this.wrongCount,
    this.timeSpentSeconds,
    this.onRetry,
    this.onReview,
    this.onContinue,
  });

  @override
  State<QuizResultScreen> createState() => _QuizResultScreenState();
}

class _QuizResultScreenState extends State<QuizResultScreen> {
  @override
  Widget build(BuildContext context) {
    final l10n = AppLocalizations.of(context);
    final score = widget.totalQuestions > 0 
        ? (widget.correctCount / widget.totalQuestions * 100).round() 
        : 0;
    final wrongCount = widget.wrongCount ?? (widget.totalQuestions - widget.correctCount);
    
    // 计算用时
    String timeText = '';
    if (widget.timeSpentSeconds != null) {
      final minutes = widget.timeSpentSeconds! ~/ 60;
      final seconds = widget.timeSpentSeconds! % 60;
      timeText = '$minutes分${seconds}秒';
    }
    
    // 根据分数给出评价
    String rating;
    Color ratingColor;
    IconData ratingIcon;
    
    if (score >= 90) {
      rating = '太棒了！';
      ratingColor = Colors.green;
      ratingIcon = Icons.emoji_events;
    } else if (score >= 70) {
      rating = '做得不错！';
      ratingColor = Colors.blue;
      ratingIcon = Icons.thumb_up;
    } else if (score >= 50) {
      rating = '继续加油！';
      ratingColor = Colors.orange;
      ratingIcon = Icons.trending_up;
    } else {
      rating = '需要多练习！';
      ratingColor = Colors.red;
      ratingIcon = Icons.school;
    }

    return Scaffold(
      appBar: AppBar(
        title: Text(l10n.quizResults),
        automaticallyImplyLeading: false,
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(24),
        child: Column(
          children: [
            // 成绩展示卡片
            Card(
              elevation: 4,
              shape: RoundedRectangleBorder(
                borderRadius: BorderRadius.circular(16),
              ),
              child: Padding(
                padding: const EdgeInsets.all(32),
                child: Column(
                  children: [
                    // 成绩图标
                    Container(
                      width: 100,
                      height: 100,
                      decoration: BoxDecoration(
                        shape: BoxShape.circle,
                        color: ratingColor.withOpacity(0.1),
                      ),
                      child: Icon(
                        ratingIcon,
                        size: 48,
                        color: ratingColor,
                      ),
                    ),
                    
                    const SizedBox(height: 24),
                    
                    // 分数
                    Text(
                      '$score%',
                      style: TextStyle(
                        fontSize: 64,
                        fontWeight: FontWeight.bold,
                        color: ratingColor,
                      ),
                    ),
                    
                    const SizedBox(height: 8),
                    
                    // 评价
                    Text(
                      rating,
                      style: TextStyle(
                        fontSize: 24,
                        fontWeight: FontWeight.bold,
                        color: ratingColor,
                      ),
                    ),
                    
                    const SizedBox(height: 24),
                    
                    // 统计信息
                    Row(
                      mainAxisAlignment: MainAxisAlignment.spaceEvenly,
                      children: [
                        _buildStatItem(
                          Icons.check_circle,
                          '${widget.correctCount}',
                          l10n.correct,
                          Colors.green,
                        ),
                        _buildStatItem(
                          Icons.cancel,
                          '$wrongCount',
                          l10n.wrong,
                          Colors.red,
                        ),
                        _buildStatItem(
                          Icons.quiz,
                          '${widget.totalQuestions}',
                          '共${widget.totalQuestions}题',
                          Colors.blue,
                        ),
                      ],
                    ),
                    
                    // 用时信息
                    if (timeText.isNotEmpty)
                      Padding(
                        padding: const EdgeInsets.only(top: 16),
                        child: Row(
                          mainAxisAlignment: MainAxisAlignment.center,
                          children: [
                            const Icon(Icons.timer, size: 20, color: Colors.grey),
                            const SizedBox(width: 8),
                            Text(
                              '用时: $timeText',
                              style: TextStyle(color: Colors.grey[600]),
                            ),
                          ],
                        ),
                      ),
                  ],
                ),
              ),
            ),
            
            const SizedBox(height: 24),
            
            // 正确率进度环
            SizedBox(
              height: 150,
              width: 150,
              child: Stack(
                alignment: Alignment.center,
                children: [
                  CircularProgressIndicator(
                    value: widget.correctCount / widget.totalQuestions,
                    strokeWidth: 10,
                    backgroundColor: Colors.grey[200],
                    valueColor: AlwaysStoppedAnimation<Color>(ratingColor),
                  ),
                  Column(
                    mainAxisAlignment: MainAxisAlignment.center,
                    children: [
                      Text(
                        '${widget.correctCount}/${widget.totalQuestions}',
                        style: const TextStyle(
                          fontSize: 24,
                          fontWeight: FontWeight.bold,
                        ),
                      ),
                      Text(
                        l10n.correct,
                        style: TextStyle(
                          fontSize: 12,
                          color: Colors.grey[600],
                        ),
                      ),
                    ],
                  ),
                ],
              ),
            ),
            
            const SizedBox(height: 32),
            
            // 学习建议
            Card(
              child: Padding(
                padding: const EdgeInsets.all(16),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Row(
                      children: [
                        Icon(Icons.lightbulb, color: ratingColor),
                        const SizedBox(width: 8),
                        Text(
                          '学习建议',
                          style: TextStyle(
                            fontSize: 16,
                            fontWeight: FontWeight.bold,
                            color: ratingColor,
                          ),
                        ),
                      ],
                    ),
                    const SizedBox(height: 12),
                    _getSuggestionText(score, wrongCount),
                  ],
                ),
              ),
            ),
            
            const SizedBox(height: 32),
            
            // 操作按钮
            if (widget.onReview != null || wrongCount > 0)
              SizedBox(
                width: double.infinity,
                child: ElevatedButton.icon(
                  onPressed: widget.onReview,
                  icon: const Icon(Icons.rate_review),
                  label: Text('复习错题 ($wrongCount)'),
                  style: ElevatedButton.styleFrom(
                    backgroundColor: Colors.orange,
                    padding: const EdgeInsets.symmetric(vertical: 16),
                  ),
                ),
              ),
            
            const SizedBox(height: 12),
            
            if (widget.onRetry != null)
              SizedBox(
                width: double.infinity,
                child: ElevatedButton.icon(
                  onPressed: widget.onRetry,
                  icon: const Icon(Icons.refresh),
                  label: const Text('重新练习'),
                  style: ElevatedButton.styleFrom(
                    backgroundColor: Colors.blue,
                    padding: const EdgeInsets.symmetric(vertical: 16),
                  ),
                ),
              ),
            
            const SizedBox(height: 12),
            
            if (widget.onContinue != null)
              SizedBox(
                width: double.infinity,
                child: OutlinedButton.icon(
                  onPressed: widget.onContinue,
                  icon: const Icon(Icons.arrow_forward),
                  label: const Text('继续学习'),
                  style: OutlinedButton.styleFrom(
                    padding: const EdgeInsets.symmetric(vertical: 16),
                  ),
                ),
              ),
            
            const SizedBox(height: 24),
            
            // 返回主页
            TextButton(
              onPressed: () => Navigator.popUntil(context, (route) => route.isFirst),
              child: const Text('返回首页'),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildStatItem(IconData icon, String value, String label, Color color) {
    return Column(
      children: [
        Icon(icon, size: 28, color: color),
        const SizedBox(height: 4),
        Text(
          value,
          style: TextStyle(
            fontSize: 20,
            fontWeight: FontWeight.bold,
            color: color,
          ),
        ),
        Text(
          label,
          style: TextStyle(fontSize: 12, color: Colors.grey[600]),
        ),
      ],
    );
  }

  Widget _getSuggestionText(int score, int wrongCount) {
    if (score >= 90) {
      return const Text(
        '太优秀了！你已经很好地掌握了这部分内容。\n'
        '建议继续挑战更高难度的练习，保持学习热情！',
        style: TextStyle(fontSize: 14),
      );
    } else if (score >= 70) {
      return const Text(
        '表现不错！基础知识掌握得较好。\n'
        '建议重点复习错题，进一步巩固知识点。',
        style: TextStyle(fontSize: 14),
      );
    } else if (score >= 50) {
      return const Text(
        '还需要继续努力！建议：\n'
        '1. 回顾教材中的基础概念\n'
        '2. 重点练习错题\n'
        '3. 不懂的地方及时请教',
        style: TextStyle(fontSize: 14),
      );
    } else {
      return const Text(
        '建议从基础开始学习：\n'
        '1. 认真阅读教材内容\n'
        '2. 理解每个知识点的含义\n'
        '3. 先做简单题目打基础\n'
        '4. 循序渐进增加难度',
        style: TextStyle(fontSize: 14),
      );
    }
  }
}