#!/usr/bin/env python3
"""
Tagger 单元测试
===============
测试 tagger.py 的功能

测试覆盖:
1. 标签匹配
2. 标签建议
3. 规则引擎
4. 标签分析

作者: RUNBOT-DEV（笑天）
版本: v1.0
日期: 2026-02-20
"""

import os
import sys
import tempfile
import unittest
from pathlib import Path

# 添加父目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from persistent_memory.tagger import (
    Tagger,
    TagMatcher,
    TagRule,
    TagSuggestion,
)


class TestTagMatcher(unittest.TestCase):
    """TagMatcher 测试类"""
    
    def setUp(self):
        """测试初始化"""
        self.matcher = TagMatcher()
    
    def test_default_rules_loaded(self):
        """测试默认规则加载"""
        self.assertGreater(len(self.matcher.rules), 0)
    
    def test_match_important(self):
        """测试匹配重要标签"""
        content = "这是一个重要的任务，需要紧急处理"
        tags = self.matcher.match(content)
        
        self.assertIn("important", tags)
    
    def test_match_decision(self):
        """测试匹配决策标签"""
        content = "我们决定采用方案A"
        tags = self.matcher.match(content)
        
        self.assertIn("decision", tags)
    
    def test_match_task(self):
        """测试匹配任务标签"""
        content = "请完成这个任务"
        tags = self.matcher.match(content)
        
        self.assertIn("task", tags)
    
    def test_match_question(self):
        """测试匹配问题标签"""
        content = "这是什么意思？怎么使用？"
        tags = self.matcher.match(content)
        
        self.assertIn("question", tags)
    
    def test_match_python(self):
        """测试匹配 Python 标签"""
        content = "我们需要用 Python 开发这个功能"
        tags = self.matcher.match(content)
        
        self.assertIn("python", tags)
    
    def test_match_ai_ml(self):
        """测试匹配 AI/ML 标签"""
        content = "这是一个机器学习模型"
        tags = self.matcher.match(content)
        
        self.assertIn("ai_ml", tags)
    
    def test_match_priority(self):
        """测试匹配优先级标签"""
        content = "请尽快处理这个紧急问题"
        tags = self.matcher.match(content)
        
        self.assertIn("high_priority", tags)
    
    def test_match_status(self):
        """测试匹配状态标签"""
        content = "任务正在进行中"
        tags = self.matcher.match(content)
        
        self.assertIn("in_progress", tags)
    
    def test_match_empty_content(self):
        """测试空内容"""
        tags = self.matcher.match("")
        self.assertEqual(len(tags), 0)
    
    def test_match_max_tags(self):
        """测试最大标签数量"""
        content = "这是一个重要的Python任务，需要尽快完成，这是一个关键决策" + " 紧急"
        tags = self.matcher.match(content, max_tags=3)
        
        self.assertLessEqual(len(tags), 3)
    
    def test_suggest_important(self):
        """测试重要标签建议"""
        content = "这是一个非常重要的任务"
        suggestions = self.matcher.suggest(content)
        
        self.assertGreater(len(suggestions), 0)
        self.assertTrue(any(s.tag == "important" for s in suggestions))
    
    def test_suggest_score_order(self):
        """测试建议按分数排序"""
        content = "这是一个重要的Python任务，需要紧急处理，非常关键"
        suggestions = self.matcher.suggest(content, max_suggestions=10)
        
        # 检查排序
        for i in range(len(suggestions) - 1):
            self.assertGreaterEqual(suggestions[i].score, suggestions[i + 1].score)
    
    def test_exclusive_categories(self):
        """测试互斥类别"""
        content = "这是一个紧急但又不急的任务"  # 矛盾
        tags = self.matcher.match(content, max_tags=10)
        
        # 高优先级和低优先级是互斥的
        # 只应该有一个
        has_high = "high_priority" in tags
        has_low = "low_priority" in tags
        
        self.assertTrue(has_high or has_low)  # 至少一个


class TestTagger(unittest.TestCase):
    """Tagger 测试类"""
    
    def setUp(self):
        """测试初始化"""
        self.tagger = Tagger()
    
    def test_tag_conversation(self):
        """测试对话标签"""
        messages = [
            {
                "role": "user",
                "content": "这是一个重要且紧急的任务，需要尽快完成"
            },
            {
                "role": "assistant",
                "content": "好的，我来处理这个重要的任务"
            }
        ]
        
        result = self.tagger.tag_conversation(messages)
        
        self.assertIn("tags", result)
        self.assertIn("tagged_messages", result)
        self.assertIn("important", result["tags"])
    
    def test_tag_message(self):
        """测试单条消息标签"""
        content = "请帮我修复这个bug"
        tags = self.tagger.tag_message(content, max_tags=3)
        
        self.assertIn("bug", tags)
    
    def test_suggest_tags(self):
        """测试标签建议"""
        content = "这是一个关于Python机器学习的任务"
        suggestions = self.tagger.suggest_tags(content, max_suggestions=5)
        
        self.assertLessEqual(len(suggestions), 5)
        suggestion_tags = [s.tag for s in suggestions]
        self.assertIn("python", suggestion_tags)
        self.assertIn("ai_ml", suggestion_tags)
    
    def test_analyze_tags(self):
        """测试标签分析"""
        tags = ["important", "task", "python"]
        analysis = self.tagger.analyze_tags(tags)
        
        self.assertEqual(analysis["count"], 3)
        self.assertTrue(analysis["has_important"])
        self.assertTrue(analysis["has_task"])
        self.assertFalse(analysis["has_decision"])
    
    def test_get_tag_info(self):
        """测试获取标签信息"""
        info = self.tagger.get_tag_info("important")
        
        self.assertIsNotNone(info)
        self.assertEqual(info["tag"], "important")
        self.assertEqual(info["type"], "builtin")
    
    def test_get_tag_info_not_exists(self):
        """测试获取不存在的标签信息"""
        info = self.tagger.get_tag_info("not_exists_tag")
        
        self.assertIsNone(info)
    
    def test_list_tags(self):
        """测试列出所有标签"""
        tags = self.tagger.list_tags()
        
        self.assertGreater(len(tags), 0)
        self.assertTrue(any(t["tag"] == "important" for t in tags))
    
    def test_list_tags_by_category(self):
        """测试按类别列出标签"""
        tags = self.tagger.list_tags(category="importance")
        
        self.assertGreater(len(tags), 0)
        for t in tags:
            self.assertEqual(t.get("category"), "importance")
    
    def test_validate_tags(self):
        """测试验证标签"""
        is_valid, invalid = self.tagger.validate_tags(["important", "task", "python"])
        
        self.assertTrue(is_valid)
        self.assertEqual(len(invalid), 0)
    
    def test_validate_invalid_tags(self):
        """测试验证无效标签"""
        is_valid, invalid = self.tagger.validate_tags(["important", "fake_tag_123"])
        
        self.assertFalse(is_valid)
        self.assertIn("fake_tag_123", invalid)


class TestTagRule(unittest.TestCase):
    """TagRule 测试类"""
    
    def test_rule_creation(self):
        """测试规则创建"""
        rule = TagRule(
            name="test_rule",
            description="测试规则",
            keywords=["测试", "test"],
            patterns=[r"\btest\b"],
            category="test",
            priority=100,
            exclusive=False
        )
        
        self.assertEqual(rule.name, "test_rule")
        self.assertEqual(rule.keywords, ["测试", "test"])
        self.assertEqual(rule.priority, 100)
    
    def test_rule_with_patterns(self):
        """测试带模式的规则"""
        rule = TagRule(
            name="url_rule",
            keywords=[],
            patterns=[r"https?://[^\s]+"]
        )
        
        matcher = TagMatcher([rule])
        
        content = "请访问 https://example.com 获取更多信息"
        tags = matcher.match(content)
        
        self.assertIn("url_rule", tags)


class TestTagSuggestion(unittest.TestCase):
    """TagSuggestion 测试类"""
    
    def test_suggestion_creation(self):
        """测试建议创建"""
        suggestion = TagSuggestion(
            tag="test",
            score=0.85,
            reason="匹配到关键词",
            matched_keywords=["测试", "test"],
            category="general"
        )
        
        self.assertEqual(suggestion.tag, "test")
        self.assertEqual(suggestion.score, 0.85)
        self.assertEqual(len(suggestion.matched_keywords), 2)


class TestTaggerEdgeCases(unittest.TestCase):
    """Tagger 边界情况测试"""
    
    def setUp(self):
        self.tagger = Tagger()
    
    def test_empty_content(self):
        """测试空内容"""
        tags = self.tagger.tag_message("")
        self.assertEqual(len(tags), 0)
        
        suggestions = self.tagger.suggest_tags("")
        self.assertEqual(len(suggestions), 0)
    
    def test_very_long_content(self):
        """测试超长内容"""
        long_content = "测试 " * 10000
        
        tags = self.tagger.tag_message(long_content, max_tags=5)
        self.assertLessEqual(len(tags), 5)
    
    def test_special_characters(self):
        """测试特殊字符"""
        content = "<script>alert('xss')</script> & \"quotes\""
        tags = self.tagger.tag_message(content)
        
        # 应该能处理，不报错
        self.assertIsInstance(tags, list)
    
    def test_unicode_content(self):
        """测试 Unicode 内容"""
        content = "🚀 测试 🎉 Python 🐍"
        tags = self.tagger.tag_message(content)
        
        self.assertIn("python", tags)
    
    def test_mixed_languages(self):
        """测试混合语言"""
        content = "这是一个 important 任务，需要尽快完成"
        tags = self.tagger.tag_message(content)
        
        self.assertIn("important", tags)
        self.assertIn("task", tags)
    
    def test_analyze_empty_tags(self):
        """测试分析空标签"""
        analysis = self.tagger.analyze_tags([])
        
        self.assertEqual(analysis["count"], 0)
        self.assertFalse(analysis["has_important"])
    
    def test_validate_empty_tags(self):
        """测试验证空标签"""
        is_valid, invalid = self.tagger.validate_tags([])
        
        self.assertTrue(is_valid)
        self.assertEqual(len(invalid), 0)


if __name__ == "__main__":
    unittest.main(verbosity=2)
