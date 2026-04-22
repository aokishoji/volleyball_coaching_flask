from flask import Blueprint, render_template, redirect, url_for, flash
from flask_login import login_required, current_user
from ..extensions import db
from ..forms import ReflectionForm
from ..models import PracticeTheme, Reflection, Goal

reflection_bp = Blueprint("reflection", __name__)

@reflection_bp.route("/new", methods=["GET", "POST"])
@login_required
def new_reflection():
    latest_theme = PracticeTheme.query.filter_by(user_id=current_user.id).order_by(PracticeTheme.created_at.desc()).first()
    if not latest_theme:
        flash("先に練習テーマを作成してください。", "warning")
        return redirect(url_for("analysis.assessment"))

    form = ReflectionForm()
    if form.validate_on_submit():
        reflection = Reflection(
            user_id=current_user.id,
            practice_theme_id=latest_theme.id,
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

    return render_template("reflection/new.html", form=form, latest_theme=latest_theme)

@reflection_bp.route("/logs")
@login_required
def logs():
    reflections = Reflection.query.filter_by(user_id=current_user.id).order_by(Reflection.created_at.desc()).all()
    goals = Goal.query.filter_by(user_id=current_user.id).order_by(Goal.created_at.desc()).all()
    themes = PracticeTheme.query.filter_by(user_id=current_user.id).order_by(PracticeTheme.created_at.desc()).all()
    return render_template("reflection/logs.html", reflections=reflections, goals=goals, themes=themes)
