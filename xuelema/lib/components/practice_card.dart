import 'package:flutter/material.dart';
import '../l10n/app_localizations.dart';
import '../extensions/l10n_extension.dart';

/// 练习卡片组件
class PracticeCard extends StatefulWidget {
  final String title;
  final List<String> options;
  final String answer;
  final String? explanation;
  final Function(String selectedAnswer) onAnswer;
  final VoidCallback onComplete;
  final int consecutiveCorrect;

  const PracticeCard({
    super.key,
    required this.title,
    required this.options,
    required this.answer,
    this.explanation,
    required this.onAnswer,
    required this.onComplete,
    this.consecutiveCorrect = 0,
  });

  @override
  State<PracticeCard> createState() => _PracticeCardState();
}

class _PracticeCardState extends State<PracticeCard> {
  String? _selectedAnswer;
  bool _answered = false;
  bool _isCorrect = false;

  void _handleAnswer(String answer) {
    if (_answered) return;

    setState(() {
      _selectedAnswer = answer;
      _answered = true;
      _isCorrect = answer.trim().toLowerCase() == widget.answer.trim().toLowerCase();
    });

    widget.onAnswer(answer);

    // 2秒后自动进入下一题或完成
    Future.delayed(const Duration(seconds: 2), () {
      if (mounted) {
        widget.onComplete();
      }
    });
  }

  Widget _buildOptionButton(String option, int index) {
    final isSelected = _selectedAnswer == option;
    final isCorrectOption = option.trim().toLowerCase() == widget.answer.trim().toLowerCase();
    
    Color backgroundColor;
    if (_answered) {
      if (isCorrectOption) {
        backgroundColor = Colors.green.shade100;
      } else if (isSelected && !isCorrectOption) {
        backgroundColor = Colors.red.shade100;
      } else {
        backgroundColor = Colors.grey.shade200;
      }
    } else {
      backgroundColor = isSelected ? Theme.of(context).primaryColor.withOpacity(0.1) : Colors.white;
    }

    return GestureDetector(
      onTap: () => _handleAnswer(option),
      child: Container(
        margin: const EdgeInsets.symmetric(vertical: 6),
        padding: const EdgeInsets.all(16),
        decoration: BoxDecoration(
          color: backgroundColor,
          borderRadius: BorderRadius.circular(12),
          border: Border.all(
            color: isSelected
                ? Theme.of(context).primaryColor
                : Colors.grey.shade300,
            width: isSelected ? 2 : 1,
          ),
        ),
        child: Row(
          children: [
            Container(
              width: 32,
              height: 32,
              decoration: BoxDecoration(
                color: _answered && isCorrectOption
                    ? Colors.green
                    : _answered && isSelected && !isCorrectOption
                        ? Colors.red
                        : Colors.grey.shade300,
                shape: BoxShape.circle,
              ),
              child: Center(
                child: Text(
                  String.fromCharCode(65 + index),
                  style: TextStyle(
                    color: _answered ? Colors.white : Colors.grey.shade700,
                    fontWeight: FontWeight.bold,
                  ),
                ),
              ),
            ),
            const SizedBox(width: 12),
            Expanded(
              child: Text(
                option,
                style: TextStyle(
                  fontSize: 16,
                  color: _answered && !isCorrectOption && !isSelected
                      ? Colors.grey.shade500
                      : Colors.black87,
                ),
              ),
            ),
            if (_answered && isCorrectOption)
              const Icon(Icons.check_circle, color: Colors.green)
            else if (_answered && isSelected && !isCorrectOption)
              const Icon(Icons.cancel, color: Colors.red),
          ],
        ),
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Card(
      elevation: 4,
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
      child: Padding(
        padding: const EdgeInsets.all(20),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // 连续正确次数指示
            if (widget.consecutiveCorrect > 0)
              Container(
                padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
                decoration: BoxDecoration(
                  color: Colors.amber.shade100,
                  borderRadius: BorderRadius.circular(20),
                ),
                child: Row(
                  mainAxisSize: MainAxisSize.min,
                  children: [
                    const Icon(Icons.stars, color: Colors.amber, size: 16),
                    const SizedBox(width: 4),
                    Text(
                      '连续正确 ${widget.consecutiveCorrect}/3 次',
                      style: const TextStyle(
                        color: Colors.amber,
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                  ],
                ),
              ),
            
            const SizedBox(height: 16),
            
            // 题目
            Text(
              widget.title,
              style: const TextStyle(
                fontSize: 18,
                fontWeight: FontWeight.w600,
              ),
            ),
            
            const SizedBox(height: 20),
            
            // 选项列表
            ...List.generate(
              widget.options.length,
              (index) => _buildOptionButton(widget.options[index], index),
            ),
            
            // 答案解析（答错后显示）
            if (_answered && !_isCorrect && widget.explanation != null)
              Container(
                margin: const EdgeInsets.only(top: 16),
                padding: const EdgeInsets.all(12),
                decoration: BoxDecoration(
                  color: Colors.blue.shade50,
                  borderRadius: BorderRadius.circular(8),
                  border: Border.all(color: Colors.blue.shade200),
                ),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Row(
                      children: [
                        Icon(Icons.lightbulb_outline, color: Colors.blue.shade700),
                        const SizedBox(width: 8),
                        Text(
                          '正确答案: ${widget.answer}',
                          style: TextStyle(
                            color: Colors.blue.shade700,
                            fontWeight: FontWeight.bold,
                          ),
                        ),
                      ],
                    ),
                    const SizedBox(height: 8),
                    Text(
                      widget.explanation!,
                      style: TextStyle(color: Colors.blue.shade800),
                    ),
                  ],
                ),
              ),
            
            // 正确反馈
            if (_answered && _isCorrect)
              Container(
                margin: const EdgeInsets.only(top: 16),
                padding: const EdgeInsets.all(12),
                decoration: BoxDecoration(
                  color: Colors.green.shade50,
                  borderRadius: BorderRadius.circular(8),
                  border: Border.all(color: Colors.green.shade200),
                ),
                child: Row(
                  children: [
                    const Icon(Icons.celebration, color: Colors.green),
                    const SizedBox(width: 8),
                    const Expanded(
                      child: Text(
                        '回答正确！继续保持！',
                        style: TextStyle(
                          color: Colors.green,
                          fontWeight: FontWeight.bold,
                        ),
                      ),
                    ),
                  ],
                ),
              ),
          ],
        ),
      ),
    );
  }
}
