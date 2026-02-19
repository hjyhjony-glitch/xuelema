"""
完整的 Flutter 项目 l10n 修复脚本
"""
import os
import re

def add_import_and_fix_l10n(file_path):
    """添加导入并修复 l10n 定义"""
    
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    # 检查是否已经有 AppLocalizations 导入
    has_import = False
    for line in lines:
        if 'app_localizations.dart' in line:
            has_import = True
            break
    
    # 如果没有导入，添加它
    if not has_import:
        # 找到最后一个 import 语句的位置
        last_import_idx = -1
        for i, line in enumerate(lines):
            if line.strip().startswith('import'):
                last_import_idx = i
        
        if last_import_idx >= 0:
            # 在最后一个导入后添加新导入
            import_line = "import '../l10n/app_localizations.dart';\n"
            lines.insert(last_import_idx + 1, import_line)
            print(f"✅ Added import to: {os.path.basename(file_path)}")
    
    fixed = False
    
    for i, line in enumerate(lines):
        # 查找 build 方法
        if 'Widget build(' in line or 'build(BuildContext context)' in line:
            # 检查后续 20 行内是否有 l10n 定义
            build_content = ''.join(lines[i:i+25])
            if 'final l10n = AppLocalizations.of(context)' not in build_content:
                # 在 build 方法第一行后插入 l10n 定义
                lines.insert(i+1, '    final l10n = AppLocalizations.of(context);\n')
                fixed = True
                print(f"✅ Added l10n definition to: {os.path.basename(file_path)}")
            break
    
    if fixed or not has_import:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.writelines(lines)

def fix_invalid_l10n_keys(file_path):
    """修复无效的 l10n 键名"""
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 定义有效的 l10n 属性
    valid_keys = {
        'confirm': 'confirm',
        'ok': 'ok', 
        'cancel': 'cancel',
        'save': 'save',
        'delete': 'delete',
        'exit': 'exit',
        'back': 'back',
        'close': 'close',
        'submit': 'submit',
        'retry': 'retry',
    }
    
    # 查找所有 l10n.$key 的使用
    matches = re.findall(r'l10n\.(\$key|\w+)', content)
    
    for match in matches:
        if match == '$key':
            # 替换 l10n.$key
            content = content.replace('l10n.$key', 'l10n.confirm')
            print(f"✅ Fixed l10n.$key in: {os.path.basename(file_path)}")
    
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)

def remove_unused_l10n(file_path):
    """移除未使用的 l10n 定义"""
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 检查是否有未使用的 l10n 变量
    # 如果定义了 l10n 但没有在 build 方法中使用
    
    lines = content.split('\n')
    result = []
    skip_next = False
    
    for i, line in enumerate(lines):
        # 查找未使用的 l10n 定义
        if 'final l10n = AppLocalizations.of(context)' in line:
            # 检查这一行是否在注释中
            if i > 0 and '//' in lines[i-1] and 'l10n' not in lines[i-1]:
                # 这可能是被注释掉的代码
                result.append(line)
                continue
            
            # 检查后续内容是否使用了 l10n
            following = ''.join(lines[i:i+30])
            if 'l10n.' not in following:
                # 未使用的变量，跳过这行
                print(f"⚠️  Removing unused l10n from: {os.path.basename(file_path)}")
                skip_next = True
                continue
        
        result.append(line)
    
    if len(result) != len(lines):
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(result))

def process_directory():
    """处理所有 Dart 文件"""
    
    base_dir = os.path.dirname(os.path.abspath(__file__))
    lib_dir = os.path.join(base_dir, 'lib')
    
    print("=" * 60)
    print("开始完整修复 Flutter 项目 l10n 问题...")
    print("=" * 60)
    
    dart_files = []
    for root, dirs, files in os.walk(lib_dir):
        for file in files:
            if file.endswith('.dart'):
                dart_files.append(os.path.join(root, file))
    
    print(f"找到 {len(dart_files)} 个 Dart 文件\n")
    
    error_count = 0
    
    for file_path in dart_files:
        try:
            add_import_and_fix_l10n(file_path)
            fix_invalid_l10n_keys(file_path)
            remove_unused_l10n(file_path)
        except Exception as e:
            print(f"❌ Error in {os.path.basename(file_path)}: {e}")
            error_count += 1
    
    print("\n" + "=" * 60)
    print("修复完成!")
    print(f"错误数: {error_count}")
    print("=" * 60)

if __name__ == '__main__':
    process_directory()
