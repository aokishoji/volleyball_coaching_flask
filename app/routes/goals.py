import json
from datetime import date
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from ..extensions import db
from ..forms import GoalForm, GoalRoadmapForm, GoalCoachMessageForm
from ..models import Goal, GoalMilestone, GoalCoachSession, Reflection
from ..services.goal_service import build_goal_text
from ..services.ai_goal_coach_service import (
    ask_goal_coach,
    build_initial_user_message,
    build_saved_goal_detail,
    get_coach_session,
    upsert_coach_session,
    clear_coach_session,
)
from ..services.goal_progress_service import build_today_theme_ai, current_month_index

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
    message_form = GoalCoachMessageForm()
    history, display_messages, result, target_date_text = get_coach_session(current_user.id)

    if request.method == "POST":
        action = request.form.get("action", "start")

        if action == "reset":
            clear_coach_session(current_user.id)
            flash("目標設定の会話をリセットしました。", "info")
            return redirect(url_for("goals.roadmap"))

        if action == "save" and result and result.get("status") == "ready":
            title = result.get("goal_title") or "3か月目標"
            detail = build_saved_goal_detail(result)
            target_date = date.fromisoformat(target_date_text) if target_date_text else None

            goal = Goal(
                user_id=current_user.id,
                skill_type="three_month_ai",
                goal_title=title,
                goal_detail=detail,
                target_date=target_date,
                status="active",
            )
            db.session.add(goal)
            db.session.flush()
            for item in result.get("milestones", []):
                if not isinstance(item, dict):
                    continue
                db.session.add(GoalMilestone(
                    goal_id=goal.id,
                    month_index=int(item.get("month") or 1),
                    title=item.get("title") or "到達目標",
                    ok_criteria=item.get("ok_criteria") or "",
                    practice_focus_json=json.dumps(
                        item.get("practice_focus") or result.get("practice_focus") or [],
                        ensure_ascii=False,
                    ),
                ))
            GoalCoachSession.query.filter_by(user_id=current_user.id).delete()
            db.session.commit()

            flash("AIコーチと作った3か月目標を保存しました。", "success")
            return redirect(url_for("main.home"))

        if action == "message" and message_form.validate_on_submit():
            player_message = message_form.message.data.strip()
            history.append({"role": "user", "content": player_message})
            display_messages.append({"role": "user", "content": player_message})
            result = ask_goal_coach(history)
            history.append({
                "role": "assistant",
                "content": json.dumps(result, ensure_ascii=False),
            })
            display_messages.append({
                "role": "assistant",
                "content": result.get("message", ""),
            })
            upsert_coach_session(current_user.id, history, display_messages, result, target_date_text)
            return redirect(url_for("goals.roadmap"))

        if action == "start" and form.validate_on_submit():
            initial_message = build_initial_user_message({
                "rough_goal": form.rough_goal.data,
                "current_level": form.current_level.data,
                "target_date": form.target_date.data,
                "weekly_practice_days": form.weekly_practice_days.data,
                "focus_hint": form.focus_hint.data,
            })
            history = [{"role": "user", "content": initial_message}]
            display_messages = [{"role": "user", "content": form.rough_goal.data}]
            result = ask_goal_coach(history)
            history.append({
                "role": "assistant",
                "content": json.dumps(result, ensure_ascii=False),
            })
            display_messages.append({
                "role": "assistant",
                "content": result.get("message", ""),
            })
            new_target_date_text = form.target_date.data.isoformat() if form.target_date.data else None
            upsert_coach_session(current_user.id, history, display_messages, result, new_target_date_text)
            return redirect(url_for("goals.roadmap"))

    return render_template(
        "goals/roadmap.html",
        form=form,
        message_form=message_form,
        display_messages=display_messages,
        result=result,
    )

@goals_bp.route("/<int:goal_id>/advance-milestone", methods=["POST"])
@login_required
def advance_milestone(goal_id):
    goal = Goal.query.filter_by(id=goal_id, user_id=current_user.id).first_or_404()
    current = current_month_index(goal)
    if current < 3:
        goal.current_month_override = current + 1
        db.session.commit()
        flash(f"{current + 1}か月目のマイルストーンに移行しました。", "success")
    else:
        flash("すでに3か月目です。", "info")
    return redirect(url_for("main.home"))

@goals_bp.route("/<int:goal_id>/reset-milestone", methods=["POST"])
@login_required
def reset_milestone(goal_id):
    goal = Goal.query.filter_by(id=goal_id, user_id=current_user.id).first_or_404()
    goal.current_month_override = None
    db.session.commit()
    flash("マイルストーンを経過日数による自動判定に戻しました。", "info")
    return redirect(url_for("main.home"))

@goals_bp.route("/<int:goal_id>/today-theme", methods=["POST"])
@login_required
def create_today_theme(goal_id):
    goal = Goal.query.filter_by(id=goal_id, user_id=current_user.id).first_or_404()
    month_index = current_month_index(goal)
    milestone = GoalMilestone.query.filter_by(
        goal_id=goal.id,
        month_index=month_index,
    ).first()

    recent_reflections = (
        Reflection.query
        .filter(Reflection.user_id == current_user.id, Reflection.daily_theme_id.isnot(None))
        .order_by(Reflection.created_at.desc())
        .limit(3)
        .all()
    )
    theme = build_today_theme_ai(current_user.id, goal, milestone, recent_reflections)
    db.session.add(theme)
    db.session.commit()

    flash("今日の練習テーマを作りました。", "success")
    return redirect(url_for("main.home"))
