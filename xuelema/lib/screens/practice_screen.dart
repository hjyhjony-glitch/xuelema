/// 练习屏幕 - 完整的学习练习功能
import 'package:flutter/material.dart';
import '../l10n/app_localizations.dart';
import '../extensions/l10n_extension.dart';
import '../models/wrong_question_model.dart';
import '../services/wrong_question_service.dart';
import 'quiz_result_screen.dart';

class PracticeScreen extends StatefulWidget {
  final String? subject;
  final List<WrongQuestion> questions;

  const PracticeScreen({
    super.key,
    this.subject,
    required this.questions,
  });

  @override
  State<PracticeScreen> createState() => _PracticeScreenState();
}

class _PracticeScreenState extends State<PracticeScreen> {
  final WrongQuestionService _service = WrongQuestionService();
  
  int _currentIndex = 0;
  int _correctCount = 0;
  int _wrongCount = 0;
  int? _selectedAnswerIndex;
  bool _answered = false;
  List<int> _userAnswers = [];

  @override
  void initState() {
    super.initState();
    _userAnswers = List.filled(widget.questions.length, -1);
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

    // 检查答案正确性
    final question = widget.questions[_currentIndex];
    if (_selectedAnswerIndex == _getCorrectAnswerIndex(question)) {
      setState(() => _correctCount++);
    } else {
      setState(() => _wrongCount++);
      // 记录错题
      _recordWrongQuestion(question);
    }
  }

  /// 从答案字符串获取正确答案索引
  int? _getCorrectAnswerIndex(WrongQuestion question) {
    final answer = question.answer;
    if (answer.isEmpty) return null;
    
    // 尝试将答案转换为索引
    try {
      return int.tryParse(answer);
    } catch (e) {
      // 如果是字母（如"A"、"B"、"C"、"D"），转换为索引
      if (answer.length == 1 && answer.codeUnitAt(0) >= 65 && answer.codeUnitAt(0) <= 90) {
        return answer.codeUnitAt(0) - 65; // A->0, B->1, C->2, D->3
      }
      return null;
    }
  }
  
  void _recordWrongQuestion(WrongQuestion question) async {
    final wrongQuestion = WrongQuestion(
      subject: question.subject,
      title: question.title,
      options: question.options,
      answer: question.answer,
      explanation: question.explanation,
    );
    
    await _service.addQuestion(wrongQuestion);
  }

  void _nextQuestion() {
    if (_currentIndex < widget.questions.length - 1) {
      setState(() {
        _currentIndex++;
        _selectedAnswerIndex = _userAnswers[_currentIndex];
        _answered = _selectedAnswerIndex != -1;
      });
    } else {
      _showResults();
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

  void _showResults() {
    Navigator.pushReplacement(
      context,
      MaterialPageRoute(
        builder: (context) => QuizResultScreen(
          totalQuestions: widget.questions.length,
          correctCount: _correctCount,
        ),
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    
    
    if (widget.questions.isEmpty) {
      return Scaffold(
        appBar: AppBar(title: Text(context.l10n.practice)),
        body: Center(
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              const Icon(Icons.quiz, size: 64, color: Colors.grey),
              const SizedBox(height: 16),
              Text(context.l10n.noQuestionsMessage),
              const SizedBox(height: 24),
              ElevatedButton(
                onPressed: () => Navigator.pop(context),
                child: Text(context.l10n.backButton),
              ),
            ],
          ),
        ),
      );
    }

    final question = widget.questions[_currentIndex];
    final progress = (_currentIndex + 1) / widget.questions.length;

    return Scaffold(
      appBar: AppBar(
        title: Text('${context.l10n.practice} - ${_currentIndex + 1}/${widget.questions.length}'),
        actions: [
          Center(
            child: Padding(
              padding: const EdgeInsets.symmetric(horizontal: 16),
              child: Text(
                '${context.l10n.correct}: $_correctCount  ${context.l10n.wrong}: $_wrongCount',
                style: TextStyle(
                  color: _correctCount > _wrongCount ? Colors.green : Colors.orange,
                  fontWeight: FontWeight.bold,
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
          
          // 题目区域
          Expanded(
            child: SingleChildScrollView(
              padding: const EdgeInsets.all(16),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  // 科目标签
                  if (question.subject.isNotEmpty)
                    Container(
                      padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                      decoration: BoxDecoration(
                        color: Colors.blue.withOpacity(0.1),
                        borderRadius: BorderRadius.circular(4),
                      ),
                      child: Text(
                        question.subject,
                        style: const TextStyle(color: Colors.blue, fontSize: 12),
                      ),
                    ),
                  
                  const SizedBox(height: 16),
                  
                  // 题目内容
                  Text(
                    question.title,
                    style: const TextStyle(fontSize: 18, fontWeight: FontWeight.w500),
                  ),
                  
                  const SizedBox(height: 24),
                  
                  // 选项列表
                  ...question.options.asMap().entries.map((entry) {
                    final index = entry.key;
                    final option = entry.value;
                    final isSelected = _selectedAnswerIndex == index;
                    final correctAnswerIndex = _getCorrectAnswerIndex(question);
                    final isCorrect = index == correctAnswerIndex;
                    final showResult = _answered;
                    
                    Color? bgColor;
                    if (showResult) {
                      if (correctAnswerIndex != null && index == correctAnswerIndex) {
                        bgColor = Colors.green.withOpacity(0.2);
                      } else if (isSelected && correctAnswerIndex != null && !isCorrect) {
                        bgColor = Colors.red.withOpacity(0.2);
                      }
                    } else if (isSelected) {
                      bgColor = Colors.blue.withOpacity(0.2);
                    }
                    
                    return Container(
                      margin: const EdgeInsets.only(bottom: 12),
                      child: ElevatedButton(
                        onPressed: () => _selectAnswer(index),
                        style: ElevatedButton.styleFrom(
                          backgroundColor: bgColor,
                          foregroundColor: isSelected ? Colors.blue : null,
                          side: BorderSide(
                            color: isSelected ? Colors.blue : Colors.grey[300]!,
                            width: isSelected ? 2 : 1,
                          ),
                          padding: const EdgeInsets.all(16),
                          alignment: Alignment.centerLeft,
                        ),
                        child: Row(
                          children: [
                            Container(
                              width: 28,
                              height: 28,
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
                              child: showResult && isCorrect
                                  ? const Icon(Icons.check, size: 16, color: Colors.green)
                                  : isSelected && showResult
                                      ? const Icon(Icons.close, size: 16, color: Colors.red)
                                      : null,
                            ),
                            const SizedBox(width: 12),
                            Expanded(
                              child: Text(
                                option,
                                style: TextStyle(
                                  fontSize: 16,
                                  color: isSelected ? Colors.blue : null,
                                ),
                              ),
                            ),
                          ],
                        ),
                      ),
                    );
                  }).toList(),
                  
                  // 答案解析（答错后显示）
                  if (_answered && _selectedAnswerIndex != _getCorrectAnswerIndex(question))
                    Card(
                      color: Colors.red.withOpacity(0.1),
                      child: Padding(
                        padding: const EdgeInsets.all(16),
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            Row(
                              children: [
                                const Icon(Icons.error, color: Colors.red),
                                const SizedBox(width: 8),
                                const Text(
                                  '回答错误',
                                  style: TextStyle(
                                    color: Colors.red,
                                    fontWeight: FontWeight.bold,
                                  ),
                                ),
                              ],
                            ),
                            const SizedBox(height: 8),
                            Text('正确答案: ${question.answer}'),
                            if (question.explanation.isNotEmpty) ...[
                              const SizedBox(height: 8),
                              Text(
                                '解析: ${question.explanation}',
                                style: TextStyle(color: Colors.grey[700]),
                              ),
                            ],
                          ],
                        ),
                      ),
                    ),
                ],
              ),
            ),
          ),
          
          // 底部按钮
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
                
                // 提交/下一题按钮
                if (!_answered)
                  ElevatedButton.icon(
                    onPressed: _submitAnswer,
                    icon: const Icon(Icons.check),
                    label: const Text('确认答案'),
                    style: ElevatedButton.styleFrom(
                      backgroundColor: Colors.blue,
                    ),
                  )
                else if (_currentIndex < widget.questions.length - 1)
                  ElevatedButton.icon(
                    onPressed: _nextQuestion,
                    icon: const Icon(Icons.arrow_forward),
                    label: Text(context.l10n.confirm),
                    style: ElevatedButton.styleFrom(
                      backgroundColor: Colors.blue,
                    ),
                  )
                else
                  ElevatedButton.icon(
                    onPressed: _showResults,
                    icon: const Icon(Icons.done_all),
                    label: Text(context.l10n.confirm),
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
}