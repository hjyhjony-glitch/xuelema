#!/usr/bin/env python3
"""
Summarizer - 摘要生成模块
=========================
为对话生成简洁的摘要

功能:
1. 提取关键信息
2. 生成对话摘要
3. 提取action items
4. 生成结构化总结

作者: RUNBOT-DEV（笑天）
版本: v1.0
日期: 2026-02-20
"""

import json
import logging
import re
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple
from collections import Counter

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@dataclass
class Summary:
    """摘要数据类"""
    title: str = ""
    brief: str = ""  # 简短摘要
    full: str = ""  # 完整摘要
    topics: List[str] = field(default_factory=list)
    action_items: List[str] = field(default_factory=list)
    decisions: List[str] = field(default_factory=list)
    key_points: List[str] = field(default_factory=list)
    participants: List[str] = field(default_factory=list)
    sentiment: str = "neutral"  # positive, negative, neutral
    urgency: str = "normal"  # low, normal, high
    word_count: int = 0
    generated_at: str = field(default_factory=lambda: datetime.now().isoformat())


@dataclass
class ActionItem:
    """待办事项数据类"""
    description: str
    assignee: Optional[str] = None
    due_date: Optional[str] = None
    priority: str = "medium"
    completed: bool = False


class Summarizer:
    """
    摘要生成器
    
    功能:
    1. 生成对话摘要
    2. 提取待办事项
    3. 提取关键决策
    4. 分析对话主题
    """
    
    def __init__(self):
        """初始化 Summarizer"""
        # 停止词列表
        self._stop_words = set([
            "的", "了", "是", "在", "和", "有", "就", "不", "都", "也",
            "我", "你", "他", "她", "它", "们", "这", "那", "要", "会",
            "可以", "可能", "应该", "要", "到", "说", "一个", "什么",
            "the", "a", "an", "is", "are", "was", "were", "be", "been",
            "being", "have", "has", "had", "do", "does", "did", "will",
            "would", "could", "should", "may", "might", "must", "shall",
            "can", "need", "dare", "ought", "used", "to", "of", "in",
            "for", "on", "with", "at", "by", "from", "as", "into",
            "through", "during", "before", "after", "above", "below",
            "between", "under", "again", "further", "then", "once"
        ])
        
        # 行动词列表（用于提取action items）
        self._action_verbs = [
            "做", "完成", "执行", "处理", "修复", "更新", "创建", "添加",
            "修改", "测试", "部署", "检查", "审核", "review", "check",
            "do", "make", "create", "add", "update", "delete", "remove",
            "fix", "test", "deploy", "review", "analyze", "design",
            "implement", "document", "write", "read", "send", "reply"
        ]
        
        # 决策关键词
        self._decision_keywords = [
            "决定", "确定", "就这么办", "同意", "批准", "采纳",
            "decision", "decided", "agreed", "approved", "accepted",
            "选择", "选定", "决定用"
        ]
        
        logger.info("Summarizer 初始化完成")
    
    def summarize(
        self,
        messages: List[Dict[str, Any]],
        options: Dict[str, bool] = None
    ) -> Summary:
        """
        生成对话摘要
        
        Args:
            messages: 消息列表
            options: 选项
                - extract_actions: 提取待办事项 (default: True)
                - extract_decisions: 提取决策 (default: True)
                - analyze_topics: 分析主题 (default: True)
                - max_summary_length: 最大摘要长度 (default: 500)
                
        Returns:
            Summary: 摘要对象
        """
        options = options or {}
        extract_actions = options.get("extract_actions", True)
        extract_decisions = options.get("extract_decisions", True)
        analyze_topics = options.get("analyze_topics", True)
        max_summary_length = options.get("max_summary_length", 500)
        
        if not messages:
            return Summary(
                title="空对话",
                brief="没有消息",
                full="没有消息可摘要"
            )
        
        # 提取基本信息
        participants = self._extract_participants(messages)
        
        # 合并消息内容
        all_content = " ".join([msg.get("content", "") for msg in messages])
        
        # 生成标题
        title = self._generate_title(messages, participants)
        
        # 生成简短摘要
        brief = self._generate_brief_summary(messages, max_summary_length)
        
        # 生成完整摘要
        full = self._generate_full_summary(messages, participants)
        
        # 创建摘要对象
        summary = Summary(
            title=title,
            brief=brief,
            full=full,
            participants=participants,
            word_count=len(all_content)
        )
        
        # 提取待办事项
        if extract_actions:
            summary.action_items = self._extract_action_items(messages)
        
        # 提取决策
        if extract_decisions:
            summary.decisions = self._extract_decisions(messages)
        
        # 分析主题
        if analyze_topics:
            summary.topics = self._analyze_topics(messages)
            summary.key_points = self._extract_key_points(messages)
        
        # 分析紧急程度
        summary.urgency = self._analyze_urgency(messages)
        
        # 分析情感
        summary.sentiment = self._analyze_sentiment(messages)
        
        return summary
    
    def _extract_participants(self, messages: List[Dict[str, Any]]) -> List[str]:
        """
        提取参与者
        
        Args:
            messages: 消息列表
            
        Returns:
            List[str]: 参与者列表
        """
        participants = set()
        
        for msg in messages:
            role = msg.get("role", "")
            sender_name = msg.get("sender_name", "")
            
            if role == "user":
                if sender_name:
                    participants.add(sender_name)
                else:
                    participants.add("用户")
            elif role == "assistant":
                participants.add("助手")
            elif role == "system":
                participants.add("系统")
        
        return list(participants)
    
    def _generate_title(
        self,
        messages: List[Dict[str, Any]],
        participants: List[str]
    ) -> str:
        """
        生成标题
        
        Args:
            messages: 消息列表
            participants: 参与者列表
            
        Returns:
            str: 标题
        """
        # 提取第一条用户消息作为标题
        for msg in messages:
            if msg.get("role") == "user":
                content = msg.get("content", "")
                # 截取前30个字符
                title = content[:30].strip()
                if len(content) > 30:
                    title += "..."
                return title
        
        # 如果没有用户消息，使用参与者
        if participants:
            return f"与 {', '.join(participants[:2])} 的对话"
        
        return "对话摘要"
    
    def _generate_brief_summary(
        self,
        messages: List[Dict[str, Any]],
        max_length: int = 500
    ) -> str:
        """
        生成简短摘要
        
        Args:
            messages: 消息列表
            max_length: 最大长度
            
        Returns:
            str: 简短摘要
        """
        if not messages:
            return "没有消息"
        
        # 收集关键信息
        key_contents = []
        
        for msg in messages:
            role = msg.get("role", "")
            content = msg.get("content", "")
            
            if role == "user" and content:
                # 保留用户消息的核心内容
                key_contents.append(content)
            elif role == "assistant" and content:
                # 保留助手回复的核心内容
                # 移除冗长的格式
                lines = content.split("\n")
                key_lines = [l.strip() for l in lines if l.strip() and not l.strip().startswith("- ")]
                key_contents.extend(key_lines[:2])
        
        # 合并
        brief = " ".join(key_contents)
        
        # 截断
        if len(brief) > max_length:
            brief = brief[:max_length].rsplit(" ", 1)[0] + "..."
        
        return brief
    
    def _generate_full_summary(
        self,
        messages: List[Dict[str, Any]],
        participants: List[str]
    ) -> str:
        """
        生成完整摘要
        
        Args:
            messages: 消息列表
            participants: 参与者列表
            
        Returns:
            str: 完整摘要
        """
        lines = []
        
        # 基本信息
        lines.append(f"参与者: {', '.join(participants)}")
        lines.append(f"消息数: {len(messages)}")
        
        # 消息概览
        user_count = sum(1 for m in messages if m.get("role") == "user")
        assistant_count = sum(1 for m in messages if m.get("role") == "assistant")
        lines.append(f"用户消息: {user_count}")
        lines.append(f"助手回复: {assistant_count}")
        
        # 关键内容
        lines.append("")
        lines.append("---")
        lines.append("")
        lines.append("关键内容:")
        
        for i, msg in enumerate(messages[:5], 1):  # 只显示前5条
            role = msg.get("role", "")
            content = msg.get("content", "")
            if content:
                # 截取内容
                display_content = content[:200]
                if len(content) > 200:
                    display_content += "..."
                lines.append(f"{i}. [{role}]: {display_content}")
        
        if len(messages) > 5:
            lines.append(f"... 还有 {len(messages) - 5} 条消息")
        
        return "\n".join(lines)
    
    def _extract_action_items(self, messages: List[Dict[str, Any]]) -> List[str]:
        """
        提取待办事项
        
        Args:
            messages: 消息列表
            
        Returns:
            List[str]: 待办事项列表
        """
        action_items = []
        
        # 匹配模式
        action_patterns = [
            r"(?:需要|要|应该|必须)\s+(.+?)[，。]",
            r"(?:请|帮我|你)\s+(.+?)[，。]",
            r"todo[:：]?\s*(.+)",
            r"待办[:：]?\s*(.+)",
            r"action[:：]?\s*(.+)",
            r"(?:待|要做)\s*(.+?)[。]",
            r"(?:完成|执行)\s*(.+?)[。]",
        ]
        
        for msg in messages:
            content = msg.get("content", "")
            
            for pattern in action_patterns:
                matches = re.findall(pattern, content, re.IGNORECASE)
                for match in matches:
                    item = match.strip()
                    if item and len(item) > 2:
                        action_items.append(item)
        
        # 去重
        return list(set(action_items))
    
    def _extract_decisions(self, messages: List[Dict[str, Any]]) -> List[str]:
        """
        提取决策
        
        Args:
            messages: 消息列表
            
        Returns:
            List[str]: 决策列表
        """
        decisions = []
        
        for msg in messages:
            content = msg.get("content", "")
            
            # 检查决策关键词
            for keyword in self._decision_keywords:
                if keyword in content:
                    # 提取决策内容
                    sentences = re.split(r"[。！？!?.]", content)
                    for sentence in sentences:
                        if keyword in sentence:
                            decision = sentence.strip()
                            if decision and len(decision) > 3:
                                decisions.append(decision)
                    break
        
        # 去重
        return list(set(decisions))
    
    def _analyze_topics(self, messages: List[Dict[str, Any]]) -> List[str]:
        """
        分析主题
        
        Args:
            messages: 消息列表
            
        Returns:
            List[str]: 主题列表
        """
        # 提取所有词汇
        words = []
        for msg in messages:
            content = msg.get("content", "")
            
            # 简单分词（按空格和标点）
            tokens = re.findall(r"[\w]+", content.lower())
            words.extend(tokens)
        
        # 移除停用词
        words = [w for w in words if w not in self._stop_words and len(w) > 1]
        
        # 统计词频
        word_freq = Counter(words)
        
        # 获取高频词
        common_words = word_freq.most_common(10)
        
        # 转换为主题
        topics = []
        topic_keywords = {
            "技术": ["python", "code", "api", "系统", "开发", "编程", "技术"],
            "设计": ["设计", "架构", "方案", "结构", "模式"],
            "项目": ["项目", "计划", "进度", "里程碑", "任务"],
            "文档": ["文档", "说明", "readme", "docs", "文档"],
            "问题": ["问题", "bug", "错误", "修复", "解决"],
            "会议": ["会议", "讨论", "沟通", "同步"],
            "飞书": ["飞书", "feishu", "飞书文档"],
        }
        
        for topic, keywords in topic_keywords.items():
            if any(kw in words for kw in keywords):
                topics.append(topic)
        
        # 如果没有匹配的主题，使用高频词
        if not topics:
            topics = [word for word, _ in common_words[:5]]
        
        return topics[:5]
    
    def _extract_key_points(self, messages: List[Dict[str, Any]]) -> List[str]:
        """
        提取关键点
        
        Args:
            messages: 消息列表
            
        Returns:
            List[str]: 关键点列表
        """
        key_points = []
        
        for msg in messages:
            content = msg.get("content", "")
            role = msg.get("role", "")
            
            # 检查关键信息标记
            key_markers = [
                r"关键[:：]?\s*(.+)",
                r"重要[:：]?\s*(.+)",
                r"要点[:：]?\s*(.+)",
                r"总结[:：]?\s*(.+)",
                r"主要[:：]?\s*(.+)",
            ]
            
            for pattern in key_markers:
                matches = re.findall(pattern, content)
                for match in matches:
                    point = match.strip()
                    if point and len(point) > 3:
                        key_points.append(point)
            
            # 如果是助手回复的核心内容
            if role == "assistant":
                lines = content.split("\n")
                for line in lines:
                    line = line.strip()
                    if line and not line.startswith("-") and not line.startswith("•"):
                        if len(line) > 10 and len(line) < 100:
                            key_points.append(line)
                            break
        
        return list(set(key_points))[:5]
    
    def _analyze_urgency(self, messages: List[Dict[str, Any]]) -> str:
        """
        分析紧急程度
        
        Args:
            messages: 消息列表
            
        Returns:
            str: 紧急程度 (low, normal, high)
        """
        urgency_keywords = {
            "high": ["紧急", "尽快", "马上", "立刻", "asap", "urgent", "immediate", "立刻", "马上"],
            "low": ["有空", "不急", "以后", "later", "when free", "慢慢"]
        }
        
        all_content = " ".join([msg.get("content", "") for msg in messages]).lower()
        
        for keyword in urgency_keywords["high"]:
            if keyword in all_content:
                return "high"
        
        for keyword in urgency_keywords["low"]:
            if keyword in all_content:
                return "low"
        
        return "normal"
    
    def _analyze_sentiment(self, messages: List[Dict[str, Any]]) -> str:
        """
        分析情感
        
        Args:
            messages: 消息列表
            
        Returns:
            str: 情感 (positive, negative, neutral)
        """
        positive_words = ["好", "棒", "优秀", "完美", "谢谢", "感谢", "不错", "好的", "OK", "好的", "👍"]
        negative_words = ["差", "烂", "糟糕", "抱歉", "对不起", "不好意思", "问题", "错误", "Bug"]
        
        all_content = " ".join([msg.get("content", "") for msg in messages])
        
        positive_count = sum(1 for w in positive_words if w in all_content)
        negative_count = sum(1 for w in negative_words if w in all_content)
        
        if positive_count > negative_count:
            return "positive"
        elif negative_count > positive_count:
            return "negative"
        else:
            return "neutral"
    
    def extract_actions_detailed(
        self,
        messages: List[Dict[str, Any]]
    ) -> List[ActionItem]:
        """
        提取详细待办事项
        
        Args:
            messages: 消息列表
            
        Returns:
            List[ActionItem]: 待办事项列表
        """
        action_items = []
        
        for msg in messages:
            content = msg.get("content", "")
            
            # 匹配 "谁 + 什么时候 + 做什么"
            patterns = [
                r"([^\s]+?)\s+(需要|要|应该)\s+(.+?)[，。]",
                r"请\s+([^\s]+?)\s+(.+?)[，。]",
                r"todo[:：]?\s*(.+?)(?:，|。|$)",
                r"待办[:：]?\s*(.+?)(?:，|。|$)",
            ]
            
            for pattern in patterns:
                matches = re.findall(pattern, content)
                for match in matches:
                    if len(match) == 3:
                        assignee, _, description = match
                        action_items.append(ActionItem(
                            description=description.strip(),
                            assignee=assignee.strip() if assignee else None
                        ))
                    elif len(match) == 1:
                        action_items.append(ActionItem(
                            description=match[0].strip()
                        ))
        
        return action_items
    
    def generate_structured_summary(
        self,
        messages: List[Dict[str, Any]],
        format: str = "markdown"
    ) -> str:
        """
        生成结构化摘要
        
        Args:
            messages: 消息列表
            format: 输出格式 (markdown, json)
            
        Returns:
            str: 结构化摘要
        """
        summary = self.summarize(messages)
        
        if format == "json":
            return json.dumps({
                "title": summary.title,
                "brief": summary.brief,
                "full": summary.full,
                "topics": summary.topics,
                "action_items": summary.action_items,
                "decisions": summary.decisions,
                "key_points": summary.key_points,
                "participants": summary.participants,
                "sentiment": summary.sentiment,
                "urgency": summary.urgency,
                "word_count": summary.word_count,
                "generated_at": summary.generated_at
            }, ensure_ascii=False, indent=2)
        
        # Markdown 格式
        lines = [
            f"# {summary.title}",
            "",
            f"**生成时间**: {summary.generated_at}",
            f"**参与者**: {', '.join(summary.participants)}",
            f"**字数**: {summary.word_count}",
            "",
            "---",
            "",
            "## 摘要",
            "",
            summary.brief,
            "",
            "---",
            "",
        ]
        
        if summary.topics:
            lines.extend([
                "## 主题",
                "",
                ", ".join(summary.topics),
                "",
                "---",
                "",
            ])
        
        if summary.action_items:
            lines.extend([
                "## 待办事项",
                "",
            ])
            for i, item in enumerate(summary.action_items, 1):
                lines.append(f"{i}. {item}")
            lines.extend([
                "",
                "---",
                "",
            ])
        
        if summary.decisions:
            lines.extend([
                "## 决策",
                "",
            ])
            for i, decision in enumerate(summary.decisions, 1):
                lines.append(f"{i}. {decision}")
            lines.extend([
                "",
                "---",
                "",
            ])
        
        if summary.key_points:
            lines.extend([
                "## 关键点",
                "",
            ])
            for i, point in enumerate(summary.key_points, 1):
                lines.append(f"{i}. {point}")
            lines.extend([
                "",
                "---",
                "",
            ])
        
        lines.extend([
            "## 详情",
            "",
            summary.full,
        ])
        
        return "\n".join(lines)
    
    def compare_summaries(
        self,
        messages1: List[Dict[str, Any]],
        messages2: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        对比两个对话摘要
        
        Args:
            messages1: 第一组消息
            messages2: 第二组消息
            
        Returns:
            Dict: 对比结果
        """
        summary1 = self.summarize(messages1)
        summary2 = self.summarize(messages2)
        
        return {
            "summary1": {
                "title": summary1.title,
                "topics": summary1.topics,
                "action_count": len(summary1.action_items),
                "decision_count": len(summary1.decisions),
                "urgency": summary1.urgency
            },
            "summary2": {
                "title": summary2.title,
                "topics": summary2.topics,
                "action_count": len(summary2.action_items),
                "decision_count": len(summary2.decisions),
                "urgency": summary2.urgency
            },
            "topics_overlap": list(set(summary1.topics) & set(summary2.topics)),
            "topics_unique_1": list(set(summary1.topics) - set(summary2.topics)),
            "topics_unique_2": list(set(summary2.topics) - set(summary1.topics)),
        }


# ============ 便捷函数 ============

_default_summarizer: Optional[Summarizer] = None


def get_summarizer() -> Summarizer:
    """获取 Summarizer 实例"""
    global _default_summarizer
    if _default_summarizer is None:
        _default_summarizer = Summarizer()
    return _default_summarizer


def summarize(messages: List[Dict], **kwargs) -> Summary:
    """
    生成对话摘要
    
    Args:
        messages: 消息列表
        **kwargs: 其他参数
        
    Returns:
        Summary: 摘要对象
    """
    return get_summarizer().summarize(messages, kwargs)


def generate_structured_summary(messages: List[Dict], format: str = "markdown") -> str:
    """
    生成结构化摘要
    
    Args:
        messages: 消息列表
        format: 输出格式
        
    Returns:
        str: 摘要文本
    """
    return get_summarizer().generate_structured_summary(messages, format)


# ============ CLI 入口 ============

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Summarizer - 摘要生成工具"
    )
    
    subparsers = parser.add_subparsers(dest="command", help="可用命令")
    
    # summarize 命令
    summarize_parser = subparsers.add_parser("summarize", help="生成摘要")
    summarize_parser.add_argument(
        "--input", "-i",
        required=True,
        help="输入文件路径 (JSON格式的对话文件)"
    )
    summarize_parser.add_argument(
        "--output", "-o",
        default=None,
        help="输出文件路径"
    )
    summarize_parser.add_argument(
        "--format", "-f",
        choices=["markdown", "json"],
        default="markdown",
        help="输出格式"
    )
    
    # extract 命令
    extract_parser = subparsers.add_parser("extract", help="提取待办事项")
    extract_parser.add_argument(
        "--input", "-i",
        required=True,
        help="输入文件路径"
    )
    
    # compare 命令
    compare_parser = subparsers.add_parser("compare", help="对比摘要")
    compare_parser.add_argument(
        "--input1", "-1",
        required=True,
        help="第一个对话文件"
    )
    compare_parser.add_argument(
        "--input2", "-2",
        required=True,
        help="第二个对话文件"
    )
    
    args = parser.parse_args()
    
    summarizer = Summarizer()
    
    if args.command == "summarize":
        with open(args.input, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        messages = data.get("messages", [])
        result = summarizer.generate_structured_summary(messages, args.format)
        
        if args.output:
            with open(args.output, 'w', encoding='utf-8') as f:
                f.write(result)
            print(f"✓ 摘要已保存: {args.output}")
        else:
            print(result)
    
    elif args.command == "extract":
        with open(args.input, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        messages = data.get("messages", [])
        action_items = summarizer.extract_actions_detailed(messages)
        
        print(f"找到 {len(action_items)} 个待办事项:")
        for i, item in enumerate(action_items, 1):
            print(f"{i}. {item.description}")
            if item.assignee:
                print(f"   负责人: {item.assignee}")
    
    elif args.command == "compare":
        with open(args.input1, 'r', encoding='utf-8') as f:
            data1 = json.load(f)
        with open(args.input2, 'r', encoding='utf-8') as f:
            data2 = json.load(f)
        
        messages1 = data1.get("messages", [])
        messages2 = data2.get("messages", [])
        
        comparison = summarizer.compare_summaries(messages1, messages2)
        
        print("对比结果:")
        print(f"  对话1: {comparison['summary1']['title']}")
        print(f"    主题: {comparison['summary1']['topics']}")
        print(f"    待办: {comparison['summary1']['action_count']}")
        print(f"  对话2: {comparison['summary2']['title']}")
        print(f"    主题: {comparison['summary2']['topics']}")
        print(f"    待办: {comparison['summary2']['action_count']}")
        print(f"  共同主题: {comparison['topics_overlap']}")
    
    else:
        parser.print_help()
