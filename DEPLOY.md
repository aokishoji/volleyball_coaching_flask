# 本番サーバー デプロイ手順

## サーバー情報
- プロジェクトルート: `/apl_coach/app/`
- 仮想環境: `/apl_coach/app/venv/`
- DB: `/apl_coach/app/instance/app.db`
- サービス名: `coach`

---

## 通常デプロイ（コードのみ変更の場合）

```bash
# 1. プロジェクトディレクトリへ移動
su aoki
cd /apl_coach/app

# 2. 最新コードを取得
git pull

# 3. サービス再起動
sudo systemctl restart coach

# 4. 起動確認
sudo systemctl status coach
```

---

## DBスキーマ変更を含むデプロイ

コードの変更に加えて、モデルにカラムが追加された場合は以下の手順を実施する。

```bash
# 1. プロジェクトディレクトリへ移動
cd /apl_coach/app

# 2. 最新コードを取得
git pull

# 3. 仮想環境を有効化
source venv/bin/activate

# 4. 依存パッケージを更新（requirements.txt が変わった場合）
pip install -r requirements.txt

# 5. DBにカラムを追加（変更内容に応じて実行）
sqlite3 instance/app.db

# --- sqlite3 の中で実行 ---
# ※ 追加済みのカラムに再度 ALTER TABLE すると「duplicate column」エラーになるので注意
# ※ 下記は今回の変更分（profiles に3カラム追加、physical_records テーブル新規）

ALTER TABLE profiles ADD COLUMN birth_date DATE;
ALTER TABLE profiles ADD COLUMN volleyball_start_date DATE;
ALTER TABLE profiles ADD COLUMN gender VARCHAR(20);
.quit
# --- ここまで ---

# 6. 新規テーブルを作成（init-db で physical_records テーブルを追加）
python -m flask --app run init-db

# 7. サービス再起動
sudo systemctl restart coach

# 8. 起動確認
sudo systemctl status coach
```

---

## パッケージ追加を含むデプロイ

```bash
cd /apl_coach/app
git pull
source venv/bin/activate
pip install -r requirements.txt
sudo systemctl restart coach
sudo systemctl status coach
```

---

## ログ確認（エラー調査）

```bash
# サービスのログをリアルタイム表示
sudo journalctl -u coach -f

# 直近50行を表示
sudo journalctl -u coach -n 50
```

---

## データ操作

### 目標関連データのみ削除（ユーザーアカウントは保持）
```bash
sqlite3 /apl_coach/app/instance/app.db
```
```sql
PRAGMA foreign_keys = OFF;
DELETE FROM reflections;
DELETE FROM daily_practice_themes;
DELETE FROM practice_themes;
DELETE FROM deep_dive_answers;
DELETE FROM assessments;
DELETE FROM goal_milestones;
DELETE FROM goals;
DELETE FROM goal_coach_sessions;
PRAGMA foreign_keys = ON;
.quit
```

### 全データ削除（テーブル構造は保持）
```bash
cd /apl_coach/app
source venv/bin/activate
python -m flask --app run clear-db
```

---

## 注意事項

- `.env` ファイルはgit管理外のため、サーバー上の `/apl_coach/app/.env` を直接編集する
- `ALTER TABLE` は同じカラムを2回追加するとエラーになる（既に追加済みかどうか確認してから実行）
- `init-db` は既存テーブルを変更しない（新規テーブルの追加のみ）
