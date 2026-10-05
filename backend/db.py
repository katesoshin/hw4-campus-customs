"""SQLite access for the Campus Customs catalogue, inventory, and users."""
from __future__ import annotations

import json
import sqlite3
from contextlib import contextmanager
from typing import Iterator

from config import DB_PATH
from models import Product, SizeStock

SIZE_ORDER = {s: i for i, s in enumerate(["XS", "S", "M", "L", "XL", "XXL", "XXXL"])}


@contextmanager
def connect() -> Iterator[sqlite3.Connection]:
    if not DB_PATH.exists():
        raise FileNotFoundError(f"Database not found at {DB_PATH}. Unzip data.zip into hw4/data/.")
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()


def _row_to_product(conn: sqlite3.Connection, row: sqlite3.Row) -> Product:
    sizes = [
        SizeStock(size=r["size"], quantity=r["quantity"])
        for r in conn.execute(
            "SELECT size, quantity FROM inventory WHERE product_id = ?", (row["product_id"],)
        )
    ]
    sizes.sort(key=lambda s: SIZE_ORDER.get(s.size, 99))
    return Product(
        product_id=row["product_id"],
        name=row["name"],
        garment_type=row["garment_type"],
        description=row["description"],
        colors=json.loads(row["colors"]),
        search_tags=json.loads(row["search_tags"]),
        image_url=f"/images/{row['product_id']}",
        price=row["price"],
        sizes=sizes,
    )


def list_products() -> list[Product]:
    with connect() as conn:
        rows = conn.execute("SELECT * FROM catalogue ORDER BY name").fetchall()
        return [_row_to_product(conn, r) for r in rows]


def get_product(product_id: str) -> Product | None:
    with connect() as conn:
        row = conn.execute("SELECT * FROM catalogue WHERE product_id = ?", (product_id,)).fetchone()
        return _row_to_product(conn, row) if row else None


def get_products(product_ids: list[str]) -> list[Product]:
    """Return products for the given ids, preserving the given order."""
    found = {p.product_id: p for p in (get_product(pid) for pid in product_ids) if p}
    return [found[pid] for pid in product_ids if pid in found]


def image_path(product_id: str) -> str | None:
    """Return the on-disk image_file_path for a product id, or None."""
    with connect() as conn:
        row = conn.execute(
            "SELECT image_file_path FROM catalogue WHERE product_id = ?", (product_id,)
        ).fetchone()
        return row["image_file_path"] if row else None


def search_catalogue(query: str, limit: int = 8) -> list[Product]:
    """Keyword search over name, description, type, colors, and search tags."""
    terms = [t for t in query.lower().split() if t]
    with connect() as conn:
        rows = conn.execute("SELECT * FROM catalogue").fetchall()
        scored: list[tuple[int, sqlite3.Row]] = []
        for row in rows:
            haystack = " ".join(
                [row["name"], row["description"], row["garment_type"], row["colors"], row["search_tags"]]
            ).lower()
            score = sum(haystack.count(term) for term in terms)
            if score:
                scored.append((score, row))
        scored.sort(key=lambda x: x[0], reverse=True)
        return [_row_to_product(conn, r) for _, r in scored[:limit]]


# ---- Users ----
def get_user_by_email(email: str) -> sqlite3.Row | None:
    with connect() as conn:
        return conn.execute(
            "SELECT * FROM users WHERE email = ? COLLATE NOCASE", (email,)
        ).fetchone()


def get_user_by_id(user_id: int) -> sqlite3.Row | None:
    with connect() as conn:
        return conn.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()


def create_user(name: str, email: str, password_hash: str, first_name: str, last_name: str) -> int:
    with connect() as conn:
        cur = conn.execute(
            "INSERT INTO users (name, email, password_hash, first_name, last_name) VALUES (?, ?, ?, ?, ?)",
            (name, email, password_hash, first_name, last_name),
        )
        return int(cur.lastrowid)


# ---- Chat history ----
def save_message(user_id: int, role: str, content: str, products_json: str | None = None) -> None:
    with connect() as conn:
        conn.execute(
            "INSERT INTO chat_messages (user_id, role, content, products_json) VALUES (?, ?, ?, ?)",
            (user_id, role, content, products_json),
        )


def recent_messages(user_id: int, limit: int = 12) -> list[sqlite3.Row]:
    """Most recent messages (oldest-first) for feeding the agent and re-rendering history."""
    with connect() as conn:
        rows = conn.execute(
            "SELECT role, content, products_json FROM chat_messages WHERE user_id = ? ORDER BY id DESC LIMIT ?",
            (user_id, limit),
        ).fetchall()
        return list(reversed(rows))
