/// 错题本屏幕（简化版）
import 'package:flutter/material.dart';
import '../l10n/app_localizations.dart';
import '../models/mistake_model.dart';

class MistakeScreen extends StatefulWidget {
  const MistakeScreen({super.key});

  @override
  State<MistakeScreen> createState() => _MistakeScreenState();
}

class _MistakeScreenState extends State<MistakeScreen> {
  @override
  Widget build(BuildContext context) {
    final l10n = AppLocalizations.of(context);
    
    return Scaffold(
      appBar: AppBar(title: Text(l10n.mistakeBook)),
      body: Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            const Icon(Icons.book, size: 64, color: Colors.grey),
            const SizedBox(height: 16),
            Text(l10n.noQuestions, style: const TextStyle(fontSize: 16, color: Colors.grey)),
          ],
        ),
      ),
    );
  }
}
