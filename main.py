# -*- coding: utf-8 -*-
"""
PC Parts Finder — приложение для поиска компьютерных комплектующих
на нескольких польских сайтах (Media Expert, Media Markt, Neonet, RTV Euro AGD).

Стек: Python + KivyMD
Парсинг: requests + BeautifulSoup (модуль parsers/)
"""

import threading
from kivy.clock import mainthread
from kivy.metrics import dp
from kivy.lang import Builder
from kivy.core.window import Window
from kivy.properties import StringProperty, ListProperty, BooleanProperty, NumericProperty

from kivymd.app import MDApp
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.card import MDCard
from kivymd.uix.button import MDIconButton
from kivymd.uix.dialog import MDDialog

from parsers.aggregator import search_all_stores, STORES

KV_FILE = "ui.kv"


class ProductCard(MDCard):
    """Карточка товара в списке результатов."""
    title_text = StringProperty("")
    price_text = StringProperty("")
    store_text = StringProperty("")
    desc_text = StringProperty("")
    url = StringProperty("")
    store_color = ListProperty([1, 1, 1, 1])


class PCPartsApp(MDApp):

    is_loading = BooleanProperty(False)
    results_count = NumericProperty(0)

    # Текущее состояние фильтров (значения по умолчанию)
    filters = {
        "stores": {key: True for key in STORES.keys()},
        "price_min": "",
        "price_max": "",
        "condition": "any",        # any | new | used
        "category": "Все категории",
        "in_stock_only": False,
        "sort": "relevance",       # relevance | price_asc | price_desc
    }

    def build(self):
        self.title = "PC Parts Finder"
        self.theme_cls.primary_palette = "Orange"
        self.theme_cls.theme_style = "Light"
        Window.clearcolor = (1, 1, 1, 1)
        return Builder.load_file(KV_FILE)

    # ---------- ПОИСК ----------

    def do_search(self, query):
        query = (query or "").strip()
        if not query:
            return
        self.is_loading = True
        self.root.ids.results_box.clear_widgets()
        self.root.ids.status_label.text = "Ищу..."
        threading.Thread(target=self._search_thread, args=(query,), daemon=True).start()

    def _search_thread(self, query):
        try:
            active_stores = [k for k, v in self.filters["stores"].items() if v]
            results = search_all_stores(query, stores=active_stores)
            results = self._apply_filters(results)
            results = self._apply_sort(results)
        except Exception as e:
            results = []
            print("Ошибка поиска:", e)
        self._render_results(results)

    def _apply_filters(self, items):
        pmin = self.filters["price_min"]
        pmax = self.filters["price_max"]
        cond = self.filters["condition"]
        stock_only = self.filters["in_stock_only"]

        def ok(item):
            if pmin:
                try:
                    if item["price"] < float(pmin):
                        return False
                except (ValueError, TypeError):
                    pass
            if pmax:
                try:
                    if item["price"] > float(pmax):
                        return False
                except (ValueError, TypeError):
                    pass
            if cond != "any" and item.get("condition", "new") != cond:
                return False
            if stock_only and not item.get("in_stock", True):
                return False
            return True

        return [i for i in items if ok(i)]

    def _apply_sort(self, items):
        sort = self.filters["sort"]
        if sort == "price_asc":
            return sorted(items, key=lambda i: i["price"] if i["price"] else 9e18)
        if sort == "price_desc":
            return sorted(items, key=lambda i: i["price"] if i["price"] else -1, reverse=True)
        return items

    @mainthread
    def _render_results(self, results):
        self.is_loading = False
        box = self.root.ids.results_box
        box.clear_widgets()
        self.results_count = len(results)
        self.root.ids.status_label.text = f"Найдено: {len(results)} товаров"

        if not results:
            self.root.ids.status_label.text = "Ничего не найдено. Попробуйте изменить запрос или фильтры."
            return

        for item in results:
            card = ProductCard(
                title_text=item.get("title", "Без названия"),
                price_text=f'{item["price"]:.2f} zł' if item.get("price") else "Цена не указана",
                store_text=item.get("store_name", ""),
                desc_text=item.get("desc", ""),
                url=item.get("url", ""),
                store_color=STORES.get(item.get("store_key"), {}).get("color", [0.9, 0.9, 0.9, 1]),
            )
            box.add_widget(card)

    def open_url(self, url):
        if not url:
            return
        import webbrowser
        webbrowser.open(url)

    # ---------- ФИЛЬТРЫ ----------

    def open_filters(self):
        self.root.ids.filter_panel.height = dp(560)
        self.root.ids.filter_panel.opacity = 1

    def close_filters(self):
        self.root.ids.filter_panel.height = 0
        self.root.ids.filter_panel.opacity = 0

    def toggle_store(self, store_key, active):
        self.filters["stores"][store_key] = active

    def set_condition(self, condition):
        self.filters["condition"] = condition

    def set_sort(self, sort_key):
        self.filters["sort"] = sort_key

    def set_stock_only(self, value):
        self.filters["in_stock_only"] = value

    def set_price_min(self, value):
        self.filters["price_min"] = value

    def set_price_max(self, value):
        self.filters["price_max"] = value

    def reset_filters(self):
        for k in self.filters["stores"]:
            self.filters["stores"][k] = True
        self.filters["price_min"] = ""
        self.filters["price_max"] = ""
        self.filters["condition"] = "any"
        self.filters["in_stock_only"] = False
        self.filters["sort"] = "relevance"
        self.root.ids.price_min_field.text = ""
        self.root.ids.price_max_field.text = ""


if __name__ == "__main__":
    PCPartsApp().run()
