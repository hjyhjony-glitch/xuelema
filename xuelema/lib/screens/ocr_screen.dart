/// OCR屏幕（简化版）
import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import '../l10n/app_localizations.dart';
import '../extensions/l10n_extension.dart';

class OcrScreen extends StatefulWidget {
  const OcrScreen({super.key});

  @override
  State<OcrScreen> createState() => _OcrScreenState();
}

class _OcrScreenState extends State<OcrScreen> {
  String _result = '';

  @override
  Widget build(BuildContext context) {
    
    return Scaffold(
      appBar: AppBar(title: Text(context.l10n.confirm)),
      body: Column(
        children: [
          Expanded(
            child: Container(
              margin: const EdgeInsets.all(16),
              padding: const EdgeInsets.all(16),
              decoration: BoxDecoration(
                border: Border.all(color: Colors.grey),
                borderRadius: BorderRadius.circular(8),
              ),
              child: _result.isEmpty
                  ? const Center(child: Text('请选择图片或输入文字'))
                  : Text(_result),
            ),
          ),
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceEvenly,
            children: [
              ElevatedButton.icon(
                onPressed: () {},
                icon: const Icon(Icons.camera_alt),
                label: Text(context.l10n.confirm),
              ),
              ElevatedButton.icon(
                onPressed: () {},
                icon: const Icon(Icons.image),
                label: Text(context.l10n.confirm),
              ),
              ElevatedButton.icon(
                onPressed: () {},
                icon: const Icon(Icons.content_paste),
                label: Text(context.l10n.confirm),
              ),
            ],
          ),
          const SizedBox(height: 16),
        ],
      ),
    );
  }
}
