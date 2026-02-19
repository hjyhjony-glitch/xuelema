import 'package:flutter/material.dart';
import 'ocr_screen.dart';
import '../l10n/app_localizations.dart';

/// OCR快捷按钮组件
class OcrButton extends StatelessWidget {
  const OcrButton({super.key});

  @override
  Widget build(BuildContext context) {
    return Card(
      elevation: 2,
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
      child: InkWell(
        onTap: () {
          Navigator.push(
            context,
            MaterialPageRoute(builder: (context) => const OcrScreen()),
          );
        },
        borderRadius: BorderRadius.circular(12),
        child: const Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(
              Icons.text_fields,
              size: 40,
              color: Color(0xFF66BB6A),
            ),
            SizedBox(height: 12),
            Text(
              '文字识别',
              style: TextStyle(
                fontSize: 16,
                fontWeight: FontWeight.w500,
              ),
            ),
          ],
        ),
      ),
    );
  }
}
