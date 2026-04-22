QUESTIONS_BY_ISSUE = {
    "timing": [
        "timing_start",
        "timing_takeoff",
        "timing_toss",
        "timing_match_only",
        "timing_tension",
    ]
}

def get_questions_by_issue(issue_category: str) -> list[str]:
    return QUESTIONS_BY_ISSUE.get(issue_category, QUESTIONS_BY_ISSUE["timing"])

def analyze_deep_dive(issue_category: str, answers: dict) -> dict:
    hypothesis = "助走と踏切位置の再現性"
    detail = "強く打つことより、毎回同じリズムで入れることが優先かもしれません。"
    self_check = "助走開始位置が毎回そろっていたかを確認する。"
    coach_check = "最後の2歩と踏切位置のズレを見てもらう。"

    if answers.get("timing_match_only") == "yes":
        detail += " 試合時の緊張による再現性低下も要因の可能性があります。"
    if answers.get("timing_tension") == "yes":
        detail += " 力みがミートや入りのズレにつながっている可能性があります。"
    if answers.get("timing_takeoff") == "yes":
        hypothesis = "踏切位置の安定化"
        self_check = "踏切位置が近くなりすぎていないか確認する。"
        coach_check = "踏切位置と打点の関係を見てもらう。"

    return {
        "hypothesis": hypothesis,
        "detail": detail,
        "theme_title": "最後の2歩を毎回そろえる",
        "theme_detail": detail,
        "self_check_point": self_check,
        "coach_check_point": coach_check,
    }
