from flask import Blueprint, render_template, redirect, url_for, flash
from flask_login import login_required, current_user
from ..extensions import db
from ..forms import GoalForm
from ..models import Goal
from ..services.goal_service import build_goal_text

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
