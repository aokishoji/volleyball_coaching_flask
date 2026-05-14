from datetime import datetime
from flask import Blueprint, render_template
from flask_login import login_required, current_user
from ..models import DailyPracticeTheme, Goal, GoalMilestone, PracticeTheme, Reflection
from ..services.goal_progress_service import current_month_index, practice_focus_list

main_bp = Blueprint("main", __name__)

@main_bp.route("/")
@login_required
def home():
    latest_goal = Goal.query.filter_by(user_id=current_user.id, status="active").order_by(Goal.updated_at.desc()).first()
    latest_theme = PracticeTheme.query.filter_by(user_id=current_user.id).order_by(PracticeTheme.created_at.desc()).first()
    latest_daily_theme = DailyPracticeTheme.query.filter_by(user_id=current_user.id).order_by(DailyPracticeTheme.created_at.desc()).first()
    latest_reflection = Reflection.query.filter_by(user_id=current_user.id).order_by(Reflection.created_at.desc()).first()
    current_milestone = None
    current_practice_focus = []
    current_month = None
    if latest_goal:
        current_month = current_month_index(latest_goal)
        current_milestone = GoalMilestone.query.filter_by(
            goal_id=latest_goal.id,
            month_index=current_month,
        ).first()
        current_practice_focus = practice_focus_list(current_milestone)

    days_on_theme = None
    if latest_daily_theme:
        days_on_theme = (datetime.utcnow().date() - latest_daily_theme.created_at.date()).days + 1

    return render_template(
        "main/home.html",
        latest_goal=latest_goal,
        latest_theme=latest_theme,
        latest_daily_theme=latest_daily_theme,
        latest_reflection=latest_reflection,
        current_month=current_month,
        current_milestone=current_milestone,
        current_practice_focus=current_practice_focus,
        days_on_theme=days_on_theme,
    )
