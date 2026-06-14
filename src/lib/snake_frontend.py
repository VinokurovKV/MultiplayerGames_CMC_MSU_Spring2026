"""Frontend screen for the Snake visual prototype."""

from __future__ import annotations

from typing import Callable

import arcade
import arcade.gui

try:
    from .frontend import Manager
    from .localization import tr
    from .menu import (
        CYAN,
        PURPLE,
        NeonBaseView,
        build_menu_button_style,
        build_primary_button_style,
    )
except ImportError:
    from frontend import Manager
    from localization import tr
    from menu import (
        CYAN,
        PURPLE,
        NeonBaseView,
        build_menu_button_style,
        build_primary_button_style,
    )


GRID_COLS = 16
GRID_ROWS = 14


class SnakeView(NeonBaseView):
    """Экран визуального прототипа Snake."""

    def __init__(self, player_name: str, on_back: Callable[[], None]):
        super().__init__()
        self.player_name = player_name
        self.on_back = on_back
        self.manager = Manager()

        self.nicks: list[str] = []
        self.lobby_id: int | None = None
        self.status = "waiting"
        self.left_score = 0
        self.right_score = 0

        self.title_label = arcade.Text(
            "SNAKE",
            x=0,
            y=0,
            color=(228, 243, 255),
            font_size=56,
            font_name=("Bahnschrift", "Calibri", "Arial"),
            anchor_x="center",
            anchor_y="center",
            bold=True,
        )
        self.status_label = arcade.Text(
            "",
            x=0,
            y=0,
            color=(154, 220, 255),
            font_size=20,
            font_name=("Bahnschrift", "Calibri", "Arial"),
            anchor_x="center",
            anchor_y="center",
            bold=True,
        )
        self.score_label = arcade.Text(
            "0 : 0",
            x=0,
            y=0,
            color=(236, 247, 255),
            font_size=40,
            font_name=("Bahnschrift", "Calibri", "Arial"),
            anchor_x="center",
            anchor_y="center",
            bold=True,
        )
        self.meta_label = arcade.Text(
            "",
            x=0,
            y=0,
            color=(196, 219, 240),
            font_size=18,
            font_name=("Calibri", "Arial"),
            anchor_x="center",
            anchor_y="center",
        )

        self._build_ui()

    def _build_ui(self) -> None:
        controls = arcade.gui.UIBoxLayout(vertical=False, space_between=14)

        self.start_button = arcade.gui.UIFlatButton(
            text=tr("snake.start"),
            width=190,
            height=64,
            style=build_primary_button_style(),
        )

        @self.start_button.event("on_click")
        def on_start(_event):
            self.manager.push_message("start")
            self.status = "prototype"

        self.back_button = arcade.gui.UIFlatButton(
            text=tr("snake.back"),
            width=220,
            height=64,
            style=build_menu_button_style(exit_button=True),
        )

        @self.back_button.event("on_click")
        def on_back(_event):
            self.manager.push_message({"action": "leave_game"})
            self.on_back()

        controls.add(self.start_button)
        controls.add(self.back_button)
        self._add_centered_widget(controls, align_y=-300)
        self._add_locale_toggle()

    def on_update(self, _delta_time: float) -> None:
        """Считывает статусы Snake от backend."""

        while True:
            status, error = self.manager.pop_status()

            if status is None and error is None:
                return

            if isinstance(status, dict) and status.get("game") == "SNAKE":
                self.nicks = status.get("nicks", self.nicks)
                self.lobby_id = status.get("lobby_id", self.lobby_id)
                self.status = status.get("status", self.status)

    def on_draw(self) -> None:
        """Отрисовывает визуальный прототип Snake."""

        self.clear()
        self._draw_neon_background()
        self._draw_shell()
        self._draw_boards()
        self._draw_text_layer()
        self.ui.draw()

    def _draw_shell(self) -> None:
        width = self.window.width
        height = self.window.height

        self._draw_filled_rect(
            width * 0.08,
            width * 0.92,
            height * 0.12,
            height * 0.80,
            (5, 12, 30, 112),
        )
        self._draw_outlined_rect(
            width * 0.08,
            width * 0.92,
            height * 0.12,
            height * 0.80,
            (66, 188, 255, 90),
            border_width=2,
        )

    def _draw_boards(self) -> None:
        left_board, right_board = self._board_bounds()

        self._draw_board(left_board, CYAN, self._left_snake(), (11, 8))
        self._draw_board(right_board, PURPLE, self._right_snake(), (4, 4))
        self._draw_separator()

    def _draw_board(self, bounds, accent, snake, food) -> None:
        left, right, bottom, top = bounds
        self._draw_filled_rect(left, right, bottom, top, (2, 10, 25, 225))
        self._draw_outlined_rect(left, right, bottom, top, accent + (170,), 3)
        self._draw_grid(bounds)
        self._draw_food(bounds, food)
        self._draw_snake(bounds, snake, accent)

    def _draw_grid(self, bounds) -> None:
        left, right, bottom, top = bounds
        cell_w = (right - left) / GRID_COLS
        cell_h = (top - bottom) / GRID_ROWS

        for col in range(1, GRID_COLS):
            x = left + col * cell_w
            arcade.draw_line(x, bottom, x, top, (82, 120, 150, 55), 1)

        for row in range(1, GRID_ROWS):
            y = bottom + row * cell_h
            arcade.draw_line(left, y, right, y, (82, 120, 150, 55), 1)

    def _draw_food(self, bounds, food) -> None:
        center_x, center_y, cell_size = self._cell_center(bounds, food)
        arcade.draw_circle_filled(
            center_x,
            center_y,
            cell_size * 0.32,
            (255, 94, 146, 245),
        )
        arcade.draw_circle_outline(
            center_x,
            center_y,
            cell_size * 0.46,
            (255, 176, 208, 150),
            2,
        )

    def _draw_snake(self, bounds, snake, accent) -> None:
        for index, cell in enumerate(snake):
            center_x, center_y, cell_size = self._cell_center(bounds, cell)
            radius = cell_size * (0.42 if index == 0 else 0.36)
            color = (230, 252, 255, 255) if index == 0 else accent + (230,)
            arcade.draw_circle_filled(center_x, center_y, radius, color)
            arcade.draw_circle_outline(
                center_x,
                center_y,
                radius + 2,
                accent + (120,),
                2,
            )

    def _draw_separator(self) -> None:
        center_x = self.window.width / 2
        bottom = self.window.height * 0.24
        top = self.window.height * 0.64
        dash_count = 11
        dash_h = (top - bottom) / (dash_count * 1.7)

        for index in range(dash_count):
            y_top = top - index * dash_h * 1.7
            self._draw_filled_rect(
                center_x - 2,
                center_x + 2,
                y_top - dash_h,
                y_top,
                (140, 230, 255, 135),
            )

    def _draw_text_layer(self) -> None:
        self._refresh_texts()

        self.title_label.x = self.window.width / 2
        self.title_label.y = self.window.height * 0.88
        self.title_label.draw()

        self.status_label.text = self._status_text()
        self.status_label.x = self.window.width / 2
        self.status_label.y = self.window.height * 0.765
        self.status_label.draw()

        self.score_label.text = f"{self.left_score} : {self.right_score}"
        self.score_label.x = self.window.width / 2
        self.score_label.y = self.window.height * 0.69
        self.score_label.draw()

        self.meta_label.text = self._meta_text()
        self.meta_label.x = self.window.width / 2
        self.meta_label.y = self.window.height * 0.18
        self.meta_label.draw()

    def _board_bounds(self):
        width = self.window.width
        height = self.window.height
        return (
            (width * 0.12, width * 0.46, height * 0.25, height * 0.64),
            (width * 0.54, width * 0.88, height * 0.25, height * 0.64),
        )

    def _cell_center(self, bounds, cell):
        left, right, bottom, top = bounds
        col, row = cell
        cell_w = (right - left) / GRID_COLS
        cell_h = (top - bottom) / GRID_ROWS
        cell_size = min(cell_w, cell_h)
        return (
            left + (col + 0.5) * cell_w,
            bottom + (row + 0.5) * cell_h,
            cell_size,
        )

    def _status_text(self) -> str:
        if self.status == "leave":
            return tr("snake.leave")

        if self.status == "joined" or len(self.nicks) >= 2:
            return tr("snake.prototype")

        return tr("snake.waiting")

    def _meta_text(self) -> str:
        if not self.nicks:
            return tr("x_o.empty_lobby")

        text = tr("x_o.lobby", players="  /  ".join(self.nicks))
        if self.lobby_id is not None:
            text = f"{text}  |  ID: {self.lobby_id}"
        return text

    def _refresh_texts(self) -> None:
        super()._refresh_texts()
        self.start_button.text = tr("snake.start")
        self.back_button.text = tr("snake.back")

    @staticmethod
    def _left_snake():
        return [(7, 7), (6, 7), (5, 7), (4, 7), (4, 6)]

    @staticmethod
    def _right_snake():
        return [(8, 6), (9, 6), (10, 6), (11, 6), (11, 7)]
