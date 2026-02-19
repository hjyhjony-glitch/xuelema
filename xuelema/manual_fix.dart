// 手动修复硬编码字符串的示例
// 这是一个Dart文件，但我们可以用Python脚本来批量处理

// 修复模式：
// 1. const Text('中文') → Text(l10n.key)
// 2. tooltip: '中文' → tooltip: l10n.key
// 3. title: '中文' → title: l10n.key
// 4. subtitle: '中文' → subtitle: l10n.key

// 需要修复的文件清单：
// 1. home_screen.dart - 修复统计卡片中的字符串
// 2. review_screen.dart - 确保已修复
// 3. mistake_screen.dart - 确保已修复
// 4. 其他屏幕文件