from datetime import datetime
from flask import Blueprint, render_template
from flask_login import login_required, current_user
from ..models import DailyPracticeTheme, Goal, GoalMilestone, PracticeTheme, Reflection
from ..services.goal_progress_service import current_month_index, practice_focus_list
from ..forms import SKILL_TYPE_LABELS

main_bp = Blueprint("main", __name__)

@main_bp.route("/manual")
def manual():
    return render_template("manual/index.html")

@main_bp.route("/")
@login_required
def home():
    active_goals = (
        Goal.query
        .filter_by(user_id=current_user.id, status="active")
        .order_by(Goal.updated_at.desc())
        .all()
    )

    goal_contexts = []
    for goal in active_goals:
        cm = current_month_index(goal)
        milestone = GoalMilestone.query.filter_by(
            goal_id=goal.id, month_index=cm
        ).first()
        focus = practice_focus_list(milestone)
        daily_theme = (
            DailyPracticeTheme.query
            .filter_by(goal_id=goal.id)
            .order_by(DailyPracticeTheme.created_at.desc())
            .first()
        )
        days = None
        if daily_theme:
            days = (datetime.utcnow().date() - daily_theme.created_at.date()).days + 1
        latest_reflection = (
            Reflection.query
            .join(DailyPracticeTheme, Reflection.daily_theme_id == DailyPracticeTheme.id)
            .filter(DailyPracticeTheme.goal_id == goal.id)
            .order_by(Reflection.created_at.desc())
            .first()
        )
        goal_contexts.append({
            "goal": goal,
            "current_month": cm,
            "current_milestone": milestone,
            "current_practice_focus": focus,
            "latest_daily_theme": daily_theme,
            "days_on_theme": days,
            "latest_reflection": latest_reflection,
        })

    return render_template(
        "main/home.html",
        goal_contexts=goal_contexts,
        skill_type_labels=SKILL_TYPE_LABELS,
    )
