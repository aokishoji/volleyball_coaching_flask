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

## 初回DB作成
現状は簡易初期化スクリプトとして Flask shell で作成できます。

```bash
python
>>> from app import create_app
>>> from app.extensions import db
>>> app = create_app()
>>> app.app_context().push()
>>> db.create_all()
>>> exit()
```

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
