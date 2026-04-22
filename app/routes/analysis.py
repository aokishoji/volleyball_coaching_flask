from flask import Blueprint, render_template, redirect, url_for, flash, session
from flask_login import login_required, current_user
from ..extensions import db
from ..forms import AssessmentForm, DeepDiveForm
from ..models import Goal, Assessment, DeepDiveAnswer, PracticeTheme
from ..services.analysis_service import parse_assessment, detect_priority_issue, serialize_assessment
from ..services.deep_dive_service import analyze_deep_dive
from ..services.theme_service import build_theme

analysis_bp = Blueprint("analysis", __name__)

@analysis_bp.route("/", methods=["GET", "POST"])
@login_required
def assessment():
    form = AssessmentForm()
    active_goal = Goal.query.filter_by(user_id=current_user.id, status="active").order_by(Goal.updated_at.desc()).first()

    if not active_goal:
        flash("先に目標を設定してください。", "warning")
        return redirect(url_for("goals.new_goal"))

    if form.validate_on_submit():
        ratings, failure_patterns = parse_assessment(form.data)
        issue_category, result = detect_priority_issue(ratings, failure_patterns)
        self_rating_json, failure_pattern_json = serialize_assessment(ratings, failure_patterns)

        assessment = Assessment(
            user_id=current_user.id,
            goal_id=active_goal.id,
            issue_category=issue_category,
            self_rating_json=self_rating_json,
            failure_pattern_json=failure_pattern_json,
            notes=form.notes.data,
        )
        db.session.add(assessment)
        db.session.commit()

        session["assessment_id"] = assessment.id
        flash(f"優先課題候補: {issue_category}。深掘りへ進みます。", "info")
        return redirect(url_for("analysis.deep_dive"))

    return render_template("analysis/assessment.html", form=form, active_goal=active_goal)

@analysis_bp.route("/deep-dive", methods=["GET", "POST"])
@login_required
def deep_dive():
    assessment_id = session.get("assessment_id")
    if not assessment_id:
        flash("先に課題分析を行ってください。", "warning")
        return redirect(url_for("analysis.assessment"))

    assessment = Assessment.query.get_or_404(assessment_id)
    form = DeepDiveForm()

    if form.validate_on_submit():
        answers = {
            "timing_start": form.timing_start.data,
            "timing_takeoff": form.timing_takeoff.data,
            "timing_toss": form.timing_toss.data,
            "timing_match_only": form.timing_match_only.data,
            "timing_tension": form.timing_tension.data,
        }

        for key, value in answers.items():
            if value:
                db.session.add(DeepDiveAnswer(
                    assessment_id=assessment.id,
                    question_key=key,
                    answer_value=value,
                ))

        issue_hypothesis = analyze_deep_dive(assessment.issue_category or "timing", answers)
        theme_data = build_theme(issue_hypothesis)

        theme = PracticeTheme(
            user_id=current_user.id,
            goal_id=assessment.goal_id,
            assessment_id=assessment.id,
            theme_title=theme_data["theme_title"],
            theme_detail=theme_data["theme_detail"],
            self_check_point=theme_data["self_check_point"],
            coach_check_point=theme_data["coach_check_point"],
        )
        db.session.add(theme)
        db.session.commit()

        flash("今日の練習テーマを作成しました。", "success")
        return redirect(url_for("analysis.latest_theme"))

    return render_template("analysis/deep_dive.html", form=form, assessment=assessment)

@analysis_bp.route("/theme/latest")
@login_required
def latest_theme():
    theme = PracticeTheme.query.filter_by(user_id=current_user.id).order_by(PracticeTheme.created_at.desc()).first()
    return render_template("analysis/theme_latest.html", theme=theme)
