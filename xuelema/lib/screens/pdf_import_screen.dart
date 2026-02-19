/// PDF试卷导入界面（暂时禁用）
/// 当前状态：等待Flutter SDK升级到3.7.2+

/// TODO: SDK升级后恢复此功能
/// 当前pdf_import_service已禁用

import 'package:flutter/material.dart';
import '../l10n/app_localizations.dart';
import '../extensions/l10n_extension.dart';

class PdfImportScreen extends StatefulWidget {
  const PdfImportScreen({super.key});

  @override
  State<PdfImportScreen> createState() => _PdfImportScreenState();
}

class _PdfImportScreenState extends State<PdfImportScreen> {
  @override
  Widget build(BuildContext context) {
    
    return Scaffold(
      appBar: AppBar(
        title: const Text('PDF导入（暂时禁用）'),
      ),
      body: Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            const Icon(Icons.picture_as_pdf, size: 64, color: Colors.grey),
            const SizedBox(height: 16),
            const Text('PDF导入功能暂时禁用'),
            const SizedBox(height: 8),
            const Text('等待Flutter SDK升级到3.7.2+'),
            const SizedBox(height: 24),
            ElevatedButton(
              onPressed: () => Navigator.pop(context),
              child: Text(context.l10n.confirm),
            ),
          ],
        ),
      ),
    );
  }
}
