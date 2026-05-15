# バレーボールコーチングアプリ 設計書

> この設計書を修正して「ここを変えてほしい」と伝えると、Claude がコードに反映します。

---

## 1. システム概要

バレーボール選手が「目標設定 → 練習テーマ作成 → 振り返り」のサイクルを繰り返すことで成長を記録するモバイルファーストWebアプリ。

| 項目 | 内容 |
|------|------|
| フレームワーク | Flask 3.x |
| DB | SQLite（本番環境も同じ） |
| ORM | Flask-SQLAlchemy |
| フォーム | Flask-WTF / WTForms |
| 認証 | Flask-Login |
| AI | OpenAI Responses API（`gpt-4o-mini`） |
| タイムゾーン | DB保存はUTC、表示はJSTに変換 |

---

## 2. 画面一覧

| 画面名 | URL | 説明 |
|--------|-----|------|
| ホーム | `/` | 現在の目標・マイルストーン・練習テーマ・前回の振り返りを表示 |
| ログイン | `/auth/login` | メールアドレス＋パスワード |
| 新規登録 | `/auth/register` | 名前・メール・パスワード・生年月日・性別・ポジション・バレー開始年月 |
| プロフィール編集 | `/profile/` | 名前・生年月日・性別・ポジション・バレー開始年月 |
| 身体データ | `/profile/physical` | 身長・体重・指高・最高到達点の時系列記録 |
| AI目標設定 | `/goals/roadmap` | AIコーチとの対話で3か月目標＋マイルストーンを作成（初期日付: 本日+90日） |
| 目標編集 | `/goals/<id>/edit` | 目標タイトル・詳細・マイルストーン3件を手動編集 |
| テーマ編集 | `/goals/theme/<id>/edit` | 今取り組むテーマのタイトル・説明・振り返りポイントを手動編集 |
| 課題分析 | `/analysis/assessment` | スパイク各要素の自己評価＋失敗パターン選択 |
| 深掘り分析 | `/analysis/deep-dive/<id>` | 課題の詳細質問（タイミング系） |
| 練習テーマ確認 | `/analysis/theme-latest` | 直近の練習テーマ表示（旧フロー） |
| 振り返り入力 | `/reflections/new` | 練習テーマへの振り返り記録 |
| 成長ログ | `/reflections/logs` | 振り返りがある練習テーマ＋振り返りのペア表示 |

---

## 3. データモデル

### User（ユーザー）

| カラム | 型 | 説明 |
|--------|-----|------|
| id | Integer PK | |
| email | String(255) unique | ログインID |
| password_hash | String(255) | bcryptハッシュ |
| created_at / updated_at | DateTime | UTC |

### Profile（プロフィール）

| カラム | 型 | 説明 |
|--------|-----|------|
| id | Integer PK | |
| user_id | FK → users | 1対1 |
| name | String(100) | 表示名 |
| birth_date | Date nullable | 生年月日（年齢は自動計算） |
| gender | String(20) nullable | `male` / `female` / `other` / `no_answer` |
| position | String(50) | WS / MB / S / L / OP |
| volleyball_start_date | Date nullable | バレー開始年月（日は常に1日、経験年数を自動計算） |
| age_group | String(50) | 旧カラム（後方互換のため残存） |
| experience_years | Integer | 旧カラム（後方互換のため残存） |

**プロパティ（計算値）**
- `profile.age` : birth_date から年齢を計算（誕生日前は1引く）
- `profile.volleyball_experience_years` : volleyball_start_date から経験年数を計算

**gender の選択肢**
`male`（男性）、`female`（女性）、`other`（その他）、`no_answer`（回答しない）

### PhysicalRecord（身体データ）

| カラム | 型 | 説明 |
|--------|-----|------|
| id | Integer PK | |
| user_id | FK → users | |
| recorded_date | Date | 計測日 |
| height | Float nullable | 身長 (cm) |
| weight | Float nullable | 体重 (kg) |
| finger_height | Float nullable | 指高 (cm) |
| max_reach | Float nullable | 最高到達点 (cm) |
| created_at | DateTime | UTC |

時系列で複数件保持。一覧は計測日の降順で表示。

### Goal（目標）

| カラム | 型 | 説明 |
|--------|-----|------|
| id | Integer PK | |
| user_id | FK → users | |
| skill_type | String(50) | `spike` / `three_month_ai` |
| goal_title | String(255) | 目標タイトル |
| goal_detail | Text | 目標詳細（テキスト） |
| target_date | Date | 期限 |
| status | String(20) | `active` / `completed` |
| current_month_override | Integer nullable | 手動マイルストーン切替（nullなら自動） |

### GoalMilestone（マイルストーン）

| カラム | 型 | 説明 |
|--------|-----|------|
| id | Integer PK | |
| goal_id | FK → goals | cascade delete |
| month_index | Integer | 1 / 2 / 3 |
| title | String(255) | 到達目標 |
| ok_criteria | Text | 達成判断基準 |
| practice_focus_json | Text | JSON配列（日々意識すること） |

### GoalCoachSession（AI目標設定セッション）

| カラム | 型 | 説明 |
|--------|-----|------|
| id | Integer PK | |
| user_id | FK → users unique | ユーザー1人につき1件 |
| history_json | Text | OpenAI APIに渡す会話履歴 |
| display_json | Text | 画面表示用の会話履歴 |
| result_json | Text | 最新のAI応答JSON |
| target_date_text | String(20) | ISO形式 `YYYY-MM-DD` |

### DailyPracticeTheme（練習テーマ）

| カラム | 型 | 説明 |
|--------|-----|------|
| id | Integer PK | |
| user_id | FK → users | |
| goal_id | FK → goals | |
| milestone_id | FK → goal_milestones nullable | |
| theme_title | String(255) | テーマタイトル（20字以内） |
| theme_detail | Text | テーマ説明と取り組み方 |
| check_point | Text | 練習後に確認するポイント |
| created_at | DateTime | UTC |

### Reflection（振り返り）

| カラム | 型 | 説明 |
|--------|-----|------|
| id | Integer PK | |
| user_id | FK → users | |
| daily_theme_id | FK → daily_practice_themes nullable | 現行フロー |
| practice_theme_id | FK → practice_themes nullable | 旧フロー用（後方互換） |
| theme_applied | String(20) | `yes` / `partial` / `no` |
| good_points | Text | できたこと |
| bad_points | Text | できなかったこと |
| cause_hypothesis | Text nullable | 原因の仮説 |
| next_action | Text | 次回意識すること |
| coach_question | Text nullable | コーチへの質問 |
| created_at | DateTime | UTC |

---

## 4. メインフロー

### 現行フロー（推奨）

```
1. AI目標設定 (/goals/roadmap)
   └─ AIコーチと対話 → Goal + GoalMilestone × 3 を保存

2. ホーム (/)
   └─ 「練習テーマを作る」ボタン → POST /goals/<id>/today-theme
      └─ AIが DailyPracticeTheme を生成・保存
   └─ 「テーマを微調整する」→ /goals/theme/<id>/edit で手動編集
   └─ 「目標を編集する」→ /goals/<id>/edit で手動編集

3. 振り返り (/reflections/new)
   └─ 最新の DailyPracticeTheme を表示しながら入力
      └─ Reflection を保存 (daily_theme_id に紐付け)

4. 成長ログ (/reflections/logs)
   └─ 振り返りがある DailyPracticeTheme と Reflection をペアで表示
```

### マイルストーン進行

| 方法 | 説明 |
|------|------|
| 自動 | 目標作成から経過日数で自動切替（〜29日: 1か月目、30〜59日: 2か月目、60日〜: 3か月目） |
| 手動（早送り） | ホームの「次のマイルストーンに進む →」ボタン |
| 手動（リセット） | ホームの「自動判定に戻す」ボタン |

---

## 5. ルート一覧

| Blueprint | prefix | ファイル |
|-----------|--------|---------|
| auth_bp | なし | `app/routes/auth.py` |
| main_bp | なし | `app/routes/main.py` |
| goals_bp | `/goals` | `app/routes/goals.py` |
| analysis_bp | `/analysis` | `app/routes/analysis.py` |
| reflection_bp | `/reflections` | `app/routes/reflection.py` |
| profile_bp | `/profile` | `app/routes/profile.py` |

### goals_bp の主要エンドポイント

| メソッド | URL | 処理 |
|----------|-----|------|
| GET/POST | `/goals/roadmap` | AI目標設定（対話）、初期日付=本日+90日 |
| GET/POST | `/goals/<id>/edit` | 目標・マイルストーンの手動編集 |
| GET/POST | `/goals/theme/<id>/edit` | 練習テーマの手動編集 |
| POST | `/goals/<id>/today-theme` | 練習テーマをAI生成 |
| POST | `/goals/<id>/advance-milestone` | 手動でマイルストーンを次へ |
| POST | `/goals/<id>/reset-milestone` | 自動判定に戻す |

### profile_bp の主要エンドポイント

| メソッド | URL | 処理 |
|----------|-----|------|
| GET/POST | `/profile/` | プロフィール編集 |
| GET/POST | `/profile/physical` | 身体データ記録・一覧 |

---

## 6. サービス層

| ファイル | 関数 | 説明 |
|----------|------|------|
| `ai_goal_coach_service.py` | `ask_goal_coach(history)` | OpenAI APIで目標設定対話 |
| `ai_goal_coach_service.py` | `get/upsert/clear_coach_session()` | DB会話セッション管理 |
| `goal_progress_service.py` | `current_month_index(goal)` | 現在のマイルストーン番号を返す |
| `goal_progress_service.py` | `build_today_theme_ai(...)` | AIで練習テーマ生成（失敗時はルールベースにフォールバック） |
| `goal_service.py` | `build_goal_text(form_data)` | 手動目標のタイトル・詳細を生成 |

---

## 7. AI機能

### AI目標設定（`ai_goal_coach_service.py`）

- モデル: `gpt-4o-mini`（設定変更可）
- APIキーなし時: フォールバックで仮モード動作
- 返答形式: JSON（`status: question/ready`）
- `ready` になったら「確定する」ボタンで DB 保存
- 「まだ調整したい」でメッセージを送信して対話継続

### AI練習テーマ生成（`goal_progress_service.py`）

- 入力: 目標・マイルストーン・直近3件の振り返り
- 出力: `theme_title`（20字以内）・`theme_detail`（3〜5文）・`check_point`
- APIキーなし・例外時: ルールベースにフォールバック

---

## 8. フォーム定義（`app/forms.py`）

| フォーム名 | 主なフィールド |
|-----------|---------------|
| LoginForm | email, password |
| RegisterForm | name, email, password, birth_date, gender, position, volleyball_start_year, volleyball_start_month |
| ProfileForm | name, birth_date, gender, position, volleyball_start_year, volleyball_start_month |
| PhysicalRecordForm | recorded_date, height, weight, finger_height, max_reach |
| GoalRoadmapForm | rough_goal, current_level, target_date（初期値=今日+90日）, weekly_practice_days, focus_hint |
| GoalEditForm | goal_title, goal_detail, m1_title/ok_criteria/practice_focus, m2_…, m3_… |
| DailyThemeEditForm | theme_title, theme_detail, check_point |
| ReflectionForm | theme_applied, good_points, bad_points, cause_hypothesis, next_action, coach_question |

---

## 9. 設定・環境変数

| 変数名 | デフォルト | 説明 |
|--------|-----------|------|
| `SECRET_KEY` | `dev-secret-key` | セッション暗号化キー（本番は必ず変更） |
| `DATABASE_URL` | `sqlite:///instance/app.db` | DB接続URL |
| `OPENAI_API_KEY` | なし | OpenAI APIキー（なしでも動作） |
| `OPENAI_MODEL` | `gpt-4o-mini` | 使用モデル |

設定ファイル: `config.py`、値は `.env` に記載

---

## 10. テンプレート構成

```
app/templates/
├── base.html
├── _form_helpers.html
├── auth/
│   ├── login.html
│   └── register.html          ← 生年月日・性別・バレー開始年月を追加
├── goals/
│   ├── roadmap.html
│   ├── edit.html              ← 目標・マイルストーン手動編集（新規）
│   └── theme_edit.html        ← 練習テーマ手動編集（新規）
├── analysis/
│   ├── assessment.html
│   ├── deep_dive.html
│   └── theme_latest.html
├── reflection/
│   ├── new.html
│   └── logs.html              ← 振り返りがないテーマは非表示
├── main/
│   └── home.html              ← 「目標を編集」「テーマを微調整」ボタン追加
└── profile/
    ├── edit.html              ← 生年月日・性別・バレー開始年月に変更
    └── physical.html          ← 身体データ記録・一覧（新規）
```

---

## 11. DBスキーマ変更時の手順

SQLAlchemy の `create_all()` は既存テーブルを変更しないため、カラム追加は以下の手順が必要。

**新規インストール（DBなし）**: `python -m flask --app run init-db` のみでOK

**既存DBへのカラム追加**:
```sql
-- profiles テーブルへの追加
ALTER TABLE profiles ADD COLUMN birth_date DATE;
ALTER TABLE profiles ADD COLUMN volleyball_start_date DATE;
ALTER TABLE profiles ADD COLUMN gender VARCHAR(20);

-- 新規テーブル（init-dbで自動作成）
-- physical_records テーブルは init-db で作成される
```

---

## 12. 既知の制約・注意事項

- Windowsローカル環境では `run.py` に `reloader_type="stat"` が必要
- 旧フロー（Assessment → PracticeTheme → Reflection）は動作するが、新規開発は新フロー優先
- 成長ログは「振り返りが1件以上ある練習テーマ」のみ表示する

---

## 13. 想定ユースフロー

### 初回登録
1. **新規登録** — 名前・メール・パスワード・生年月日・性別・ポジション・バレー開始年月
2. （任意）**身体データ記録** — 身長・体重・指高・最高到達点を初回計測として記録

---

### 目標設定（初回 / 目標が終わったとき）
3. **AI目標設定** — AIコーチと対話して3か月目標を作成
   - 「3か月後にどうなりたいか」を入力
   - AIが質問しながら具体的な目標・3段階マイルストーンを提案
   - 納得できたら「確定する」で保存
   - 気に入らなければ「まだ調整したい」で対話継続
4. （必要なら）**目標を手動で微調整** — 保存後もホーム→「目標を編集する」から修正可能

---

### 日々の練習サイクル（繰り返し）
5. **練習テーマを作る** — ホームで「練習テーマを作る」→ AIが目標・マイルストーン・最近の振り返りをもとに今日の集中ポイントを1つ提案
6. （任意）**テーマを微調整** — 「テーマを微調整する」から内容を手動編集
7. **練習する** — テーマを意識して練習
8. **振り返りを書く** — 練習後にホーム→「振り返りを書く」
   - テーマを意識できたか
   - できたこと / できなかったこと
   - 原因の仮説
   - 次回意識すること
   - コーチへの質問（任意）
9. （必要なら）**テーマを作り直す** — 同じテーマを数日続けるか、新しいテーマに切り替えるか選択

> 1テーマを数日〜1週間集中 → 振り返り → 次のテーマへ、を繰り返す

---

### 1か月後
10. **成長ログを確認** — 振り返りの積み上げを見返す
11. **マイルストーンを進める** — ホーム「次のマイルストーンに進む →」（または経過30日で自動切替）
    - 2か月目マイルストーンに合わせたテーマがAIで生成されるようになる
12. （任意）**身体データ更新** — 身長・体重・指高・最高到達点を再計測

---

### 2か月後
13. 同様に3か月目マイルストーンへ進む
14. 成長ログで1〜2か月目の変化を振り返る

---

### 3か月後
15. **最終振り返り** — 成長ログ全体を見渡し、目標達成度を確認
16. **新しい目標を設定** — 次の3か月目標をAIと設定する
17. （任意）**身体データ更新** — 3か月の体の変化を記録

---

### 利用頻度のイメージ

| タイミング | 操作 | 所要時間 |
|-----------|------|---------|
| 月1回 | 目標設定・マイルストーン進行 | 10〜15分 |
| 週1〜2回 | 練習テーマ作成 | 1〜2分 |
| 練習ごと | 振り返り記録 | 3〜5分 |
| 月1回 | 身体データ計測 | 1分 |

---

## 14. 今後の拡張候補

> ここに追加・変更したい機能を書いてください。Claude が実装します。

- [ ] （例）振り返りの一覧に日付フィルター
- [ ] （例）目標を「完了」にする機能
- [ ] （例）ポジション・性別・年代に応じたAIプロンプトの調整
- [ ] （例）身体データのグラフ表示
