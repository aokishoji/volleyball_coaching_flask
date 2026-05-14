# バレーボール選手向けコーチングアプリ 詳細設計書

## 1. 文書情報

- 文書名: バレーボール選手向けコーチングアプリ 詳細設計書
- 対象システム: Flask製Webアプリ
- 想定利用端末: スマートフォン中心、PC対応
- 開発方針: MVPから段階的に拡張
- 初期対象スキル: スパイク

---

## 2. システム概要

### 2.1 システムの目的
本システムは、バレーボール選手が自分の目標を具体化し、現状とのGapを整理し、日々の練習を振り返りながら改善を継続できるよう支援するWebアプリである。

本システムは単なる練習メニュー提示ではなく、以下を支援する。

- 目標の具体化
- 課題の分析
- 原因の深掘り
- 今日の練習テーマの明確化
- 練習後の振り返り
- 次回へ向けた改善整理
- リアルコーチへ相談すべき内容の整理

### 2.2 システムコンセプト
選手の「なんとなくの悩み」を、
「次の練習で意識する具体的行動」に変換する伴走型コーチングアプリ。

### 2.3 想定ユーザー
- 中学生・高校生のバレーボール選手
- 将来的には小学生、高校卒業後の競技者も対象
- 将来的にはコーチ、保護者の閲覧拡張も可能

### 2.4 初期リリース範囲
MVPでは、以下の流れを成立させることを目的とする。

1. ユーザー登録・ログイン
2. 目標設定
3. 課題分析
4. 深掘り質問
5. 今日の練習テーマ表示
6. 振り返り入力
7. 成長ログ閲覧

---

## 3. 開発方針

### 3.1 採用技術
- バックエンド: Python / Flask
- ORM: SQLAlchemy
- 認証: Flask-Login
- フォーム: Flask-WTF
- DB: SQLite（開発・MVP）
- フロント: HTML / CSS / Jinja2
- CSS方針: スマホ優先のレスポンシブ設計

### 3.2 UI方針
- スマホ縦画面を最優先
- 1画面あたりの情報量は少なめ
- 大きめのボタンと余白を確保
- 入力は選択式を中心にする
- 練習前1分、練習後2分程度で使える体験を目指す

### 3.3 ロジック方針
- 初期版はルールベース中心で実装する
- AIに全面依存しない
- 原因を断定しない
- 仮説として提示する
- リアルコーチへ確認すべき観点を整理する

### 3.4 MVPで対象外とする項目
- 動画自動解析
- フォーム自動採点
- SNS機能
- ランキング機能
- 保護者共有
- コーチ専用管理画面
- Push通知

---

## 4. ユースケース

### 4.1 初回利用
1. ユーザーが会員登録する
2. ログインする
3. 目標設定を行う
4. 課題分析に回答する
5. 深掘り質問に回答する
6. 今日の練習テーマを確認する

### 4.2 日常利用
1. ホームで現在の目標と今日のテーマを確認する
2. 練習後に振り返りを入力する
3. 成長ログで過去の記録を見る
4. 必要に応じて再度課題分析を行う

### 4.3 コーチ相談準備
1. 振り返り内容をもとに課題を整理する
2. コーチに見てもらうポイントを確認する
3. 練習時に相談する

---

## 5. 画面一覧

| 画面ID | 画面名 | 目的 |
|---|---|---|
| SCR-001 | ログイン画面 | 認証 |
| SCR-002 | 新規登録画面 | ユーザー作成 |
| SCR-003 | ホーム画面 | 現在の状況確認 |
| SCR-004 | 目標設定画面 | 目標の具体化 |
| SCR-005 | 課題分析画面 | 課題の大分類整理 |
| SCR-006 | 深掘り画面 | 原因候補の絞り込み |
| SCR-007 | 今日の練習テーマ画面 | 練習時の意識ポイント確認 |
| SCR-008 | 振り返り画面 | 練習結果の記録 |
| SCR-009 | 成長ログ画面 | 過去履歴の閲覧 |
| SCR-010 | プロフィール画面 | 基本情報管理 |

---

## 6. 画面詳細設計

## 6.1 SCR-001 ログイン画面

### 目的
ユーザー認証を行う。

### 表示項目
- メールアドレス入力欄
- パスワード入力欄
- ログインボタン
- 新規登録へのリンク

### 入力項目
| 項目名 | 必須 | 形式 | 備考 |
|---|---|---|---|
| メールアドレス | 必須 | email | 一意 |
| パスワード | 必須 | password | 8文字以上想定 |

### 動作
- 入力値を認証
- 成功時はホーム画面へ遷移
- 失敗時はエラーメッセージ表示

---

## 6.2 SCR-002 新規登録画面

### 目的
新規ユーザーを登録する。

### 入力項目
| 項目名 | 必須 | 形式 | 備考 |
|---|---|---|---|
| 表示名 | 必須 | text | ニックネーム可 |
| メールアドレス | 必須 | email | 一意 |
| パスワード | 必須 | password | ハッシュ化保存 |
| パスワード確認 | 必須 | password | 一致確認 |
| 学年/年代区分 | 任意 | select | 中1〜高3など |
| ポジション | 任意 | select | WS, MB, S, L など |

### 動作
- 入力チェック
- users, profilesへ登録
- 登録後はログインまたはホームへ遷移

---

## 6.3 SCR-003 ホーム画面

### 目的
現在の目標、優先課題、今日のテーマを一目で確認できるようにする。

### 表示項目
- 現在の目標
- 目標期限
- 現在の最優先課題
- 今日の練習テーマ
- 前回の振り返り要約
- メニュー一覧

### ボタン
- 目標を設定する
- 課題分析をする
- 今日のテーマを見る
- 振り返りを書く
- 成長ログを見る

### レイアウト方針
- カードUI
- 上から順に情報を並べる
- 最重要情報を上部に配置

---

## 6.4 SCR-004 目標設定画面

### 目的
選手の曖昧な目標を具体化する。

### 入力項目
| 項目名 | 必須 | 形式 | 例 |
|---|---|---|---|
| 対象スキル | 必須 | select | スパイク |
| 改善したいこと | 必須 | select/text | 決定率を上げたい |
| 困っている場面 | 必須 | textarea | 試合でタイミングが合わない |
| 理想の状態 | 任意 | textarea | 力まず打ち分けできる |
| 期限 | 任意 | date | 1か月後 |

### 出力項目
- 目標タイトル
- 目標詳細文

### 生成ルール例
入力内容をもとに以下のような文章を生成する。

例:
- タイトル: スパイクのミート安定化
- 詳細: 試合形式でもタイミングを崩さず、ミートミスを減らして安定して打てる状態を目指す

---

## 6.5 SCR-005 課題分析画面

### 目的
課題を大きなカテゴリで整理する。

### 入力項目
#### 自己評価（1〜5）
- 助走
- 踏切
- ジャンプ
- 空中姿勢
- ミート
- 打点
- コース打ち分け
- ブロック対応
- トスとのタイミング
- メンタル

#### 失敗パターン（複数選択可）
- ネットにかかる
- アウトになる
- ミートミスが多い
- 打点が低いと感じる
- ブロックにつかまる
- タイミングが合わない
- 力んでしまう

#### 自由記述
- 困っていること詳細

### 出力
- 課題候補一覧
- 深掘り対象カテゴリ

### 課題候補抽出ルール例
- 自己評価が低い項目を優先候補とする
- 失敗パターンとの関連性を加味する
- 上位1〜2個を深掘り対象とする

---

## 6.6 SCR-006 深掘り画面

### 目的
課題分析結果をもとに、原因候補を絞り込む。

### 基本仕様
- 課題カテゴリごとに質問テンプレートを持つ
- 表示質問は条件分岐で出し分ける

### 例: タイミング課題の深掘り質問
| 質問キー | 質問内容 | 回答形式 |
|---|---|---|
| timing_start | 助走の入りが早い/遅いと感じるか | select |
| timing_takeoff | 踏切位置が近くなりやすいか | yes/no |
| timing_toss | トスの種類で崩れやすいか | yes/no |
| timing_match_only | 練習ではできるが試合で崩れるか | yes/no |
| timing_tension | 力みを感じるか | yes/no |

### 出力
- 優先課題仮説
- 課題説明文
- 今日の練習テーマ候補
- コーチ確認ポイント

### 出力例
- 優先課題仮説: 助走開始位置と踏切位置の再現性
- 説明: 強く打つことより、毎回同じリズムで入れることが優先かもしれません
- コーチ確認ポイント: 助走開始位置と最後の2歩のズレ

---

## 6.7 SCR-007 今日の練習テーマ画面

### 目的
今回の練習で意識すべき最重要ポイントを明確にする。

### 表示項目
- 今日のテーマ
- 意識ポイント
- セルフチェック項目
- コーチに見てもらうポイント

### 表示例
- 今日のテーマ: 最後の2歩を毎回そろえる
- 意識ポイント: 高く跳ぶよりも、同じリズムで踏み切ることを優先する
- セルフチェック: 助走開始位置は一定だったか
- コーチ確認: 踏切位置が前に詰まりすぎていないか

---

## 6.8 SCR-008 振り返り画面

### 目的
練習後の結果を記録し、次回へつなげる。

### 入力項目
| 項目名 | 必須 | 形式 |
|---|---|---|
| 今日のテーマを意識できたか | 必須 | select |
| できたこと | 必須 | textarea |
| できなかったこと | 必須 | textarea |
| 原因の仮説 | 任意 | textarea |
| 次回意識すること | 必須 | textarea |
| コーチに聞きたいこと | 任意 | textarea |

### 出力
- 振り返り要約
- 次回の重点メモ

---

## 6.9 SCR-009 成長ログ画面

### 目的
過去の取り組みを振り返れるようにする。

### 表示項目
- 目標履歴一覧
- 練習テーマ履歴一覧
- 振り返り履歴一覧
- よく出る課題

### 検討事項
- 絞り込み条件追加
- カレンダー表示
- グラフ化は将来対応

---

## 6.10 SCR-010 プロフィール画面

### 目的
ユーザー基本情報を管理する。

### 項目
- 表示名
- 学年/年代区分
- ポジション
- 経験年数

---

## 7. 画面遷移設計

```text
SCR-001 ログイン
  └─ SCR-003 ホーム

SCR-002 新規登録
  └─ SCR-003 ホーム

SCR-003 ホーム
  ├─ SCR-004 目標設定
  ├─ SCR-005 課題分析
  ├─ SCR-007 今日の練習テーマ
  ├─ SCR-008 振り返り
  ├─ SCR-009 成長ログ
  └─ SCR-010 プロフィール

SCR-004 目標設定
  └─ SCR-005 課題分析

SCR-005 課題分析
  └─ SCR-006 深掘り

SCR-006 深掘り
  └─ SCR-007 今日の練習テーマ

SCR-007 今日の練習テーマ
  └─ SCR-008 振り返り
```

---

## 8. DB詳細設計

## 8.1 テーブル一覧
- users
- profiles
- goals
- assessments
- deep_dive_answers
- practice_themes
- reflections

---

## 8.2 users

### 用途
認証情報を管理する。

| カラム名 | 型 | NULL | PK | 備考 |
|---|---|---|---|---|
| id | Integer | No | Yes | 自動採番 |
| email | String(255) | No | No | 一意 |
| password_hash | String(255) | No | No | ハッシュ |
| created_at | DateTime | No | No | 作成日時 |
| updated_at | DateTime | No | No | 更新日時 |

### 制約
- emailにユニーク制約

---

## 8.3 profiles

### 用途
ユーザーの基本情報を管理する。

| カラム名 | 型 | NULL | PK | 備考 |
|---|---|---|---|---|
| id | Integer | No | Yes | 自動採番 |
| user_id | Integer | No | No | users.id FK |
| name | String(100) | No | No | 表示名 |
| age_group | String(50) | Yes | No | 中1〜高3など |
| position | String(50) | Yes | No | WS, MB, S, L |
| experience_years | Integer | Yes | No | 経験年数 |
| created_at | DateTime | No | No | 作成日時 |
| updated_at | DateTime | No | No | 更新日時 |

---

## 8.4 goals

### 用途
ユーザーの目標を管理する。

| カラム名 | 型 | NULL | PK | 備考 |
|---|---|---|---|---|
| id | Integer | No | Yes | 自動採番 |
| user_id | Integer | No | No | users.id FK |
| skill_type | String(50) | No | No | spike など |
| goal_title | String(255) | No | No | 目標見出し |
| goal_detail | Text | No | No | 目標詳細 |
| target_date | Date | Yes | No | 期限 |
| status | String(20) | No | No | active / archived |
| created_at | DateTime | No | No | 作成日時 |
| updated_at | DateTime | No | No | 更新日時 |

---

## 8.5 assessments

### 用途
課題分析結果を保存する。

| カラム名 | 型 | NULL | PK | 備考 |
|---|---|---|---|---|
| id | Integer | No | Yes | 自動採番 |
| user_id | Integer | No | No | users.id FK |
| goal_id | Integer | No | No | goals.id FK |
| issue_category | String(100) | Yes | No | 優先カテゴリ |
| self_rating_json | Text | No | No | JSON文字列 |
| failure_pattern_json | Text | No | No | JSON文字列 |
| notes | Text | Yes | No | 補足 |
| created_at | DateTime | No | No | 作成日時 |

### self_rating_json 例
```json
{
  "approach": 2,
  "takeoff": 2,
  "jump": 3,
  "air_posture": 3,
  "contact": 2,
  "contact_point": 3,
  "course": 2,
  "block": 2,
  "timing": 1,
  "mental": 3
}
```

---

## 8.6 deep_dive_answers

### 用途
深掘り質問への回答を保存する。

| カラム名 | 型 | NULL | PK | 備考 |
|---|---|---|---|---|
| id | Integer | No | Yes | 自動採番 |
| assessment_id | Integer | No | No | assessments.id FK |
| question_key | String(100) | No | No | 識別子 |
| answer_value | String(255) | No | No | 回答値 |
| created_at | DateTime | No | No | 作成日時 |

---

## 8.7 practice_themes

### 用途
その時点の練習テーマを保存する。

| カラム名 | 型 | NULL | PK | 備考 |
|---|---|---|---|---|
| id | Integer | No | Yes | 自動採番 |
| user_id | Integer | No | No | users.id FK |
| goal_id | Integer | No | No | goals.id FK |
| assessment_id | Integer | No | No | assessments.id FK |
| theme_title | String(255) | No | No | 今日のテーマ |
| theme_detail | Text | No | No | 詳細説明 |
| self_check_point | Text | Yes | No | セルフチェック |
| coach_check_point | Text | Yes | No | コーチ確認点 |
| created_at | DateTime | No | No | 作成日時 |

---

## 8.8 reflections

### 用途
練習後の振り返りを保存する。

| カラム名 | 型 | NULL | PK | 備考 |
|---|---|---|---|---|
| id | Integer | No | Yes | 自動採番 |
| user_id | Integer | No | No | users.id FK |
| practice_theme_id | Integer | No | No | practice_themes.id FK |
| theme_applied | String(20) | No | No | yes/no/partial |
| good_points | Text | No | No | 良かったこと |
| bad_points | Text | No | No | 課題 |
| cause_hypothesis | Text | Yes | No | 原因仮説 |
| next_action | Text | No | No | 次回意識点 |
| coach_question | Text | Yes | No | コーチ質問 |
| created_at | DateTime | No | No | 作成日時 |

---

## 9. Flaskアプリ構成案

```text
project/
├─ app.py
├─ config.py
├─ requirements.txt
├─ /app
│  ├─ __init__.py
│  ├─ models.py
│  ├─ forms.py
│  ├─ routes/
│  │  ├─ auth.py
│  │  ├─ main.py
│  │  ├─ goals.py
│  │  ├─ analysis.py
│  │  ├─ reflection.py
│  │  └─ profile.py
│  ├─ services/
│  │  ├─ goal_service.py
│  │  ├─ analysis_service.py
│  │  ├─ deep_dive_service.py
│  │  └─ theme_service.py
│  ├─ templates/
│  │  ├─ base.html
│  │  ├─ auth/
│  │  ├─ main/
│  │  ├─ goals/
│  │  ├─ analysis/
│  │  ├─ reflection/
│  │  └─ profile/
│  └─ static/
│     ├─ css/
│     └─ js/
└─ /instance
   └─ app.db
```

### 方針
- routes は画面単位で分割
- services に業務ロジックを寄せる
- models はSQLAlchemyで一元管理
- templates は画面カテゴリで分ける

---

## 10. ルーティング設計

| メソッド | パス | 機能 |
|---|---|---|
| GET/POST | /login | ログイン |
| GET/POST | /register | 新規登録 |
| GET | / | ホーム |
| GET/POST | /goals/new | 目標設定 |
| GET/POST | /analysis | 課題分析 |
| GET/POST | /analysis/deep-dive | 深掘り |
| GET | /theme/latest | 今日の練習テーマ |
| GET/POST | /reflections/new | 振り返り入力 |
| GET | /logs | 成長ログ |
| GET/POST | /profile | プロフィール |
| GET | /logout | ログアウト |

---

## 11. フォーム設計

## 11.1 GoalForm

### 項目
- skill_type
- improve_target
- problem_scene
- ideal_state
- target_date

---

## 11.2 AssessmentForm

### 項目
- approach_rating
- takeoff_rating
- jump_rating
- air_posture_rating
- contact_rating
- contact_point_rating
- course_rating
- block_rating
- timing_rating
- mental_rating
- failure_patterns
- notes

---

## 11.3 DeepDiveForm

### 項目
- question_keyごとの回答
- 質問はカテゴリ別に動的生成

---

## 11.4 ReflectionForm

### 項目
- theme_applied
- good_points
- bad_points
- cause_hypothesis
- next_action
- coach_question

---

## 12. サービスロジック設計

## 12.1 goal_service.py

### 役割
- 目標設定入力から目標タイトル/詳細文を生成する

### 関数案
- build_goal_text(form_data)
- create_goal(user_id, form_data)

---

## 12.2 analysis_service.py

### 役割
- 自己評価と失敗パターンから課題候補を抽出する

### 関数案
- parse_assessment(form_data)
- detect_priority_issue(self_ratings, failure_patterns)
- create_assessment(user_id, goal_id, form_data)

### ロジック例
- 自己評価が低い順に候補化
- failure_patternsとの関連度で重みづけ
- 最優先カテゴリを返す

---

## 12.3 deep_dive_service.py

### 役割
- 優先カテゴリに応じた質問を返す
- 回答から原因仮説を生成する

### 関数案
- get_questions_by_issue(issue_category)
- analyze_deep_dive(issue_category, answers)
- save_deep_dive_answers(assessment_id, answers)

### ルール例
- timing課題で takeoffが近い=yes → 踏切位置再現性を優先仮説にする
- timing_match_only=yes → メンタル/試合時再現性も補助要因にする

---

## 12.4 theme_service.py

### 役割
- 課題仮説から今日のテーマを生成する

### 関数案
- build_theme(issue_hypothesis)
- create_practice_theme(user_id, goal_id, assessment_id, theme_data)

### 出力項目
- theme_title
- theme_detail
- self_check_point
- coach_check_point

---

## 13. 課題分析ロジック詳細

## 13.1 課題カテゴリ一覧
- approach
- takeoff
- jump
- air_posture
- contact
- contact_point
- course
- block
- timing
- mental

## 13.2 失敗パターンと関連カテゴリ例

| 失敗パターン | 関連カテゴリ |
|---|---|
| ネットにかかる | contact_point, timing, takeoff |
| アウトになる | contact, course, timing |
| ミートミスが多い | contact, timing, approach |
| 打点が低い | jump, takeoff, contact_point |
| ブロックにつかまる | course, block, timing |
| タイミングが合わない | timing, approach, takeoff |
| 力んでしまう | mental, contact, timing |

## 13.3 優先課題抽出の考え方
1. 自己評価の低いカテゴリを抽出
2. 失敗パターンとの一致カテゴリに加点
3. 最もスコアが高いカテゴリを優先課題候補とする
4. 2位カテゴリも補助候補として保持する

---

## 14. バリデーション設計

### 共通
- 必須入力漏れチェック
- 最大文字数チェック
- 不正な日付チェック
- ログイン必須画面制御

### 例
- メールアドレス形式チェック
- パスワード一致チェック
- 目標設定で対象スキル未選択不可
- 振り返りで next_action 未入力不可

---

## 15. エラーハンドリング方針

- 画面入力エラーは項目下に表示
- DB保存失敗時はフラッシュメッセージ表示
- 対象データ未存在時は404またはホームへ戻す
- 未ログイン時はログイン画面へリダイレクト

---

## 16. セキュリティ設計

- パスワードはWerkzeug等でハッシュ化
- CSRF対策を行う
- セッション管理を行う
- SQLAlchemyを利用しSQLインジェクションを避ける
- XSSを避けるためテンプレートで適切にエスケープする

---

## 17. 非機能要件

### 17.1 操作性
- スマホで片手操作しやすい
- ボタンはタップしやすいサイズ
- 文字サイズは小さすぎない

### 17.2 保守性
- スキル追加時にカテゴリと質問テンプレートを増やしやすい
- ルールベースのロジックをサービス層へ分離する

### 17.3 拡張性
- 将来的にPostgreSQLへ移行可能
- 将来的にAPI化しやすい構成
- 将来的に生成AIの補助を差し込みやすい構造

---

## 18. 今後の拡張候補

### フェーズ2
- コーチへの相談内容自動生成
- サーブ、レシーブ対応
- 課題推移の可視化

### フェーズ3
- 動画アップロード
- セルフ動画チェック
- コーチ/保護者共有
- PWA対応

---

## 19. 実装着手順の推奨

1. Flaskのひな形作成
2. 認証機能実装
3. DBモデル作成
4. ホーム画面作成
5. 目標設定画面作成
6. 課題分析画面作成
7. 深掘り画面作成
8. 練習テーマ生成ロジック実装
9. 振り返り画面作成
10. 成長ログ画面作成
11. デザイン調整
12. テスト

---

## 20. 開発時の実務メモ

- 最初から見た目を作り込みすぎない
- まずは一連の導線が通ることを優先する
- 課題分析ロジックはハードコードでもよいのでまず動かす
- deep_diveの質問テンプレートは辞書やJSON管理でもよい
- 将来的なAI活用を見越しても、MVPではルールベースを優先する

---

## 21. まとめ

本詳細設計書は、Flaskで開発するバレーボール選手向けコーチングWebアプリのMVP開発を前提としている。

本システムの中心価値は、
「目標設定 → 課題分析 → 深掘り → 今日のテーマ → 振り返り」
という成長サイクルを、スマホで継続しやすい形で提供することである。

今後は本設計書をベースに、
- 画面テンプレート作成
- DBモデル作成
- Flaskルーティング作成
- サービスロジック実装

へ進める。

---

## 22. 追加機能: 長期目標ロードマップ

### 22.1 目的
「1年後の大会で優勝したい」のような抽象的な長期目標を、AIコーチとの対話を通じて、バレーボールの具体的な強化テーマ・期限・OK基準・日々の練習案に分解する。

### 22.2 画面
| 画面ID | 画面名 | 目的 |
|---|---|---|
| SCR-011 | 長期目標ロードマップ画面 | ざっくりした目標を入力し、スパイク・サーブ・レセプション等へ分解する |

### 22.3 入力項目
| 項目名 | 必須 | 形式 | 例 |
|---|---|---|---|
| ざっくりした目標 | 必須 | textarea | 1年後の大会で優勝したい |
| 今の状態・課題感 | 任意 | textarea | スパイク決定力とレセプションが不安定 |
| 達成したい日 | 任意 | date | 大会日 |
| 週に練習できる日数 | 必須 | select | 週3日 |
| 特に強化したい要素 | 任意 | multiple select | スパイク、サーブ、レセプション |

### 22.4 出力項目
- 最終目標
- 現在地
- 達成期限
- 分解した強化テーマ
- 各テーマのゴール
- 各テーマの練習案
- 各テーマのOK基準
- 1か月、3か月、6か月、9か月、12か月のマイルストーン
- 週単位の練習案
- 次にAIコーチと決めること

### 22.5 保存方針
MVPでは既存の goals テーブルへ保存する。

- skill_type: long_term
- goal_title: 長期目標のタイトル
- goal_detail: 分解結果の本文
- target_date: 達成したい日
- status: active

将来的には goal_items / milestones / practice_plans のような子テーブルへ分割し、進捗管理やチェックリスト化に対応する。

### 22.6 ルーティング
| メソッド | パス | 機能 |
|---|---|---|
| GET/POST | /goals/roadmap | 長期目標ロードマップ作成 |

### 22.7 AI活用方針
MVPではルールベースで分解案を生成する。将来的に生成AIを接続する場合は、以下の対話を行う。

1. 最終目標を確認する
2. 現在地を質問する
3. 競技要素へ分解する
4. 優先順位を決める
5. 期限とOK基準を設定する
6. 日々の練習メニューに落とし込む
7. 練習後の振り返り結果から計画を更新する

---

## 23. 再設計: AI対話型3か月目標設定

### 23.1 目的
選手が入力した3か月先の抽象的な目標を、AIコーチとの対話によって具体的な目標へ変換し、その達成に必要な1か月目・2か月目・3か月目のマイルストーンを作成する。

### 23.2 基本フロー
1. 選手が3か月先のざっくりした目標を入力する
2. AIコーチが現在地、試合場面、OK基準、練習頻度などを質問する
3. 選手が質問に答える
4. AIコーチが具体目標、OK基準、マイルストーン、日々の練習フォーカスを提示する
5. 選手が内容を確認して保存する

### 23.3 APIキー管理
OpenAI APIキーはコードに直接書かない。

- ローカル開発: .env に OPENAI_API_KEY を保存する
- 本番環境: サーバーの環境変数またはシークレット管理サービスに保存する
- .env は .gitignore の対象とし、Gitへコミットしない

### 23.4 実装方針
- 画面: /goals/roadmap
- 会話履歴: Flask session に一時保存
- 最終目標: 既存 goals テーブルに保存
- skill_type: three_month_ai
- OpenAI未設定時: 仮モードで質問と保存候補を返し、画面が壊れないようにする
