/// 错题详情屏幕（简化版）
import 'package:flutter/material.dart';

class MistakeDetailScreen extends StatefulWidget {
  const MistakeDetailScreen({super.key});

  @override
  State<MistakeDetailScreen> createState() => _MistakeDetailScreenState();
}

class _MistakeDetailScreenState extends State<MistakeDetailScreen> {
  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: Text(l10n.$key)),
      body: const Center(child: Text(l10n.$key)),
    );
  }
}
