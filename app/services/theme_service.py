def build_theme(issue_hypothesis: dict) -> dict:
    return {
        "theme_title": issue_hypothesis["theme_title"],
        "theme_detail": issue_hypothesis["theme_detail"],
        "self_check_point": issue_hypothesis["self_check_point"],
        "coach_check_point": issue_hypothesis["coach_check_point"],
    }
