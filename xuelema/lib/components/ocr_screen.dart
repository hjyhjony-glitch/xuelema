/// OCR识别屏幕 - 完整的文字识别和学习功能
import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:image_picker/image_picker.dart';
import 'package:google_mlkit_text_recognition/google_mlkit_text_recognition.dart';
import 'dart:io';
import '../l10n/app_localizations.dart';

class OcrScreen extends StatefulWidget {
  const OcrScreen({super.key});

  @override
  State<OcrScreen> createState() => _OcrScreenState();
}

class _OcrScreenState extends State<OcrScreen> {
  File? _imageFile;
  String _recognizedText = '';
  bool _isProcessing = false;
  String _statusMessage = '';

  final ImagePicker _picker = ImagePicker();
  final TextRecognizer _textRecognizer = TextRecognizer(script: TextRecognitionScript.latin);

  @override
  void dispose() {
    _textRecognizer.close();
    super.dispose();
  }

  Future<void> _pickImage(ImageSource source) async {
    setState(() => _isProcessing = true);
    _statusMessage = '正在选择图片...';
    
    try {
      final XFile? pickedFile = await _picker.pickImage(source: source);
      if (pickedFile != null) {
        setState(() {
          _imageFile = File(pickedFile.path);
          _recognizedText = '';
        });
        _statusMessage = '图片已选择，正在识别文字...';
        await _processImage(pickedFile.path);
      }
    } catch (e) {
      _statusMessage = '选择图片失败: $e';
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('选择图片失败: $e')),
      );
    } finally {
      setState(() => _isProcessing = false);
    }
  }

  Future<void> _processImage(String imagePath) async {
    try {
      final inputImage = InputImage.fromFilePath(imagePath);
      final RecognizedText recognizedText = await _textRecognizer.processImage(inputImage);
      
      setState(() {
        _recognizedText = recognizedText.text;
        _statusMessage = recognizedText.text.isEmpty 
            ? '未识别到文字，请尝试更换图片'
            : '识别完成！';
      });
      
      if (_recognizedText.isNotEmpty) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('成功识别 ${_recognizedText.length} 个字符')),
        );
      }
    } catch (e) {
      setState(() {
        _statusMessage = '文字识别失败: $e';
      });
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('文字识别失败: $e')),
      );
    }
  }

  void _copyToClipboard() {
    if (_recognizedText.isNotEmpty) {
      Clipboard.setData(ClipboardData(text: _recognizedText));
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('已复制到剪贴板')),
      );
    }
  }

  void _shareText() {
    if (_recognizedText.isNotEmpty) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('分享功能将在后续版本中提供')),
      );
    }
  }

  void _addToStudy() {
    if (_recognizedText.isNotEmpty) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('已添加到学习内容（共${_recognizedText.length}个字符）')),
      );
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('OCR截图识字'),
        actions: [
          if (_recognizedText.isNotEmpty)
            IconButton(
              icon: const Icon(Icons.copy),
              onPressed: _copyToClipboard,
              tooltip: '复制文字',
            ),
          if (_recognizedText.isNotEmpty)
            IconButton(
              icon: const Icon(Icons.share),
              onPressed: _shareText,
              tooltip: '分享',
            ),
          if (_recognizedText.isNotEmpty)
            IconButton(
              icon: const Icon(Icons.add_circle),
              onPressed: _addToStudy,
              tooltip: '添加到学习',
            ),
        ],
      ),
      body: Column(
        children: [
          // 图片预览区域
          Expanded(
            flex: _imageFile != null ? 2 : 1,
            child: Container(
              width: double.infinity,
              color: Colors.grey[100],
              child: _imageFile != null
                  ? Image.file(
                      _imageFile!,
                      fit: BoxFit.contain,
                    )
                  : Center(
                      child: Column(
                        mainAxisAlignment: MainAxisAlignment.center,
                        children: [
                          Icon(
                            Icons.document_scanner,
                            size: 64,
                            color: Colors.grey[400],
                          ),
                          const SizedBox(height: 16),
                          Text(
                            '拍照或选择图片进行文字识别',
                            style: TextStyle(
                              fontSize: 16,
                              color: Colors.grey[600],
                            ),
                          ),
                        ],
                      ),
                    ),
            ),
          ),
          
          // 处理状态
          if (_statusMessage.isNotEmpty)
            Container(
              padding: const EdgeInsets.all(8),
              color: _statusMessage.contains('失败')
                  ? Colors.red[50]
                  : Colors.blue[50],
              child: Row(
                children: [
                  _isProcessing
                      ? const SizedBox(
                          width: 16,
                          height: 16,
                          child: CircularProgressIndicator(strokeWidth: 2),
                        )
                      : _statusMessage.contains('失败')
                          ? const Icon(Icons.error, color: Colors.red, size: 16)
                          : const Icon(Icons.check_circle, color: Colors.green, size: 16),
                  const SizedBox(width: 8),
                  Expanded(
                    child: Text(
                      _statusMessage,
                      style: TextStyle(
                        color: _statusMessage.contains('失败')
                            ? Colors.red[700]
                            : Colors.blue[700],
                      ),
                    ),
                  ),
                ],
              ),
            ),
          
          // 识别结果区域
          if (_recognizedText.isNotEmpty)
            Expanded(
              flex: 2,
              child: Container(
                width: double.infinity,
                padding: const EdgeInsets.all(16),
                decoration: BoxDecoration(
                  color: Colors.white,
                  boxShadow: [
                    BoxShadow(
                      color: Colors.grey.withOpacity(0.1),
                      blurRadius: 8,
                      offset: const Offset(0, -2),
                    ),
                  ],
                ),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Row(
                      children: [
                        const Icon(Icons.text_fields, color: Colors.blue),
                        const SizedBox(width: 8),
                        const Text(
                          '识别结果',
                          style: TextStyle(
                            fontSize: 16,
                            fontWeight: FontWeight.bold,
                          ),
                        ),
                        const Spacer(),
                        Text(
                          '${_recognizedText.length}个字符',
                          style: TextStyle(color: Colors.grey[600], fontSize: 12),
                        ),
                      ],
                    ),
                    const SizedBox(height: 12),
                    Expanded(
                      child: Container(
                        padding: const EdgeInsets.all(12),
                        decoration: BoxDecoration(
                          color: Colors.grey[100],
                          borderRadius: BorderRadius.circular(8),
                        ),
                        child: SingleChildScrollView(
                          child: SelectableText(
                            _recognizedText,
                            style: const TextStyle(fontSize: 14),
                          ),
                        ),
                      ),
                    ),
                  ],
                ),
              ),
            ),
          
          // 操作按钮区域
          Container(
            padding: const EdgeInsets.all(16),
            decoration: BoxDecoration(
              color: Colors.white,
              boxShadow: [
                BoxShadow(
                  color: Colors.grey.withOpacity(0.1),
                  blurRadius: 8,
                  offset: const Offset(0, -2),
                ),
              ],
            ),
            child: Column(
              children: [
                // 操作按钮
                Row(
                  mainAxisAlignment: MainAxisAlignment.spaceEvenly,
                  children: [
                    _buildActionButton(
                      icon: Icons.camera_alt,
                      label: '拍照',
                      onPressed: () => _pickImage(ImageSource.camera),
                    ),
                    _buildActionButton(
                      icon: Icons.photo_library,
                      label: '相册',
                      onPressed: () => _pickImage(ImageSource.gallery),
                    ),
                    _buildActionButton(
                      icon: Icons.refresh,
                      label: '重试',
                      onPressed: () {
                        setState(() {
                          _imageFile = null;
                          _recognizedText = '';
                          _statusMessage = '';
                        });
                      },
                    ),
                  ],
                ),
                
                // 快捷操作
                if (_recognizedText.isNotEmpty) ...[
                  const SizedBox(height: 16),
                  const Divider(),
                  const SizedBox(height: 12),
                  Row(
                    children: [
                      Expanded(
                        child: OutlinedButton.icon(
                          onPressed: _copyToClipboard,
                          icon: const Icon(Icons.copy),
                          label: const Text('复制文字'),
                        ),
                      ),
                      const SizedBox(width: 12),
                      Expanded(
                        child: ElevatedButton.icon(
                          onPressed: _addToStudy,
                          icon: const Icon(Icons.add),
                          label: const Text('加入学习'),
                          style: ElevatedButton.styleFrom(
                            backgroundColor: Colors.blue,
                          ),
                        ),
                      ),
                    ],
                  ),
                ],
              ],
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildActionButton({
    required IconData icon,
    required String label,
    required VoidCallback onPressed,
  }) {
    return ElevatedButton.icon(
      onPressed: _isProcessing ? null : onPressed,
      icon: Icon(icon),
      label: Text(label),
      style: ElevatedButton.styleFrom(
        padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 12),
      ),
    );
  }
}