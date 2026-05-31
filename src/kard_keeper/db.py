from __future__ import annotations
from tinydb import TinyDB, Query
from tinydb.table import Document
from typing import List, Optional, Dict, Any
from pathlib import Path

from .models import GiftCard

DB_PATH = Path("cards.json")
db = TinyDB(DB_PATH)
Card = Query()


def _normalize(doc: Document | List[Document] | None) -> Optional[Dict[str, Any]]:
    if doc is None:
        return None
    if isinstance(doc, Document):
        return dict(doc)
    if isinstance(doc, dict):
        return doc


def add_card(card: GiftCard) -> int:
    """Insert a validated GiftCard into the DB."""
    return db.insert(card.model_dump())


def get_cards() -> List[GiftCard]:
    """Return all cards as typed GiftCard objects."""
    raw_cards: List[Document] = db.all()
    normalized: List[Dict[str, Any]] = [dict(doc) for doc in raw_cards]
    return [GiftCard(**raw) for raw in normalized]


def get_card_by_name(name: str) -> Optional[GiftCard]:
    """Return a single card or None."""
    raw: Document | None | List[Document] = db.get(Card.name == name)
    normalized = _normalize(raw)

    if normalized is None:
        return None

    # Pyright-safe: raw is now guaranteed to be a dict[str, Any]
    return GiftCard(**normalized)


def update_balance(name: str, new_balance: float) -> bool:
    """Update balance with type and value guards."""
    if new_balance < 0:
        raise ValueError("Balance cannot be negative")

    updated = db.update({"balance": new_balance}, Card.name == name)
    return bool(updated)


def make_purchase(name: str, amount: float) -> bool:
    """Update the balance by making a purchase and subtracting the price from the balance."""
    raw = db.get(Card.name == name)
    normalized = _normalize(raw)
    if normalized is None:
        return False
    card = GiftCard(**normalized)
    card.balance -= amount
    updated = db.update({"balance": card.balance}, Card.name == name)
    return bool(updated)


def delete_card(name: str) -> bool:
    """Delete a card by name."""
    removed = db.remove(Card.name == name)
    return bool(removed)
