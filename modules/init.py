"""
Persistent Memory System - 目录结构初始化
=========================================
创建完整的 .memory/ 目录结构
"""

from pathlib import Path
import os

def create_directory_structure(root: str = ".memory"):
    """创建完整目录结构"""
    
    dirs = [
        # 根目录
        root,
        
        # 对话目录
        f"{root}/conversations/raw",
        f"{root}/conversations/tagged/important",
        f"{root}/conversations/tagged/decision",
        f"{root}/conversations/tagged/todo",
        
        # 目标目录
        f"{root}/goals/annual",
        f"{root}/goals/quarterly",
        f"{root}/goals/monthly",
        f"{root}/goals/milestones",
        
        # 目标闭环目录
        f"{root}/goals/_闭环/daily_checkin",
        f"{root}/goals/_闭环/weekly_review",
        f"{root}/goals/_闭环/monthly_review",
        f"{root}/goals/_闭环/quarterly_review",
        f"{root}/goals/_templates",
        
        # 知识目录
        f"{root}/knowledge/topics/programming",
        f"{root}/knowledge/topics/project",
        f"{root}/knowledge/topics/personal",
        f"{root}/knowledge/resources",
        f"{root}/knowledge/summaries",
        
        # 索引目录
        f"{root}/_index",
        f"{root}/_index/_wal",
        f"{root}/_index/tags",
        
        # 备份目录
        f"{root}/_backup/daily",
        f"{root}/_backup/weekly",
        f"{root}/_backup/versions",
        
        # 归档目录
        f"{root}/_archive/conversations",
        f"{root}/_archive/goals",
        f"{root}/_archive/knowledge",
    ]
    
    created_dirs = []
    
    for d in dirs:
        path = Path(d)
        path.mkdir(parents=True, exist_ok=True)
        created_dirs.append(str(path))
        
        # 创建 __init__.py
        init_file = path / "__init__.py"
        if not init_file.exists():
            init_file.write_text(f"# {path.name}\n")
    
    print(f"✓ 目录结构创建完成: {len(created_dirs)} 个目录")
    
    # 验证结果
    print("\n📁 目录结构验证:")
    print("=" * 50)
    
    # 按类别分组显示
    categories = {
        "对话 (Conversations)": ["conversations"],
        "目标 (Goals)": ["goals"],
        "知识 (Knowledge)": ["knowledge"],
        "索引 (Index)": ["_index"],
        "备份 (Backup)": ["_backup"],
        "归档 (Archive)": ["_archive"],
    }
    
    for category, prefixes in categories.items():
        print(f"\n📂 {category}:")
        for d in created_dirs:
            for prefix in prefixes:
                if prefix in d:
                    rel_path = d.replace(f"{root}/", "")
                    print(f"   ├── {rel_path}")
                    break
    
    return created_dirs


def create_core_files():
    """创建核心文件"""
    
    root = Path(".memory")
    
    # 创建索引文件
    tags_index = root / "_index" / "tags.yaml"
    if not tags_index.exists():
        tags_index.write_text("""# 全局标签索引
version: 1.0
last_updated: null

tag_hierarchy:
  importance:
    - critical    # 紧急/关键
    - high        # 高优先级
    - medium      # 中优先级
    - low         # 低优先级
    - archive     # 已归档

  domain:
    - programming
    - ai_ml
    - project
    - personal

  type:
    - task        # 任务
    - goal        # 目标
    - knowledge   # 知识
    - decision    # 决策
    - lesson      # 教训

auto_suggestions:
  python: [programming, python, code]
  memory: [knowledge, system_design]
  设计: [important, project]

tag_aliases:
  重要: important
  关键: critical
  任务: task
  决策: decision
""")
        print(f"✓ 创建索引文件: {tags_index}")
    
    # 创建 _index.json
    index_json = root / "_index.json"
    if not index_json.exists():
        index_json.write_text("""{
  "version": "1.0",
  "created_at": null,
  "last_updated": null,
  "stats": {
    "conversations": 0,
    "goals": 0,
    "knowledge": 0
  }
}
""")
        print(f"✓ 创建索引文件: {index_json}")
    
    # 创建目标模板
    template_dir = root / "goals" / "_templates"
    template_dir.mkdir(parents=True, exist_ok=True)
    
    goal_template = template_dir / "goal_template.md"
    if not goal_template.exists():
        goal_template.write_text("""# {目标名称}

## 基本信息
- **目标名称**: {名称}
- **创建时间**: {日期}
- **截止日期**: {日期}
- **优先级**: {high/medium/low}

## 目标描述
{详细描述}

## 关键结果 (Key Results)
- [ ] KR1: {可衡量的结果1}
- [ ] KR2: {可衡量的结果2}
- [ ] KR3: {可衡量的结果3}

## 里程碑
| 里程碑 | 计划日期 | 完成日期 | 状态 |
|--------|----------|----------|------|
| {里程碑1} | {日期} | | pending |
| {里程碑2} | {日期} | | pending |
| {里程碑3} | {日期} | | pending |

## 进度追踪
- 开始日期: {日期}
- 当前进度: 0%
- 最后更新: {日期}

## 备注
{其他需要记录的信息}
""")
        print(f"✓ 创建模板文件: {goal_template}")
    
    review_template = template_dir / "review_template.md"
    if not review_template.exists():
        review_template.write_text("""# {周期}回顾 - {时间}

## 回顾概览
- **回顾周期**: {起始日期} - {结束日期}
- **完成目标数**: {X}/{总数}
- **整体完成率**: {百分比}%

## 成就与亮点
- 
- 
- 

## 不足与反思
- 
- 
- 

## 数据分析
### 目标完成情况
| 目标 | 计划 | 实际 | 差异 |
|------|------|------|------|
| {目标1} | {计划值} | {实际值} | {差异} |

### 时间分配
| 类别 | 时间占比 |
|------|----------|
| {类别1} | {百分比}% |

## 下周期计划
- [ ] 目标1
- [ ] 目标2
- [ ] 目标3

## 改进措施
1. 
2. 
3. 

---
*回顾时间: {时间戳}*
""")
        print(f"✓ 创建模板文件: {review_template}")


def validate_structure():
    """验证目录结构"""
    root = Path(".memory")
    
    required = [
        "conversations/raw",
        "conversations/tagged",
        "goals/annual",
        "goals/quarterly",
        "goals/monthly",
        "goals/milestones",
        "goals/_templates",
        "knowledge/topics",
        "knowledge/resources",
        "knowledge/summaries",
        "_index",
        "_backup",
        "_archive",
    ]
    
    missing = []
    for path in required:
        if not (root / path).exists():
            missing.append(path)
    
    if missing:
        print(f"\n❌ 缺少目录: {missing}")
        return False
    else:
        print("\n✅ 所有必需目录存在")
        return True


if __name__ == "__main__":
    print("=" * 50)
    print("Persistent Memory - 目录结构初始化")
    print("=" * 50)
    
    # 创建目录
    create_directory_structure()
    
    # 创建核心文件
    create_core_files()
    
    # 验证
    validate_structure()
    
    print("\n" + "=" * 50)
    print("初始化完成！")
    print("=" * 50)
