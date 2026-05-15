from datetime import date
from flask import Blueprint, render_template, flash, redirect, url_for, request
from flask_login import login_required, current_user
from ..extensions import db
from ..forms import ProfileForm, PhysicalRecordForm
from ..models import Profile, PhysicalRecord

profile_bp = Blueprint("profile", __name__)

@profile_bp.route("/", methods=["GET", "POST"])
@login_required
def edit_profile():
    profile = current_user.profile
    form = ProfileForm(obj=profile)

    if request.method == "GET" and profile:
        if profile.birth_date:
            form.birth_year.data = str(profile.birth_date.year)
            form.birth_month.data = str(profile.birth_date.month)
            form.birth_day.data = str(profile.birth_date.day)
        if profile.volleyball_start_date:
            form.volleyball_start_year.data = str(profile.volleyball_start_date.year)
            form.volleyball_start_month.data = str(profile.volleyball_start_date.month)

    if form.validate_on_submit():
        birth_date = None
        if form.birth_year.data and form.birth_month.data and form.birth_day.data:
            try:
                birth_date = date(int(form.birth_year.data), int(form.birth_month.data), int(form.birth_day.data))
            except ValueError:
                pass

        volleyball_start_date = None
        if form.volleyball_start_year.data and form.volleyball_start_month.data:
            try:
                volleyball_start_date = date(int(form.volleyball_start_year.data), int(form.volleyball_start_month.data), 1)
            except ValueError:
                pass

        profile.name = form.name.data
        profile.birth_date = birth_date
        profile.gender = form.gender.data or None
        profile.position = form.position.data or None
        profile.volleyball_start_date = volleyball_start_date
        db.session.commit()
        flash("プロフィールを更新しました。", "success")
        return redirect(url_for("profile.edit_profile"))

    return render_template("profile/edit.html", form=form, profile=profile)


@profile_bp.route("/physical", methods=["GET", "POST"])
@login_required
def physical():
    form = PhysicalRecordForm()
    if not form.recorded_date.data:
        form.recorded_date.data = date.today()

    if form.validate_on_submit():
        record = PhysicalRecord(
            user_id=current_user.id,
            recorded_date=form.recorded_date.data,
            height=form.height.data,
            weight=form.weight.data,
            finger_height=form.finger_height.data,
            max_reach=form.max_reach.data,
        )
        db.session.add(record)
        db.session.commit()
        flash("身体データを記録しました。", "success")
        return redirect(url_for("profile.physical"))

    records = (
        PhysicalRecord.query
        .filter_by(user_id=current_user.id)
        .order_by(PhysicalRecord.recorded_date.desc())
        .all()
    )
    return render_template("profile/physical.html", form=form, records=records)
