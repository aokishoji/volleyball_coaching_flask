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

VOLLEYBALL_AREAS = {
    "spike": {
        "label": "スパイク",
        "outcome": "試合で狙ったコースへ強く打ち切れる",
        "practice": "助走リズム、踏み切り位置、最高到達点でのミート、コース打ち分けを分けて練習する",
        "metric": "10本中6本以上を狙ったコースに打てる",
    },
    "serve": {
        "label": "サーブ",
        "outcome": "相手のレセプションを崩すサーブを安定して打てる",
        "practice": "ターゲットサーブ、強弱の打ち分け、試合終盤を想定した連続成功を練習する",
        "metric": "10本中8本入り、3本以上は相手を崩せる",
    },
    "reception": {
        "label": "レセプション",
        "outcome": "強いサーブに対してもセッターへ返球できる",
        "practice": "構えの早さ、面の角度、左右移動後の静止、声かけをセットで練習する",
        "metric": "10本中7本以上を攻撃可能な位置へ返せる",
    },
    "defense": {
        "label": "ディグ・守備",
        "outcome": "相手の攻撃に対して予測して拾える",
        "practice": "構える位置、相手の肩と助走の観察、低い姿勢からの一歩目を練習する",
        "metric": "強打・フェイントの反応遅れを練習ごとに1つ減らす",
    },
    "setting": {
        "label": "トス・つなぎ",
        "outcome": "次の攻撃につながるボールを安定して上げられる",
        "practice": "落下地点への入り、体の向き、ハイセットと二段トスの再現性を練習する",
        "metric": "10本中7本以上をアタッカーが助走できる位置へ上げる",
    },
    "physical": {
        "label": "フィジカル",
        "outcome": "最後までフォームが崩れない体力と出力を作る",
        "practice": "ジャンプ、体幹、股関節、肩甲骨、着地動作を週の中で分けて鍛える",
        "metric": "練習終盤でもジャンプや低い姿勢の質を保てる",
    },
    "mental": {
        "label": "メンタル",
        "outcome": "大事な場面でも判断とプレー選択を崩さない",
        "practice": "点差・終盤・ミス直後を想定し、次の一本でやることを言語化する",
        "metric": "ミス後の次プレーで決めた行動を実行できる",
    },
}

DEFAULT_ROADMAP_AREAS = ["spike", "serve", "reception", "defense", "physical", "mental"]

def _selected_areas(focus_hint: list[str] | None) -> list[str]:
    selected = [area for area in (focus_hint or []) if area in VOLLEYBALL_AREAS]
    if not selected:
        selected = DEFAULT_ROADMAP_AREAS
    return selected

def build_goal_roadmap(form_data: dict) -> tuple[str, str]:
    rough_goal = (form_data.get("rough_goal") or "").strip()
    current_level = (form_data.get("current_level") or "").strip()
    weekly_days = str(form_data.get("weekly_practice_days") or "3")
    target_date = form_data.get("target_date")
    areas = _selected_areas(form_data.get("focus_hint"))

    title = f"長期目標: {rough_goal[:80]}" if rough_goal else "長期目標ロードマップ"

    lines = [
        "【最終目標】",
        rough_goal or "大会で結果を出す",
        "",
        "【現在地】",
        current_level or "AIコーチとの対話で現在地を確認しながら更新する",
        "",
        "【達成期限】",
        target_date.strftime("%Y-%m-%d") if target_date else "未設定",
        "",
        "【分解した強化テーマ】",
    ]

    for index, area_key in enumerate(areas, start=1):
        area = VOLLEYBALL_AREAS[area_key]
        lines.extend([
            f"{index}. {area['label']}",
            f"   ゴール: {area['outcome']}",
            f"   練習: {area['practice']}",
            f"   OK基準: {area['metric']}",
        ])

    lines.extend([
        "",
        "【マイルストーン】",
        "1か月目: 現在地を数値化し、各テーマのフォーム・判断の基準を決める",
        "3か月目: 練習内でOK基準を安定して達成できる状態にする",
        "6か月目: 練習試合で再現できる場面を増やし、弱点テーマを1つに絞る",
        "9か月目: 試合の点差・終盤・ミス直後でも実行できるようにする",
        "12か月目: 大会で使うプレー選択と役割を明確にしてピークを合わせる",
        "",
        "【週の練習案】",
        f"週{weekly_days}日の練習を想定する。",
        "技術練習: 強化テーマを1回につき1つに絞り、OK基準を記録する",
        "ゲーム形式: その日のテーマを試合の中で1つだけ意識する",
        "振り返り: できたこと、できなかったこと、次回の一手を短く残す",
        "",
        "【次にAIコーチと決めること】",
        "最初の2週間で一番伸ばしたいテーマを1つ選び、今日の練習メニューに落とし込む",
    ])

    return title, "\n".join(lines)
