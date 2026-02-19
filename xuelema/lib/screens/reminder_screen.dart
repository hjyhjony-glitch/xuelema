/// 定时提醒设置屏幕 - 管理各种定时提醒功能
import 'package:flutter/material.dart';
import 'package:flutter_local_notifications/flutter_local_notifications.dart';
import '../l10n/app_localizations.dart';
import '../services/notification_service.dart';

class ReminderScreen extends StatefulWidget {
  const ReminderScreen({super.key});

  @override
  State<ReminderScreen> createState() => _ReminderScreenState();
}

class _ReminderScreenState extends State<ReminderScreen> {
  final NotificationService _notificationService = NotificationService();
  
  // 每日提醒设置
  bool _dailyMorningReminder = true;
  bool _dailyEveningReminder = true;
  bool _dailyBedtimeReminder = true;
  
  // 任务提醒设置
  bool _taskReminderEnabled = true;
  int _taskReminderMinutesBefore = 30;
  
  // 专注提醒设置
  bool _focusCompleteReminder = true;
  
  // 复习提醒设置
  bool _reviewReminderEnabled = true;
  TimeOfDay _reviewReminderTime = const TimeOfDay(hour: 20, minute: 0);
  
  @override
  void initState() {
    super.initState();
    _loadSettings();
  }
  
  Future<void> _loadSettings() async {
    // 这里可以添加从SharedPreferences加载设置的逻辑
    // 暂时使用默认值
  }
  
  Future<void> _saveSettings() async {
    // 这里可以添加保存到SharedPreferences的逻辑
    await _applyReminderChanges();
    
    ScaffoldMessenger.of(context).showSnackBar(
      const SnackBar(content: Text('提醒设置已保存')),
    );
  }
  
  Future<void> _applyReminderChanges() async {
    // 取消所有现有提醒
    await _notificationService.cancelAllNotifications();
    
    // 根据设置重新安排提醒
    if (_dailyMorningReminder) {
      await _notificationService.scheduleDailyNotification(
        id: 1,
        title: '学习时间到！',
        body: '新的一天，开始今天的学习计划吧！',
        time: const TimeOfDay(hour: 8, minute: 0),
        payload: 'daily_morning',
      );
    }
    
    if (_dailyEveningReminder) {
      await _notificationService.scheduleDailyNotification(
        id: 2,
        title: '复习时间',
        body: '别忘了复习今天学习的内容',
        time: const TimeOfDay(hour: 20, minute: 0),
        payload: 'daily_evening',
      );
    }
    
    if (_dailyBedtimeReminder) {
      await _notificationService.scheduleDailyNotification(
        id: 3,
        title: '睡前总结',
        body: '总结今天的学习成果，计划明天的学习任务',
        time: const TimeOfDay(hour: 22, minute: 0),
        payload: 'daily_bedtime',
      );
    }
    
    if (_reviewReminderEnabled) {
      await _notificationService.scheduleDailyNotification(
        id: 4,
        title: l10n.dailyReminder,
        body: '及时复习能更好地记住知识',
        time: _reviewReminderTime,
        payload: 'review',
      );
    }
    
    // print('提醒设置已应用');
  }
  
  Future<void> _testNotification() async {
    await _notificationService.showNotification(
      id: 9999,
      title: '测试提醒',
      body: '这是一个测试通知，说明提醒功能正常工作！',
      payload: 'test',
    );
    
    ScaffoldMessenger.of(context).showSnackBar(
      const SnackBar(content: Text('测试通知已发送')),
    );
  }
  
  Future<void> _viewPendingNotifications() async {
    final notifications = await _notificationService.getPendingNotifications();
    
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('已计划的提醒'),
        content: SizedBox(
          height: 300,
          width: 300,
          child: notifications.isEmpty
            ? const Center(child: Text('没有已计划的提醒'))
            : ListView.builder(
                itemCount: notifications.length,
                itemBuilder: (context, index) {
                  final notif = notifications[index];
                  return ListTile(
                    title: Text(notif.title ?? '无标题'),
                    subtitle: Text(notif.body ?? '无内容'),
                    trailing: Text(notif.payload ?? ''),
                  );
                },
              ),
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: Text(l10n.confirm),
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
        title: Text(l10n.reminderSettings),
        leading: IconButton(
          icon: const Icon(Icons.arrow_back),
          onPressed: () => Navigator.pop(context),
        ),
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // 每日提醒设置
            _buildSectionTitle('每日提醒'),
            Card(
              child: Column(
                children: [
                  _buildSwitchTile(
                    title: '早上8:00学习提醒',
                    subtitle: '提醒开始今天的学习计划',
                    value: _dailyMorningReminder,
                    onChanged: (value) => setState(() => _dailyMorningReminder = value),
                  ),
                  const Divider(height: 1),
                  _buildSwitchTile(
                    title: '晚上8:00复习提醒',
                    subtitle: '提醒复习今天学习的内容',
                    value: _dailyEveningReminder,
                    onChanged: (value) => setState(() => _dailyEveningReminder = value),
                  ),
                  const Divider(height: 1),
                  _buildSwitchTile(
                    title: '晚上10:00睡前提醒',
                    subtitle: '总结学习成果，计划明天任务',
                    value: _dailyBedtimeReminder,
                    onChanged: (value) => setState(() => _dailyBedtimeReminder = value),
                  ),
                ],
              ),
            ),
            
            const SizedBox(height: 16),
            
            // 任务提醒设置
            _buildSectionTitle('任务提醒'),
            Card(
              child: Column(
                children: [
                  _buildSwitchTile(
                    title: '任务截止提醒',
                    subtitle: '任务截止前30分钟提醒',
                    value: _taskReminderEnabled,
                    onChanged: (value) => setState(() => _taskReminderEnabled = value),
                  ),
                  const Divider(height: 1),
                  Padding(
                    padding: const EdgeInsets.all(16),
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        const Text('提醒提前时间'),
                        Slider(
                          value: _taskReminderMinutesBefore.toDouble(),
                          min: 5,
                          max: 120,
                          divisions: 23,
                          label: '${_taskReminderMinutesBefore}分钟',
                          onChanged: _taskReminderEnabled ? (value) {
                            setState(() => _taskReminderMinutesBefore = value.toInt());
                          } : null,
                        ),
                        Text(
                          '任务截止前$_taskReminderMinutesBefore分钟提醒',
                          style: TextStyle(color: Colors.grey[600], fontSize: 12),
                        ),
                      ],
                    ),
                  ),
                ],
              ),
            ),
            
            const SizedBox(height: 16),
            
            // 复习提醒设置
            _buildSectionTitle('复习提醒'),
            Card(
              child: Column(
                children: [
                  _buildSwitchTile(
                    title: '每日复习提醒',
                    subtitle: '提醒复习错题和知识点',
                    value: _reviewReminderEnabled,
                    onChanged: (value) => setState(() => _reviewReminderEnabled = value),
                  ),
                  const Divider(height: 1),
                  if (_reviewReminderEnabled)
                    _buildTimeTile(
                      title: '提醒时间',
                      time: _reviewReminderTime,
                      onTap: () => _selectTime(context),
                    ),
                ],
              ),
            ),
            
            const SizedBox(height: 16),
            
            // 专注提醒设置
            _buildSectionTitle('专注提醒'),
            Card(
              child: _buildSwitchTile(
                title: '专注完成提醒',
                subtitle: '专注时间结束后提醒休息',
                value: _focusCompleteReminder,
                onChanged: (value) => setState(() => _focusCompleteReminder = value),
              ),
            ),
            
            const SizedBox(height: 24),
            
            // 功能按钮
            Row(
              children: [
                Expanded(
                  child: OutlinedButton.icon(
                    onPressed: _testNotification,
                    icon: const Icon(Icons.notifications),
                    label: const Text('测试通知'),
                  ),
                ),
                const SizedBox(width: 12),
                Expanded(
                  child: OutlinedButton.icon(
                    onPressed: _viewPendingNotifications,
                    icon: const Icon(Icons.list),
                    label: const Text('查看计划'),
                  ),
                ),
              ],
            ),
            
            const SizedBox(height: 12),
            
            Row(
              children: [
                Expanded(
                  child: OutlinedButton.icon(
                    onPressed: () => _notificationService.cancelAllNotifications(),
                    icon: const Icon(Icons.cancel),
                    label: const Text('取消所有'),
                  ),
                ),
                const SizedBox(width: 12),
                Expanded(
                  child: OutlinedButton.icon(
                    onPressed: () => _notificationService.setupDefaultReminders(),
                    icon: const Icon(Icons.restore),
                    label: const Text('恢复默认'),
                  ),
                ),
              ],
            ),
            
            const SizedBox(height: 24),
            
            // 保存按钮
            ElevatedButton.icon(
              onPressed: _saveSettings,
              icon: const Icon(Icons.save),
              label: const Text('保存设置'),
              style: ElevatedButton.styleFrom(
                minimumSize: const Size(double.infinity, 48),
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
  
  Widget _buildSwitchTile({
    required String title,
    required String subtitle,
    required bool value,
    required ValueChanged<bool> onChanged,
  }) {
    return SwitchListTile(
      title: Text(title, style: const TextStyle(fontWeight: FontWeight.w500)),
      subtitle: Text(subtitle, style: TextStyle(color: Colors.grey[600])),
      value: value,
      onChanged: onChanged,
    );
  }
  
  Widget _buildTimeTile({
    required String title,
    required TimeOfDay time,
    required VoidCallback onTap,
  }) {
    return ListTile(
      title: Text(title),
      subtitle: Text('${time.hour.toString().padLeft(2, '0')}:${time.minute.toString().padLeft(2, '0')}'),
      trailing: const Icon(Icons.chevron_right),
      onTap: onTap,
    );
  }
  
  Future<void> _selectTime(BuildContext context) async {
    final TimeOfDay? picked = await showTimePicker(
      context: context,
      initialTime: _reviewReminderTime,
    );
    
    if (picked != null) {
      setState(() => _reviewReminderTime = picked);
    }
  }
}