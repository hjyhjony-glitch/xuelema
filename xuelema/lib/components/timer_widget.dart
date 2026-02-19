import 'package:flutter/material.dart';
import '../config/theme.dart';
import '../l10n/app_localizations.dart';

class TimerWidget extends StatefulWidget {
  final int totalSeconds;
  final int remainingSeconds;
  final bool isRunning;
  final bool isFocusMode;
  final VoidCallback? onStart;
  final VoidCallback? onPause;
  final VoidCallback? onReset;
  final VoidCallback? onSkip;

  const TimerWidget({
    super.key,
    required this.totalSeconds,
    required this.remainingSeconds,
    required this.isRunning,
    required this.isFocusMode,
    this.onStart,
    this.onPause,
    this.onReset,
    this.onSkip,
  });

  @override
  State<TimerWidget> createState() => _TimerWidgetState();
}

class _TimerWidgetState extends State<TimerWidget> {
  @override
  Widget build(BuildContext context) {
    final progress = widget.remainingSeconds / widget.totalSeconds;
    final color = widget.isFocusMode ? AppTheme.focusColor : AppTheme.restColor;

    return Column(
      mainAxisAlignment: MainAxisAlignment.center,
      children: [
        // 进度圆环
        SizedBox(
          width: 200,
          height: 200,
          child: Stack(
            alignment: Alignment.center,
            children: [
              // 背景
              SizedBox(
                width: 190,
                height: 190,
                child: CircularProgressIndicator(
                  value: 1,
                  strokeWidth: 10,
                  valueColor: AlwaysStoppedAnimation<Color>(color.withOpacity(0.2)),
                ),
              ),
              // 进度
              SizedBox(
                width: 190,
                height: 190,
                child: CircularProgressIndicator(
                  value: progress,
                  strokeWidth: 10,
                  valueColor: AlwaysStoppedAnimation<Color>(color),
                  backgroundColor: Colors.transparent,
                ),
              ),
              // 时间显示
              Column(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  Text(
                    _formatTime(widget.remainingSeconds),
                    style: const TextStyle(
                      fontSize: 48,
                      fontWeight: FontWeight.bold,
                      fontFamily: 'monospace',
                    ),
                  ),
                  const SizedBox(height: 8),
                  Text(
                    widget.isFocusMode ? '专注时间' : '休息时间',
                    style: TextStyle(
                      fontSize: 14,
                      color: Colors.grey[600],
                    ),
                  ),
                ],
              ),
            ],
          ),
        ),
        
        const SizedBox(height: 32),
        
        // 控制按钮
        Row(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            // 重置
            SizedBox(
              width: 50,
              height: 50,
              child: IconButton(
                icon: const Icon(Icons.refresh),
                onPressed: widget.onReset,
                style: IconButton.styleFrom(
                  backgroundColor: Colors.grey[200],
                ),
              ),
            ),
            const SizedBox(width: 20),
            // 开始/暂停
            SizedBox(
              width: 80,
              height: 80,
              child: ElevatedButton(
                onPressed: widget.isRunning ? widget.onPause : widget.onStart,
                style: ElevatedButton.styleFrom(
                  shape: const CircleBorder(),
                  backgroundColor: color,
                  elevation: 4,
                ),
                child: Icon(
                  widget.isRunning ? Icons.pause : Icons.play_arrow,
                  size: 36,
                  color: Colors.white,
                ),
              ),
            ),
            const SizedBox(width: 20),
            // 跳过
            SizedBox(
              width: 50,
              height: 50,
              child: IconButton(
                icon: const Icon(Icons.skip_next),
                onPressed: widget.onSkip,
                style: IconButton.styleFrom(
                  backgroundColor: Colors.grey[200],
                ),
              ),
            ),
          ],
        ),
      ],
    );
  }

  String _formatTime(int seconds) {
    final mins = seconds ~/ 60;
    final secs = seconds % 60;
    return '${mins.toString().padLeft(2, '0')}:${secs.toString().padLeft(2, '0')}';
  }
}
