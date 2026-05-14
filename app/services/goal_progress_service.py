import json
from datetime import datetime

from ..models import DailyPracticeTheme, GoalMilestone

def current_month_index(goal) -> int:
    elapsed_days = (datetime.utcnow() - goal.created_at).days
    if elapsed_days < 30:
        return 1
    if elapsed_days < 60:
        return 2
    return 3

def practice_focus_list(milestone: GoalMilestone | None) -> list[str]:
    if not milestone:
        return []
    try:
        data = json.loads(milestone.practice_focus_json or "[]")
        return data if isinstance(data, list) else []
    except json.JSONDecodeError:
        return []

def build_today_theme(user_id: int, goal, milestone: GoalMilestone | None) -> DailyPracticeTheme:
    focus = practice_focus_list(milestone)
    main_focus = focus[0] if focus else "今日の練習で目標につながる行動を1つ決める"
    month_label = f"{milestone.month_index}か月目" if milestone else "現在"

    detail_parts = [
        f"{month_label}の目標: {milestone.title if milestone else goal.goal_title}",
        f"今日の意識: {main_focus}",
    ]
    if milestone and milestone.ok_criteria:
        detail_parts.append(f"OK基準: {milestone.ok_criteria}")
    if len(focus) > 1:
        detail_parts.append("補助ポイント: " + " / ".join(focus[1:]))

    return DailyPracticeTheme(
        user_id=user_id,
        goal_id=goal.id,
        milestone_id=milestone.id if milestone else None,
        theme_title=f"今日のテーマ: {main_focus}",
        theme_detail="\n".join(detail_parts),
        check_point="練習後に、できた場面・崩れた場面・次回の修正点を1つずつ書く",
    )
