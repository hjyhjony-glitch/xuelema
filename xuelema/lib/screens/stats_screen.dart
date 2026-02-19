/// 统计数据页面（简化版）
import 'package:flutter/material.dart';
import '../l10n/app_localizations.dart';
import '../extensions/l10n_extension.dart';

class StatsScreen extends StatefulWidget {
  const StatsScreen({super.key});

  @override
  State<StatsScreen> createState() => _StatsScreenState();
}

class _StatsScreenState extends State<StatsScreen> {
  @override
  Widget build(BuildContext context) {
    
    return Scaffold(
      appBar: AppBar(title: Text(context.l10n.confirm)),
      body: const Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(Icons.bar_chart, size: 64),
            SizedBox(height: 16),
            Text('统计数据'),
          ],
        ),
      ),
    );
  }
}
