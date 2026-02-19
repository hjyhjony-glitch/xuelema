/// 错题详情屏幕（简化版）
import 'package:flutter/material.dart';
import '../l10n/app_localizations.dart';

class MistakeDetailScreen extends StatefulWidget {
  const MistakeDetailScreen({super.key});

  @override
  State<MistakeDetailScreen> createState() => _MistakeDetailScreenState();
}

class _MistakeDetailScreenState extends State<MistakeDetailScreen> {
  @override
  Widget build(BuildContext context) {
    final l10n = AppLocalizations.of(context);
    return Scaffold(
      appBar: AppBar(title: Text(l10n.confirm)),
      body: const Center(child: Text(l10n.confirm)),
    );
  }
}
