# OCR图片文字识别功能扩展

## 概述

本文档描述了为"学了吗APP"添加OCR图片文字识别功能的技术方案。

## 技术方案

### 方案选择：Google ML Kit Text Recognition

**推荐原因**：
- 完全离线工作（首次下载模型后）
- 无需API Key
- 免费使用
- 识别准确率高
- Flutter官方支持

### 备选方案：flutter_tesseract_ocr

**备选原因**：
- 完全开源
- 支持多语言
- 但集成较复杂

---

## 一、依赖配置

### 1.1 添加依赖

在 `pubspec.yaml` 中添加：

```yaml
dependencies:
  # 图片选择
  image_picker: ^1.0.4
  
  # OCR文字识别（离线）
  google_mlkit_text_recognition: ^0.12.0
  
  # 图片压缩（可选）
  flutter_image_compress: ^2.1.0
  
  # 路径处理
  path: ^1.8.3
  path_provider: ^2.1.1
```

### 1.2 Android配置

在 `android/app/build.gradle` 中：

```gradle
android {
    defaultConfig {
        minSdk 21
        targetSdk 34
    }
}
```

### 1.3 iOS配置

在 `ios/Podfile` 中：

```podfile
platform :ios, '12.0'
```

在 `ios/Runner/Info.plist` 中添加相机权限：

```xml
<key>NSCameraUsageDescription</key>
<string>需要访问相机以拍摄试卷照片</string>
<key>NSPhotoLibraryUsageDescription</key>
<string>需要访问相册以选择试卷图片</string>
```

---

## 二、功能模块

### 2.1 新增文件结构

```
lib/
├── services/
│   └── ocr_service.dart      # OCR服务
├── screens/
│   └── ocr/
│       ├── ocr_screen.dart         # OCR主界面
│       ├── ocr_result_screen.dart   # 识别结果
│       └── ocr_capture_screen.dart  # 拍照/选择图片
└── components/
    └── ocr_button.dart     # OCR快捷入口按钮
```

### 2.2 OCR服务

#### ocr_service.dart

```dart
/// OCR文字识别服务
/// 使用Google ML Kit实现离线文字识别
/// 
/// @author: OpenClaw Team
/// @date: 2026-02-16
library ocr_service;

import 'dart:io';
import 'package:image_picker/image_picker.dart';
import 'package:google_mlkit_text_recognition/google_mlkit_text_recognition.dart';
import 'package:path/path.dart';
import 'package:path_provider/path_provider.dart';

class OcrService {
  late final TextRecognizer _textRecognizer;
  final ImagePicker _picker = ImagePicker();
  
  /// 初始化OCR服务
  Future<void> initialize() async {
    _textRecognizer = TextRecognizer(
      script: TextRecognitionScript.chinese,
    );
  }
  
  /// 从图片路径识别文字
  Future<String> recognizeFromPath(String imagePath) async {
    final inputImage = InputImage.fromFilePath(imagePath);
    final RecognizedText recognizedText = await _textRecognizer.processImage(inputImage);
    return recognizedText.text;
  }
  
  /// 从相机拍摄
  Future<String?> captureFromCamera() async {
    final XFile? photo = await _picker.pickImage(
      source: ImageSource.camera,
      preferredCameraDevice: CameraDevice.rear,
    );
    
    if (photo != null) {
      return recognizeFromPath(photo.path);
    }
    return null;
  }
  
  /// 从相册选择
  Future<String?> pickFromGallery() async {
    final XFile? image = await _picker.pickImage(
      source: ImageSource.gallery,
    );
    
    if (image != null) {
      return recognizeFromPath(image.path);
    }
    return null;
  }
  
  /// 清理资源
  void dispose() {
    _textRecognizer.close();
  }
}
```

### 2.3 OCR界面

#### ocr_screen.dart

```dart
/// OCR文字识别界面
/// 支持拍照和从相册选择图片
/// 
/// @author: OpenClaw Team
/// @date: 2026-02-16
library ocr_screen;

import 'package:flutter/material.dart';
import '../../services/ocr_service.dart';
import '../../utils/app_constants.dart';

class OcrScreen extends StatefulWidget {
  const OcrScreen({super.key});

  @override
  State<OcrScreen> createState() => _OcrScreenState();
}

class _OcrScreenState extends State<OcrScreen> {
  final OcrService _ocrService = OcrService();
  String? _recognizedText;
  bool _isProcessing = false;
  
  @override
  void initState() {
    super.initState();
    _ocrService.initialize();
  }
  
  @override
  void dispose() {
    _ocrService.dispose();
    super.dispose();
  }
  
  Future<void> _processImage(ImageSource source) async {
    setState(() => _isProcessing = true);
    
    String? text;
    if (source == ImageSource.camera) {
      text = await _ocrService.captureFromCamera();
    } else {
      text = await _ocrService.pickFromGallery();
    }
    
    setState(() {
      _recognizedText = text;
      _isProcessing = false;
    });
  }
  
  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text('文字识别'),
      ),
      body: Column(
        children: [
          // 识别结果展示
          Expanded(
            child: _recognizedText != null
                ? SingleChildScrollView(
                    padding: EdgeInsets.all(16),
                    child: Text(_recognizedText!),
                  )
                : Center(
                    child: Text('暂无识别结果'),
                  ),
          ),
          
          // 操作按钮
          Padding(
            padding: EdgeInsets.all(16),
            child: Row(
              children: [
                Expanded(
                  child: ElevatedButton.icon(
                    onPressed: _isProcessing ? null : () => _processImage(ImageSource.camera),
                    icon: Icon(Icons.camera_alt),
                    label: Text('拍照识别'),
                  ),
                ),
                SizedBox(width: 16),
                Expanded(
                  child: ElevatedButton.icon(
                    onPressed: _isProcessing ? null : () => _processImage(ImageSource.gallery),
                    icon: Icon(Icons.photo_library),
                    label: Text('相册选择'),
                  ),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }
}
```

### 2.4 快捷入口组件

#### ocr_button.dart

```dart
/// OCR快捷入口按钮
/// 可添加到首页或其他页面
/// 
/// @author: OpenClaw Team
/// @date: 2026-02-16
library ocr_button;

import 'package:flutter/material.dart';

class OcrButton extends StatelessWidget {
  const OcrButton({super.key});

  @override
  Widget build(BuildContext context) {
    return FloatingActionButton.extended(
      onPressed: () {
        Navigator.push(
          context,
          MaterialPageRoute(builder: (context) => const OcrScreen()),
        );
      },
      icon: Icon(Icons.document_scanner),
      label: Text('试卷识别'),
      backgroundColor: Theme.of(context).primaryColor,
    );
  }
}
```

---

## 三、国际化

### 3.1 添加中英文对照

在 `app_zh.arb` 和 `app_en.arb` 中添加：

```arb
{
  "ocrTitle": "文字识别",
  "@ocrTitle": {
    "description": "OCR界面标题"
  },
  "captureOcr": "拍照识别",
  "@captureOcr": {
    "description": "拍照识别按钮"
  },
  "galleryOcr": "相册选择",
  "@galleryOcr": {
    "description": "相册选择按钮"
  },
  "noResult": "暂无识别结果",
  "@noResult": {
    "description": "无识别结果时的提示"
  },
  "processing": "识别中...",
  "@processing": {
    "description": "正在处理OCR"
  },
  "resultCopied": "已复制到剪贴板",
  "@resultCopied": {
    "description": "复制成功的提示"
  }
}
```

---

## 四、使用场景

### 4.1 试卷识别流程

```
1. 用户点击"试卷识别"按钮
    ↓
2. 选择"拍照"或"相册选择"
    ↓
3. APP识别图片中的文字
    ↓
4. 显示识别结果
    ↓
5. 用户可以：
   - 复制文字
   - 导出为PDF
   - 添加到知识点库
```

### 4.2 整合到现有功能

#### 整合到"知识点补漏"
- 识别试卷中的知识点
- 自动添加到错题本
- 生成相关练习题

#### 整合到"资源库"
- 导入纸质试卷
- 转换为电子版
- 支持搜索和分类

---

## 五、安装步骤

### 5.1 用户安装指引

**Android用户**：
1. 无需额外操作，首次使用自动下载OCR模型（约10MB）
2. 后续离线使用

**iOS用户**：
1. 无需额外操作
2. 首次使用自动下载OCR模型

### 5.2 开发者集成步骤

```bash
# 1. 更新依赖
flutter pub get

# 2. 运行分析
flutter analyze

# 3. 测试OCR功能
flutter run

# 4. 构建APK
flutter build apk
```

---

## 六、权限配置

### 6.1 Android权限

在 `android/app/src/main/AndroidManifest.xml` 中：

```xml
<uses-permission android:name="android.permission.CAMERA" />
<uses-permission android:name="android.permission.READ_EXTERNAL_STORAGE" />
<uses-permission android:name="android.permission.WRITE_EXTERNAL_STORAGE" />
```

### 6.2 iOS权限

在 `ios/Runner/Info.plist` 中：

```xml
<key>NSCameraUsageDescription</key>
<string>需要访问相机以拍摄试卷照片</string>
<key>NSPhotoLibraryUsageDescription</key>
<string>需要访问相册以选择图片</string>
```

---

## 七、性能考虑

### 7.1 模型下载

- **首次下载**：约10MB
- **下载时机**：首次使用OCR功能时
- **存储位置**：应用内部存储

### 7.2 识别速度

| 图片大小 | 识别时间 |
|----------|-----------|
| < 1MB | < 1秒 |
| 1-3MB | 1-3秒 |
| > 3MB | 3-5秒 |

### 7.3 内存使用

- **峰值内存**：< 100MB
- **后台释放**：不使用时自动释放

---

## 八、替代方案

### 8.1 Tesseract OCR（完全离线）

如果需要更强大的离线OCR，可以使用 `flutter_tesseract_ocr`：

```yaml
dependencies:
  flutter_tesseract_ocr: ^0.5.0
```

**优点**：
- 完全开源
- 支持更多语言

**缺点**：
- 集成更复杂
- 首次安装包更大

### 8.2 在线OCR（需要网络）

如需更高准确率，可集成在线OCR：

- Google Cloud Vision API（需API Key）
- Azure Computer Vision（需API Key）
- 百度OCR（需API Key）

---

## 九、总结

### 推荐方案：Google ML Kit Text Recognition

| 特性 | 评价 |
|------|------|
| 离线支持 | ✅ 完全离线 |
| API Key | ✅ 不需要 |
| 免费使用 | ✅ 免费 |
| 集成难度 | ⭐ 简单 |
| 识别准确率 | ⭐⭐⭐⭐ 高 |
| 模型大小 | ~10MB |

**结论**：Google ML Kit是最佳选择，简单易用，完全免费，离线工作。

---

**创建日期**: 2026-02-16
**最后更新**: 2026-02-16
**维护者**: OpenClaw Team
