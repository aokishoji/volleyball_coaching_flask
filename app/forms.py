from datetime import date
from flask_wtf import FlaskForm
from wtforms import (
    StringField, PasswordField, SubmitField, SelectField,
    SelectMultipleField, TextAreaField, DateField, IntegerField, FloatField
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

GENDER_CHOICES = [
    ("", "選択してください"),
    ("male", "男性"),
    ("female", "女性"),
    ("no_answer", "回答しない"),
]

POSITION_CHOICES = [
    ("", "選択してください"),
    ("WS", "ウイングスパイカー"),
    ("MB", "ミドルブロッカー"),
    ("S", "セッター"),
    ("L", "リベロ"),
    ("OP", "オポジット"),
]

_current_year = date.today().year
YEAR_CHOICES = [("", "年")] + [(str(y), str(y)) for y in range(_current_year, _current_year - 30, -1)]
MONTH_CHOICES = [("", "月")] + [(str(m), f"{m}月") for m in range(1, 13)]
DAY_CHOICES = [("", "日")] + [(str(d), f"{d}日") for d in range(1, 32)]
BIRTH_YEAR_CHOICES = [("", "年")] + [(str(y), str(y)) for y in range(_current_year, 1939, -1)]

SKILL_TYPE_CHOICES = [
    ("spike", "スパイク"),
    ("receive", "レシーブ"),
    ("serve", "サーブ"),
    ("block", "ブロック"),
    ("set", "トス・セット"),
    ("physical", "フィジカル"),
    ("mental", "メンタル"),
]

SKILL_TYPE_LABELS = {k: v for k, v in SKILL_TYPE_CHOICES}
SKILL_TYPE_LABELS["three_month_ai"] = "3か月目標"

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
    birth_year = SelectField("生年", choices=BIRTH_YEAR_CHOICES, validators=[Optional()])
    birth_month = SelectField("生月", choices=MONTH_CHOICES, validators=[Optional()])
    birth_day = SelectField("生日", choices=DAY_CHOICES, validators=[Optional()])
    gender = SelectField("性別", choices=GENDER_CHOICES, validators=[Optional()])
    position = SelectField("ポジション", choices=POSITION_CHOICES, validators=[Optional()])
    volleyball_start_year = SelectField("バレー開始年", choices=YEAR_CHOICES, validators=[Optional()])
    volleyball_start_month = SelectField("バレー開始月", choices=MONTH_CHOICES, validators=[Optional()])
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
    skill_type = SelectField(
        "強化したいスキル",
        choices=SKILL_TYPE_CHOICES,
        validators=[DataRequired()],
    )
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
    birth_year = SelectField("生年", choices=BIRTH_YEAR_CHOICES, validators=[Optional()])
    birth_month = SelectField("生月", choices=MONTH_CHOICES, validators=[Optional()])
    birth_day = SelectField("生日", choices=DAY_CHOICES, validators=[Optional()])
    gender = SelectField("性別", choices=GENDER_CHOICES, validators=[Optional()])
    position = SelectField("ポジション", choices=POSITION_CHOICES, validators=[Optional()])
    volleyball_start_year = SelectField("バレー開始年", choices=YEAR_CHOICES, validators=[Optional()])
    volleyball_start_month = SelectField("バレー開始月", choices=MONTH_CHOICES, validators=[Optional()])
    submit = SubmitField("更新する")


class PhysicalRecordForm(FlaskForm):
    recorded_date = DateField("計測日", validators=[DataRequired()])
    height = FloatField("身長 (cm)", validators=[Optional(), NumberRange(min=50, max=250)])
    weight = FloatField("体重 (kg)", validators=[Optional(), NumberRange(min=10, max=200)])
    finger_height = FloatField("指高 (cm)", validators=[Optional(), NumberRange(min=100, max=350)])
    max_reach = FloatField("最高到達点 (cm)", validators=[Optional(), NumberRange(min=100, max=400)])
    submit = SubmitField("記録する")


class GoalEditForm(FlaskForm):
    goal_title = StringField("目標タイトル", validators=[DataRequired(), Length(max=255)])
    goal_detail = TextAreaField("目標詳細", validators=[Optional(), Length(max=2000)])
    m1_title = StringField("1か月目 到達目標", validators=[Optional(), Length(max=255)])
    m1_ok_criteria = TextAreaField("1か月目 OK基準", validators=[Optional(), Length(max=500)])
    m1_practice_focus = TextAreaField("1か月目 日々の練習で意識すること（1行1項目）", validators=[Optional()])
    m2_title = StringField("2か月目 到達目標", validators=[Optional(), Length(max=255)])
    m2_ok_criteria = TextAreaField("2か月目 OK基準", validators=[Optional(), Length(max=500)])
    m2_practice_focus = TextAreaField("2か月目 日々の練習で意識すること（1行1項目）", validators=[Optional()])
    m3_title = StringField("3か月目 到達目標", validators=[Optional(), Length(max=255)])
    m3_ok_criteria = TextAreaField("3か月目 OK基準", validators=[Optional(), Length(max=500)])
    m3_practice_focus = TextAreaField("3か月目 日々の練習で意識すること（1行1項目）", validators=[Optional()])
    submit = SubmitField("保存する")


class DailyThemeEditForm(FlaskForm):
    theme_title = StringField("テーマタイトル", validators=[DataRequired(), Length(max=255)])
    theme_detail = TextAreaField("テーマの説明", validators=[DataRequired(), Length(max=2000)])
    check_point = TextAreaField("振り返りポイント", validators=[Optional(), Length(max=500)])
    submit = SubmitField("保存する")
