"""
マニュアル用スクリーンショット撮影スクリプト
seed_demo.py でデータ作成後に実行すること
"""
import subprocess, time, sys, os

ROOT  = r"c:\Users\shoji\Documents\GitHub\volleyball_coaching_flask"
OUT   = os.path.join(ROOT, "app", "static", "images", "manual")
os.makedirs(OUT, exist_ok=True)

BASE  = "http://localhost:5000"
EMAIL = "demo.manual@example.com"   # seed_demo.py と合わせる
PASS  = "DemoPass2026"


def wait_server(url, timeout=40):
    import urllib.request
    for _ in range(timeout):
        try:
            urllib.request.urlopen(url, timeout=2)
            return True
        except Exception:
            time.sleep(1)
    return False


def ss(page, fname):
    path = os.path.join(OUT, fname)
    page.screenshot(path=path)
    print(f"  [SS] {fname}  ({page.url})")


def nav(page, url):
    page.goto(url)
    page.wait_for_load_state("networkidle")


def login(page):
    nav(page, f"{BASE}/login")
    page.fill('[name=email]', EMAIL)
    page.fill('[name=password]', PASS)
    page.locator('input[type=submit], button[type=submit]').first.click()
    page.wait_for_load_state("networkidle")
    ok = page.url == f"{BASE}/" or page.url.startswith(f"{BASE}/?")
    print(f"  login -> {page.url}  ok={ok}")
    return ok


def main():
    flask = subprocess.Popen(
        [sys.executable, "run.py"],
        cwd=ROOT,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    print("Flask starting...")
    if not wait_server(f"{BASE}/login"):
        print("ERROR: Flask did not start")
        flask.terminate()
        return
    print("Flask ready")

    from playwright.sync_api import sync_playwright
    with sync_playwright() as p:
        browser = p.chromium.launch()

        # ─── ① ログイン画面（未ログイン状態）
        ctx1 = browser.new_context(viewport={"width": 390, "height": 844}, device_scale_factor=2)
        p1   = ctx1.new_page()
        p1.set_default_timeout(10000)

        nav(p1, f"{BASE}/login")
        ss(p1, "01_login.png")

        # ─── ② 新規登録画面（未ログイン状態、送信しない）
        nav(p1, f"{BASE}/register")
        ss(p1, "02_register.png")
        ctx1.close()

        # ─── ログイン済みコンテキスト
        ctx2 = browser.new_context(viewport={"width": 390, "height": 844}, device_scale_factor=2)
        page = ctx2.new_page()
        page.set_default_timeout(12000)

        if not login(page):
            print("ERROR: login failed - run seed_demo.py first")
            ctx2.close()
            browser.close()
            flask.terminate()
            flask.wait()
            return

        # ─── ③ ホーム画面（データあり）
        nav(page, f"{BASE}/")
        ss(page, "03_home.png")

        # ─── ④ AI目標設定フォーム（送信前）
        # GoalCoachSession がないのでフォームが表示される
        nav(page, f"{BASE}/goals/roadmap")
        ss(page, "04_goal_form.png")

        # ─── ⑤ AIチャット画面（フォーム送信後）
        # フォームを送信してAIのチャット画面を表示する
        try:
            page.fill('[name=rough_goal]', '試合でスパイクを安定して決めたい')
            page.fill('[name=current_level]', 'タイミングが合わずアウトになることが多い')
            page.select_option('[name=weekly_practice_days]', '3')
            page.locator('[name=focus_hint]').select_option(['spike'])
            page.locator('form').filter(
                has=page.locator('[name=rough_goal]')
            ).locator('button[type=submit], input[type=submit]').first.click()
            page.wait_for_load_state("networkidle")
            time.sleep(1)
            ss(page, "05_goal_chat.png")
        except Exception as e:
            print(f"  WARN goal chat: {e}")
            ss(page, "05_goal_chat.png")

        # チャットセッションをリセット（ホームに影響しないように）
        try:
            page.goto(f"{BASE}/goals/roadmap", wait_until="networkidle")
            reset_btn = page.locator('button:has-text("最初からやり直す")')
            if reset_btn.count() > 0:
                reset_btn.first.click()
                page.wait_for_load_state("networkidle")
        except Exception:
            pass

        # ─── ⑥ 課題分析フォーム（スパイク自己診断）
        nav(page, f"{BASE}/analysis/")
        ss(page, "06_assessment.png")

        # フォーム送信して session["assessment_id"] をセット（⑦の深掘りに必要）
        for field, val in [
            ('approach_rating', '3'), ('takeoff_rating', '3'),
            ('jump_rating', '4'),    ('air_posture_rating', '3'),
            ('contact_rating', '4'), ('contact_point_rating', '3'),
            ('course_rating', '3'),  ('block_rating', '3'),
            ('timing_rating', '2'),  ('mental_rating', '3'),
        ]:
            try: page.select_option(f'[name={field}]', val)
            except: pass
        try:
            page.locator('[name=failure_patterns]').select_option(['timing', 'out'])
        except: pass
        page.locator('input[type=submit], button[type=submit]').first.click()
        page.wait_for_load_state("networkidle")
        print(f"  after assessment -> {page.url}")

        # ─── ⑦ 深掘り質問（セッション有りで表示）
        if "deep-dive" in page.url:
            ss(page, "07_deepdive.png")
        else:
            nav(page, f"{BASE}/analysis/deep-dive")
            ss(page, "07_deepdive.png")

        # 深掘りを送信して練習テーマを生成
        try:
            for field, val in [
                ('timing_start',     'early'),
                ('timing_takeoff',   'yes'),
                ('timing_toss',      'yes'),
                ('timing_match_only','yes'),
                ('timing_tension',   'no'),
            ]:
                page.select_option(f'[name={field}]', val)
            page.locator('input[type=submit], button[type=submit]').first.click()
            page.wait_for_load_state("networkidle")
            print(f"  after deepdive -> {page.url}")
        except Exception as e:
            print(f"  WARN deepdive submit: {e}")

        # ─── ⑧ 今日の練習テーマ
        if "theme/latest" in page.url:
            ss(page, "08_theme.png")
        else:
            nav(page, f"{BASE}/analysis/theme/latest")
            ss(page, "08_theme.png")

        # ─── ③ ホーム再撮影（テーマ生成後の最終状態）
        nav(page, f"{BASE}/")
        ss(page, "03_home.png")

        # ─── ⑨ 振り返り記録フォーム
        nav(page, f"{BASE}/reflections/new")
        ss(page, "09_reflection.png")

        # ─── ⑩ 成長ログ（過去記録 + シードデータ）
        nav(page, f"{BASE}/reflections/logs")
        ss(page, "10_logs.png")

        # ─── ⑪ 身体データ（シードデータ3件の一覧）
        nav(page, f"{BASE}/profile/physical")
        ss(page, "11_physical.png")

        ctx2.close()
        browser.close()
        print(f"\nDONE -> {OUT}")

    flask.terminate()
    flask.wait()
    print("Flask stopped")


if __name__ == "__main__":
    main()
