/// 测验屏幕 - 自测系统入口
import 'package:flutter/material.dart';
import '../l10n/app_localizations.dart';
import '../extensions/l10n_extension.dart';
import '../models/quiz_models.dart';
import '../services/quiz_service.dart';
import 'quiz_practice_screen.dart';

class QuizScreen extends StatefulWidget {
  const QuizScreen({super.key});

  @override
  State<QuizScreen> createState() => _QuizScreenState();
}

class _QuizScreenState extends State<QuizScreen> {
  final QuizService _quizService = QuizService();
  List<QuizSet> _quizSets = [];
  bool _isLoading = true;
  QuizStats? _stats;

  @override
  void initState() {
    super.initState();
    _loadData();
  }

  Future<void> _loadData() async {
    await _quizService.init();
    final sets = await _quizService.getAllQuizSets();
    final stats = await _quizService.getStatistics();
    
    setState(() {
      _quizSets = sets;
      _stats = stats;
      _isLoading = false;
    });
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text(context.l10n.quiz),
        actions: [
          IconButton(
            icon: const Icon(Icons.bar_chart),
            onPressed: () => _showStatsDialog(context),
            tooltip: '测验统计',
          ),
        ],
      ),
      body: _isLoading
          ? const Center(child: CircularProgressIndicator())
          : RefreshIndicator(
              onRefresh: _loadData,
              child: ListView(
                padding: const EdgeInsets.all(16),
                children: [
                  // 统计卡片
                  _buildStatsCard(context),
                  
                  const SizedBox(height: 24),
                  
                  // 题库列表标题
                  Row(
                    mainAxisAlignment: MainAxisAlignment.spaceBetween,
                    children: [
                      Text(
                        '测验题库',
                        style: TextStyle(
                          fontSize: 18,
                          fontWeight: FontWeight.bold,
                          color: Colors.grey[800],
                        ),
                      ),
                      TextButton(
                        onPressed: () => _showAddQuizDialog(context),
                        child: const Text('+ 添加题库'),
                      ),
                    ],
                  ),
                  
                  const SizedBox(height: 12),
                  
                  // 题库列表
                  if (_quizSets.isEmpty)
                    _buildEmptyState(context)
                  else
                    ..._quizSets.map((quizSet) => _buildQuizSetCard(context, quizSet)),
                  
                  const SizedBox(height: 24),
                  
                  // 最近测验记录
                  _buildRecentRecords(context),
                ],
              ),
            ),
      floatingActionButton: FloatingActionButton(
        onPressed: () => _showAddQuizDialog(context),
        child: const Icon(Icons.add),
      ),
    );
  }

  Widget _buildStatsCard(BuildContext context) {
    final stats = _stats;
    if (stats == null || stats.totalQuizzes == 0) {
      return Card(
        child: Padding(
          padding: const EdgeInsets.all(16),
          child: Column(
            children: [
              const Icon(Icons.quiz, size: 48, color: Colors.blue),
              const SizedBox(height: 8),
              const Text(
                '开始你的第一次测验',
                style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold),
              ),
              const SizedBox(height: 4),
              Text(
                '从下方选择一个题库开始练习',
                style: TextStyle(color: Colors.grey[600]),
              ),
            ],
          ),
        ),
      );
    }

    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          children: [
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceAround,
              children: [
                _buildStatItem(
                  Icons.assignment_turned_in,
                  '${stats.totalQuizzes}',
                  '已完成测验',
                  Colors.green,
                ),
                _buildStatItem(
                  Icons.quiz,
                  '${stats.totalQuestions}',
                  '累计题目',
                  Colors.blue,
                ),
                _buildStatItem(
                  Icons.score,
                  '${stats.averageScore}%',
                  '平均分',
                  Colors.orange,
                ),
              ],
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

  Widget _buildQuizSetCard(BuildContext context, QuizSet quizSet) {
    final difficultyColor = _getDifficultyColor(quizSet.difficulty);
    
    return Card(
      margin: const EdgeInsets.only(bottom: 12),
      child: InkWell(
        onTap: () => _startQuiz(context, quizSet),
        borderRadius: BorderRadius.circular(12),
        child: Padding(
          padding: const EdgeInsets.all(16),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  Expanded(
                    child: Text(
                      quizSet.name,
                      style: const TextStyle(
                        fontSize: 16,
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                  ),
                  Container(
                    padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                    decoration: BoxDecoration(
                      color: difficultyColor.withOpacity(0.1),
                      borderRadius: BorderRadius.circular(4),
                    ),
                    child: Text(
                      _getDifficultyText(quizSet.difficulty),
                      style: TextStyle(color: difficultyColor, fontSize: 12),
                    ),
                  ),
                ],
              ),
              
              const SizedBox(height: 8),
              
              Text(
                quizSet.description,
                style: TextStyle(color: Colors.grey[600], fontSize: 14),
              ),
              
              const SizedBox(height: 12),
              
              Row(
                children: [
                  _buildInfoChip(Icons.book, '${quizSet.questionCount}题'),
                  const SizedBox(width: 8),
                  _buildInfoChip(Icons.access_time, '${quizSet.estimatedTime}分钟'),
                  const SizedBox(width: 8),
                  _buildInfoChip(Icons.category, quizSet.subject),
                ],
              ),
              
              const SizedBox(height: 12),
              
              SizedBox(
                width: double.infinity,
                child: ElevatedButton.icon(
                  onPressed: () => _startQuiz(context, quizSet),
                  icon: const Icon(Icons.play_arrow),
                  label: const Text('开始测验'),
                  style: ElevatedButton.styleFrom(
                    backgroundColor: Colors.blue,
                  ),
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildInfoChip(IconData icon, String text) {
    return Row(
      children: [
        Icon(icon, size: 14, color: Colors.grey[600]),
        const SizedBox(width: 4),
        Text(
          text,
          style: TextStyle(fontSize: 12, color: Colors.grey[600]),
        ),
      ],
    );
  }

  Widget _buildEmptyState(BuildContext context) {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(32),
        child: Column(
          children: [
            const Icon(Icons.library_books, size: 64, color: Colors.grey),
            const SizedBox(height: 16),
            const Text(
              '暂无测验题库',
              style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
            ),
            const SizedBox(height: 8),
            Text(
              '点击右下角添加题库或导入题目',
              style: TextStyle(color: Colors.grey[600]),
            ),
            const SizedBox(height: 16),
            ElevatedButton.icon(
              onPressed: () => _showAddQuizDialog(context),
              icon: const Icon(Icons.add),
              label: const Text('添加题库'),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildRecentRecords(BuildContext context) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          '最近测验',
          style: TextStyle(
            fontSize: 18,
            fontWeight: FontWeight.bold,
            color: Colors.grey[800],
          ),
        ),
        const SizedBox(height: 12),
        Card(
          child: Padding(
            padding: const EdgeInsets.all(16),
            child: Column(
              children: [
                const Icon(Icons.history, size: 48, color: Colors.grey),
                const SizedBox(height: 8),
                Text(
                  '暂无测验记录',
                  style: TextStyle(color: Colors.grey[600]),
                ),
                const SizedBox(height: 8),
                Text(
                  '完成测验后这里会显示历史记录',
                  style: TextStyle(fontSize: 12, color: Colors.grey[500]),
                ),
              ],
            ),
          ),
        ),
      ],
    );
  }

  void _startQuiz(BuildContext context, QuizSet quizSet) {
    Navigator.push(
      context,
      MaterialPageRoute(
        builder: (context) => QuizPracticeScreen(quizSet: quizSet),
      ),
    ).then((_) => _loadData());
  }

  void _showAddQuizDialog(BuildContext context) {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('添加题库'),
        content: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            ListTile(
              leading: const Icon(Icons.add_circle),
              title: const Text('手动创建题库'),
              subtitle: const Text('创建新的测验题库'),
              onTap: () {
                Navigator.pop(context);
                _showCreateQuizDialog(context);
              },
            ),
            ListTile(
              leading: const Icon(Icons.file_upload),
              title: const Text('导入题库'),
              subtitle: const Text('从文件导入题目'),
              onTap: () {
                Navigator.pop(context);
                // TODO: 实现导入功能
                ScaffoldMessenger.of(context).showSnackBar(
                  const SnackBar(content: Text('导入功能开发中')),
                );
              },
            ),
          ],
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: Text(context.l10n.confirm),
          ),
        ],
      ),
    );
  }

  void _showCreateQuizDialog(BuildContext context) {
    final nameController = TextEditingController();
    final descController = TextEditingController();
    String selectedSubject = '数学';
    Difficulty selectedDifficulty = Difficulty.medium;

    showDialog(
      context: context,
      builder: (context) => StatefulBuilder(
        builder: (context, setState) => AlertDialog(
          title: const Text('创建题库'),
          content: SingleChildScrollView(
            child: Column(
              mainAxisSize: MainAxisSize.min,
              children: [
                TextField(
                  controller: nameController,
                  decoration: const InputDecoration(
                    labelText: '题库名称',
                    hintText: '例如：小学数学练习',
                    border: OutlineInputBorder(),
                  ),
                ),
                const SizedBox(height: 12),
                TextField(
                  controller: descController,
                  decoration: const InputDecoration(
                    labelText: '题库描述',
                    hintText: '描述这个题库的用途',
                    border: OutlineInputBorder(),
                  ),
                ),
                const SizedBox(height: 12),
                DropdownButtonFormField<String>(
                  value: selectedSubject,
                  decoration: const InputDecoration(
                    labelText: '科目',
                    border: OutlineInputBorder(),
                  ),
                  items: ['数学', '语文', '英语', '物理', '化学', '生物', '历史', '地理']
                      .map((e) => DropdownMenuItem(value: e, child: Text(e)))
                      .toList(),
                  onChanged: (value) => setState(() => selectedSubject = value!),
                ),
                const SizedBox(height: 12),
                DropdownButtonFormField<Difficulty>(
                  value: selectedDifficulty,
                  decoration: const InputDecoration(
                    labelText: '难度',
                    border: OutlineInputBorder(),
                  ),
                  items: Difficulty.values
                      .map((e) => DropdownMenuItem(
                            value: e,
                            child: Text(_getDifficultyText(e)),
                          ))
                      .toList(),
                  onChanged: (value) => setState(() => selectedDifficulty = value!),
                ),
              ],
            ),
          ),
          actions: [
            TextButton(
              onPressed: () => Navigator.pop(context),
              child: Text(context.l10n.confirm),
            ),
            ElevatedButton(
              onPressed: () {
                if (nameController.text.isEmpty) {
                  ScaffoldMessenger.of(context).showSnackBar(
                    const SnackBar(content: Text('请输入题库名称')),
                  );
                  return;
                }

                final newSet = QuizSet(
                  name: nameController.text,
                  subject: selectedSubject,
                  description: descController.text,
                  difficulty: selectedDifficulty,
                  questionCount: 0,
                  estimatedTime: 10,
                  questions: [],
                );

                _quizService.addQuizSet(newSet);
                Navigator.pop(context);
                _loadData();
                
                ScaffoldMessenger.of(context).showSnackBar(
                  SnackBar(content: Text('已创建题库: ${nameController.text}')),
                );
              },
              child: const Text('创建'),
            ),
          ],
        ),
      ),
    );
  }

  void _showStatsDialog(BuildContext context) {
    final stats = _stats;
    
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('测验统计'),
        content: stats == null || stats.totalQuizzes == 0
            ? const Text('暂无测验数据')
            : SingleChildScrollView(
                child: Column(
                  mainAxisSize: MainAxisSize.min,
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    _buildStatsRow('已完成测验', '${stats.totalQuizzes}次'),
                    _buildStatsRow('累计答题', '${stats.totalQuestions}题'),
                    _buildStatsRow('平均正确率', '${stats.averageScore}%'),
                    _buildStatsRow('总用时', _formatTime(stats.totalTimeSpent)),
                    const Divider(),
                    const Text('按科目统计', style: TextStyle(fontWeight: FontWeight.bold)),
                    const SizedBox(height: 8),
                    ...stats.subjectStats.entries.map((e) {
                      final subjectStats = e.value;
                      return Padding(
                        padding: const EdgeInsets.only(bottom: 8),
                        child: Row(
                          mainAxisAlignment: MainAxisAlignment.spaceBetween,
                          children: [
                            Text(e.key),
                            Text('${subjectStats.averageScore.toInt()}% (${subjectStats.quizCount}次)'),
                          ],
                        ),
                      );
                    }),
                  ],
                ),
              ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: Text(context.l10n.confirm),
          ),
        ],
      ),
    );
  }

  Widget _buildStatsRow(String label, String value) {
    return Padding(
      padding: const EdgeInsets.only(bottom: 8),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.spaceBetween,
        children: [
          Text(label, style: const TextStyle(color: Colors.grey)),
          Text(value, style: const TextStyle(fontWeight: FontWeight.bold)),
        ],
      ),
    );
  }

  String _formatTime(int seconds) {
    final minutes = seconds ~/ 60;
    final secs = seconds % 60;
    return '${minutes}分${secs}秒';
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

  String _getDifficultyText(Difficulty difficulty) {
    switch (difficulty) {
      case Difficulty.easy:
        return '简单';
      case Difficulty.medium:
        return '中等';
      case Difficulty.hard:
        return '困难';
    }
  }
}
