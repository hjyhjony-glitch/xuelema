import 'package:flutter/material.dart';
import '../models/task_model.dart';
import '../l10n/app_localizations.dart';

class TaskDetailScreen extends StatefulWidget {
  final Task task;

  const TaskDetailScreen({super.key, required this.task});

  @override
  State<TaskDetailScreen> createState() => _TaskDetailScreenState();
}

class _TaskDetailScreenState extends State<TaskDetailScreen> {
  @override
  Widget build(BuildContext context) {
    final l10n = AppLocalizations.of(context);
    final task = widget.task;

    return Scaffold(
      appBar: AppBar(title: Text(l10n.confirm)),
      body: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(task.title, style: const TextStyle(fontSize: 24, fontWeight: FontWeight.bold)),
            const SizedBox(height: 16),
            if (task.description.isNotEmpty)
              Text(task.description, style: const TextStyle(fontSize: 16)),
            const SizedBox(height: 24),
            Text('截止时间: ${task.dueTime}'),
            const SizedBox(height: 8),
            Text('优先级: ${task.priority}'),
            const SizedBox(height: 24),
            Row(
              children: [
                ElevatedButton(
                  onPressed: () {},
                  child: Text(l10n.confirm),
                ),
                const SizedBox(width: 16),
                OutlinedButton(
                  onPressed: () => Navigator.pop(context),
                  child: Text(l10n.confirm),
                ),
              ],
            ),
          ],
        ),
      ),
    );
  }
}
