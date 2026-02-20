#!/usr/bin/env python3
"""
Tagger - 自动标签模块
=====================
基于规则和关键词的对话自动标签

功能:
1. 关键词匹配标签
2. 规则引擎标签
3. 标签建议
4. 标签统计分析

作者: RUNBOT-DEV（笑天）
版本: v1.0
日期: 2026-02-20
"""

import json
import logging
import re
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple
from threading import Lock

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@dataclass
class TagRule:
    """标签规则数据类"""
    name: str
    description: str = ""
    keywords: List[str] = field(default_factory=list)
    patterns: List[str] = field(default_factory=list)
    category: str = "general"
    priority: int = 0  # 数值越大优先级越高
    exclusive: bool = False  # 是否互斥（与其他互斥标签只能选一个）


@dataclass
class TagSuggestion:
    """标签建议数据类"""
    tag: str
    score: float
    reason: str
    matched_keywords: List[str] = field(default_factory=list)
    category: str = "general"


class TagMatcher:
    """标签匹配器"""
    
    def __init__(self, rules: List[TagRule] = None):
        """
        初始化标签匹配器
        
        Args:
            rules: 标签规则列表
        """
        self.rules = rules or self._get_default_rules()
        self._compile_patterns()
    
    def _get_default_rules(self) -> List[TagRule]:
        """
        获取默认标签规则
        
        Returns:
            List[TagRule]: 默认规则列表
        """
        return [
            # 重要性标签
            TagRule(
                name="important",
                description="重要对话",
                keywords=["重要", "紧急", "关键", "critical", "urgent", "important", "必须", "一定要"],
                category="importance",
                priority=100
            ),
            TagRule(
                name="decision",
                description="决策相关",
                keywords=["决定", "决策", "确定", "就这么办", "同意", "decision", "decided"],
                category="type",
                priority=80
            ),
            
            # 类型标签
            TagRule(
                name="task",
                description="任务/待办",
                keywords=["任务", "todo", "待办", "完成", "做", "执行", "action", "task", "todo"],
                category="type",
                priority=70
            ),
            TagRule(
                name="question",
                description="问题/咨询",
                keywords=["?", "？", "怎么", "如何", "为什么", "什么", "?", "how", "why", "what"],
                category="type",
                priority=60
            ),
            TagRule(
                name="discussion",
                description="讨论/交流",
                keywords=["讨论", "交流", "分享", "看看", "说说", "discuss", "share"],
                category="type",
                priority=50
            ),
            TagRule(
                name="announcement",
                description="公告/通知",
                keywords=["通知", "公告", "注意", "提醒", "announcement", "notice", "reminder"],
                category="type",
                priority=60
            ),
            
            # 优先级标签
            TagRule(
                name="high_priority",
                description="高优先级",
                keywords=["紧急", "尽快", "马上", "立刻", "asap", "urgent", "immediate"],
                category="priority",
                priority=90
            ),
            TagRule(
                name="medium_priority",
                description="中优先级",
                keywords=["尽快", "本周", "近期", "soon", "this week"],
                category="priority",
                priority=50
            ),
            TagRule(
                name="low_priority",
                description="低优先级",
                keywords=["有空", "不急", "以后", "later", "when free", "no rush"],
                category="priority",
                priority=30
            ),
            
            # 主题标签
            TagRule(
                name="python",
                description="Python 相关",
                keywords=["python", "Python", "PYTHON", "py文件", "pip", "venv", "django", "flask"],
                category="topic",
                priority=70
            ),
            TagRule(
                name="ai_ml",
                description="AI/机器学习",
                keywords=["ai", "AI", "人工智能", "机器学习", "ML", "LLM", "模型", "model", "神经网络"],
                category="topic",
                priority=70
            ),
            TagRule(
                name="design",
                description="设计相关",
                keywords=["设计", "架构", "方案", "design", "architecture", "schema"],
                category="topic",
                priority=60
            ),
            TagRule(
                name="bug",
                description="Bug/问题修复",
                keywords=["bug", "Bug", "BUG", "错误", "报错", "修复", "fix", "issue", "problem"],
                category="topic",
                priority=80
            ),
            TagRule(
                name="documentation",
                description="文档相关",
                keywords=["文档", "说明", "README", "docs", "document"],
                category="topic",
                priority=50
            ),
            
            # 状态标签
            TagRule(
                name="in_progress",
                description="进行中",
                keywords=["进行中", "正在做", "in progress", "working on"],
                category="status",
                priority=60
            ),
            TagRule(
                name="completed",
                description="已完成",
                keywords=["完成", "做好了", "done", "completed", "finished"],
                category="status",
                priority=50
            ),
            TagRule(
                name="blocked",
                description="阻塞中",
                keywords=["阻塞", "卡住了", "blocked", "stuck"],
                category="status",
                priority=70
            ),
            
            # 平台标签
            TagRule(
                name="feishu",
                description="飞书相关",
                keywords=["飞书", "feishu", "飞书文档", "飞书群"],
                category="platform",
                priority=60
            ),
            TagRule(
                name="github",
                description="GitHub 相关",
                keywords=["github", "GitHub", "PR", "issue", "commit", "branch"],
                category="platform",
                priority=60
            ),
        ]
    
    def _compile_patterns(self) -> None:
        """编译正则表达式模式"""
        for rule in self.rules:
            rule.compiled_patterns = [
                re.compile(p, re.IGNORECASE) for p in rule.patterns
            ]
    
    def match(
        self,
        content: str,
        max_tags: int = 5,
        exclusive_categories: List[str] = None
    ) -> List[str]:
        """
        匹配内容，返回匹配的标签列表
        
        Args:
            content: 要匹配的内容
            max_tags: 最大标签数量
            exclusive_categories: 互斥类别（每类只选最高优先级）
            
        Returns:
            List[str]: 匹配的标签列表
        """
        if not content:
            return []
        
        content_lower = content.lower()
        matches: List[Tuple[TagRule, int]] = []  # (rule, match_count)
        
        for rule in self.rules:
            match_count = 0
            
            # 关键词匹配
            for keyword in rule.keywords:
                if keyword.lower() in content_lower:
                    match_count += 1
            
            # 模式匹配
            for pattern in rule.compiled_patterns:
                matches_found = len(pattern.findall(content))
                match_count += matches_found
            
            if match_count > 0:
                matches.append((rule, match_count))
        
        # 按优先级和匹配数量排序
        matches.sort(key=lambda x: (x[0].priority, x[1]), reverse=True)
        
        # 选择标签（处理互斥类别）
        selected_tags: List[str] = []
        selected_categories: Set[str] = set()
        exclusive_categories = exclusive_categories or ["type", "priority", "status"]
        
        for rule, _ in matches:
            # 检查互斥类别
            if rule.category in exclusive_categories:
                if rule.category in selected_categories:
                    continue  # 已选同类别标签
                selected_categories.add(rule.category)
            
            # 检查互斥标签
            if rule.exclusive:
                # 移除已选的互斥标签
                selected_tags = [t for t in selected_tags 
                               if t not in self._get_mutually_exclusive(rule.name)]
            
            if rule.name not in selected_tags:
                selected_tags.append(rule.name)
            
            if len(selected_tags) >= max_tags:
                break
        
        return selected_tags
    
    def _get_mutually_exclusive(self, tag: str) -> Set[str]:
        """
        获取互斥标签集合
        
        Args:
            tag: 标签名
            
        Returns:
            Set[str]: 互斥标签集合
        """
        exclusive_groups = [
            {"high_priority", "medium_priority", "low_priority"},
            {"important", "low_priority"},
            {"in_progress", "completed", "blocked"},
            {"task", "question", "discussion", "announcement"},
        ]
        
        for group in exclusive_groups:
            if tag in group:
                return group - {tag}
        
        return set()
    
    def suggest(
        self,
        content: str,
        max_suggestions: int = 5
    ) -> List[TagSuggestion]:
        """
        为内容提供标签建议
        
        Args:
            content: 要分析的内容
            max_suggestions: 最大建议数量
            
        Returns:
            List[TagSuggestion]: 标签建议列表
        """
        if not content:
            return []
        
        suggestions: List[TagSuggestion] = []
        content_lower = content.lower()
        
        for rule in self.rules:
            matched_keywords: List[str] = []
            pattern_matches = 0
            
            # 匹配关键词
            for keyword in rule.keywords:
                if keyword.lower() in content_lower:
                    matched_keywords.append(keyword)
            
            # 匹配模式
            for pattern in rule.compiled_patterns:
                matches = pattern.findall(content)
                pattern_matches += len(matches)
                if matches:
                    matched_keywords.extend([pattern.pattern] * len(matches))
            
            if matched_keywords or pattern_matches > 0:
                # 计算分数
                total_matches = len(matched_keywords) + pattern_matches
                score = min(total_matches / max(len(rule.keywords) + len(rule.patterns), 1), 1.0)
                
                suggestions.append(TagSuggestion(
                    tag=rule.name,
                    score=score,
                    reason=f"匹配到 {total_matches} 个规则特征",
                    matched_keywords=list(set(matched_keywords[:5])),  # 去重并限制数量
                    category=rule.category
                ))
        
        # 按分数排序
        suggestions.sort(key=lambda x: x.score, reverse=True)
        
        return suggestions[:max_suggestions]


class Tagger:
    """
    自动标签系统
    
    Attributes:
        matcher: 标签匹配器
        tag_rules_file: 标签规则文件路径
    """
    
    # 默认标签规则文件
    DEFAULT_TAG_RULES_FILE = "tags.yaml"
    
    # 常用标签定义
    BUILTIN_TAGS = {
        "important": {"color": "red", "description": "重要"},
        "decision": {"color": "purple", "description": "决策"},
        "task": {"color": "blue", "description": "任务"},
        "question": {"color": "yellow", "description": "问题"},
        "bug": {"color": "red", "description": "Bug"},
        "completed": {"color": "green", "description": "已完成"},
        "in_progress": {"color": "blue", "description": "进行中"},
        "python": {"color": "green", "description": "Python"},
        "ai_ml": {"color": "purple", "description": "AI/ML"},
    }
    
    def __init__(
        self,
        rules_dir: str = None,
        custom_rules: List[TagRule] = None
    ):
        """
        初始化 Tagger
        
        Args:
            rules_dir: 规则目录
            custom_rules: 自定义规则
        """
        self.matcher = TagMatcher(custom_rules)
        self.rules_dir = Path(rules_dir) if rules_dir else None
        self._lock = Lock()
        
        # 加载自定义规则
        self.custom_rules: List[TagRule] = []
        if self.rules_dir and self.rules_dir.exists():
            self._load_custom_rules()
        
        logger.info(f"Tagger 初始化完成")
        logger.info(f"内置规则: {len(self.matcher.rules)}")
        logger.info(f"自定义规则: {len(self.custom_rules)}")
    
    def _load_custom_rules(self) -> None:
        """加载自定义规则"""
        rules_file = self.rules_dir / "tag_rules.yaml"
        
        if not rules_file.exists():
            return
        
        try:
            import yaml
            with open(rules_file, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f)
            
            if not data:
                return
            
            for rule_data in data.get("rules", []):
                rule = TagRule(
                    name=rule_data["name"],
                    description=rule_data.get("description", ""),
                    keywords=rule_data.get("keywords", []),
                    patterns=rule_data.get("patterns", []),
                    category=rule_data.get("category", "general"),
                    priority=rule_data.get("priority", 0),
                    exclusive=rule_data.get("exclusive", False)
                )
                self.custom_rules.append(rule)
            
            # 更新匹配器
            self.matcher = TagMatcher(self.matcher.rules + self.custom_rules)
            logger.info(f"加载了 {len(self.custom_rules)} 条自定义规则")
            
        except Exception as e:
            logger.error(f"加载自定义规则失败: {e}")
    
    def tag_conversation(
        self,
        messages: List[Dict[str, Any]],
        max_tags: int = 5,
        existing_tags: List[str] = None
    ) -> Dict[str, Any]:
        """
        为对话添加标签
        
        Args:
            messages: 消息列表
            max_tags: 最大标签数量
            existing_tags: 已有标签
            
        Returns:
            Dict: 包含 tags 和 tagged_messages 的字典
        """
        with self._lock:
            # 合并所有消息内容
            all_content = " ".join([msg.get("content", "") for msg in messages])
            
            # 匹配标签
            tags = self.matcher.match(all_content, max_tags)
            
            # 保留已有标签
            if existing_tags:
                tags = list(set(tags + existing_tags))[:max_tags]
            
            # 为每条消息添加标签
            tagged_messages = []
            for msg in messages:
                content = msg.get("content", "")
                msg_tags = self.matcher.match(content, max_tags=3)
                
                tagged_messages.append({
                    **msg,
                    "tags": msg_tags
                })
            
            return {
                "tags": tags,
                "tagged_messages": tagged_messages,
                "tagger_version": "1.0"
            }
    
    def tag_message(
        self,
        content: str,
        max_tags: int = 3
    ) -> List[str]:
        """
        为单条消息添加标签
        
        Args:
            content: 消息内容
            max_tags: 最大标签数量
            
        Returns:
            List[str]: 标签列表
        """
        return self.matcher.match(content, max_tags)
    
    def suggest_tags(
        self,
        content: str,
        max_suggestions: int = 5
    ) -> List[TagSuggestion]:
        """
        提供标签建议
        
        Args:
            content: 内容
            max_suggestions: 最大建议数量
            
        Returns:
            List[TagSuggestion]: 建议列表
        """
        return self.matcher.suggest(content, max_suggestions)
    
    def analyze_tags(
        self,
        tags: List[str]
    ) -> Dict[str, Any]:
        """
        分析标签
        
        Args:
            tags: 标签列表
            
        Returns:
            Dict: 分析结果
        """
        categories: Dict[str, List[str]] = {}
        builtins = set(self.BUILTIN_TAGS.keys())
        custom_tags = []
        
        for tag in tags:
            if tag in builtins:
                if "builtin" not in categories:
                    categories["builtin"] = []
                categories["builtin"].append(tag)
            else:
                custom_tags.append(tag)
        
        if custom_tags:
            categories["custom"] = custom_tags
        
        return {
            "tags": tags,
            "count": len(tags),
            "categories": categories,
            "has_important": "important" in tags,
            "has_decision": "decision" in tags,
            "has_task": "task" in tags,
            "is_question": "question" in tags,
            "is_completed": "completed" in tags,
            "is_in_progress": "in_progress" in tags
        }
    
    def get_tag_info(self, tag: str) -> Optional[Dict[str, Any]]:
        """
        获取标签信息
        
        Args:
            tag: 标签名
            
        Returns:
            Dict: 标签信息，不存在返回 None
        """
        # 检查内置标签
        if tag in self.BUILTIN_TAGS:
            return {
                "tag": tag,
                "type": "builtin",
                **self.BUILTIN_TAGS[tag]
            }
        
        # 检查规则
        for rule in self.matcher.rules:
            if rule.name == tag:
                return {
                    "tag": tag,
                    "type": "rule",
                    "description": rule.description,
                    "category": rule.category,
                    "priority": rule.priority,
                    "keywords": rule.keywords
                }
        
        return None
    
    def list_tags(self, category: str = None) -> List[Dict[str, Any]]:
        """
        列出所有标签
        
        Args:
            category: 类别过滤
            
        Returns:
            List[Dict]: 标签信息列表
        """
        tags: List[Dict[str, Any]] = []
        
        # 添加内置标签
        for tag, info in self.BUILTIN_TAGS.items():
            if not category or info.get("category") == category:
                tags.append({
                    "tag": tag,
                    "type": "builtin",
                    **info
                })
        
        # 添加规则标签
        for rule in self.matcher.rules:
            if not category or rule.category == category:
                tags.append({
                    "tag": rule.name,
                    "type": "rule",
                    "description": rule.description,
                    "category": rule.category,
                    "priority": rule.priority
                })
        
        return tags
    
    def validate_tags(self, tags: List[str]) -> Tuple[bool, List[str]]:
        """
        验证标签
        
        Args:
            tags: 标签列表
            
        Returns:
            Tuple[bool, List[str]]: (是否有效, 无效标签列表)
        """
        valid_tags = self.BUILTIN_TAGS.keys()
        valid_rules = {r.name for r in self.matcher.rules}
        all_valid = valid_tags | valid_rules
        
        invalid_tags = [t for t in tags if t not in all_valid]
        
        return len(invalid_tags) == 0, invalid_tags
    
    def save_tag_rules(self, file_path: str = None) -> str:
        """
        保存标签规则
        
        Args:
            file_path: 文件路径（默认保存到规则目录）
            
        Returns:
            str: 保存的文件路径
        """
        if not file_path and self.rules_dir:
            file_path = str(self.rules_dir / self.DEFAULT_TAG_RULES_FILE)
        elif not file_path:
            raise ValueError("未指定文件路径")
        
        rules_data = {
            "version": "1.0",
            "created_at": datetime.now().isoformat(),
            "rules": [
                {
                    "name": rule.name,
                    "description": rule.description,
                    "keywords": rule.keywords,
                    "patterns": rule.patterns,
                    "category": rule.category,
                    "priority": rule.priority,
                    "exclusive": rule.exclusive
                }
                for rule in self.custom_rules
            ]
        }
        
        import yaml
        with open(file_path, 'w', encoding='utf-8') as f:
            yaml.dump(rules_data, f, allow_unicode=True, indent=2)
        
        logger.info(f"标签规则已保存: {file_path}")
        return file_path


# ============ 便捷函数 ============

_default_tagger: Optional[Tagger] = None


def get_tagger(rules_dir: str = None) -> Tagger:
    """
    获取 Tagger 实例
    
    Args:
        rules_dir: 规则目录
        
    Returns:
        Tagger: 实例
    """
    global _default_tagger
    if _default_tagger is None:
        _default_tagger = Tagger(rules_dir)
    return _default_tagger


def tag_conversation(messages: List[Dict], **kwargs) -> Dict:
    """
    为对话添加标签
    
    Args:
        messages: 消息列表
        **kwargs: 其他参数
        
    Returns:
        Dict: 标签结果
    """
    return get_tagger().tag_conversation(messages, **kwargs)


def suggest_tags(content: str, **kwargs) -> List[TagSuggestion]:
    """
    提供标签建议
    
    Args:
        content: 内容
        **kwargs: 其他参数
        
    Returns:
        List[TagSuggestion]: 建议列表
    """
    return get_tagger().suggest_tags(content, **kwargs)


def analyze_tags(tags: List[str]) -> Dict:
    """
    分析标签
    
    Args:
        tags: 标签列表
        
    Returns:
        Dict: 分析结果
    """
    return get_tagger().analyze_tags(tags)


# ============ CLI 入口 ============

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Tagger - 自动标签工具"
    )
    
    subparsers = parser.add_subparsers(dest="command", help="可用命令")
    
    # tag 命令
    tag_parser = subparsers.add_parser("tag", help="为内容添加标签")
    tag_parser.add_argument("content", help="要标签的内容")
    tag_parser.add_argument("--max-tags", "-m", type=int, default=5)
    
    # suggest 命令
    suggest_parser = subparsers.add_parser("suggest", help="标签建议")
    suggest_parser.add_argument("content", help="内容")
    suggest_parser.add_argument("--max", "-n", type=int, default=5)
    
    # analyze 命令
    analyze_parser = subparsers.add_parser("analyze", help="分析标签")
    analyze_parser.add_argument("tags", nargs="+", help="标签列表")
    
    # list 命令
    list_parser = subparsers.add_parser("list", help="列出所有标签")
    list_parser.add_argument("--category", "-c", default=None)
    
    # info 命令
    info_parser = subparsers.add_parser("info", help="查看标签信息")
    info_parser.add_argument("tag", help="标签名")
    
    args = parser.parse_args()
    
    tagger = Tagger()
    
    if args.command == "tag":
        tags = tagger.tag_message(args.content, args.max_tags)
        print(f"标签: {', '.join(tags)}")
    
    elif args.command == "suggest":
        suggestions = tagger.suggest_tags(args.content, args.max)
        print(f"建议:")
        for s in suggestions:
            print(f"  - {s.tag}: {s.score:.2f} ({s.reason})")
            if s.matched_keywords:
                print(f"    匹配: {', '.join(s.matched_keywords[:3])}")
    
    elif args.command == "analyze":
        analysis = tagger.analyze_tags(args.tags)
        print(f"分析结果:")
        print(f"  标签数: {analysis['count']}")
        print(f"  类别: {analysis['categories']}")
        print(f"  重要: {analysis['has_important']}")
        print(f"  决策: {analysis['has_decision']}")
        print(f"  任务: {analysis['has_task']}")
    
    elif args.command == "list":
        tags = tagger.list_tags(args.category)
        print(f"标签 ({len(tags)} 个):")
        for t in tags:
            print(f"  - {t['tag']}: {t.get('description', 'N/A')}")
    
    elif args.command == "info":
        info = tagger.get_tag_info(args.tag)
        if info:
            print(f"标签信息:")
            for k, v in info.items():
                print(f"  {k}: {v}")
        else:
            print(f"未找到标签: {args.tag}")
    
    else:
        parser.print_help()
