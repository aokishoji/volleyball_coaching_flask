def build_goal_text(form_data: dict) -> tuple[str, str]:
    improve_target = form_data.get("improve_target", "").strip()
    problem_scene = form_data.get("problem_scene", "").strip()
    ideal_state = form_data.get("ideal_state", "").strip()

    title = f"スパイク: {improve_target}" if improve_target else "スパイク上達"
    detail_parts = []
    if problem_scene:
        detail_parts.append(f"現在の課題: {problem_scene}")
    if ideal_state:
        detail_parts.append(f"理想の状態: {ideal_state}")
    detail_parts.append("日々の練習で課題を整理し、再現性の高い動きと判断を身につける。")
    detail = "\n".join(detail_parts)
    return title, detail
