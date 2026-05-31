from __future__ import annotations

from typing import List, Optional
from pathlib import Path

from kivy.app import App
from kivy.lang import Builder
from kivy.properties import ObjectProperty, StringProperty
from kivy.uix.screenmanager import Screen, ScreenManager

from .db import get_cards, get_card_by_name, add_card, update_balance, delete_card
from .models import GiftCard

KV_PATH = Path(__file__).parent / "main.kv"


class HomeScreen(Screen):
    pass


class AddCardScreen(Screen):
    name_input = ObjectProperty(None)
    balance_input = ObjectProperty(None)
    expires_input = ObjectProperty(None)
    notes_input = ObjectProperty(None)


class CardDetailScreen(Screen):
    card_name = StringProperty("")
    card: Optional[GiftCard] = None  # stored on load


class EditCardScreen(Screen):
    name_input = ObjectProperty(None)
    balance_input = ObjectProperty(None)
    expires_input = ObjectProperty(None)
    notes_input = ObjectProperty(None)
    original_name = StringProperty("")


class RootManager(ScreenManager):
    pass


class KardKeeperApp(App):
    root: RootManager
    cards_data: List[GiftCard] = []

    def build(self) -> RootManager:
        return Builder.load_file(str(KV_PATH))

    # ---------- Data helpers ----------

    def refresh_cards(self) -> None:
        self.cards_data = get_cards()
        home = self.root.get_screen("home")
        rv = home.ids.card_list
        rv.data = [
            {
                "text": f"{card.name} - ${card.balance:.2f}",
                "card_name": card.name,
            }
            for card in self.cards_data
        ]

    # ---------- Navigation ----------

    def on_start(self) -> None:
        self.refresh_cards()

    def go_home(self) -> None:
        self.root.current = "home"
        self.refresh_cards()

    def go_add_card(self) -> None:
        self.root.current = "add_card"

    def go_card_detail(self, card_name: str) -> None:
        screen: CardDetailScreen = self.root.get_screen("card_detail")
        card = get_card_by_name(card_name)
        if card is None:
            return
        screen.card = card
        screen.card_name = card.name
        self.root.current = "card_detail"

    def go_edit_card(self, card_name: str) -> None:
        card = get_card_by_name(card_name)
        if card is None:
            return
        screen: EditCardScreen = self.root.get_screen("edit_card")
        screen.original_name = card.name
        screen.name_input.text = card.name
        screen.balance_input.text = f"{card.balance:.2f}"
        screen.expires_input.text = card.expires.isoformat() if card.expires else ""
        screen.notes_input.text = card.notes or ""
        self.root.current = "edit_card"

    # ---------- Actions ----------

    def add_card_from_inputs(
        self,
        name: str,
        balance_str: str,
        expires_str: str,
        notes: str,
    ) -> None:
        name = name.strip()
        if not name:
            return

        try:
            balance = float(balance_str)
        except ValueError:
            return

        expires = None
        if expires_str.strip():
            from datetime import date

            try:
                year, month, day = map(int, expires_str.split("-"))
                expires = date(year, month, day)
            except ValueError:
                expires = None

        card = GiftCard(
            name=name, balance=balance, expires=expires, notes=notes or None
        )
        add_card(card)
        self.go_home()

    def update_card_from_inputs(
        self,
        original_name: str,
        name: str,
        balance_str: str,
        expires_str: str,
        notes: str,
    ) -> None:
        try:
            balance = float(balance_str)
        except ValueError:
            return

        update_balance(original_name, balance)
        # if you later add update_card(), you’d call it here for name/notes/expires
        self.go_home()

    def delete_card_and_back(self, card_name: str) -> None:
        delete_card(card_name)
        self.go_home()


def main() -> None:
    KardKeeperApp().run()


if __name__ == "__main__":
    main()
