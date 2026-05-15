from datetime import datetime, date
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from .extensions import db, login_manager

class TimestampMixin:
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False
    )

class User(UserMixin, db.Model, TimestampMixin):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)

    profile = db.relationship("Profile", back_populates="user", uselist=False)
    goals = db.relationship("Goal", back_populates="user", lazy=True)
    assessments = db.relationship("Assessment", back_populates="user", lazy=True)
    practice_themes = db.relationship("PracticeTheme", back_populates="user", lazy=True)
    reflections = db.relationship("Reflection", back_populates="user", lazy=True)

    def set_password(self, password: str) -> None:
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        return check_password_hash(self.password_hash, password)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class Profile(db.Model, TimestampMixin):
    __tablename__ = "profiles"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, unique=True)
    name = db.Column(db.String(100), nullable=False)
    age_group = db.Column(db.String(50))
    position = db.Column(db.String(50))
    experience_years = db.Column(db.Integer)
    birth_date = db.Column(db.Date, nullable=True)
    volleyball_start_date = db.Column(db.Date, nullable=True)
    gender = db.Column(db.String(20), nullable=True)

    user = db.relationship("User", back_populates="profile")

    @property
    def age(self):
        if not self.birth_date:
            return None
        today = date.today()
        return today.year - self.birth_date.year - (
            (today.month, today.day) < (self.birth_date.month, self.birth_date.day)
        )

    @property
    def volleyball_experience(self):
        if not self.volleyball_start_date:
            return None
        today = date.today()
        total_months = (today.year - self.volleyball_start_date.year) * 12 + (today.month - self.volleyball_start_date.month)
        total_months = max(total_months, 0)
        years, months = divmod(total_months, 12)
        if years == 0:
            return f"{months}か月"
        if months == 0:
            return f"{years}年"
        return f"{years}年{months}か月"

class Goal(db.Model, TimestampMixin):
    __tablename__ = "goals"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    skill_type = db.Column(db.String(50), nullable=False, default="spike")
    goal_title = db.Column(db.String(255), nullable=False)
    goal_detail = db.Column(db.Text, nullable=False)
    target_date = db.Column(db.Date)
    status = db.Column(db.String(20), nullable=False, default="active")
    current_month_override = db.Column(db.Integer, nullable=True)

    user = db.relationship("User", back_populates="goals")
    assessments = db.relationship("Assessment", back_populates="goal", lazy=True)
    milestones = db.relationship(
        "GoalMilestone",
        back_populates="goal",
        lazy=True,
        cascade="all, delete-orphan",
        order_by="GoalMilestone.month_index",
    )
    daily_themes = db.relationship("DailyPracticeTheme", back_populates="goal", lazy=True)

class GoalMilestone(db.Model, TimestampMixin):
    __tablename__ = "goal_milestones"

    id = db.Column(db.Integer, primary_key=True)
    goal_id = db.Column(db.Integer, db.ForeignKey("goals.id"), nullable=False)
    month_index = db.Column(db.Integer, nullable=False)
    title = db.Column(db.String(255), nullable=False)
    ok_criteria = db.Column(db.Text)
    practice_focus_json = db.Column(db.Text, nullable=False, default="[]")

    goal = db.relationship("Goal", back_populates="milestones")
    daily_themes = db.relationship("DailyPracticeTheme", back_populates="milestone", lazy=True)

class DailyPracticeTheme(db.Model):
    __tablename__ = "daily_practice_themes"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    goal_id = db.Column(db.Integer, db.ForeignKey("goals.id"), nullable=False)
    milestone_id = db.Column(db.Integer, db.ForeignKey("goal_milestones.id"), nullable=True)
    theme_title = db.Column(db.String(255), nullable=False)
    theme_detail = db.Column(db.Text, nullable=False)
    check_point = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    goal = db.relationship("Goal", back_populates="daily_themes")
    milestone = db.relationship("GoalMilestone", back_populates="daily_themes")

class PhysicalRecord(db.Model):
    __tablename__ = "physical_records"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    recorded_date = db.Column(db.Date, nullable=False)
    height = db.Column(db.Float, nullable=True)
    weight = db.Column(db.Float, nullable=True)
    finger_height = db.Column(db.Float, nullable=True)
    max_reach = db.Column(db.Float, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    user = db.relationship("User", backref=db.backref("physical_records", lazy=True, order_by="PhysicalRecord.recorded_date.desc()"))


class GoalCoachSession(db.Model, TimestampMixin):
    """AI目標設定の会話セッション（ユーザーごとに1件）"""
    __tablename__ = "goal_coach_sessions"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, unique=True)
    history_json = db.Column(db.Text, nullable=False, default="[]")
    display_json = db.Column(db.Text, nullable=False, default="[]")
    result_json = db.Column(db.Text)
    target_date_text = db.Column(db.String(20))

    user = db.relationship("User", backref=db.backref("goal_coach_session", uselist=False))


class Assessment(db.Model):
    __tablename__ = "assessments"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    goal_id = db.Column(db.Integer, db.ForeignKey("goals.id"), nullable=False)
    issue_category = db.Column(db.String(100))
    self_rating_json = db.Column(db.Text, nullable=False)
    failure_pattern_json = db.Column(db.Text, nullable=False)
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    user = db.relationship("User", back_populates="assessments")
    goal = db.relationship("Goal", back_populates="assessments")
    deep_dive_answers = db.relationship("DeepDiveAnswer", back_populates="assessment", lazy=True)
    practice_themes = db.relationship("PracticeTheme", back_populates="assessment", lazy=True)

class DeepDiveAnswer(db.Model):
    __tablename__ = "deep_dive_answers"

    id = db.Column(db.Integer, primary_key=True)
    assessment_id = db.Column(db.Integer, db.ForeignKey("assessments.id"), nullable=False)
    question_key = db.Column(db.String(100), nullable=False)
    answer_value = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    assessment = db.relationship("Assessment", back_populates="deep_dive_answers")

class PracticeTheme(db.Model):
    __tablename__ = "practice_themes"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    goal_id = db.Column(db.Integer, db.ForeignKey("goals.id"), nullable=False)
    assessment_id = db.Column(db.Integer, db.ForeignKey("assessments.id"), nullable=False)
    theme_title = db.Column(db.String(255), nullable=False)
    theme_detail = db.Column(db.Text, nullable=False)
    self_check_point = db.Column(db.Text)
    coach_check_point = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    user = db.relationship("User", back_populates="practice_themes")
    assessment = db.relationship("Assessment", back_populates="practice_themes")

class Reflection(db.Model):
    __tablename__ = "reflections"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    practice_theme_id = db.Column(db.Integer, db.ForeignKey("practice_themes.id"), nullable=True)
    daily_theme_id = db.Column(db.Integer, db.ForeignKey("daily_practice_themes.id"), nullable=True)
    theme_applied = db.Column(db.String(20), nullable=False)
    good_points = db.Column(db.Text, nullable=False)
    bad_points = db.Column(db.Text, nullable=False)
    cause_hypothesis = db.Column(db.Text)
    next_action = db.Column(db.Text, nullable=False)
    coach_question = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    user = db.relationship("User", back_populates="reflections")
    daily_theme = db.relationship("DailyPracticeTheme", backref=db.backref("reflections", lazy=True))
