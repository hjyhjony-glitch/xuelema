/// 错题详情屏幕（简化版）
import 'package:flutter/material.dart';
import '../l10n/app_localizations.dart';
import '../extensions/l10n_extension.dart';

class MistakeDetailScreen extends StatefulWidget {
  const MistakeDetailScreen({super.key});

  @override
  State<MistakeDetailScreen> createState() => _MistakeDetailScreenState();
}

class _MistakeDetailScreenState extends State<MistakeDetailScreen> {
  @override
  Widget build(BuildContext context) {
    
    return Scaffold(
      appBar: AppBar(title: Text(context.l10n.confirm)),
      body: const Center(child: Text(context.l10n.confirm)),
    );
  }
}
