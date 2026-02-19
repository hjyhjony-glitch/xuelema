/// 专注屏幕（完整版）- 包含定时功能
import 'dart:async';
import 'package:flutter/material.dart';
import '../services/notification_service.dart';
import '../l10n/app_localizations.dart';

class FocusScreen extends StatefulWidget {
  const FocusScreen({super.key});

  @override
  State<FocusScreen> createState() => _FocusScreenState();
}

class _FocusScreenState extends State<FocusScreen> {
  Timer? _timer;
  bool _isRunning = false;
  int _timeLeft = 25 * 60; // 25分钟专注时间
  bool _isFocusMode = true; // true: 专注模式, false: 休息模式
  int _completedSessions = 0;

  @override
  void initState() {
    super.initState();
    _startTimer();
  }

  @override
  void dispose() {
    _timer?.cancel();
    super.dispose();
  }

  void _startTimer() {
    _timer = Timer.periodic(const Duration(seconds: 1), (timer) {
      if (!_isRunning) return;
      
      setState(() {
        if (_timeLeft > 0) {
          _timeLeft--;
        } else {
          // 时间到，切换模式
          _timerCompleted();
        }
      });
    });
  }

  void _timerCompleted() {
    _timer?.cancel();
    setState(() {
      _isRunning = false;
      
      if (_isFocusMode) {
        // 专注完成，进入休息模式
        _isFocusMode = false;
        _timeLeft = 5 * 60; // 5分钟休息
        _completedSessions++;
        
        // 显示完成提醒
        _showCompletionDialog();
        
        // 发送专注完成通知
        _sendFocusCompleteNotification();
      } else {
        // 休息完成，回到专注模式
        _isFocusMode = true;
        _timeLeft = 25 * 60; // 25分钟专注
      }
    });
    
    // 重新启动计时器
    _startTimer();
  }
  
  Future<void> _sendFocusCompleteNotification() async {
    final notificationService = NotificationService();
    await notificationService.showNotification(
      id: 1,
      title: '专注完成！',
      body: '你已经完成了 $_completedSessions 个番茄钟，休息一下吧！',
    );
  }

  void _showCompletionDialog() {
    WidgetsBinding.instance.addPostFrameCallback((_) {
      showDialog(
        context: context,
        builder: (context) => AlertDialog(
          title: const Text('专注完成！'),
          content: Text('你已经完成了 $_completedSessions 个番茄钟，休息一下吧！'),
          actions: [
            TextButton(
              onPressed: () => Navigator.pop(context),
              child: const Text('好的'),
            ),
          ],
        ),
      );
    });
  }

  void _toggleTimer() {
    setState(() {
      _isRunning = !_isRunning;
    });
  }

  void _resetTimer() {
    setState(() {
      _timer?.cancel();
      _isRunning = false;
      _isFocusMode = true;
      _timeLeft = 25 * 60;
      _startTimer();
    });
  }

  void _skipToNext() {
    setState(() {
      _timer?.cancel();
      _isFocusMode = !_isFocusMode;
      _timeLeft = _isFocusMode ? 25 * 60 : 5 * 60;
      _isRunning = false;
      _startTimer();
    });
  }

  @override
  Widget build(BuildContext context) {
    final minutes = _timeLeft ~/ 60;
    final seconds = _timeLeft % 60;
    final progress = _isFocusMode 
      ? 1.0 - (_timeLeft / (25 * 60))
      : 1.0 - (_timeLeft / (5 * 60));

    return Scaffold(
      appBar: AppBar(
        title: Text(_isFocusMode ? '专注模式' : '休息模式'),
        leading: IconButton(
          icon: const Icon(Icons.arrow_back),
          onPressed: () => Navigator.pop(context),
        ),
        actions: [
          IconButton(
            icon: const Icon(Icons.settings),
            onPressed: () {
              // 设置定时提醒
              _showTimerSettings(context);
            },
          ),
        ],
      ),
      body: Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            // 进度指示器
            SizedBox(
              width: 200,
              height: 200,
              child: Stack(
                alignment: Alignment.center,
                children: [
                  CircularProgressIndicator(
                    value: progress,
                    strokeWidth: 8,
                    backgroundColor: Colors.grey[200],
                    valueColor: AlwaysStoppedAnimation<Color>(
                      _isFocusMode ? Colors.blue : Colors.green,
                    ),
                  ),
                  Column(
                    mainAxisAlignment: MainAxisAlignment.center,
                    children: [
                      Text(
                        '${minutes.toString().padLeft(2, '0')}:${seconds.toString().padLeft(2, '0')}',
                        style: const TextStyle(fontSize: 48, fontWeight: FontWeight.bold),
                      ),
                      Text(
                        _isFocusMode ? '专注时间' : '休息时间',
                        style: TextStyle(
                          fontSize: 16,
                          color: Colors.grey[600],
                        ),
                      ),
                    ],
                  ),
                ],
              ),
            ),
            
            const SizedBox(height: 32),
            
            // 已完成番茄钟
            Text(
              '已完成: $_completedSessions 个番茄钟',
              style: const TextStyle(fontSize: 16),
            ),
            
            const SizedBox(height: 32),
            
            // 控制按钮
            Row(
              mainAxisAlignment: MainAxisAlignment.center,
              children: [
                ElevatedButton(
                  onPressed: _toggleTimer,
                  style: ElevatedButton.styleFrom(
                    padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 12),
                    backgroundColor: _isRunning ? Colors.orange : Colors.blue,
                  ),
                  child: Row(
                    children: [
                      Icon(_isRunning ? Icons.pause : Icons.play_arrow),
                      const SizedBox(width: 8),
                      Text(_isRunning ? '暂停' : '开始'),
                    ],
                  ),
                ),
                
                const SizedBox(width: 16),
                
                OutlinedButton(
                  onPressed: _resetTimer,
                  child: Row(
                    children: [
                      const Icon(Icons.refresh),
                      const SizedBox(width: 8),
                      Text(l10n.confirm),
                    ],
                  ),
                ),
              ],
            ),
            
            const SizedBox(height: 16),
            
            // 跳过按钮
            OutlinedButton(
              onPressed: _skipToNext,
              child: Row(
                mainAxisSize: MainAxisSize.min,
                children: [
                  const Icon(Icons.skip_next),
                  const SizedBox(width: 8),
                  Text(_isFocusMode ? '跳过专注' : '跳过休息'),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }

  void _showTimerSettings(BuildContext context) {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('定时提醒设置'),
        content: SizedBox(
          height: 200,
          child: Column(
            children: [
              ListTile(
                leading: const Icon(Icons.timer),
                title: Text(l10n.confirm),
                trailing: const Text('25分钟'),
                onTap: () {
                  _selectFocusDuration(context);
                },
              ),
              ListTile(
                leading: const Icon(Icons.coffee),
                title: const Text('休息时长'),
                trailing: const Text('5分钟'),
                onTap: () {
                  // 简化实现
                  ScaffoldMessenger.of(context).showSnackBar(
                    const SnackBar(content: Text('休息时长设置功能将在后续版本中添加')),
                  );
                },
              ),
              ListTile(
                leading: const Icon(Icons.notifications),
                title: const Text('提醒声音'),
                trailing: const Text('默认'),
                onTap: () {
                  // 简化实现
                  ScaffoldMessenger.of(context).showSnackBar(
                    const SnackBar(content: Text('提醒声音功能将在后续版本中添加')),
                  );
                },
              ),
            ],
          ),
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: Text(l10n.confirm),
          ),
          ElevatedButton(
            onPressed: () {
              Navigator.pop(context);
              ScaffoldMessenger.of(context).showSnackBar(
                const SnackBar(content: Text('定时提醒设置已保存')),
              );
            },
            child: Text(l10n.confirm),
          ),
        ],
      ),
    );
  }

  void _selectFocusDuration(BuildContext context) {
    showModalBottomSheet(
      context: context,
      builder: (context) => SizedBox(
        height: 300,
        child: Column(
          children: [
            Padding(
              padding: const EdgeInsets.all(16.0),
              child: Text(
                '选择专注时长',
                style: Theme.of(context).textTheme.titleLarge,
              ),
            ),
            Expanded(
              child: ListView(
                children: [5, 10, 15, 20, 25, 30, 45, 60].map((minutes) {
                  return ListTile(
                    title: Text('$minutes 分钟'),
                    onTap: () {
                      Navigator.pop(context);
                      setState(() {
                        _timeLeft = minutes * 60;
                        _isFocusMode = true;
                      });
                    },
                  );
                }).toList(),
              ),
            ),
          ],
        ),
      ),
    );
  }
}