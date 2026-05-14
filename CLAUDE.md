# CLAUDE.md

## Project overview
This is a Flask-based mobile-first coaching web app for volleyball players.
The MVP focuses on spike improvement.

## Stack
- Python
- Flask
- Flask-SQLAlchemy
- Flask-WTF
- Jinja2
- SQLite for local/dev

## Architecture rules
- Keep routes thin
- Put business logic in app/services
- Keep templates grouped by feature
- Prefer minimal changes over large rewrites
- Preserve Japanese UI labels

## Current priorities
1. Improve deep-dive logic beyond timing only
2. Improve mobile UI
3. Stabilize DB init and deployment flow
4. Add tests

## Run commands
- pip install -r requirements.txt
- python -m flask --app run init-db
- python run.py