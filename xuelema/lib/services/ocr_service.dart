import 'package:flutter/material.dart';
import 'package:google_mlkit_text_recognition/google_mlkit_text_recognition.dart';
import 'package:image_picker/image_picker.dart';
import 'dart:io';
import 'package:path/path.dart';
import 'package:path_provider/path_provider.dart';
import '../l10n/app_localizations.dart';
import '../extensions/l10n_extension.dart';

/// OCR文字识别服务
class OcrService {
  TextRecognizer? _textRecognizer;

  /// 初始化OCR识别器
  void initialize() {
    _textRecognizer = TextRecognizer(script: TextRecognitionScript.chinese);
  }

  /// 初始化拉丁文识别器
  void initializeLatin() {
    _textRecognizer = TextRecognizer(script: TextRecognitionScript.latin);
  }

  /// 从图片文件路径识别文字
  Future<String> recognizeFromImage(String imagePath) async {
    if (_textRecognizer == null) {
      initialize();
    }
    
    final inputImage = InputImage.fromFilePath(imagePath);
    final RecognizedText recognizedText = await _textRecognizer!.processImage(inputImage);
    
    return recognizedText.text;
  }

  /// 从XFile识别文字（相机拍摄或相册选择）
  Future<String> recognizeFromFile(XFile imageFile) async {
    if (_textRecognizer == null) {
      initialize();
    }
    
    final inputImage = InputImage.fromFilePath(imageFile.path);
    final RecognizedText recognizedText = await _textRecognizer!.processImage(inputImage);
    
    return recognizedText.text;
  }

  /// 从相机拍摄图片并识别
  Future<String> captureAndRecognize({bool useChinese = true}) async {
    final ImagePicker picker = ImagePicker();
    
    if (useChinese) {
      initialize();
    } else {
      initializeLatin();
    }
    
    final XFile? photo = await picker.pickImage(
      source: ImageSource.camera,
      maxWidth: 1920,
      maxHeight: 1080,
      imageQuality: 85,
    );
    
    if (photo == null) {
      return '';
    }
    
    return recognizeFromFile(photo);
  }

  /// 从相册选择图片并识别
  Future<String> pickFromGalleryAndRecognize({bool useChinese = true}) async {
    final ImagePicker picker = ImagePicker();
    
    if (useChinese) {
      initialize();
    } else {
      initializeLatin();
    }
    
    final XFile? image = await picker.pickImage(
      source: ImageSource.gallery,
      maxWidth: 1920,
      maxHeight: 1080,
      imageQuality: 85,
    );
    
    if (image == null) {
      return '';
    }
    
    return recognizeFromFile(image);
  }

  /// 复制图片到应用缓存目录
  Future<String> copyImageToCache(File imageFile) async {
    final Directory cacheDir = await getTemporaryDirectory();
    final String fileName = '${DateTime.now().millisecondsSinceEpoch}${extension(imageFile.path)}';
    final String targetPath = join(cacheDir.path, fileName);
    
    await imageFile.copy(targetPath);
    return targetPath;
  }

  /// 清理资源
  void dispose() {
    _textRecognizer?.close();
    _textRecognizer = null;
  }
}
