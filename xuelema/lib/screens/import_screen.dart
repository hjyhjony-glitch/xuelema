/// 批量导入界面（简化版）
import 'dart:io';
import 'package:flutter/material.dart';
import '../l10n/app_localizations.dart';
import '../extensions/l10n_extension.dart';
import 'package:file_picker/file_picker.dart';

class ImportScreen extends StatefulWidget {
  const ImportScreen({super.key});

  @override
  State<ImportScreen> createState() => _ImportScreenState();
}

class _ImportScreenState extends State<ImportScreen> {
  File? _selectedFile;
  bool _isImporting = false;

  @override
  Widget build(BuildContext context) {
    
    
    return Scaffold(
      appBar: AppBar(title: Text(context.l10n.importTitle)),
      body: Padding(
        padding: EdgeInsets.all(16),
        child: Column(
          children: [
            if (_selectedFile != null)
              Card(
                child: ListTile(
                  leading: Icon(Icons.file_present),
                  title: Text(_selectedFile!.path.split('/').last),
                  trailing: IconButton(
                    icon: Icon(Icons.close),
                    onPressed: () => setState(() => _selectedFile = null),
                  ),
                ),
              ),
            SizedBox(height: 16),
            ElevatedButton.icon(
              onPressed: _pickFile,
              icon: Icon(Icons.folder_open),
              label: Text(context.l10n.selectFileButton),
            ),
            SizedBox(height: 16),
            if (_isImporting) CircularProgressIndicator(),
          ],
        ),
      ),
    );
  }

  Future<void> _pickFile() async {
    setState(() => _isImporting = true);
    try {
      final result = await FilePicker.platform.pickFiles();
      if (result != null) {
        setState(() {
          _selectedFile = File(result.files.single.path!);
        });
      }
    } catch (e) {
      if (context.mounted) {
        ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text('导入失败: $e')));
      }
    } finally {
      setState(() => _isImporting = false);
    }
  }
}
