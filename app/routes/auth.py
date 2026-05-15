from flask import Blueprint, render_template, redirect, url_for, flash, session
from flask_login import login_user, logout_user, current_user
from ..extensions import db
from ..forms import LoginForm, RegisterForm
from ..models import User, Profile

auth_bp = Blueprint("auth", __name__)

@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("main.home"))

    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data.lower()).first()
        if user and user.check_password(form.password.data):
            login_user(user)
            flash("ログインしました。", "success")
            return redirect(url_for("main.home"))
        flash("メールアドレスまたはパスワードが正しくありません。", "danger")

    return render_template("auth/login.html", form=form)

@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("main.home"))

    form = RegisterForm()
    if form.validate_on_submit():
        existing = User.query.filter_by(email=form.email.data.lower()).first()
        if existing:
            flash("そのメールアドレスは既に登録されています。", "danger")
            return render_template("auth/register.html", form=form)

        user = User(email=form.email.data.lower())
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.flush()

        from datetime import date as date_type

        birth_date = None
        if form.birth_year.data and form.birth_month.data and form.birth_day.data:
            try:
                birth_date = date_type(int(form.birth_year.data), int(form.birth_month.data), int(form.birth_day.data))
            except ValueError:
                pass

        volleyball_start_date = None
        if form.volleyball_start_year.data and form.volleyball_start_month.data:
            try:
                volleyball_start_date = date_type(int(form.volleyball_start_year.data), int(form.volleyball_start_month.data), 1)
            except ValueError:
                pass

        profile = Profile(
            user_id=user.id,
            name=form.name.data,
            birth_date=birth_date,
            gender=form.gender.data or None,
            position=form.position.data or None,
            volleyball_start_date=volleyball_start_date,
        )
        db.session.add(profile)
        db.session.commit()

        flash("登録が完了しました。ログインしてください。", "success")
        return redirect(url_for("auth.login"))

    return render_template("auth/register.html", form=form)

@auth_bp.route("/logout")
def logout():
    logout_user()
    for key in (
        "goal_coach_history",
        "goal_coach_display",
        "goal_coach_result",
        "goal_coach_target_date",
    ):
        session.pop(key, None)
    flash("ログアウトしました。", "info")
    return redirect(url_for("auth.login"))
