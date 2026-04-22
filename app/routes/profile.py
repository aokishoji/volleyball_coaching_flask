from flask import Blueprint, render_template, flash, redirect, url_for
from flask_login import login_required, current_user
from ..extensions import db
from ..forms import ProfileForm
from ..models import Profile

profile_bp = Blueprint("profile", __name__)

@profile_bp.route("/", methods=["GET", "POST"])
@login_required
def edit_profile():
    profile = current_user.profile
    form = ProfileForm(obj=profile)

    if form.validate_on_submit():
        profile.name = form.name.data
        profile.age_group = form.age_group.data or None
        profile.position = form.position.data or None
        profile.experience_years = form.experience_years.data
        db.session.commit()
        flash("プロフィールを更新しました。", "success")
        return redirect(url_for("profile.edit_profile"))

    return render_template("profile/edit.html", form=form)
