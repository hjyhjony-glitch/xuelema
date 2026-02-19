import os
import re

def fix_l10n_usage(file_path):
    """修复文件中错误的 l10n 使用"""
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original_content = content
    
    # 修复 l10n.$key 为合理的默认值
    # 这里我们替换为具体的中文文本作为占位符
    replacements = {
        r'l10n\.\$key': 'l10n.confirm',  # 或其他合适的属性
    }
    
    for pattern, replacement in replacements.items():
        content = re.sub(pattern, replacement, content)
    
    if content != original_content:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"Fixed: {file_path}")

def check_and_fix_build_method(file_path):
    """检查并修复缺少 l10n 定义的问题"""
    
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    # 查找使用 l10n 但没有定义的地方
    needs_l10n_definition = False
    build_method_line = -1
    last_import_line = -1
    
    for i, line in enumerate(lines):
        if 'import' in line and 'app_localizations' in line.lower():
            last_import_line = i
        if 'Widget build(' in line:
            build_method_line = i
            break
    
    # 检查 build 方法中是否使用了 l10n 但没有定义
    if build_method_line >= 0:
        build_method_content = ''.join(lines[build_method_line:build_method_line+50])
        if 'l10n.' in build_method_content and 'final l10n = AppLocalizations.of(context)' not in build_method_content:
            # 在 build 方法开头添加 l10n 定义
            lines.insert(build_method_line + 1, '    final l10n = AppLocalizations.of(context);\n')
            with open(file_path, 'w', encoding='utf-8') as f:
                f.writelines(lines)
            print(f"Added l10n definition to: {file_path}")

def remove_dangling_comments(file_path):
    """移除悬空的库文档注释"""
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 移除开头的悬空文档注释
    lines = content.split('\n')
    fixed_lines = []
    i = 0
    
    while i < len(lines):
        line = lines[i]
        # 如果是悬空的 /// 注释（不是文件顶部注释的一部分）
        if line.strip().startswith('///') and not line.strip().startswith('/// '):
            # 检查前一行是否是有效的注释或 dart 声明
            if i == 0 or (i > 0 and not lines[i-1].strip().startswith('///')):
                # 这是一个悬空注释，跳过它
                i += 1
                continue
        
        # 检查是否有 dart 文件以 '///' 开头但没有包声明
        if i == 0 and line.strip().startswith('///'):
            # 检查是否有空行
            if len(lines) > 1 and lines[1].strip() == '':
                # 这可能是悬空注释
                if 'import' in lines[2]:
                    i += 1
                    continue
        
        fixed_lines.append(line)
        i += 1
    
    if len(fixed_lines) != len(lines):
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(fixed_lines))
        print(f"Removed dangling comments from: {file_path}")

def fix_async_build_context(file_path):
    """修复异步方法中使用 BuildContext 的问题"""
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 修复模式: 在 async 方法中使用 BuildContext
    # 添加 mounted 检查
    patterns = [
        (r'(\S+)\(\) async \{', r'\1() async {\n    if (!mounted) return;'),
    ]
    
    for pattern, replacement in patterns:
        content = re.sub(pattern, replacement, content)
    
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)

def process_directory(directory):
    """处理目录中的所有 dart 文件"""
    
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith('.dart'):
                file_path = os.path.join(root, file)
                
                # 只处理 lib 目录下的文件
                if 'lib' in file_path:
                    try:
                        remove_dangling_comments(file_path)
                        check_and_fix_build_method(file_path)
                        fix_l10n_usage(file_path)
                    except Exception as e:
                        print(f"Error processing {file_path}: {e}")

if __name__ == '__main__':
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    lib_dir = os.path.join(base_dir, 'lib')
    
    print(f"Processing: {lib_dir}")
    process_directory(lib_dir)
    print("Done!")
