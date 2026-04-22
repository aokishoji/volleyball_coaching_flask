from flask import Blueprint, render_template
from flask_login import login_required, current_user
from ..models import Goal, PracticeTheme, Reflection

main_bp = Blueprint("main", __name__)

@main_bp.route("/")
@login_required
def home():
    latest_goal = Goal.query.filter_by(user_id=current_user.id, status="active").order_by(Goal.updated_at.desc()).first()
    latest_theme = PracticeTheme.query.filter_by(user_id=current_user.id).order_by(PracticeTheme.created_at.desc()).first()
    latest_reflection = Reflection.query.filter_by(user_id=current_user.id).order_by(Reflection.created_at.desc()).first()
    return render_template(
        "main/home.html",
        latest_goal=latest_goal,
        latest_theme=latest_theme,
        latest_reflection=latest_reflection,
    )
