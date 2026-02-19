/// 错题本屏幕 - 完整的错题管理和复习功能
import 'package:flutter/material.dart';
import '../l10n/app_localizations.dart';
import '../models/wrong_question_model.dart';
import '../services/wrong_question_service.dart';
import 'practice_screen.dart';
import 'quiz_result_screen.dart';

class WrongQuestionScreen extends StatefulWidget {
  const WrongQuestionScreen({super.key});

  @override
  State<WrongQuestionScreen> createState() => _WrongQuestionScreenState();
}

class _WrongQuestionScreenState extends State<WrongQuestionScreen> {
  final WrongQuestionService _service = WrongQuestionService();
  
  List<WrongQuestion> _allQuestions = [];
  List<WrongQuestion> _filteredQuestions = [];
  bool _isLoading = true;
  String _selectedSubject = '全部';
  String _searchQuery = '';

  @override
  void initState() {
    super.initState();
    _loadQuestions();
  }

  Future<void> _loadQuestions() async {
    setState(() => _isLoading = true);
    
    final questions = await _service.getAllQuestions();
    
    setState(() {
      _allQuestions = questions;
      _filteredQuestions = questions;
      _isLoading = false;
    });
  }

  void _filterQuestions() {
    List<WrongQuestion> filtered = _allQuestions;
    
    // 按科目筛选
    if (_selectedSubject != '全部') {
      filtered = filtered.where((q) => q.subject == _selectedSubject).toList();
    }
    
    // 按搜索查询筛选
    if (_searchQuery.isNotEmpty) {
      filtered = filtered.where((q) {
        return q.title.toLowerCase().contains(_searchQuery.toLowerCase()) ||
               q.explanation.toLowerCase().contains(_searchQuery.toLowerCase());
      }).toList();
    }
    
    setState(() {
      _filteredQuestions = filtered;
    });
  }

  void _selectSubject(String subject) {
    setState(() {
      _selectedSubject = subject;
    });
    _filterQuestions();
  }

  void _searchQuestions(String query) {
    setState(() {
      _searchQuery = query;
    });
    _filterQuestions();
  }

  Future<void> _deleteQuestion(WrongQuestion question) async {
    await _service.deleteQuestion(question.id);
    _loadQuestions();
    
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(content: Text('已删除: ${question.title}')),
    );
  }

  void _startPractice() {
    if (_filteredQuestions.isEmpty) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('没有可练习的错题')),
      );
      return;
    }
    
    Navigator.push(
      context,
      MaterialPageRoute(
        builder: (context) => PracticeScreen(
          subject: _selectedSubject,
          questions: _filteredQuestions,
        ),
      ),
    );
  }

  void _clearAllWrongQuestions() async {
    final confirm = await showDialog<bool>(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('确认清空'),
        content: const Text('确定要清空所有错题吗？此操作不可恢复。'),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context, false),
            child: Text(l10n.confirm),
          ),
          ElevatedButton(
            onPressed: () => Navigator.pop(context, true),
            style: ElevatedButton.styleFrom(backgroundColor: Colors.red),
            child: const Text('清空'),
          ),
        ],
      ),
    );
    
    if (confirm == true) {
      await _service.clearAllQuestions();
      _loadQuestions();
      
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('已清空所有错题')),
      );
    }
  }

  @override
  Widget build(BuildContext context) {
    final l10n = AppLocalizations.of(context);
    // 获取所有科目
    final subjects = {'全部', ..._allQuestions.map((q) => q.subject)};
    
    return Scaffold(
      appBar: AppBar(
        title: Text(l10n.wrongQuestionBank),
        actions: [
          IconButton(
            icon: const Icon(Icons.delete_sweep),
            onPressed: _allQuestions.isEmpty ? null : _clearAllWrongQuestions,
            tooltip: '清空错题',
          ),
        ],
      ),
      body: _isLoading
          ? const Center(child: CircularProgressIndicator())
          : Column(
              children: [
                // 搜索框
                Padding(
                  padding: const EdgeInsets.all(16),
                  child: TextField(
                    decoration: InputDecoration(
                      hintText: '搜索错题...',
                      prefixIcon: const Icon(Icons.search),
                      border: OutlineInputBorder(
                        borderRadius: BorderRadius.circular(12),
                      ),
                      filled: true,
                      fillColor: Colors.grey[100],
                    ),
                    onChanged: _searchQuestions,
                  ),
                ),
                
                // 科目筛选
                SizedBox(
                  height: 40,
                  child: ListView(
                    scrollDirection: Axis.horizontal,
                    padding: const EdgeInsets.symmetric(horizontal: 16),
                    children: subjects.map((subject) {
                      final isSelected = subject == _selectedSubject;
                      return Padding(
                        padding: const EdgeInsets.only(right: 8),
                        child: FilterChip(
                          label: Text(subject),
                          selected: isSelected,
                          onSelected: (_) => _selectSubject(subject),
                          selectedColor: Colors.blue.withOpacity(0.2),
                          checkmarkColor: Colors.blue,
                        ),
                      );
                    }).toList(),
                  ),
                ),
                
                const SizedBox(height: 8),
                
                // 统计信息
                Padding(
                  padding: const EdgeInsets.symmetric(horizontal: 16),
                  child: Row(
                    children: [
                      Text(
                        '共 $_filteredQuestions 道错题',
                        style: TextStyle(color: Colors.grey[600]),
                      ),
                      const Spacer(),
                      TextButton.icon(
                        onPressed: _startPractice,
                        icon: const Icon(Icons.play_arrow),
                        label: const Text('开始练习'),
                      ),
                    ],
                  ),
                ),
                
                const Divider(),
                
                // 错题列表
                Expanded(
                  child: _filteredQuestions.isEmpty
                      ? Center(
                          child: Column(
                            mainAxisAlignment: MainAxisAlignment.center,
                            children: [
                              Icon(
                                Icons.check_circle,
                                size: 64,
                                color: Colors.green[300],
                              ),
                              const SizedBox(height: 16),
                              const Text(
                                '没有错题',
                                style: TextStyle(fontSize: 18, color: Colors.grey),
                              ),
                              const SizedBox(height: 8),
                              Text(
                                _searchQuery.isEmpty 
                                    ? '继续保持！练习中做错的题目会自动加入错题本。'
                                    : '没有找到匹配的错题',
                                style: TextStyle(fontSize: 14, color: Colors.grey[600]),
                                textAlign: TextAlign.center,
                              ),
                            ],
                          ),
                        )
                      : RefreshIndicator(
                          onRefresh: _loadQuestions,
                          child: ListView.builder(
                            padding: const EdgeInsets.all(16),
                            itemCount: _filteredQuestions.length,
                            itemBuilder: (context, index) {
                              final question = _filteredQuestions[index];
                              return _buildQuestionCard(question);
                            },
                          ),
                        ),
                ),
              ],
            ),
      
      // 浮动按钮
      floatingActionButton: _filteredQuestions.isNotEmpty
          ? FloatingActionButton.extended(
              onPressed: _startPractice,
              icon: const Icon(Icons.play_arrow),
              label: Text('练习全部 (${_filteredQuestions.length})'),
            )
          : null,
    );
  }

  Widget _buildQuestionCard(WrongQuestion question) {
    return Card(
      margin: const EdgeInsets.only(bottom: 12),
      child: ExpansionTile(
        title: Text(
          question.title,
          maxLines: 2,
          overflow: TextOverflow.ellipsis,
        ),
        subtitle: Row(
          children: [
            Container(
              padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 2),
              decoration: BoxDecoration(
                color: Colors.blue.withOpacity(0.1),
                borderRadius: BorderRadius.circular(4),
              ),
              child: Text(
                question.subject,
                style: const TextStyle(color: Colors.blue, fontSize: 12),
              ),
            ),
            const SizedBox(width: 8),
            if (question.questionType.isNotEmpty)
              Container(
                padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 2),
                decoration: BoxDecoration(
                  color: Colors.orange.withOpacity(0.1),
                  borderRadius: BorderRadius.circular(4),
                ),
                child: Text(
                  question.questionType,
                  style: TextStyle(color: Colors.orange[700], fontSize: 12),
                ),
              ),
          ],
        ),
        children: [
          Padding(
            padding: const EdgeInsets.all(16),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                // 选项
                ...question.options.asMap().entries.map((entry) {
                  final index = entry.key;
                  final option = entry.value;
                  final isCorrect = index == question.correctAnswerIndex;
                  
                  return Padding(
                    padding: const EdgeInsets.only(bottom: 8),
                    child: Row(
                      children: [
                        Container(
                          width: 24,
                          height: 24,
                          decoration: BoxDecoration(
                            shape: BoxShape.circle,
                            color: isCorrect 
                                ? Colors.green.withOpacity(0.2)
                                : (index == question.userAnswerIndex 
                                    ? Colors.red.withOpacity(0.2)
                                    : Colors.grey[100]),
                            border: Border.all(
                              color: isCorrect 
                                  ? Colors.green
                                  : (index == question.userAnswerIndex 
                                      ? Colors.red 
                                      : Colors.grey),
                              width: 1,
                            ),
                          ),
                          child: Center(
                            child: Text(
                              String.fromCharCode(65 + index),
                              style: TextStyle(
                                fontSize: 12,
                                color: isCorrect 
                                    ? Colors.green
                                    : (index == question.userAnswerIndex 
                                        ? Colors.red 
                                        : Colors.grey),
                              ),
                            ),
                          ),
                        ),
                        const SizedBox(width: 12),
                        Text(option),
                      ],
                    ),
                  );
                }),
                
                // 解析
                if (question.explanation.isNotEmpty)
                  Container(
                    margin: const EdgeInsets.only(top: 12),
                    padding: const EdgeInsets.all(12),
                    decoration: BoxDecoration(
                      color: Colors.blue.withOpacity(0.1),
                      borderRadius: BorderRadius.circular(8),
                    ),
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Row(
                          children: [
                            const Icon(Icons.lightbulb, size: 16, color: Colors.blue),
                            const SizedBox(width: 8),
                            const Text(
                              '解析',
                              style: TextStyle(
                                fontWeight: FontWeight.bold,
                                color: Colors.blue,
                              ),
                            ),
                          ],
                        ),
                        const SizedBox(height: 4),
                        Text(question.explanation),
                      ],
                    ),
                  ),
                
                // 操作按钮
                const SizedBox(height: 16),
                Row(
                  children: [
                    Expanded(
                      child: OutlinedButton.icon(
                        onPressed: () => _startPracticeWithOne([question]),
                        icon: const Icon(Icons.play_arrow),
                        label: const Text('练习这道'),
                      ),
                    ),
                    const SizedBox(width: 8),
                    Expanded(
                      child: OutlinedButton.icon(
                        onPressed: () => _deleteQuestion(question),
                        icon: const Icon(Icons.delete),
                        label: Text(l10n.confirm),
                        style: OutlinedButton.styleFrom(
                          foregroundColor: Colors.red,
                        ),
                      ),
                    ),
                  ],
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }

  void _startPracticeWithOne(List<WrongQuestion> questions) {
    Navigator.push(
      context,
      MaterialPageRoute(
        builder: (context) => PracticeScreen(
          subject: questions.first.subject,
          questions: questions,
        ),
      ),
    );
  }
}