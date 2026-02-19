import 'package:flutter/material.dart';
import '../l10n/app_localizations.dart';
import '../extensions/l10n_extension.dart';

/// BuildContext 扩展，提供便捷的 l10n 访问方式
extension L10nExtension on BuildContext {
  /// 获取当前上下文的本地化字符串
  AppLocalizations get l10n => AppLocalizations.of(this);
}
