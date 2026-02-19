import 'package:flutter/material.dart';
import '../l10n/app_localizations.dart';
import '../extensions/l10n_extension.dart';
import '../models/task_model.dart';
import '../services/task_service.dart';
import '../services/streak_service.dart';

class HomeScreen extends StatefulWidget {
  const HomeScreen({super.key});

  @override
  State<HomeScreen> createState() => _HomeScreenState();
}

class _HomeScreenState extends State<HomeScreen> {
  final TaskService _taskService = TaskService();
  final StreakService _streakService = StreakService();
  List<Task> _todayTasks = [];
  bool _isLoading = true;
  int _streakDays = 0;
  Map<String, dynamic> _taskStats = {};

  int _selectedIndex = 0;

  @override
  void initState() {
    super.initState();
    _loadData();
  }

  Future<void> _loadData() async {
    final tasks = await _taskService.getTodayTasks();
    final streak = await _streakService.getStreakDays();
    final stats = await _taskService.getTaskStats();
    
    setState(() {
      _todayTasks = tasks;
      _streakDays = streak;
      _taskStats = stats;
      _isLoading = false;
    });
  }

  void _onItemTapped(int index) {
    setState(() {
      _selectedIndex = index;
    });
    switch (index) {
      case 0:
        _loadData(); // 刷新首页数据
        break;
      case 1:
        Navigator.pushNamed(context, '/tasks');
        break;
      case 2:
        Navigator.pushNamed(context, '/focus');
        break;
      case 3:
        Navigator.pushNamed(context, '/profile');
        break;
    }
  }

  void _completeTask(Task task) async {
    await _taskService.completeTask(task.id);
    _loadData(); // 刷新数据
    
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(content: Text('${context.l10n.taskCompleted}: ${task.title}')),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text(context.l10n.appTitle),
        actions: [
          IconButton(
            icon: const Icon(Icons.refresh),
            onPressed: _loadData,
            tooltip: context.l10n.refresh,
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
                  Card(
                    child: Padding(
                      padding: const EdgeInsets.all(16),
                      child: Column(
                        children: [
                          Row(
                            mainAxisAlignment: MainAxisAlignment.spaceAround,
                            children: [
                              _buildStatCard(context.l10n.todayTasksLabel, '${_todayTasks.length}', Icons.list),
                              _buildStatCard(context.l10n.streak, '$_streakDays', Icons.star),
                              _buildStatCard(context.l10n.completionRate, '${_taskStats['completionRate']}%', Icons.check_circle),
                            ],
                          ),
                          const SizedBox(height: 8),
                          Row(
                            mainAxisAlignment: MainAxisAlignment.spaceAround,
                            children: [
                              _buildStatCard(context.l10n.total, '${_taskStats['total']}', Icons.stacked_bar_chart),
                              _buildStatCard(context.l10n.completedTask, '${_taskStats['completed']}', Icons.done_all),
                              _buildStatCard(context.l10n.highPriority, '${_taskStats['highPriority']}', Icons.priority_high),
                            ],
                          ),
                        ],
                      ),
                    ),
                  ),
                  
                  const SizedBox(height: 16),
                  
                  // 今日任务标题
                  Row(
                    mainAxisAlignment: MainAxisAlignment.spaceBetween,
                    children: [
                      Text('${context.l10n.todayTasksLabel} (${_todayTasks.length})', 
                          style: const TextStyle(fontSize: 18, fontWeight: FontWeight.bold)),
                      if (_todayTasks.isNotEmpty)
                        TextButton(
                          onPressed: () {
                            // 一键完成今日任务
                            for (final task in _todayTasks) {
                              if (!task.isCompleted) {
                                _completeTask(task);
                              }
                            }
                          },
                          child: Text(context.l10n.confirm),
                        ),
                    ],
                  ),
                  
                  const SizedBox(height: 8),
                  
                  // 任务列表
                  if (_todayTasks.isEmpty)
                    Card(
                      child: Padding(
                        padding: const EdgeInsets.all(32),
                        child: Column(
                          children: [
                            const Icon(Icons.check_circle_outline, size: 64, color: Colors.green),
                            const SizedBox(height: 16),
                            Text(context.l10n.noTasksToday, style: const TextStyle(fontSize: 16)),
                            const SizedBox(height: 8),
                            Text(context.l10n.restOrAddTask, style: TextStyle(fontSize: 14, color: Colors.grey[600])),
                            const SizedBox(height: 16),
                            ElevatedButton(
                              onPressed: () => Navigator.pushNamed(context, '/tasks'),
                              child: Text(context.l10n.confirm),
                            ),
                          ],
                        ),
                      ),
                    )
                  else
                    ..._todayTasks.map((task) => Card(
                      child: ListTile(
                        leading: Container(
                          width: 8,
                          height: 8,
                          decoration: BoxDecoration(
                            color: task.priorityColor,
                            shape: BoxShape.circle,
                          ),
                        ),
                        title: Text(task.title),
                        subtitle: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            Text(task.description),
                            const SizedBox(height: 4),
                            Row(
                              children: [
                                Icon(Icons.access_time, size: 12, color: Colors.grey[600]),
                                const SizedBox(width: 4),
                                Text(
                                  '截止: ${task.dueTime.hour.toString().padLeft(2, '0')}:${task.dueTime.minute.toString().padLeft(2, '0')}',
                                  style: TextStyle(fontSize: 12, color: Colors.grey[600]),
                                ),
                                const SizedBox(width: 8),
                                Container(
                                  padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 2),
                                  decoration: BoxDecoration(
                                    color: task.priorityColor.withOpacity(0.1),
                                    borderRadius: BorderRadius.circular(4),
                                  ),
                                  child: Text(
                                    task.priorityText,
                                    style: TextStyle(fontSize: 10, color: task.priorityColor),
                                  ),
                                ),
                              ],
                            ),
                          ],
                        ),
                        trailing: task.isCompleted 
                            ? const Icon(Icons.check_circle, color: Colors.green, size: 24)
                            : IconButton(
                                icon: const Icon(Icons.check_circle_outline, size: 24),
                                color: Colors.grey[400],
                                onPressed: () => _completeTask(task),
                                tooltip: context.l10n.completedTask,
                              ),
                        onTap: () {
                          // 暂时用简单方式展示详情
                          showDialog(
                            context: context,
                            builder: (context) => AlertDialog(
                              title: Text(task.title),
                              content: SingleChildScrollView(
                                child: Column(
                                  crossAxisAlignment: CrossAxisAlignment.start,
                                  children: [
                                    Text(task.description),
                                    const SizedBox(height: 16),
                                    Text('优先级: ${task.priorityText}'),
                                    Text('截止时间: ${task.dueTime.toString()}'),
                                    Text('状态: ${task.isCompleted ? '已完成' : '未完成'}'),
                                    if (task.isCompleted)
                                      Text('完成时间: ${task.completedAt?.toString() ?? ''}'),
                                    const SizedBox(height: 8),
                                    Wrap(
                                      spacing: 4,
                                      children: task.tags.map((tag) => Chip(
                                        label: Text(tag),
                                        visualDensity: VisualDensity.compact,
                                      )).toList(),
                                    ),
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
                        },
                      ),
                    )).toList(),
                ],
              ),
            ),
      bottomNavigationBar: BottomNavigationBar(
        items: [
          BottomNavigationBarItem(icon: const Icon(Icons.home), label: context.l10n.home),
          BottomNavigationBarItem(icon: const Icon(Icons.list), label: context.l10n.tasks),
          BottomNavigationBarItem(icon: const Icon(Icons.timer), label: context.l10n.focusMode),
          BottomNavigationBarItem(icon: const Icon(Icons.person), label: context.l10n.profile),
        ],
        currentIndex: _selectedIndex,
        onTap: _onItemTapped,
        type: BottomNavigationBarType.fixed,
      ),
      floatingActionButton: FloatingActionButton(
        onPressed: () => _showAddTaskDialog(context),
        child: const Icon(Icons.add),
      ),
    );
  }

  Widget _buildStatCard(String title, String value, IconData icon) {
    return Column(
      children: [
        Icon(icon, size: 24, color: Colors.blue),
        const SizedBox(height: 4),
        Text(value, style: const TextStyle(fontSize: 16, fontWeight: FontWeight.bold)),
        Text(title, style: const TextStyle(fontSize: 12, color: Colors.grey)),
      ],
    );
  }

  void _showAddTaskDialog(BuildContext context) {
    
    final now = DateTime.now();
    final textController = TextEditingController();
    final descController = TextEditingController();
    int priority = 2;
    
    showDialog(
      context: context,
      builder: (context) => StatefulBuilder(
        builder: (context, setState) => AlertDialog(
          title: Text(context.l10n.confirm),
          content: SingleChildScrollView(
            child: Column(
              mainAxisSize: MainAxisSize.min,
              children: [
                TextField(
                  controller: textController,
                  decoration: const InputDecoration(
                    labelText: '任务标题',
                    hintText: '输入任务名称',
                    border: OutlineInputBorder(),
                  ),
                ),
                const SizedBox(height: 12),
                TextField(
                  controller: descController,
                  decoration: const InputDecoration(
                    labelText: '任务描述',
                    hintText: '输入任务描述',
                    border: OutlineInputBorder(),
                  ),
                ),
                const SizedBox(height: 12),
                const Text('优先级:', textAlign: TextAlign.left),
                Row(
                  mainAxisAlignment: MainAxisAlignment.spaceAround,
                  children: [
                    ChoiceChip(
                      label: Text(context.l10n.confirm),
                      selected: priority == 1,
                      onSelected: (selected) {
                        setState(() => priority = 1);
                      },
                    ),
                    ChoiceChip(
                      label: Text(context.l10n.confirm),
                      selected: priority == 2,
                      onSelected: (selected) {
                        setState(() => priority = 2);
                      },
                    ),
                    ChoiceChip(
                      label: Text(context.l10n.confirm),
                      selected: priority == 3,
                      onSelected: (selected) {
                        setState(() => priority = 3);
                      },
                    ),
                  ],
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
              onPressed: () async {
                if (textController.text.isEmpty) {
                  ScaffoldMessenger.of(context).showSnackBar(
                    SnackBar(content: Text(context.l10n.confirm)),
                  );
                  return;
                }
                
                final task = Task(
                  title: textController.text,
                  description: descController.text,
                  dueTime: DateTime(now.year, now.month, now.day, 19, 0),
                  priority: priority,
                );
                
                await _taskService.addTask(task);
                _loadData(); // 刷新数据
                
                Navigator.pop(context);
                
                ScaffoldMessenger.of(context).showSnackBar(
                  SnackBar(content: Text('已添加任务: ${task.title}')),
                );
              },
              child: Text(context.l10n.confirm),
            ),
          ],
        ),
      ),
    );
  }
}
