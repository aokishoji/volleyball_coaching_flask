import json

ISSUE_LABELS = {
    "approach": "助走",
    "takeoff": "踏切",
    "jump": "ジャンプ",
    "air_posture": "空中姿勢",
    "contact": "ミート",
    "contact_point": "打点",
    "course": "コース打ち分け",
    "block": "ブロック対応",
    "timing": "トスとのタイミング",
    "mental": "メンタル",
}

FAILURE_TO_ISSUES = {
    "net": ["contact_point", "timing", "takeoff"],
    "out": ["contact", "course", "timing"],
    "contact_miss": ["contact", "timing", "approach"],
    "low_contact": ["jump", "takeoff", "contact_point"],
    "blocked": ["course", "block", "timing"],
    "timing": ["timing", "approach", "takeoff"],
    "tense": ["mental", "contact", "timing"],
}

def parse_assessment(form_data: dict) -> tuple[dict, list]:
    ratings = {
        "approach": int(form_data["approach_rating"]),
        "takeoff": int(form_data["takeoff_rating"]),
        "jump": int(form_data["jump_rating"]),
        "air_posture": int(form_data["air_posture_rating"]),
        "contact": int(form_data["contact_rating"]),
        "contact_point": int(form_data["contact_point_rating"]),
        "course": int(form_data["course_rating"]),
        "block": int(form_data["block_rating"]),
        "timing": int(form_data["timing_rating"]),
        "mental": int(form_data["mental_rating"]),
    }
    failure_patterns = list(form_data.get("failure_patterns", []))
    return ratings, failure_patterns

def detect_priority_issue(ratings: dict, failure_patterns: list[str]) -> tuple[str, dict]:
    scores = {k: 6 - v for k, v in ratings.items()}  # 低い評価ほど高スコア
    for pattern in failure_patterns:
        for issue in FAILURE_TO_ISSUES.get(pattern, []):
            scores[issue] += 2

    sorted_items = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    top_issue = sorted_items[0][0]
    return top_issue, {
        "scores": scores,
        "top_issues": sorted_items[:3],
    }

def serialize_assessment(ratings: dict, failure_patterns: list[str]) -> tuple[str, str]:
    return json.dumps(ratings, ensure_ascii=False), json.dumps(failure_patterns, ensure_ascii=False)
