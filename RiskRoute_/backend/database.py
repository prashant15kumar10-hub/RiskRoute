from __future__ import annotations

import hashlib
import hmac
import json
import secrets
import sqlite3
from contextlib import contextmanager
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DB_PATH = ROOT / "artifacts" / "counterfact_x.db"


@contextmanager
def connection():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    db = sqlite3.connect(DB_PATH)
    db.row_factory = sqlite3.Row
    try:
        yield db
        db.commit()
    finally:
        db.close()


def initialize() -> None:
    with connection() as db:
        db.executescript(
            """
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT NOT NULL UNIQUE,
                password_hash TEXT NOT NULL,
                salt TEXT NOT NULL,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            );
            CREATE TABLE IF NOT EXISTS sessions (
                token TEXT PRIMARY KEY,
                user_id INTEGER NOT NULL,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(user_id) REFERENCES users(id)
            );
            CREATE TABLE IF NOT EXISTS predictions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                input_json TEXT NOT NULL,
                probability REAL NOT NULL,
                scenarios_json TEXT NOT NULL,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(user_id) REFERENCES users(id)
            );
            """
        )


def _password_hash(password: str, salt: str) -> str:
    value = hashlib.pbkdf2_hmac(
        "sha256", password.encode(), bytes.fromhex(salt), 180_000
    )
    return value.hex()


def create_user(name: str, email: str, password: str) -> dict:
    salt = secrets.token_hex(16)
    password_hash = _password_hash(password, salt)
    try:
        with connection() as db:
            cursor = db.execute(
                "INSERT INTO users(name, email, password_hash, salt) VALUES (?, ?, ?, ?)",
                (name.strip(), email.strip().lower(), password_hash, salt),
            )
            user_id = int(cursor.lastrowid)
    except sqlite3.IntegrityError as exc:
        raise ValueError("An account with this email already exists.") from exc
    return create_session(user_id)


def authenticate(email: str, password: str) -> dict:
    with connection() as db:
        row = db.execute(
            "SELECT * FROM users WHERE email = ?", (email.strip().lower(),)
        ).fetchone()
    if not row or not hmac.compare_digest(
        row["password_hash"], _password_hash(password, row["salt"])
    ):
        raise ValueError("Incorrect email or password.")
    return create_session(int(row["id"]))


def create_session(user_id: int) -> dict:
    token = secrets.token_urlsafe(32)
    with connection() as db:
        db.execute("INSERT INTO sessions(token, user_id) VALUES (?, ?)", (token, user_id))
        user = db.execute(
            "SELECT id, name, email FROM users WHERE id = ?", (user_id,)
        ).fetchone()
    return {"token": token, "user": dict(user)}


def user_for_token(token: str) -> dict | None:
    with connection() as db:
        row = db.execute(
            """
            SELECT users.id, users.name, users.email
            FROM sessions JOIN users ON users.id = sessions.user_id
            WHERE sessions.token = ?
            """,
            (token,),
        ).fetchone()
    return dict(row) if row else None


def save_prediction(user_id: int, record: dict, probability: float, scenarios: list) -> int:
    with connection() as db:
        cursor = db.execute(
            """
            INSERT INTO predictions(user_id, input_json, probability, scenarios_json)
            VALUES (?, ?, ?, ?)
            """,
            (user_id, json.dumps(record), probability, json.dumps(scenarios)),
        )
        return int(cursor.lastrowid)


def prediction_history(user_id: int, limit: int = 50) -> list[dict]:
    with connection() as db:
        rows = db.execute(
            """
            SELECT id, input_json, probability, scenarios_json, created_at
            FROM predictions WHERE user_id = ?
            ORDER BY id DESC LIMIT ?
            """,
            (user_id, limit),
        ).fetchall()
    return [
        {
            "id": row["id"],
            "input": json.loads(row["input_json"]),
            "probability": row["probability"],
            "scenarios": json.loads(row["scenarios_json"]),
            "created_at": row["created_at"],
        }
        for row in rows
    ]
