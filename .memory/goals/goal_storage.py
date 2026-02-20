"""
目标存储模块
管理目标、里程碑和闭环的系统化存储
"""
import json
import os
from datetime import datetime
from typing import Any, Dict, List, Optional


class GoalStorage:
    """
    目标存储
    
    支持：
    - 年度/季度/月度目标
    - 里程碑管理
    - 闭环检查（日/周/月/季度回顾）
    - 目标进度跟踪
    """
    
    def __init__(self, base_path: str = None):
        self.base_path = base_path or os.path.join(
            os.path.dirname(__file__), 'goals'
        )
        
        # 子目录
        self.annual_path = os.path.join(self.base_path, 'annual')
        self.quarterly_path = os.path.join(self.base_path, 'quarterly')
        self.monthly_path = os.path.join(self.base_path, 'monthly')
        self.milestones_path = os.path.join(self.base_path, 'milestones')
        self.closed_loop_path = os.path.join(self.base_path, '_闭环')
        
        # 确保目录存在
        os.makedirs(self.annual_path, exist_ok=True)
        os.makedirs(self.quarterly_path, exist_ok=True)
        os.makedirs(self.monthly_path, exist_ok=True)
        os.makedirs(self.milestones_path, exist_ok=True)
        os.makedirs(os.path.join(self.closed_loop_path, 'daily_checkin'), exist_ok=True)
        os.makedirs(os.path.join(self.closed_loop_path, 'weekly_review'), exist_ok=True)
        os.makedirs(os.path.join(self.closed_loop_path, 'monthly_review'), exist_ok=True)
        os.makedirs(os.path.join(self.closed_loop_path, 'quarterly_review'), exist_ok=True)
    
    # ==================== 目标管理 ====================
    
    def save_annual_goal(
        self,
        year: int,
        goals: List[Dict],
        vision: str = None,
        metadata: Dict = None
    ) -> str:
        """保存年度目标"""
        file_path = os.path.join(self.annual_path, f'{year}.json')
        
        data = {
            "year": year,
            "vision": vision,
            "goals": goals,
            "metadata": metadata or {},
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        }
        
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        return file_path
    
    def save_quarterly_goal(
        self,
        year: int,
        quarter: int,
        goals: List[Dict],
        focus: str = None,
        metadata: Dict = None
    ) -> str:
        """保存季度目标"""
        file_path = os.path.join(self.quarterly_path, f'{year}_Q{quarter}.json')
        
        data = {
            "year": year,
            "quarter": quarter,
            "focus": focus,
            "goals": goals,
            "metadata": metadata or {},
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        }
        
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        return file_path
    
    def save_monthly_goal(
        self,
        year: int,
        month: int,
        goals: List[Dict],
        theme: str = None,
        metadata: Dict = None
    ) -> str:
        """保存月度目标"""
        file_path = os.path.join(
            self.monthly_path, f'{year}-{month:02d}.json'
        )
        
        data = {
            "year": year,
            "month": month,
            "theme": theme,
            "goals": goals,
            "metadata": metadata or {},
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        }
        
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        return file_path
    
    def save_milestone(
        self,
        milestone_id: str,
        title: str,
        description: str,
        target_date: str,
        status: str = 'pending',  # pending/in_progress/completed
        related_goal: str = None,
        metadata: Dict = None
    ) -> str:
        """保存里程碑"""
        file_path = os.path.join(self.milestones_path, f'{milestone_id}.json')
        
        data = {
            "id": milestone_id,
            "title": title,
            "description": description,
            "target_date": target_date,
            "status": status,
            "related_goal": related_goal,
            "metadata": metadata or {},
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        }
        
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        return file_path
    
    # ==================== 闭环管理 ====================
    
    def daily_checkin(
        self,
        date: str = None,
        completed_tasks: List[str] = None,
        reflections: str = None,
        energy_level: int = None,  # 1-10
        tomorrow_plan: List[str] = None
    ) -> str:
        """每日签到"""
        date = date or datetime.now().strftime('%Y-%m-%d')
        file_path = os.path.join(
            self.closed_loop_path, 'daily_checkin', f'{date}.json'
        )
        
        data = {
            "date": date,
            "completed_tasks": completed_tasks or [],
            "reflections": reflections,
            "energy_level": energy_level,
            "tomorrow_plan": tomorrow_plan or [],
            "created_at": datetime.now().isoformat()
        }
        
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        return file_path
    
    def weekly_review(
        self,
        week_start: str,
        accomplishments: List[str] = None,
        challenges: List[str] = None,
        learnings: List[str] = None,
        next_week_focus: List[str] = None
    ) -> str:
        """周回顾"""
        file_path = os.path.join(
            self.closed_loop_path, 'weekly_review', f'{week_start}.json'
        )
        
        data = {
            "week_start": week_start,
            "accomplishments": accomplishments or [],
            "challenges": challenges or [],
            "learnings": learnings or [],
            "next_week_focus": next_week_focus or [],
            "created_at": datetime.now().isoformat()
        }
        
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        return file_path
    
    def monthly_review(
        self,
        year: int,
        month: int,
        achievements: List[str] = None,
        missed: List[str] = None,
        insights: List[str] = None,
        next_month_focus: List[str] = None
    ) -> str:
        """月回顾"""
        file_path = os.path.join(
            self.closed_loop_path, 'monthly_review', f'{year}-{month:02d}.json'
        )
        
        data = {
            "year": year,
            "month": month,
            "achievements": achievements or [],
            "missed": missed or [],
            "insights": insights or [],
            "next_month_focus": next_month_focus or [],
            "created_at": datetime.now().isoformat()
        }
        
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        return file_path
    
    def quarterly_review(
        self,
        year: int,
        quarter: int,
        wins: List[str] = None,
        losses: List[str] = None,
        adjustments: List[str] = None,
        next_quarter_goals: List[str] = None
    ) -> str:
        """季度回顾"""
        file_path = os.path.join(
            self.closed_loop_path, 'quarterly_review', f'{year}_Q{quarter}.json'
        )
        
        data = {
            "year": year,
            "quarter": quarter,
            "wins": wins or [],
            "losses": losses or [],
            "adjustments": adjustments or [],
            "next_quarter_goals": next_quarter_goals or [],
            "created_at": datetime.now().isoformat()
        }
        
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        return file_path
    
    # ==================== 数据加载 ====================
    
    def load_annual_goal(self, year: int) -> Optional[Dict]:
        """加载年度目标"""
        file_path = os.path.join(self.annual_path, f'{year}.json')
        if not os.path.exists(file_path):
            return None
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def load_quarterly_goal(self, year: int, quarter: int) -> Optional[Dict]:
        """加载季度目标"""
        file_path = os.path.join(
            self.quarterly_path, f'{year}_Q{quarter}.json'
        )
        if not os.path.exists(file_path):
            return None
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def load_monthly_goal(self, year: int, month: int) -> Optional[Dict]:
        """加载月度目标"""
        file_path = os.path.join(
            self.monthly_path, f'{year}-{month:02d}.json'
        )
        if not os.path.exists(file_path):
            return None
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def load_milestone(self, milestone_id: str) -> Optional[Dict]:
        """加载里程碑"""
        file_path = os.path.join(
            self.milestones_path, f'{milestone_id}.json'
        )
        if not os.path.exists(file_path):
            return None
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def load_daily_checkin(self, date: str) -> Optional[Dict]:
        """加载每日签到"""
        file_path = os.path.join(
            self.closed_loop_path, 'daily_checkin', f'{date}.json'
        )
        if not os.path.exists(file_path):
            return None
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def load_weekly_review(self, week_start: str) -> Optional[Dict]:
        """加载周回顾"""
        file_path = os.path.join(
            self.closed_loop_path, 'weekly_review', f'{week_start}.json'
        )
        if not os.path.exists(file_path):
            return None
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def load_monthly_review(self, year: int, month: int) -> Optional[Dict]:
        """加载月回顾"""
        file_path = os.path.join(
            self.closed_loop_path, 'monthly_review', f'{year}-{month:02d}.json'
        )
        if not os.path.exists(file_path):
            return None
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def load_quarterly_review(self, year: int, quarter: int) -> Optional[Dict]:
        """加载季度回顾"""
        file_path = os.path.join(
            self.closed_loop_path, 'quarterly_review', f'{year}_Q{quarter}.json'
        )
        if not os.path.exists(file_path):
            return None
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    # ==================== 统计信息 ====================
    
    def get_stats(self) -> Dict:
        """获取统计信息"""
        now = datetime.now()
        
        return {
            "annual_goal": self.load_annual_goal(now.year) is not None,
            "quarterly_goal": self.load_quarterly_goal(now.year, (now.month - 1) // 3 + 1) is not None,
            "monthly_goal": self.load_monthly_goal(now.year, now.month) is not None,
            "milestones": len([
                f for f in os.listdir(self.milestones_path) if f.endswith('.json')
            ]),
            "today_checkin": self.load_daily_checkin(now.strftime('%Y-%m-%d')) is not None,
            "weekly_review": len([
                f for f in os.listdir(
                    os.path.join(self.closed_loop_path, 'weekly_review')
                ) if f.endswith('.json')
            ]),
            "monthly_review": len([
                f for f in os.listdir(
                    os.path.join(self.closed_loop_path, 'monthly_review')
                ) if f.endswith('.json')
            ])
        }


# 全局实例
_goal_storage = None

def get_goal_storage(base_path: str = None) -> GoalStorage:
    """获取目标存储实例"""
    global _goal_storage
    if _goal_storage is None:
        _goal_storage = GoalStorage(base_path)
    return _goal_storage
