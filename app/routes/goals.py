from flask import Blueprint, render_template, redirect, url_for, flash
from flask_login import login_required, current_user
from ..extensions import db
from ..forms import GoalForm, GoalRoadmapForm
from ..models import Goal
from ..services.goal_service import build_goal_text, build_goal_roadmap

goals_bp = Blueprint("goals", __name__)

@goals_bp.route("/new", methods=["GET", "POST"])
@login_required
def new_goal():
    form = GoalForm()
    if form.validate_on_submit():
        title, detail = build_goal_text({
            "improve_target": form.improve_target.data,
            "problem_scene": form.problem_scene.data,
            "ideal_state": form.ideal_state.data,
        })

        goal = Goal(
            user_id=current_user.id,
            skill_type=form.skill_type.data,
            goal_title=title,
            goal_detail=detail,
            target_date=form.target_date.data,
            status="active",
        )
        db.session.add(goal)
        db.session.commit()

        flash("目標を保存しました。続けて課題分析を行ってください。", "success")
        return redirect(url_for("analysis.assessment"))

    return render_template("goals/new.html", form=form)

@goals_bp.route("/roadmap", methods=["GET", "POST"])
@login_required
def roadmap():
    form = GoalRoadmapForm()
    if form.validate_on_submit():
        title, detail = build_goal_roadmap({
            "rough_goal": form.rough_goal.data,
            "current_level": form.current_level.data,
            "target_date": form.target_date.data,
            "weekly_practice_days": form.weekly_practice_days.data,
            "focus_hint": form.focus_hint.data,
        })

        goal = Goal(
            user_id=current_user.id,
            skill_type="long_term",
            goal_title=title,
            goal_detail=detail,
            target_date=form.target_date.data,
            status="active",
        )
        db.session.add(goal)
        db.session.commit()

        flash("長期目標を分解して保存しました。次は最初の練習テーマに落とし込みましょう。", "success")
        return redirect(url_for("main.home"))

    return render_template("goals/roadmap.html", form=form)
