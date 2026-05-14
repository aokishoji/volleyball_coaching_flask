import json
from datetime import datetime

from flask import current_app
from openai import OpenAI

from ..models import DailyPracticeTheme, GoalMilestone

def current_month_index(goal) -> int:
    if goal.current_month_override is not None:
        return goal.current_month_override
    elapsed_days = (datetime.utcnow() - goal.created_at).days
    if elapsed_days < 30:
        return 1
    if elapsed_days < 60:
        return 2
    return 3

def practice_focus_list(milestone: GoalMilestone | None) -> list[str]:
    if not milestone:
        return []
    try:
        data = json.loads(milestone.practice_focus_json or "[]")
        return data if isinstance(data, list) else []
    except json.JSONDecodeError:
        return []

def build_today_theme(user_id: int, goal, milestone: GoalMilestone | None) -> DailyPracticeTheme:
    focus = practice_focus_list(milestone)
    main_focus = focus[0] if focus else "今日の練習で目標につながる行動を1つ決める"
    month_label = f"{milestone.month_index}か月目" if milestone else "現在"

    detail_parts = [
        f"{month_label}の目標: {milestone.title if milestone else goal.goal_title}",
        f"今日の意識: {main_focus}",
    ]
    if milestone and milestone.ok_criteria:
        detail_parts.append(f"OK基準: {milestone.ok_criteria}")
    if len(focus) > 1:
        detail_parts.append("補助ポイント: " + " / ".join(focus[1:]))

    return DailyPracticeTheme(
        user_id=user_id,
        goal_id=goal.id,
        milestone_id=milestone.id if milestone else None,
        theme_title=f"今日のテーマ: {main_focus}",
        theme_detail="\n".join(detail_parts),
        check_point="練習後に、できた場面・崩れた場面・次回の修正点を1つずつ書く",
    )

_THEME_SYSTEM_PROMPT = """あなたはバレーボール専門のコーチです。
選手の目標・マイルストーン・最近の振り返りをもとに、今日1回の練習で集中すべきテーマを1つ提案してください。
必ずJSONのみで返してください。Markdownは使わないでください。
形式:
{"theme_title": "今日のテーマ（20字以内）", "theme_detail": "テーマの説明と取り組み方（3〜5文）", "check_point": "練習後に確認するポイント（1〜2文）"}"""

def build_today_theme_ai(user_id: int, goal, milestone, recent_reflections=None) -> DailyPracticeTheme:
    api_key = current_app.config.get("OPENAI_API_KEY")
    if not api_key:
        return build_today_theme(user_id, goal, milestone)

    try:
        focus = practice_focus_list(milestone)
        lines = [f"3か月目標: {goal.goal_title}"]
        if milestone:
            lines.append(f"{milestone.month_index}か月目マイルストーン: {milestone.title}")
            if milestone.ok_criteria:
                lines.append(f"OK基準: {milestone.ok_criteria}")
            if focus:
                lines.append(f"練習フォーカス: {', '.join(focus)}")
        if recent_reflections:
            lines.append("最近の振り返り:")
            for r in recent_reflections:
                lines.append(f"  できたこと: {r.good_points[:100]}")
                lines.append(f"  次回意識: {r.next_action[:100]}")

        client = OpenAI(api_key=api_key)
        model = current_app.config.get("OPENAI_MODEL", "gpt-4o-mini")
        response = client.responses.create(
            model=model,
            input=[
                {"role": "system", "content": _THEME_SYSTEM_PROMPT},
                {"role": "user", "content": "\n".join(lines)},
            ],
        )
        data = json.loads(response.output_text)
        return DailyPracticeTheme(
            user_id=user_id,
            goal_id=goal.id,
            milestone_id=milestone.id if milestone else None,
            theme_title=data.get("theme_title") or "今日のテーマ",
            theme_detail=data.get("theme_detail") or "",
            check_point=data.get("check_point") or "",
        )
    except Exception:
        current_app.logger.exception("AI theme generation failed, using rule-based fallback")
        return build_today_theme(user_id, goal, milestone)
