"""
决策存储模块
管理重要决策的持久化和检索
"""
import json
import os
from datetime import datetime
from typing import Any, Dict, List, Optional


class DecisionStorage:
    """
    决策存储
    
    支持：
    - 决策记录（标题、选项、结果、影响范围）
    - 决策过程追溯
    - 决策效果评估
    - 按时间/标签检索
    """
    
    def __init__(self, base_path: str = None):
        self.base_path = base_path or os.path.join(
            os.path.dirname(__file__), 'decisions'
        )
        
        # 确保目录存在
        os.makedirs(self.base_path, exist_ok=True)
        
        # 决策文件
        self.decisions_file = os.path.join(self.base_path, 'decisions.json')
        self.effects_file = os.path.join(self.base_path, 'effects.json')
    
    # ==================== 决策管理 ====================
    
    def save_decision(
        self,
        decision_id: str,
        title: str,
        problem: str,
        options: List[Dict],  # [{"option": "...", "pros": [...], "cons": [...]}]
        chosen_option: str,
        reason: str,
        expected_outcome: str,
        impact_scope: str = 'team',  # personal/team/project/organization
        impact_duration: str = 'short',  # short/medium/long
        tags: List[str] = None,
        metadata: Dict = None
    ) -> str:
        """
        保存决策
        
        Args:
            decision_id: 决策 ID
            title: 标题
            problem: 问题描述
            options: 选项列表
            chosen_option: 选择的选项
            reason: 选择原因
            expected_outcome: 预期结果
            impact_scope: 影响范围
            impact_duration: 影响时长
            tags: 标签
            metadata: 元数据
        """
        data = {
            "id": decision_id,
            "title": title,
            "problem": problem,
            "options": options,
            "chosen_option": chosen_option,
            "reason": reason,
            "expected_outcome": expected_outcome,
            "impact_scope": impact_scope,
            "impact_duration": impact_duration,
            "tags": tags or [],
            "metadata": metadata or {},
            "status": "active",  # active/revisited/overturned
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        }
        
        # 追加到决策文件
        decisions = self._load_decisions()
        decisions.append(data)
        
        with open(self.decisions_file, 'w', encoding='utf-8') as f:
            json.dump(decisions, f, ensure_ascii=False, indent=2)
        
        return decision_id
    
    def update_decision(
        self,
        decision_id: str,
        status: str = None,
        actual_outcome: str = None,
        lessons_learned: str = None,
        revisit_note: str = None
    ) -> bool:
        """
        更新决策状态
        
        Args:
            decision_id: 决策 ID
            status: 新状态
            actual_outcome: 实际结果
            lessons_learned: 经验教训
            revisit_note: 回顾备注
        """
        decisions = self._load_decisions()
        
        for i, decision in enumerate(decisions):
            if decision["id"] == decision_id:
                if status:
                    decision["status"] = status
                if actual_outcome:
                    decision["actual_outcome"] = actual_outcome
                if lessons_learned:
                    decision["lessons_learned"] = lessons_learned
                if revisit_note:
                    decision["revisit_note"] = revisit_note
                
                decision["updated_at"] = datetime.now().isoformat()
                
                with open(self.decisions_file, 'w', encoding='utf-8') as f:
                    json.dump(decisions, f, ensure_ascii=False, indent=2)
                
                return True
        
        return False
    
    def record_effect(
        self,
        decision_id: str,
        effect_type: str,  # positive/negative/neutral
        description: str,
        evidence: str = None,
        impact_score: int = None  # 1-10
    ) -> str:
        """
        记录决策效果
        
        Args:
            decision_id: 决策 ID
            effect_type: 效果类型
            description: 效果描述
            evidence: 证据
            impact_score: 影响评分
        """
        effect = {
            "id": f"eff_{datetime.now().strftime('%Y%m%d%H%M%S')}",
            "decision_id": decision_id,
            "effect_type": effect_type,
            "description": description,
            "evidence": evidence,
            "impact_score": impact_score,
            "recorded_at": datetime.now().isoformat()
        }
        
        # 追加到效果文件
        effects = self._load_effects()
        effects.append(effect)
        
        with open(self.effects_file, 'w', encoding='utf-8') as f:
            json.dump(effects, f, ensure_ascii=False, indent=2)
        
        return effect["id"]
    
    # ==================== 数据加载 ====================
    
    def _load_decisions(self) -> List[Dict]:
        """加载所有决策"""
        if not os.path.exists(self.decisions_file):
            return []
        
        with open(self.decisions_file, 'r', encoding='utf-8') as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                return []
    
    def _load_effects(self) -> List[Dict]:
        """加载所有效果记录"""
        if not os.path.exists(self.effects_file):
            return []
        
        with open(self.effects_file, 'r', encoding='utf-8') as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                return []
    
    def load_decision(self, decision_id: str) -> Optional[Dict]:
        """加载指定决策"""
        decisions = self._load_decisions()
        
        for decision in decisions:
            if decision["id"] == decision_id:
                return decision
        
        return None
    
    def load_decision_effects(self, decision_id: str) -> List[Dict]:
        """加载指定决策的所有效果"""
        effects = self._load_effects()
        return [e for e in effects if e["decision_id"] == decision_id]
    
    def load_all_decisions(
        self,
        status: str = None,
        impact_scope: str = None,
        tags: List[str] = None,
        limit: int = 100
    ) -> List[Dict]:
        """
        加载所有决策（可筛选）
        
        Args:
            status: 按状态筛选
            impact_scope: 按影响范围筛选
            tags: 按标签筛选
            limit: 返回数量
        """
        decisions = self._load_decisions()
        
        # 筛选
        if status:
            decisions = [d for d in decisions if d["status"] == status]
        
        if impact_scope:
            decisions = [d for d in decisions if d["impact_scope"] == impact_scope]
        
        if tags:
            decisions = [
                d for d in decisions 
                if all(t in d.get("tags", []) for t in tags)
            ]
        
        return decisions[:limit]
    
    # ==================== 搜索 ====================
    
    def search(
        self,
        query: str = None,
        status: str = None,
        impact_scope: str = None,
        impact_duration: str = None,
        start_date: str = None,
        end_date: str = None,
        limit: int = 100
    ) -> List[Dict]:
        """
        搜索决策
        
        Args:
            query: 关键词搜索
            status: 按状态筛选
            impact_scope: 按影响范围筛选
            impact_duration: 按影响时长筛选
            start_date: 开始日期
            end_date: 结束日期
            limit: 返回数量
        """
        decisions = self._load_decisions()
        
        # 筛选
        if query:
            decisions = [
                d for d in decisions 
                if query in json.dumps(d)
            ]
        
        if status:
            decisions = [d for d in decisions if d["status"] == status]
        
        if impact_scope:
            decisions = [d for d in decisions if d["impact_scope"] == impact_scope]
        
        if impact_duration:
            decisions = [d for d in decisions if d["impact_duration"] == impact_duration]
        
        return decisions[:limit]
    
    # ==================== 统计信息 ====================
    
    def get_stats(self) -> Dict:
        """获取统计信息"""
        decisions = self._load_decisions()
        effects = self._load_effects()
        
        # 按状态统计
        status_counts = {}
        for d in decisions:
            status = d.get("status", "unknown")
            status_counts[status] = status_counts.get(status, 0) + 1
        
        # 按影响范围统计
        scope_counts = {}
        for d in decisions:
            scope = d.get("impact_scope", "unknown")
            scope_counts[scope] = scope_counts.get(scope, 0) + 1
        
        # 效果统计
        effect_counts = {"positive": 0, "negative": 0, "neutral": 0}
        for e in effects:
            effect_type = e.get("effect_type", "neutral")
            effect_counts[effect_type] = effect_counts.get(effect_type, 0) + 1
        
        return {
            "total_decisions": len(decisions),
            "by_status": status_counts,
            "by_scope": scope_counts,
            "total_effects": len(effects),
            "effects_by_type": effect_counts
        }
    
    # ==================== 回顾功能 ====================
    
    def get_decisions_for_review(
        self,
        days: int = 30
    ) -> List[Dict]:
        """
        获取需要回顾的决策
        
        Args:
            days: 多少天前的决策需要回顾
        
        Returns:
            List[Dict]: 需要回顾的决策列表
        """
        from datetime import timedelta
        
        cutoff_date = (datetime.now() - timedelta(days=days)).isoformat()
        
        decisions = self._load_decisions()
        
        # 只返回活跃的、超过指定时间的决策
        return [
            d for d in decisions 
            if d["status"] == "active" and d["created_at"] > cutoff_date
        ]


# 全局实例
_decision_storage = None

def get_decision_storage(base_path: str = None) -> DecisionStorage:
    """获取决策存储实例"""
    global _decision_storage
    if _decision_storage is None:
        _decision_storage = DecisionStorage(base_path)
    return _decision_storage
