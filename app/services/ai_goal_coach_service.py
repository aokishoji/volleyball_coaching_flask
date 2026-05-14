import json
from flask import current_app
from openai import OpenAI
from ..extensions import db
from ..models import GoalCoachSession

SYSTEM_PROMPT = """
あなたは中高生から競技者までを支援するバレーボール専門のAIコーチです。
選手が入力した3か月先の抽象的な目標を、対話で具体的な目標にします。

方針:
- 1回の返答で質問は最大2つまで。
- 選手が答えやすい短い日本語で話す。
- 目標は「何を」「いつまでに」「どの場面で」「どの基準ならOKか」まで具体化する。
- マイルストーンは1か月目、2か月目、3か月目で作る。
- スパイク、サーブ、レセプション、ディグ、トス、フィジカル、メンタルの要素へ必要に応じて分解する。
- 医療・ケガの診断はしない。痛みがある場合は専門家や指導者に相談するよう促す。

必ずJSONだけで返してください。Markdownは使わないでください。
形式:
{
  "status": "question" または "ready",
  "message": "選手に見せる返答",
  "goal_title": "保存する具体目標。readyの時だけ必須",
  "goal_detail": "保存する詳細。readyの時だけ必須",
  "milestones": [
    {
      "month": 1,
      "title": "1か月目の到達目標",
      "ok_criteria": "1か月目が達成できたと判断する基準",
      "practice_focus": ["1か月目の日々の練習で意識すること"]
    },
    {
      "month": 2,
      "title": "2か月目の到達目標",
      "ok_criteria": "2か月目が達成できたと判断する基準",
      "practice_focus": ["2か月目の日々の練習で意識すること"]
    },
    {
      "month": 3,
      "title": "3か月目の到達目標",
      "ok_criteria": "3か月目が達成できたと判断する基準",
      "practice_focus": ["3か月目の日々の練習で意識すること"]
    }
  ],
  "practice_focus": ["全期間で日々の練習で意識すること"]
}
"""

def build_initial_user_message(form_data: dict) -> str:
    focus = ", ".join(form_data.get("focus_hint") or []) or "未選択"
    target_date = form_data.get("target_date")
    target_date_text = target_date.strftime("%Y-%m-%d") if target_date else "未設定"
    return "\n".join([
        "3か月先の目標設定をしたいです。",
        f"抽象目標: {form_data.get('rough_goal') or ''}",
        f"今の状態・課題感: {form_data.get('current_level') or '未入力'}",
        f"目安日: {target_date_text}",
        f"週に練習できる日数: 週{form_data.get('weekly_practice_days') or '3'}日",
        f"特に強化したい要素: {focus}",
    ])

def _extract_json(text: str) -> dict:
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        start = text.find("{")
        end = text.rfind("}")
        if start >= 0 and end > start:
            return json.loads(text[start:end + 1])
        raise

def _fallback_reply(history: list[dict]) -> dict:
    user_turns = [item["content"] for item in history if item.get("role") == "user"]
    if len(user_turns) <= 1:
        return {
            "status": "question",
            "message": "AI接続前の仮モードです。まず、3か月後の試合や練習で「できた」と判断できる具体的な場面を1つ教えてください。例: サーブで相手を崩す、レセプションをセッターへ返す、スパイクを決め切る。",
            "goal_title": "",
            "goal_detail": "",
            "milestones": [],
            "practice_focus": [],
        }

    rough_goal = user_turns[0].split("抽象目標:", 1)[-1].splitlines()[0].strip()
    return {
        "status": "ready",
        "message": "仮モードで具体目標と3か月のマイルストーンを作りました。OpenAI APIキーを設定すると、ここがAI対話でより細かく調整されます。",
        "goal_title": f"3か月目標: {rough_goal[:80] or '試合で使える強みを作る'}",
        "goal_detail": "\n".join([
            "【具体目標】",
            rough_goal or "3か月後に試合で使える強みを1つ作る",
            "",
            "【OK基準】",
            "練習とゲーム形式の両方で、決めたプレーを安定して再現できる。",
            "",
            "【日々の練習】",
            "毎回の練習でテーマを1つに絞り、できた本数・崩れた場面・次回の修正点を記録する。",
        ]),
        "milestones": [
            {
                "month": 1,
                "title": "現在地を確認し、フォーム・判断の基準を決める",
                "ok_criteria": "練習で意識する形と成功条件を言葉にできる",
                "practice_focus": ["毎回同じフォームで入る", "成功した時と失敗した時の違いを記録する"],
            },
            {
                "month": 2,
                "title": "練習内でOK基準を安定して達成する",
                "ok_criteria": "練習内で決めた基準を半分以上の本数で達成できる",
                "practice_focus": ["本数を決めて成功率を記録する", "崩れた時の修正ポイントを1つに絞る"],
            },
            {
                "month": 3,
                "title": "ゲーム形式や試合で再現できる状態にする",
                "ok_criteria": "ゲーム形式でも決めたプレーを選んで実行できる",
                "practice_focus": ["試合場面を想定して練習する", "点差やミス後でも同じ準備をする"],
            },
        ],
        "practice_focus": [
            "練習前に今日のテーマを1つ決める",
            "練習後に成功条件と失敗条件を短く記録する",
        ],
    }

def ask_goal_coach(history: list[dict]) -> dict:
    api_key = current_app.config.get("OPENAI_API_KEY")
    model = current_app.config.get("OPENAI_MODEL", "gpt-5.4-mini")
    if not api_key:
        return normalize_goal_result(_fallback_reply(history))

    try:
        client = OpenAI(api_key=api_key)
        response = client.responses.create(
            model=model,
            input=[{"role": "system", "content": SYSTEM_PROMPT}] + history,
        )
        return normalize_goal_result(_extract_json(response.output_text))
    except Exception as exc:
        current_app.logger.exception("Goal coach API call failed")
        fallback = _fallback_reply(history)
        fallback["message"] = f"AIコーチへの接続でエラーが出たため、仮モードで進めます。詳細: {exc}"
        return normalize_goal_result(fallback)

def normalize_goal_result(result: dict) -> dict:
    milestones = result.get("milestones") or []
    normalized = []
    for index in range(1, 4):
        raw = milestones[index - 1] if index - 1 < len(milestones) else {}
        if isinstance(raw, str):
            normalized.append({
                "month": index,
                "title": raw,
                "ok_criteria": "",
                "practice_focus": result.get("practice_focus") or [],
            })
            continue

        normalized.append({
            "month": int(raw.get("month") or index),
            "title": raw.get("title") or f"{index}か月目の到達目標",
            "ok_criteria": raw.get("ok_criteria") or "",
            "practice_focus": raw.get("practice_focus") or result.get("practice_focus") or [],
        })

    result["milestones"] = normalized
    return result

def get_coach_session(user_id: int) -> tuple:
    record = GoalCoachSession.query.filter_by(user_id=user_id).first()
    if record is None:
        return [], [], None, None
    return (
        json.loads(record.history_json),
        json.loads(record.display_json),
        json.loads(record.result_json) if record.result_json else None,
        record.target_date_text,
    )

def upsert_coach_session(user_id: int, history: list, display: list, result: dict, target_date_text) -> None:
    record = GoalCoachSession.query.filter_by(user_id=user_id).first()
    if record is None:
        record = GoalCoachSession(user_id=user_id)
        db.session.add(record)
    record.history_json = json.dumps(history, ensure_ascii=False)
    record.display_json = json.dumps(display, ensure_ascii=False)
    record.result_json = json.dumps(result, ensure_ascii=False)
    record.target_date_text = target_date_text
    db.session.commit()

def clear_coach_session(user_id: int) -> None:
    GoalCoachSession.query.filter_by(user_id=user_id).delete()
    db.session.commit()

def build_saved_goal_detail(result: dict) -> str:
    lines = [result.get("goal_detail", "").strip()]
    milestones = result.get("milestones") or []
    practice_focus = result.get("practice_focus") or []

    if milestones:
        lines.extend(["", "【3か月マイルストーン】"])
        for item in milestones:
            if isinstance(item, dict):
                lines.append(f"- {item.get('month')}か月目: {item.get('title')}")
                if item.get("ok_criteria"):
                    lines.append(f"  OK基準: {item.get('ok_criteria')}")
            else:
                lines.append(f"- {item}")

    if practice_focus:
        lines.extend(["", "【日々の練習で意識すること】"])
        lines.extend(f"- {item}" for item in practice_focus)

    return "\n".join(line for line in lines if line is not None).strip()
