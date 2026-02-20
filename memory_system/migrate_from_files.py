"""
数据迁移脚本
将现有 .md 文件迁移到 SQLite 数据库
"""
import sys
import os
import json
import re
from datetime import datetime
from pathlib import Path

# 添加项目根目录到路径
_project_root = os.path.dirname(os.path.dirname(__file__))
_memory_path = os.path.join(_project_root, '.memory')
_memory_system_path = os.path.join(_project_root, 'memory_system')

for path in [_project_root, _memory_path, _memory_system_path]:
    if path not in sys.path:
        sys.path.insert(0, path)

from memory_system import get_unified_memory
from memory.conversations.conversation_storage import get_conversation_storage
from memory.knowledge.knowledge_storage import get_knowledge_storage


def parse_frontmatter(content: str) -> tuple:
    """
    解析 Markdown frontmatter
    
    Returns:
        (metadata, body)
    """
    frontmatter = {}
    body = content
    
    # 检查是否有 frontmatter
    if content.startswith('---'):
        parts = content.split('---', 2)
        if len(parts) >= 3:
            fm_text = parts[1].strip()
            body = parts[2].strip()
            
            # 解析 frontmatter
            for line in fm_text.split('\n'):
                if ':' in line:
                    key, value = line.split(':', 1)
                    frontmatter[key.strip()] = value.strip()
    
    return frontmatter, body


def migrate_MEMORY_md():
    """迁移 MEMORY.md 到长期记忆"""
    print("\n" + "=" * 60)
    print("迁移 MEMORY.md")
    print("=" * 60)
    
    memory_md = os.path.join(_project_root, 'MEMORY.md')
    if not os.path.exists(memory_md):
        print("  ⚠️ MEMORY.md 不存在")
        return 0
    
    with open(memory_md, 'r', encoding='utf-8') as f:
        content = f.read()
    
    um = get_unified_memory()
    
    # 解析 MEMORY.md 的结构
    sections = re.split(r'^## ', content, flags=re.MULTILINE)
    
    count = 0
    for section in sections[1:]:  # 跳过第一个空部分
        lines = section.split('\n')
        title = lines[0].strip()
        section_body = '\n'.join(lines[1:]).strip()
        
        if title and section_body:
            # 根据标题确定类型
            if '团队' in title or '协作' in title:
                mem_type = 'knowledge'
                tags = ['team', 'collaboration']
            elif '自动化' in title or '测试' in title:
                mem_type = 'knowledge'
                tags = ['automation', 'testing']
            elif '模型' in title or '配置' in title:
                mem_type = 'knowledge'
                tags = ['model', 'config']
            elif '规则' in title or '原则' in title:
                mem_type = 'decision'
                tags = ['rule', 'principle']
            elif '历史' in title or '变更' in title:
                mem_type = 'conversation'
                tags = ['history', 'changelog']
            else:
                mem_type = 'knowledge'
                tags = ['memory', 'migrated']
            
            um.save(
                key=f"memory_{title[:30]}",
                value=section_body,
                memory_type=mem_type,
                tags=tags,
                metadata={
                    "source": "MEMORY.md",
                    "title": title,
                    "migrated_at": datetime.now().isoformat()
                }
            )
            count += 1
    
    print(f"  ✅ 迁移了 {count} 条记录")
    return count


def migrate_daily_notes():
    """迁移每日笔记"""
    print("\n" + "=" * 60)
    print("迁移每日笔记")
    print("=" * 60)
    
    memory_dir = os.path.join(_project_root, 'memory')
    if not os.path.exists(memory_dir):
        print("  ⚠️ memory/ 目录不存在")
        return 0
    
    cs = get_conversation_storage()
    
    count = 0
    for filename in os.listdir(memory_dir):
        if filename.endswith('.md') and filename != 'DEVELOPMENT_LOG.md':
            date = filename.replace('.md', '')
            file_path = os.path.join(memory_dir, filename)
            
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 解析对话条目
            entries = content.split('\n---\n')
            
            for entry in entries:
                if entry.strip():
                    metadata, body = parse_frontmatter(entry)
                    
                    if body:
                        # 生成对话 ID
                        conv_id = f"daily_{date}_{count}"
                        
                        # 保存到对话存储
                        cs.save_raw(
                            conversation_id=conv_id,
                            messages=[{"role": "user", "content": body}],
                            metadata={
                                "source": filename,
                                "date": date,
                                "migrated_at": datetime.now().isoformat()
                            }
                        )
                        count += 1
    
    print(f"  ✅ 迁移了 {count} 条每日记录")
    return count


def migrate_development_log():
    """迁移开发日志"""
    print("\n" + "=" * 60)
    print("迁移 DEVELOPMENT_LOG.md")
    print("=" * 60)
    
    dev_log = os.path.join(_project_root, 'memory', 'DEVELOPMENT_LOG.md')
    if not os.path.exists(dev_log):
        print("  ⚠️ DEVELOPMENT_LOG.md 不存在")
        return 0
    
    with open(dev_log, 'r', encoding='utf-8') as f:
        content = f.read()
    
    ks = get_knowledge_storage()
    
    # 解析 Phase 和 Task
    phases = re.split(r'^## ', content, flags=re.MULTILINE)
    
    count = 0
    for phase in phases[1:]:
        lines = phase.split('\n')
        title = lines[0].strip()
        body = '\n'.join(lines[1:]).strip()
        
        if title and body:
            ks.save_topic(
                topic=f"phase_{title[:30]}".lower().replace(' ', '_'),
                title=title,
                content=body,
                category='project',
                tags=['development', 'log', 'migrated'],
                metadata={
                    "source": "DEVELOPMENT_LOG.md",
                    "migrated_at": datetime.now().isoformat()
                }
            )
            count += 1
    
    print(f"  ✅ 迁移了 {count} 个阶段记录")
    return count


def run_migration():
    """运行完整迁移"""
    print("\n" + "=" * 60)
    print("开始数据迁移")
    print("=" * 60)
    print(f"时间: {datetime.now().isoformat()}")
    print("=" * 60)
    
    total = 0
    
    # 迁移 MEMORY.md
    total += migrate_MEMORY_md()
    
    # 迁移每日笔记
    total += migrate_daily_notes()
    
    # 迁移开发日志
    total += migrate_development_log()
    
    print("\n" + "=" * 60)
    print(f"迁移完成！总计迁移 {total} 条记录")
    print("=" * 60)
    
    # 同步到文件
    print("\n同步到文件备份...")
    um = get_unified_memory()
    sync_stats = um.sync_to_file()
    print(f"  同步统计: {sync_stats}")
    
    return total


if __name__ == "__main__":
    run_migration()
