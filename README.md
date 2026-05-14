# バレーボール選手向けコーチングアプリ Flask初期ひな形

## 概要
スマホ画面を意識した Flask 製Webアプリの初期ひな形です。  
以下の導線をひとまず動かせる構成にしています。

- ユーザー登録 / ログイン
- ホーム
- 目標設定
- 課題分析
- 深掘り
- 今日の練習テーマ表示
- 振り返り
- 成長ログ
- プロフィール

## OpenAI APIキーの設定

AI目標設定機能を使うには OpenAI API キーが必要です。

`.env.example` をコピーして `.env` を作成し、キーを設定してください。

```bash
cp .env.example .env
```

```
OPENAI_API_KEY=sk-...       # OpenAI のAPIキー
OPENAI_MODEL=gpt-4o-mini    # 使用モデル（省略可、デフォルト: gpt-4o-mini）
```

キーを設定しない場合は仮モードで動作し、固定応答が返ります。

## セットアップ

```bash
python -m venv .venv
# Windows
.venv\Scripts\activate
# macOS / Linux
source .venv/bin/activate

pip install -r requirements.txt
```

`.env.example` を参考に `.env` を作成してもよいです。

## 起動方法

```bash
python run.py
```

## 初回DB作成 / テーブル追加後の再作成

```bash
python -m flask --app run init-db
```

> AI目標設定の会話をDBに保存する `goal_coach_sessions` テーブルが追加されています。  
> 既存のDBがある場合は `init-db` を再実行するか、SQLite ブラウザ等でテーブルを追加してください。

## ディレクトリ構成

```text
project/
├─ run.py
├─ config.py
├─ requirements.txt
├─ app/
│  ├─ __init__.py
│  ├─ extensions.py
│  ├─ models.py
│  ├─ forms.py
│  ├─ routes/
│  ├─ services/
│  ├─ templates/
│  └─ static/
└─ instance/
```

## 補足
- 課題分析 / 深掘り / 練習テーマ生成は、まずルールベースのたたき台です
- ここから DB の見直し、UI 改善、質問テンプレート追加が可能です
