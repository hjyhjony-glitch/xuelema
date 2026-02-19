/// 测验练习屏幕 - 实际答题界面
import 'package:flutter/material.dart';
import '../l10n/app_localizations.dart';
import '../extensions/l10n_extension.dart';
import '../models/quiz_models.dart';
import '../services/quiz_service.dart';
import 'quiz_result_screen.dart';

class QuizPracticeScreen extends StatefulWidget {
  final QuizSet quizSet;

  const QuizPracticeScreen({super.key, required this.quizSet});

  @override
  State<QuizPracticeScreen> createState() => _QuizPracticeScreenState();
}

class _QuizPracticeScreenState extends State<QuizPracticeScreen> {
  final QuizService _quizService = QuizService();
  
  late List<QuizQuestion> _questions;
  int _currentIndex = 0;
  int _correctCount = 0;
  int _wrongCount = 0;
  int? _selectedAnswerIndex;
  bool _answered = false;
  List<int> _userAnswers = [];
  int _startTime = 0;
  int _elapsedSeconds = 0;
  bool _showAnalysis = true;

  @override
  void initState() {
    super.initState();
    _startTime = DateTime.now().millisecondsSinceEpoch;
    _questions = widget.quizSet.questions.toList();
    if (_questions.isNotEmpty) {
      _userAnswers = List.filled(_questions.length, -1);
    }
    _loadSettings();
  }

  Future<void> _loadSettings() async {
    final settings = await _quizService.getSettings();
    setState(() {
      _showAnalysis = settings.showAnalysis;
    });
  }

  void _selectAnswer(int index) {
    if (_answered) return;
    
    setState(() {
      _selectedAnswerIndex = index;
      _userAnswers[_currentIndex] = index;
    });
  }

  void _submitAnswer() {
    if (_selectedAnswerIndex == null) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('请选择一个答案')),
      );
      return;
    }

    setState(() {
      _answered = true;
    });

    final question = _questions[_currentIndex];
    if (_selectedAnswerIndex == question.correctIndex) {
      setState(() => _correctCount++);
    } else {
      setState(() => _wrongCount++);
    }
  }

  void _nextQuestion() {
    if (_currentIndex < _questions.length - 1) {
      setState(() {
        _currentIndex++;
        _selectedAnswerIndex = _userAnswers[_currentIndex];
        _answered = _selectedAnswerIndex != -1;
      });
    } else {
      _finishQuiz();
    }
  }

  void _previousQuestion() {
    if (_currentIndex > 0) {
      setState(() {
        _currentIndex--;
        _selectedAnswerIndex = _userAnswers[_currentIndex];
        _answered = _selectedAnswerIndex != -1;
      });
    }
  }

  void _finishQuiz() {
    final endTime = DateTime.now().millisecondsSinceEpoch;
    final timeSpentSeconds = (endTime - _startTime) ~/ 1000;
    final score = _questions.isNotEmpty 
        ? (_correctCount / _questions.length * 100).round() 
        : 0;

    // 保存记录
    final record = QuizRecord(
      setId: widget.quizSet.id,
      setName: widget.quizSet.name,
      subject: widget.quizSet.subject,
      totalQuestions: _questions.length,
      correctCount: _correctCount,
      wrongCount: _wrongCount,
      score: score.toDouble(),
      timeSpentSeconds: timeSpentSeconds,
      completedAt: DateTime.now(),
      userAnswers: _userAnswers,
    );

    _quizService.saveRecord(record);

    Navigator.pushReplacement(
      context,
      MaterialPageRoute(
        builder: (context) => QuizResultScreen(
          totalQuestions: _questions.length,
          correctCount: _correctCount,
          timeSpentSeconds: timeSpentSeconds,
          setName: widget.quizSet.name,
        ),
      ),
    );
  }

  void _confirmExit() {
    if (_userAnswers.where((a) => a != -1).isNotEmpty) {
      showDialog(
        context: context,
        builder: (context) => AlertDialog(
          title: const Text('确认退出'),
          content: const Text('测验尚未完成，确定要退出吗？'),
          actions: [
            TextButton(
              onPressed: () => Navigator.pop(context),
              child: const Text('继续答题'),
            ),
            ElevatedButton(
              onPressed: () {
                Navigator.pop(context);
                Navigator.pop(context);
              },
              child: const Text('退出'),
            ),
          ],
        ),
      );
    } else {
      Navigator.pop(context);
    }
  }

  @override
  Widget build(BuildContext context) {
    if (_questions.isEmpty) {
      return Scaffold(
        appBar: AppBar(title: Text(widget.quizSet.name)),
        body: Center(
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              const Icon(Icons.warning, size: 64, color: Colors.orange),
              const SizedBox(height: 16),
              const Text(
                '该题库暂无题目',
                style: TextStyle(fontSize: 18),
              ),
              const SizedBox(height: 8),
              Text(
                '请先添加题目到 "${widget.quizSet.name}"',
                style: TextStyle(color: Colors.grey[600]),
                textAlign: TextAlign.center,
              ),
              const SizedBox(height: 24),
              ElevatedButton(
                onPressed: () => Navigator.pop(context),
                child: const Text('返回'),
              ),
            ],
          ),
        ),
      );
    }

    final question = _questions[_currentIndex];
    final progress = (_currentIndex + 1) / _questions.length;
    _elapsedSeconds = (DateTime.now().millisecondsSinceEpoch - _startTime) ~/ 1000;

    return WillPopScope(
      onWillPop: () async {
        _confirmExit();
        return false;
      },
      child: Scaffold(
        appBar: AppBar(
          title: Text('${widget.quizSet.name} - $_currentIndex/${_questions.length}'),
          actions: [
            Center(
              child: Padding(
                padding: const EdgeInsets.symmetric(horizontal: 16),
                child: Text(
                  _formatTime(_elapsedSeconds),
                  style: TextStyle(
                    fontSize: 16,
                    fontWeight: FontWeight.bold,
                    color: _elapsedSeconds > widget.quizSet.estimatedTime * 60 ? Colors.red : null,
                  ),
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
            
            // 统计栏
            Container(
              padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
              color: Colors.grey[100],
              child: Row(
                mainAxisAlignment: MainAxisAlignment.spaceAround,
                children: [
                  _buildStatChip(Icons.check_circle, '$_correctCount', Colors.green),
                  _buildStatChip(Icons.cancel, '$_wrongCount', Colors.red),
                  _buildStatChip(Icons.access_time, _formatTime(_elapsedSeconds), Colors.blue),
                ],
              ),
            ),
            
            // 题目区域
            Expanded(
              child: SingleChildScrollView(
                padding: const EdgeInsets.all(16),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    // 题目标题
                    Row(
                      children: [
                        Container(
                          width: 28,
                          height: 28,
                          decoration: BoxDecoration(
                            color: _getDifficultyColor(question.difficulty),
                            borderRadius: BorderRadius.circular(4),
                          ),
                          child: Center(
                            child: Text(
                              '${_currentIndex + 1}',
                              style: const TextStyle(
                                color: Colors.white,
                                fontSize: 14,
                                fontWeight: FontWeight.bold,
                              ),
                            ),
                          ),
                        ),
                        const SizedBox(width: 8),
                        Expanded(
                          child: Text(
                            question.question,
                            style: const TextStyle(
                              fontSize: 18,
                              fontWeight: FontWeight.w500,
                            ),
                          ),
                        ),
                      ],
                    ),
                    
                    const SizedBox(height: 24),
                    
                    // 选项列表
                    ...question.options.asMap().entries.map((entry) {
                      final index = entry.key;
                      final option = entry.value;
                      final isSelected = _selectedAnswerIndex == index;
                      final isCorrect = index == question.correctIndex;
                      final showResult = _answered;
                      
                      Color? bgColor;
                      Color? borderColor;
                      
                      if (showResult) {
                        if (isCorrect) {
                          bgColor = Colors.green.withOpacity(0.2);
                          borderColor = Colors.green;
                        } else if (isSelected && !isCorrect) {
                          bgColor = Colors.red.withOpacity(0.2);
                          borderColor = Colors.red;
                        }
                      } else if (isSelected) {
                        bgColor = Colors.blue.withOpacity(0.2);
                        borderColor = Colors.blue;
                      }
                      
                      return Container(
                        margin: const EdgeInsets.only(bottom: 12),
                        child: ElevatedButton(
                          onPressed: () => _selectAnswer(index),
                          style: ElevatedButton.styleFrom(
                            backgroundColor: bgColor,
                            foregroundColor: isSelected ? Colors.blue : null,
                            side: BorderSide(
                              color: borderColor ?? (isSelected ? Colors.blue : Colors.grey[300]!),
                              width: isSelected ? 2 : 1,
                            ),
                            padding: const EdgeInsets.all(16),
                            alignment: Alignment.topLeft,
                          ),
                          child: Row(
                            crossAxisAlignment: CrossAxisAlignment.start,
                            children: [
                              // 选项字母
                              Container(
                                width: 24,
                                height: 24,
                                decoration: BoxDecoration(
                                  shape: BoxShape.circle,
                                  border: Border.all(
                                    color: showResult 
                                      ? (isCorrect ? Colors.green : (isSelected ? Colors.red : Colors.grey))
                                      : (isSelected ? Colors.blue : Colors.grey),
                                    width: 2,
                                  ),
                                  color: showResult && isCorrect ? Colors.green : Colors.transparent,
                                ),
                                child: Center(
                                  child: Text(
                                    String.fromCharCode(65 + index),
                                    style: TextStyle(
                                      fontSize: 12,
                                      fontWeight: FontWeight.bold,
                                      color: showResult && isCorrect 
                                          ? Colors.white 
                                          : (isSelected ? Colors.blue : Colors.grey[700]),
                                    ),
                                  ),
                                ),
                              ),
                              const SizedBox(width: 12),
                              Expanded(
                                child: Text(
                                  option,
                                  style: const TextStyle(
                                    fontSize: 16,
                                  ),
                                ),
                              ),
                            ],
                          ),
                        ),
                      );
                    }).toList(),
                    
                    // 答案解析
                    if (_answered && _showAnalysis)
                      _buildAnalysisCard(question),
                  ],
                ),
              ),
            ),
            
            // 底部按钮
            _buildBottomButtons(context),
          ],
        ),
      ),
    );
  }

  Widget _buildStatChip(IconData icon, String value, Color color) {
    return Row(
      children: [
        Icon(icon, size: 16, color: color),
        const SizedBox(width: 4),
        Text(
          value,
          style: TextStyle(
            fontSize: 14,
            fontWeight: FontWeight.bold,
            color: color,
          ),
        ),
      ],
    );
  }

  Widget _buildAnalysisCard(QuizQuestion question) {
    final isCorrect = _selectedAnswerIndex == question.correctIndex;
    
    return Card(
      color: isCorrect ? Colors.green.withOpacity(0.1) : Colors.red.withOpacity(0.1),
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                Icon(
                  isCorrect ? Icons.check_circle : Icons.cancel,
                  color: isCorrect ? Colors.green : Colors.red,
                ),
                const SizedBox(width: 8),
                Text(
                  isCorrect ? '回答正确' : '回答错误',
                  style: TextStyle(
                    color: isCorrect ? Colors.green : Colors.red,
                    fontWeight: FontWeight.bold,
                    fontSize: 16,
                  ),
                ),
              ],
            ),
            if (!isCorrect) ...[
              const SizedBox(height: 8),
              Text('正确答案: ${String.fromCharCode(65 + question.correctIndex)}. ${question.options[question.correctIndex]}'),
            ],
            if (question.explanation.isNotEmpty) ...[
              const SizedBox(height: 12),
              const Text(
                '解析:',
                style: TextStyle(fontWeight: FontWeight.bold),
              ),
              const SizedBox(height: 4),
              Text(
                question.explanation,
                style: TextStyle(color: Colors.grey[700]),
              ),
            ],
          ],
        ),
      ),
    );
  }

  Widget _buildBottomButtons(BuildContext context) {
    return Container(
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
          // 上一题
          ElevatedButton.icon(
            onPressed: _currentIndex > 0 ? _previousQuestion : null,
            icon: const Icon(Icons.arrow_back),
            label: const Text('上一题'),
            style: ElevatedButton.styleFrom(
              backgroundColor: Colors.grey[200],
            ),
          ),
          
          const Spacer(),
          
          // 确认/下一题/完成按钮
          if (!_answered)
            ElevatedButton.icon(
              onPressed: _selectedAnswerIndex != null ? _submitAnswer : null,
              icon: const Icon(Icons.check),
              label: const Text('确认答案'),
              style: ElevatedButton.styleFrom(
                backgroundColor: Colors.blue,
                padding: const EdgeInsets.symmetric(horizontal: 24),
              ),
            )
          else if (_currentIndex < _questions.length - 1)
            ElevatedButton.icon(
              onPressed: _nextQuestion,
              icon: const Icon(Icons.arrow_forward),
              label: const Text('下一题'),
              style: ElevatedButton.styleFrom(
                backgroundColor: Colors.blue,
              ),
            )
          else
            ElevatedButton.icon(
              onPressed: _finishQuiz,
              icon: const Icon(Icons.done_all),
              label: const Text('完成测验'),
              style: ElevatedButton.styleFrom(
                backgroundColor: Colors.green,
                padding: const EdgeInsets.symmetric(horizontal: 24),
              ),
            ),
        ],
      ),
    );
  }

  String _formatTime(int seconds) {
    final mins = seconds ~/ 60;
    final secs = seconds % 60;
    return '${mins.toString().padLeft(2, '0')}:${secs.toString().padLeft(2, '0')}';
  }

  Color _getDifficultyColor(Difficulty difficulty) {
    switch (difficulty) {
      case Difficulty.easy:
        return Colors.green;
      case Difficulty.medium:
        return Colors.orange;
      case Difficulty.hard:
        return Colors.red;
    }
  }
}
