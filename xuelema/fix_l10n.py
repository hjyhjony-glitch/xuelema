import os
import re

# 扩展方法模板
EXTENSION_IMPORT = "import '../extensions/l10n_extension.dart';"

def fix_file(filepath):
    """修复单个文件中的 l10n 引用"""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original_content = content
    
    # 1. 添加扩展导入（如果还没有）
    if "import '../extensions/l10n_extension.dart'" not in content:
        if "import '../l10n/app_localizations.dart'" in content:
            content = content.replace(
                "import '../l10n/app_localizations.dart';",
                "import '../l10n/app_localizations.dart';\n" + EXTENSION_IMPORT
            )
    
    # 2. 修复模式：将 build 方法中的 final l10n = AppLocalizations.of(context); 替换
    # 并且将所有 l10n.xxx 替换为 context.l10n.xxx
    content = re.sub(
        r'final l10n = AppLocalizations\.of\(context\);',
        '',
        content
    )
    
    # 3. 替换直接使用的 l10n.xxx 为 context.l10n.xxx
    content = re.sub(
        r'\bl10n\.(\w+)',
        r'context.l10n.\1',
        content
    )
    
    # 只有内容改变时才写入
    if content != original_content:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"Fixed: {filepath}")
        return True
    return False

def process_directory(directory):
    """处理目录中的所有 dart 文件"""
    fixed_count = 0
    for root, dirs, files in os.walk(directory):
        for filename in files:
            if filename.endswith('.dart'):
                filepath = os.path.join(root, filename)
                if fix_file(filepath):
                    fixed_count += 1
    return fixed_count

if __name__ == '__main__':
    lib_dir = 'lib'
    count = process_directory(lib_dir)
    print(f"\nTotal files fixed: {count}")
