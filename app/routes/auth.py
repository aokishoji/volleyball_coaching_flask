from flask import Blueprint, render_template, redirect, url_for, flash
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

        profile = Profile(
            user_id=user.id,
            name=form.name.data,
            age_group=form.age_group.data or None,
            position=form.position.data or None,
        )
        db.session.add(profile)
        db.session.commit()

        flash("登録が完了しました。ログインしてください。", "success")
        return redirect(url_for("auth.login"))

    return render_template("auth/register.html", form=form)

@auth_bp.route("/logout")
def logout():
    logout_user()
    flash("ログアウトしました。", "info")
    return redirect(url_for("auth.login"))
