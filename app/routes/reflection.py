from flask import Blueprint, render_template, redirect, url_for, flash
from flask_login import login_required, current_user
from ..extensions import db
from ..forms import ReflectionForm, SKILL_TYPE_LABELS
from ..models import PracticeTheme, DailyPracticeTheme, Reflection, Goal

reflection_bp = Blueprint("reflection", __name__)

@reflection_bp.route("/new", methods=["GET", "POST"])
@login_required
def new_reflection():
    latest_daily_theme = (
        DailyPracticeTheme.query
        .filter_by(user_id=current_user.id)
        .order_by(DailyPracticeTheme.created_at.desc())
        .first()
    )
    latest_practice_theme = (
        PracticeTheme.query
        .filter_by(user_id=current_user.id)
        .order_by(PracticeTheme.created_at.desc())
        .first()
    )

    active_theme = latest_daily_theme or latest_practice_theme
    if not active_theme:
        flash("先に今日の練習テーマを作成してください。", "warning")
        return redirect(url_for("main.home"))

    form = ReflectionForm()
    if form.validate_on_submit():
        reflection = Reflection(
            user_id=current_user.id,
            practice_theme_id=latest_practice_theme.id if latest_practice_theme and not latest_daily_theme else None,
            daily_theme_id=latest_daily_theme.id if latest_daily_theme else None,
            theme_applied=form.theme_applied.data,
            good_points=form.good_points.data,
            bad_points=form.bad_points.data,
            cause_hypothesis=form.cause_hypothesis.data,
            next_action=form.next_action.data,
            coach_question=form.coach_question.data,
        )
        db.session.add(reflection)
        db.session.commit()
        flash("振り返りを保存しました。", "success")
        return redirect(url_for("reflection.logs"))

    return render_template("reflection/new.html", form=form, latest_theme=active_theme)

@reflection_bp.route("/logs")
@login_required
def logs():
    goals = (
        Goal.query
        .filter_by(user_id=current_user.id)
        .order_by(Goal.created_at.desc())
        .all()
    )

    # スキル別にグループ化（active→archived の順で最初に出てきた skill_type を優先）
    skill_order = []
    skill_goals = {}
    for goal in goals:
        st = goal.skill_type or "other"
        if st not in skill_goals:
            skill_order.append(st)
            skill_goals[st] = []
        skill_goals[st].append(goal)

    skill_tabs = []
    for st in skill_order:
        goals_data = []
        for goal in skill_goals[st]:
            daily_themes = (
                DailyPracticeTheme.query
                .filter_by(goal_id=goal.id)
                .order_by(DailyPracticeTheme.created_at.desc())
                .all()
            )
            goals_data.append({
                "goal": goal,
                "daily_themes": daily_themes,
            })
        skill_tabs.append({
            "skill_type": st,
            "goals_data": goals_data,
        })

    return render_template(
        "reflection/logs.html",
        skill_tabs=skill_tabs,
        skill_type_labels=SKILL_TYPE_LABELS,
    )
