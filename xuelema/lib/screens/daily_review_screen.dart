/// 每日复习屏幕 - 完整的复习流程界面
import 'package:flutter/material.dart';
import '../l10n/app_localizations.dart';
import '../services/wrong_question_service.dart';
import 'quiz_result_screen.dart';

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
    required this.reviewCount,
  });
}

class DailyReviewScreen extends StatefulWidget {
  final List<ReviewItem> reviewItems;

  const DailyReviewScreen({super.key, required this.reviewItems});

  @override
  State<DailyReviewScreen> createState() => _DailyReviewScreenState();
}

class _DailyReviewScreenState extends State<DailyReviewScreen> {
  final WrongQuestionService _service = WrongQuestionService();
  
  int _currentIndex = 0;
  int _correctCount = 0;
  int _wrongCount = 0;
  bool _isReviewing = false;
  List<bool> _reviewResults = [];

  @override
  void initState() {
    super.initState();
    _reviewResults = List.filled(widget.reviewItems.length, false);
  }

  void _markAsReviewed(bool correct) {
    setState(() {
      _reviewResults[_currentIndex] = correct;
      if (correct) {
        _correctCount++;
      } else {
        _wrongCount++;
      }
    });
  }

  void _nextReview() {
    if (_currentIndex < widget.reviewItems.length - 1) {
      setState(() {
        _currentIndex++;
        _isReviewing = false;
      });
    } else {
      _showResults();
    }
  }

  void _previousReview() {
    if (_currentIndex > 0) {
      setState(() {
        _currentIndex--;
        _isReviewing = false;
      });
    }
  }

  void _showResults() {
    Navigator.pushReplacement(
      context,
      MaterialPageRoute(
        builder: (context) => QuizResultScreen(
          totalQuestions: widget.reviewItems.length,
          correctCount: _correctCount,
          wrongCount: _wrongCount,
          onContinue: () => Navigator.popUntil(context, (route) => route.isFirst),
        ),
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    final l10n = AppLocalizations.of(context);
    final currentItem = widget.reviewItems[_currentIndex];
    final progress = (_currentIndex + 1) / widget.reviewItems.length;

    return Scaffold(
      appBar: AppBar(
        title: Text('复习进度 (${_currentIndex + 1}/${widget.reviewItems.length})'),
        leading: IconButton(
          icon: const Icon(Icons.close),
          onPressed: () => _showExitConfirmDialog(context),
        ),
        actions: [
          Center(
            child: Padding(
              padding: const EdgeInsets.symmetric(horizontal: 16),
              child: Row(
                children: [
                  Container(
                    padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                    decoration: BoxDecoration(
                      color: Colors.green.withOpacity(0.1),
                      borderRadius: BorderRadius.circular(4),
                    ),
                    child: Text(
                      '${l10n.correct}: $_correctCount',
                      style: const TextStyle(color: Colors.green),
                    ),
                  ),
                  const SizedBox(width: 8),
                  Container(
                    padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                    decoration: BoxDecoration(
                      color: Colors.red.withOpacity(0.1),
                      borderRadius: BorderRadius.circular(4),
                    ),
                    child: Text(
                      '${l10n.wrong}: $_wrongCount',
                      style: const TextStyle(color: Colors.red),
                    ),
                  ),
                ],
              ),
            ),
          ),
        ],
      ),
      body: Column(
        children: [
          // 进度条
          LinearProgressIndicator(
            value: progress,
            minHeight: 4,
            backgroundColor: Colors.grey[200],
          ),
          
          // 进度指示器
          Container(
            padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
            child: Row(
              mainAxisAlignment: MainAxisAlignment.center,
              children: widget.reviewItems.asMap().entries.map((entry) {
                final index = entry.key;
                final reviewed = index < _currentIndex;
                final isCurrent = index == _currentIndex;
                
                Color color;
                if (reviewed) {
                  color = _reviewResults[index] ? Colors.green : Colors.red;
                } else {
                  color = isCurrent ? Colors.blue : Colors.grey[300]!;
                }
                
                return Container(
                  margin: const EdgeInsets.symmetric(horizontal: 4),
                  width: 12,
                  height: 12,
                  decoration: BoxDecoration(
                    shape: BoxShape.circle,
                    color: color,
                  ),
                );
              }).toList(),
            ),
          ),
          
          // 复习内容卡片
          Expanded(
            child: Padding(
              padding: const EdgeInsets.all(16),
              child: Card(
                elevation: 2,
                child: SingleChildScrollView(
                  padding: const EdgeInsets.all(24),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      // 科目标签
                      Row(
                        children: [
                          Container(
                            padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
                            decoration: BoxDecoration(
                              color: Colors.blue.withOpacity(0.1),
                              borderRadius: BorderRadius.circular(16),
                            ),
                            child: Text(
                              currentItem.subject,
                              style: const TextStyle(
                                color: Colors.blue,
                                fontWeight: FontWeight.bold,
                              ),
                            ),
                          ),
                          const Spacer(),
                          Text(
                            '第${currentItem.reviewCount}次复习',
                            style: TextStyle(color: Colors.grey[600]),
                          ),
                        ],
                      ),
                      
                      const SizedBox(height: 24),
                      
                      // 复习内容标题
                      Text(
                        currentItem.title,
                        style: const TextStyle(
                          fontSize: 20,
                          fontWeight: FontWeight.bold,
                        ),
                      ),
                      
                      const SizedBox(height: 24),
                      
                      // 复习提示
                      Card(
                        color: Colors.amber.withOpacity(0.1),
                        child: Padding(
                          padding: const EdgeInsets.all(16),
                          child: Column(
                            children: [
                              Row(
                                children: [
                                  const Icon(Icons.lightbulb, color: Colors.amber),
                                  const SizedBox(width: 8),
                                  const Text(
                                    '回忆提示',
                                    style: TextStyle(
                                      fontWeight: FontWeight.bold,
                                    ),
                                  ),
                                ],
                              ),
                              const SizedBox(height: 8),
                              Text(
                                '试着回忆这个知识点的主要内容。'
                                '点击"显示答案"查看详细内容，然后评价自己的掌握程度。',
                                style: TextStyle(color: Colors.grey[700]),
                              ),
                            ],
                          ),
                        ),
                      ),
                      
                      const SizedBox(height: 24),
                      
                      // 显示答案按钮
                      SizedBox(
                        width: double.infinity,
                        child: ElevatedButton.icon(
                          onPressed: () {
                            setState(() => _isReviewing = true);
                          },
                          icon: const Icon(Icons.visibility),
                          label: const Text('显示答案'),
                          style: ElevatedButton.styleFrom(
                            backgroundColor: Colors.blue,
                            padding: const EdgeInsets.symmetric(vertical: 16),
                          ),
                        ),
                      ),
                      
                      // 详细内容（展开后显示）
                      if (_isReviewing) ...[
                        const SizedBox(height: 24),
                        const Divider(),
                        const SizedBox(height: 24),
                        
                        // 详细内容
                        Text(
                          '知识点详情',
                          style: TextStyle(
                            fontSize: 16,
                            fontWeight: FontWeight.bold,
                            color: Colors.grey[700],
                          ),
                        ),
                        const SizedBox(height: 12),
                        Text(
                          '这是知识点的详细内容。在实际应用中，这里会显示从数据库或文件中读取的具体知识点内容。',
                          style: TextStyle(fontSize: 16, height: 1.6),
                        ),
                        
                        const SizedBox(height: 24),
                        
                        // 掌握程度评价
                        Text(
                          '你的掌握程度',
                          style: TextStyle(
                            fontSize: 16,
                            fontWeight: FontWeight.bold,
                            color: Colors.grey[700],
                          ),
                        ),
                        const SizedBox(height: 12),
                        
                        Row(
                          children: [
                            Expanded(
                              child: ElevatedButton.icon(
                                onPressed: () => _markAsReviewed(false),
                                icon: const Icon(Icons.close),
                                label: const Text('不熟悉'),
                                style: ElevatedButton.styleFrom(
                                  backgroundColor: Colors.red[100],
                                  foregroundColor: Colors.red[700],
                                ),
                              ),
                            ),
                            const SizedBox(width: 12),
                            Expanded(
                              child: ElevatedButton.icon(
                                onPressed: () => _markAsReviewed(true),
                                icon: const Icon(Icons.check),
                                label: const Text('已掌握'),
                                style: ElevatedButton.styleFrom(
                                  backgroundColor: Colors.green[100],
                                  foregroundColor: Colors.green[700],
                                ),
                              ),
                            ),
                          ],
                        ),
                      ],
                    ],
                  ),
                ),
              ),
            ),
          ),
          
          // 底部导航
          Container(
            padding: const EdgeInsets.all(16),
            decoration: BoxDecoration(
              color: Colors.white,
              boxShadow: [
                BoxShadow(
                  color: Colors.grey.withOpacity(0.1),
                  blurRadius: 8,
                  offset: const Offset(0, -2),
                ),
              ],
            ),
            child: Row(
              children: [
                ElevatedButton.icon(
                  onPressed: _currentIndex > 0 ? _previousReview : null,
                  icon: const Icon(Icons.arrow_back),
                  label: const Text('上一个'),
                  style: ElevatedButton.styleFrom(
                    backgroundColor: Colors.grey[200],
                  ),
                ),
                const Spacer(),
                
                if (_currentIndex < widget.reviewItems.length - 1)
                  ElevatedButton.icon(
                    onPressed: _nextReview,
                    icon: const Icon(Icons.arrow_forward),
                    label: const Text('下一个'),
                    style: ElevatedButton.styleFrom(
                      backgroundColor: Colors.blue,
                    ),
                  )
                else
                  ElevatedButton.icon(
                    onPressed: _showResults,
                    icon: const Icon(Icons.done_all),
                    label: const Text('完成复习'),
                    style: ElevatedButton.styleFrom(
                      backgroundColor: Colors.green,
                    ),
                  ),
              ],
            ),
          ),
        ],
      ),
    );
  }

  void _showExitConfirmDialog(BuildContext context) {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: Text(l10n.$key),
        content: Text('确定要退出复习吗？已复习 $_currentIndex/${widget.reviewItems.length} 个'),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: const Text('继续复习'),
          ),
          ElevatedButton(
            onPressed: () {
              Navigator.pop(context);
              Navigator.pop(context);
            },
            style: ElevatedButton.styleFrom(backgroundColor: Colors.red),
            child: Text(l10n.$key),
          ),
        ],
      ),
    );
  }
}