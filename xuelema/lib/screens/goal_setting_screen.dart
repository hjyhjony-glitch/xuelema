/// 目标设置屏幕 - 完整的学习目标管理功能
import 'package:flutter/material.dart';
import 'package:shared_preferences/shared_preferences.dart';
import '../l10n/app_localizations.dart';

class GoalSettingScreen extends StatefulWidget {
  const GoalSettingScreen({super.key});

  @override
  State<GoalSettingScreen> createState() => _GoalSettingScreenState();
}

class _GoalSettingScreenState extends State<GoalSettingScreen> {
  // 学习目标
  int _dailyStudyMinutes = 60;
  int _weeklyTasks = 10;
  int _dailyFocusSessions = 3;
  
  // 专注时长目标
  int _focusSessionMinutes = 25;
  
  // 复习目标
  int _dailyReviewQuestions = 20;
  
  // 提醒设置
  bool _morningReminder = true;
  bool _eveningReminder = true;
  bool _weekendReview = true;

  @override
  void initState() {
    super.initState();
    _loadSettings();
  }

  Future<void> _loadSettings() async {
    final prefs = await SharedPreferences.getInstance();
    setState(() {
      _dailyStudyMinutes = prefs.getInt('dailyStudyMinutes') ?? 60;
      _weeklyTasks = prefs.getInt('weeklyTasks') ?? 10;
      _dailyFocusSessions = prefs.getInt('dailyFocusSessions') ?? 3;
      _focusSessionMinutes = prefs.getInt('focusSessionMinutes') ?? 25;
      _dailyReviewQuestions = prefs.getInt('dailyReviewQuestions') ?? 20;
      _morningReminder = prefs.getBool('morningReminder') ?? true;
      _eveningReminder = prefs.getBool('eveningReminder') ?? true;
      _weekendReview = prefs.getBool('weekendReview') ?? true;
    });
  }

  Future<void> _saveSettings() async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.setInt('dailyStudyMinutes', _dailyStudyMinutes);
    await prefs.setInt('weeklyTasks', _weeklyTasks);
    await prefs.setInt('dailyFocusSessions', _dailyFocusSessions);
    await prefs.setInt('focusSessionMinutes', _focusSessionMinutes);
    await prefs.setInt('dailyReviewQuestions', _dailyReviewQuestions);
    await prefs.setBool('morningReminder', _morningReminder);
    await prefs.setBool('eveningReminder', _eveningReminder);
    await prefs.setBool('weekendReview', _weekendReview);
    
    ScaffoldMessenger.of(context).showSnackBar(
      const SnackBar(content: Text('目标设置已保存')),
    );
  }

  void _resetToDefaults() {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('恢复默认设置'),
        content: const Text('确定要恢复默认目标设置吗？'),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: Text(l10n.confirm),
          ),
          ElevatedButton(
            onPressed: () {
              setState(() {
                _dailyStudyMinutes = 60;
                _weeklyTasks = 10;
                _dailyFocusSessions = 3;
                _focusSessionMinutes = 25;
                _dailyReviewQuestions = 20;
                _morningReminder = true;
                _eveningReminder = true;
                _weekendReview = true;
              });
              Navigator.pop(context);
              _saveSettings();
            },
            child: const Text('恢复'),
          ),
        ],
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    final l10n = AppLocalizations.of(context);
    
    return Scaffold(
      appBar: AppBar(
        title: Text(l10n.goalSetting),
        actions: [
          TextButton(
            onPressed: _resetToDefaults,
            child: const Text('恢复默认'),
          ),
          ElevatedButton(
            onPressed: _saveSettings,
            child: Text(l10n.confirm),
          ),
        ],
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // 学习目标
            _buildSectionTitle('学习目标'),
            Card(
              child: Column(
                children: [
                  _buildSliderTile(
                    title: '每日学习时长',
                    value: _dailyStudyMinutes,
                    unit: '分钟',
                    min: 15,
                    max: 240,
                    divisions: 45,
                    onChanged: (value) => setState(() => _dailyStudyMinutes = value),
                  ),
                  const Divider(height: 1),
                  _buildSliderTile(
                    title: '每周完成任务',
                    value: _weeklyTasks,
                    unit: '个',
                    min: 3,
                    max: 30,
                    divisions: 27,
                    onChanged: (value) => setState(() => _weeklyTasks = value),
                  ),
                ],
              ),
            ),
            
            const SizedBox(height: 16),
            
            // 专注目标
            _buildSectionTitle('专注目标'),
            Card(
              child: Column(
                children: [
                  _buildSliderTile(
                    title: '每日专注次数',
                    value: _dailyFocusSessions,
                    unit: '次',
                    min: 1,
                    max: 10,
                    divisions: 9,
                    onChanged: (value) => setState(() => _dailyFocusSessions = value),
                  ),
                  const Divider(height: 1),
                  _buildSliderTile(
                    title: '单次专注时长',
                    value: _focusSessionMinutes,
                    unit: '分钟',
                    min: 15,
                    max: 60,
                    divisions: 9,
                    onChanged: (value) => setState(() => _focusSessionMinutes = value),
                  ),
                ],
              ),
            ),
            
            const SizedBox(height: 16),
            
            // 复习目标
            _buildSectionTitle('复习目标'),
            Card(
              child: _buildSliderTile(
                title: '每日复习题数',
                value: _dailyReviewQuestions,
                unit: '题',
                min: 5,
                max: 50,
                divisions: 45,
                onChanged: (value) => setState(() => _dailyReviewQuestions = value),
              ),
            ),
            
            const SizedBox(height: 16),
            
            // 提醒设置
            _buildSectionTitle('提醒设置'),
            Card(
              child: Column(
                children: [
                  _buildSwitchTile(
                    title: '早上学习提醒',
                    subtitle: '每天早上提醒开始学习',
                    value: _morningReminder,
                    onChanged: (value) => setState(() => _morningReminder = value),
                  ),
                  const Divider(height: 1),
                  _buildSwitchTile(
                    title: '晚上复习提醒',
                    subtitle: '每天晚上提醒复习',
                    value: _eveningReminder,
                    onChanged: (value) => setState(() => _eveningReminder = value),
                  ),
                  const Divider(height: 1),
                  _buildSwitchTile(
                    title: '周末复习提醒',
                    subtitle: '周末提醒进行系统复习',
                    value: _weekendReview,
                    onChanged: (value) => setState(() => _weekendReview = value),
                  ),
                ],
              ),
            ),
            
            const SizedBox(height: 24),
            
            // 当前目标总结
            Card(
              color: Colors.blue.withOpacity(0.1),
              child: Padding(
                padding: const EdgeInsets.all(16),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Row(
                      children: [
                        Icon(Icons.flag, color: Colors.blue),
                        const SizedBox(width: 8),
                        const Text(
                          '今日目标进度',
                          style: TextStyle(
                            fontSize: 16,
                            fontWeight: FontWeight.bold,
                          ),
                        ),
                      ],
                    ),
                    const SizedBox(height: 12),
                    _buildProgressRow('已完成专注', '2/$_dailyFocusSessions', 0.67),
                    _buildProgressRow('今日学习', '30/$_dailyStudyMinutes 分钟', 0.5),
                    _buildProgressRow('已复习', '8/$_dailyReviewQuestions 题', 0.4),
                  ],
                ),
              ),
            ),
            
            const SizedBox(height: 24),
            
            // 保存按钮
            SizedBox(
              width: double.infinity,
              child: ElevatedButton.icon(
                onPressed: _saveSettings,
                icon: const Icon(Icons.save),
                label: const Text('保存设置'),
                style: ElevatedButton.styleFrom(
                  padding: const EdgeInsets.symmetric(vertical: 16),
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildSectionTitle(String title) {
    return Padding(
      padding: const EdgeInsets.only(bottom: 8),
      child: Text(
        title,
        style: const TextStyle(
          fontSize: 16,
          fontWeight: FontWeight.w600,
          color: Colors.blue,
        ),
      ),
    );
  }

  Widget _buildSliderTile({
    required String title,
    required int value,
    required String unit,
    required int min,
    required int max,
    required int divisions,
    required ValueChanged<int> onChanged,
  }) {
    return Padding(
      padding: const EdgeInsets.all(16),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Text(title),
              Text(
                '$value $unit',
                style: const TextStyle(
                  fontWeight: FontWeight.bold,
                  color: Colors.blue,
                ),
              ),
            ],
          ),
          Slider(
            value: value.toDouble(),
            min: min.toDouble(),
            max: max.toDouble(),
            divisions: divisions,
            label: '$value',
            onChanged: (v) => onChanged(v.toInt()),
          ),
        ],
      ),
    );
  }

  Widget _buildSwitchTile({
    required String title,
    required String subtitle,
    required bool value,
    required ValueChanged<bool> onChanged,
  }) {
    return SwitchListTile(
      title: Text(title),
      subtitle: Text(subtitle),
      value: value,
      onChanged: onChanged,
    );
  }

  Widget _buildProgressRow(String label, String value, double progress) {
    return Padding(
      padding: const EdgeInsets.only(bottom: 8),
      child: Row(
        children: [
          SizedBox(
            width: 100,
            child: Text(label, style: const TextStyle(fontSize: 14)),
          ),
          Expanded(
            child: LinearProgressIndicator(
              value: progress,
              minHeight: 8,
              backgroundColor: Colors.white,
            ),
          ),
          const SizedBox(width: 12),
          SizedBox(
            width: 60,
            child: Text(
              value,
              style: const TextStyle(fontSize: 12),
              textAlign: TextAlign.end,
            ),
          ),
        ],
      ),
    );
  }
}