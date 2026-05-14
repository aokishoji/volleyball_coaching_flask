from flask_wtf import FlaskForm
from wtforms import (
    StringField, PasswordField, SubmitField, SelectField,
    SelectMultipleField, TextAreaField, DateField, IntegerField
)
from wtforms.validators import DataRequired, Email, EqualTo, Length, Optional, NumberRange

RATING_CHOICES = [(str(i), str(i)) for i in range(1, 6)]
YES_NO_CHOICES = [("yes", "はい"), ("no", "いいえ")]
YES_NO_PARTIAL_CHOICES = [("yes", "はい"), ("partial", "一部"), ("no", "いいえ")]

AGE_GROUP_CHOICES = [
    ("", "選択してください"),
    ("elem_1", "小1"), ("elem_2", "小2"), ("elem_3", "小3"),
    ("elem_4", "小4"), ("elem_5", "小5"), ("elem_6", "小6"),
    ("junior_1", "中1"), ("junior_2", "中2"), ("junior_3", "中3"),
    ("high_1", "高1"), ("high_2", "高2"), ("high_3", "高3"),
]

class LoginForm(FlaskForm):
    email = StringField("メールアドレス", validators=[DataRequired(), Email()])
    password = PasswordField("パスワード", validators=[DataRequired()])
    submit = SubmitField("ログイン")

class RegisterForm(FlaskForm):
    name = StringField("表示名", validators=[DataRequired(), Length(max=100)])
    email = StringField("メールアドレス", validators=[DataRequired(), Email()])
    password = PasswordField("パスワード", validators=[DataRequired(), Length(min=8)])
    password_confirm = PasswordField(
        "パスワード確認",
        validators=[DataRequired(), EqualTo("password", message="パスワードが一致しません")]
    )
    age_group = SelectField(
        "学年/年代区分",
        choices=AGE_GROUP_CHOICES,
        validators=[Optional()]
    )
    position = SelectField(
        "ポジション",
        choices=[
            ("", "選択してください"),
            ("WS", "ウイングスパイカー"),
            ("MB", "ミドルブロッカー"),
            ("S", "セッター"),
            ("L", "リベロ"),
            ("OP", "オポジット"),
        ],
        validators=[Optional()]
    )
    submit = SubmitField("登録する")

class GoalForm(FlaskForm):
    skill_type = SelectField(
        "対象スキル",
        choices=[("spike", "スパイク")],
        validators=[DataRequired()]
    )
    improve_target = StringField("改善したいこと", validators=[DataRequired(), Length(max=255)])
    problem_scene = TextAreaField("困っている場面", validators=[DataRequired(), Length(max=1000)])
    ideal_state = TextAreaField("理想の状態", validators=[Optional(), Length(max=1000)])
    target_date = DateField("期限", validators=[Optional()])
    submit = SubmitField("目標を保存する")

class GoalRoadmapForm(FlaskForm):
    rough_goal = TextAreaField(
        "3か月先のざっくりした目標",
        validators=[DataRequired(), Length(max=1000)]
    )
    current_level = TextAreaField(
        "今の状態・課題感",
        validators=[Optional(), Length(max=1000)]
    )
    target_date = DateField("3か月後の目安日", validators=[Optional()])
    weekly_practice_days = SelectField(
        "週に練習できる日数",
        choices=[
            ("2", "週2日"),
            ("3", "週3日"),
            ("4", "週4日"),
            ("5", "週5日以上"),
        ],
        validators=[DataRequired()]
    )
    focus_hint = SelectMultipleField(
        "特に強化したい要素",
        choices=[
            ("spike", "スパイク"),
            ("serve", "サーブ"),
            ("reception", "レセプション"),
            ("defense", "ディグ・守備"),
            ("setting", "トス・つなぎ"),
            ("physical", "フィジカル"),
            ("mental", "メンタル"),
        ],
        validators=[Optional()]
    )
    submit = SubmitField("AIコーチと目標設定を始める")

class GoalCoachMessageForm(FlaskForm):
    message = TextAreaField(
        "AIコーチへの返答",
        validators=[DataRequired(), Length(max=1000)]
    )
    submit = SubmitField("返答する")

class AssessmentForm(FlaskForm):
    approach_rating = SelectField("助走", choices=RATING_CHOICES, validators=[DataRequired()])
    takeoff_rating = SelectField("踏切", choices=RATING_CHOICES, validators=[DataRequired()])
    jump_rating = SelectField("ジャンプ", choices=RATING_CHOICES, validators=[DataRequired()])
    air_posture_rating = SelectField("空中姿勢", choices=RATING_CHOICES, validators=[DataRequired()])
    contact_rating = SelectField("ミート", choices=RATING_CHOICES, validators=[DataRequired()])
    contact_point_rating = SelectField("打点", choices=RATING_CHOICES, validators=[DataRequired()])
    course_rating = SelectField("コース打ち分け", choices=RATING_CHOICES, validators=[DataRequired()])
    block_rating = SelectField("ブロック対応", choices=RATING_CHOICES, validators=[DataRequired()])
    timing_rating = SelectField("トスとのタイミング", choices=RATING_CHOICES, validators=[DataRequired()])
    mental_rating = SelectField("メンタル", choices=RATING_CHOICES, validators=[DataRequired()])

    failure_patterns = SelectMultipleField(
        "失敗パターン",
        choices=[
            ("net", "ネットにかかる"),
            ("out", "アウトになる"),
            ("contact_miss", "ミートミスが多い"),
            ("low_contact", "打点が低いと感じる"),
            ("blocked", "ブロックにつかまる"),
            ("timing", "タイミングが合わない"),
            ("tense", "力んでしまう"),
        ],
        validators=[DataRequired()]
    )
    notes = TextAreaField("困っていること詳細", validators=[Optional(), Length(max=1000)])
    submit = SubmitField("課題を分析する")

class DeepDiveForm(FlaskForm):
    timing_start = SelectField(
        "助走の入りが早い/遅いと感じるか",
        choices=[("", "選択してください"), ("early", "早い"), ("late", "遅い"), ("stable", "特に感じない")],
        validators=[Optional()]
    )
    timing_takeoff = SelectField(
        "踏切位置が近くなりやすいか",
        choices=[("", "選択してください")] + YES_NO_CHOICES,
        validators=[Optional()]
    )
    timing_toss = SelectField(
        "トスの種類で崩れやすいか",
        choices=[("", "選択してください")] + YES_NO_CHOICES,
        validators=[Optional()]
    )
    timing_match_only = SelectField(
        "練習ではできるが試合で崩れるか",
        choices=[("", "選択してください")] + YES_NO_CHOICES,
        validators=[Optional()]
    )
    timing_tension = SelectField(
        "力みを感じるか",
        choices=[("", "選択してください")] + YES_NO_CHOICES,
        validators=[Optional()]
    )
    submit = SubmitField("深掘りしてテーマを作る")

class ReflectionForm(FlaskForm):
    theme_applied = SelectField(
        "今日のテーマを意識できたか",
        choices=YES_NO_PARTIAL_CHOICES,
        validators=[DataRequired()]
    )
    good_points = TextAreaField("できたこと", validators=[DataRequired(), Length(max=1000)])
    bad_points = TextAreaField("できなかったこと", validators=[DataRequired(), Length(max=1000)])
    cause_hypothesis = TextAreaField("原因の仮説", validators=[Optional(), Length(max=1000)])
    next_action = TextAreaField("次回意識すること", validators=[DataRequired(), Length(max=1000)])
    coach_question = TextAreaField("コーチに聞きたいこと", validators=[Optional(), Length(max=1000)])
    submit = SubmitField("振り返りを保存する")

class ProfileForm(FlaskForm):
    name = StringField("表示名", validators=[DataRequired(), Length(max=100)])
    age_group = SelectField(
        "学年/年代区分",
        choices=AGE_GROUP_CHOICES,
        validators=[Optional()]
    )
    position = SelectField(
        "ポジション",
        choices=[
            ("", "選択してください"),
            ("WS", "ウイングスパイカー"),
            ("MB", "ミドルブロッカー"),
            ("S", "セッター"),
            ("L", "リベロ"),
            ("OP", "オポジット"),
        ],
        validators=[Optional()]
    )
    experience_years = IntegerField(
        "経験年数",
        validators=[Optional(), NumberRange(min=0, max=50)]
    )
    submit = SubmitField("更新する")
