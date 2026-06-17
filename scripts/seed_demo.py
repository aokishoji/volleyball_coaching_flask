"""
マニュアル用デモデータを直接 DB に作成するスクリプト。
Flask サーバーは不要。app context だけ使う。
"""
import sys, os, json
sys.path.insert(0, r"c:\Users\shoji\Documents\GitHub\volleyball_coaching_flask")

from app import create_app
from app.extensions import db
from app.models import (
    User, Profile, Goal, GoalMilestone,
    Assessment, DeepDiveAnswer, PracticeTheme,
    DailyPracticeTheme, Reflection, PhysicalRecord,
)
from datetime import date, timedelta

EMAIL = "demo.manual@example.com"
PASS  = "DemoPass2026"

app = create_app()

with app.app_context():
    # ── 既存ユーザー削除（再実行対応）
    existing = User.query.filter_by(email=EMAIL).first()
    if existing:
        print("Deleting existing demo user...")
        db.session.delete(existing)
        db.session.commit()

    # ── User
    user = User(email=EMAIL)
    user.set_password(PASS)
    db.session.add(user)
    db.session.flush()
    print(f"User created: id={user.id}")

    # ── Profile
    profile = Profile(
        user_id=user.id,
        name="デモ選手",
        birth_date=date(2008, 4, 15),
        gender="female",
        position="WS",
        volleyball_start_date=date(2022, 4, 1),
    )
    db.session.add(profile)
    db.session.flush()

    # ── Goal（60日前に作成 → 3か月目判定に）
    goal_created = date.today() - timedelta(days=62)
    goal = Goal(
        user_id=user.id,
        skill_type="three_month_ai",
        goal_title="3か月目標: 試合でスパイクを安定して決める",
        goal_detail=(
            "【具体目標】\n"
            "試合でスパイクのタイミングを合わせ、狙ったコースに打ち分けられるようになる。\n\n"
            "【OK基準】\n"
            "練習ゲームで自分のスパイクを3本以上連続して決められる。\n\n"
            "【日々の練習】\n"
            "毎回の練習でテーマを1つに絞り、できた場面とできなかった場面を記録する。"
        ),
        target_date=date.today() + timedelta(days=28),
        status="active",
        current_month_override=3,
    )
    db.session.add(goal)
    db.session.flush()
    print(f"Goal created: id={goal.id}")

    # ── GoalMilestones
    milestones_data = [
        {
            "month_index": 1,
            "title": "現在地を確認し、基準フォームを決める",
            "ok_criteria": "練習で意識する形と成功条件を言葉にできる",
            "focus": ["毎回同じ助走リズムで入る", "成功・失敗の違いを記録する"],
        },
        {
            "month_index": 2,
            "title": "練習内でOK基準を安定して達成する",
            "ok_criteria": "練習で決めた基準を半分以上の本数で達成できる",
            "focus": ["本数を決めて成功率を記録する", "崩れた時の修正ポイントを1つに絞る"],
        },
        {
            "month_index": 3,
            "title": "ゲーム形式で再現できる状態にする",
            "ok_criteria": "ゲーム形式でも狙いのコースへ打てる",
            "focus": ["試合場面を想定して練習する", "点差やミス後でも同じ準備をする"],
        },
    ]
    for m in milestones_data:
        db.session.add(GoalMilestone(
            goal_id=goal.id,
            month_index=m["month_index"],
            title=m["title"],
            ok_criteria=m["ok_criteria"],
            practice_focus_json=json.dumps(m["focus"], ensure_ascii=False),
        ))
    db.session.flush()

    # ── Assessment
    ratings = {
        "approach_rating": 3, "takeoff_rating": 3, "jump_rating": 4,
        "air_posture_rating": 3, "contact_rating": 4, "contact_point_rating": 3,
        "course_rating": 3, "block_rating": 3, "timing_rating": 2, "mental_rating": 3,
    }
    assessment = Assessment(
        user_id=user.id,
        goal_id=goal.id,
        issue_category="timing",
        self_rating_json=json.dumps(ratings, ensure_ascii=False),
        failure_pattern_json=json.dumps(["timing", "out"], ensure_ascii=False),
        notes="クイックトスのときにタイミングがずれやすい。",
    )
    db.session.add(assessment)
    db.session.flush()

    # ── DeepDiveAnswers
    for q, a in [
        ("timing_start",     "early"),
        ("timing_takeoff",   "yes"),
        ("timing_toss",      "yes"),
        ("timing_match_only","yes"),
        ("timing_tension",   "no"),
    ]:
        db.session.add(DeepDiveAnswer(
            assessment_id=assessment.id,
            question_key=q,
            answer_value=a,
        ))

    # ── PracticeTheme
    theme = PracticeTheme(
        user_id=user.id,
        goal_id=goal.id,
        assessment_id=assessment.id,
        theme_title="踏切位置の安定化でタイミングを整える",
        theme_detail=(
            "今日は「踏切位置を一定に保つ」ことだけに集中します。\n"
            "助走の最後の1歩で止まる位置を毎回同じにする意識で打ちましょう。\n"
            "トスの高さや方向が変わっても、踏切位置を先に決めてから跳ぶ順序を守ります。\n"
            "打てる本数より「同じ形で踏み切れた本数」を大切にしてください。"
        ),
        self_check_point="踏み切り後に『さっきと同じ位置だったか?』と自問する。",
        coach_check_point="踏切位置がトスによってズレていないか。最後の1歩の位置を定点観測する。",
    )
    db.session.add(theme)
    db.session.flush()

    # ── DailyPracticeTheme
    daily_theme = DailyPracticeTheme(
        user_id=user.id,
        goal_id=goal.id,
        milestone_id=GoalMilestone.query.filter_by(goal_id=goal.id, month_index=3).first().id,
        theme_title="試合場面でも同じ踏切リズムを作る",
        theme_detail=(
            "今日は試合を想定したゲーム形式で練習します。\n"
            "点差がある場面やミスの後こそ、助走リズムを変えずに踏み切る練習です。\n"
            "焦っても慌てても、踏切位置だけは守る意識を持ちましょう。\n"
            "1セット終わったら、何本中何本を狙いの形で踏み切れたか数えます。"
        ),
        check_point="ミスをした後の次のスパイクで、同じリズムで踏み切れたか確認する。",
    )
    db.session.add(daily_theme)
    db.session.flush()

    # ── Reflections（3件）
    reflection_data = [
        {
            "theme_applied": "partial",
            "good_points": "最初の数本は踏切位置を意識できた。コースも少し打ち分けられた。",
            "bad_points": "セッターのトスが乱れた場面で踏切位置がバラバラになった。",
            "cause_hypothesis": "乱れたトスに反応しようとして助走リズムが崩れた。",
            "next_action": "乱れたトスほど、一歩目のタイミングを遅らせて踏切位置を確保する。",
            "coach_question": "トスが短いとき、踏切をどこで止めるのが正解ですか？",
        },
        {
            "theme_applied": "yes",
            "good_points": "ゲーム形式でも5本中3本は同じ形で踏み切れた。コースも2本決まった。",
            "bad_points": "ブロックが跳んでくると視線が上がって踏切が狂う。",
            "cause_hypothesis": "ブロックを意識するあまり、踏切の直前に視線が上がってしまう。",
            "next_action": "ブロックは打つ直前まで見ないで、踏切を完了してから判断する。",
            "coach_question": "",
        },
        {
            "theme_applied": "yes",
            "good_points": "ブロックを意識せずに踏み切ることに集中したら、タイミングが格段に合ってきた。",
            "bad_points": "試合の終盤、疲れてくると助走が短くなる。",
            "cause_hypothesis": "疲労で足が動かなくなり、助走距離を無意識に短くしている。",
            "next_action": "後半こそ意識して助走距離を確保する。疲れたと感じたら一歩分引いて入る。",
            "coach_question": "",
        },
    ]
    for rd in reflection_data:
        r = Reflection(
            user_id=user.id,
            daily_theme_id=daily_theme.id,
            theme_applied=rd["theme_applied"],
            good_points=rd["good_points"],
            bad_points=rd["bad_points"],
            cause_hypothesis=rd.get("cause_hypothesis") or "",
            next_action=rd["next_action"],
            coach_question=rd.get("coach_question") or "",
        )
        db.session.add(r)

    # ── PhysicalRecords（3件）
    for i, (h, w, fh, mr) in enumerate([
        (166.5, 56.2, 210, 275),
        (167.0, 56.8, 210, 278),
        (167.0, 57.1, 210, 280),
    ]):
        db.session.add(PhysicalRecord(
            user_id=user.id,
            recorded_date=date.today() - timedelta(days=60 - i * 28),
            height=h,
            weight=w,
            finger_height=fh,
            max_reach=mr,
        ))

    db.session.commit()
    print("Demo data seeded successfully!")
    print(f"  Email: {EMAIL}")
    print(f"  Pass:  {PASS}")
