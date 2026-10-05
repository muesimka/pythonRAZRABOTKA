#!/usr/bin/env python3
"""8 звёздочек — компактная версия"""

import tkinter as tk
from tkinter import messagebox, ttk
from typing import List, Set, Tuple, Optional

N, CELL = 8, 70

FORBIDDEN: Set[Tuple[int, int]] = {(i, i) for i in range(1, N+1)} | {(i, N+1-i) for i in range(1, N+1)}

COLORS = {
    "bg": "#ffffff", "panel": "#f0f0f0", "light": "#ffffff", "dark": "#e0e0e0",
    "forbidden": "#000000", "forbidden_fg": "#ffffff",
    "star_fixed": "#000000", "star_fixed_bg": "#9e9e9e",
    "star_sol": "#000000", "star_sol_bg": "#bdbdbd",
    "hover": "#cccccc", "text": "#222222", "accent": "#000000", "border": "#333333",
}


class StarsApp:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("8 звёздочек")
        self.root.resizable(False, False)
        self.root.configure(bg=COLORS["bg"])

        self.fixed: Optional[Tuple[int, int]] = None
        self.solutions: List[List[int]] = []
        self.current_sol_idx = 0
        self._last_hover = None

        style = ttk.Style()
        style.theme_use("clam")
        style.configure("TFrame", background=COLORS["bg"])
        style.configure("TLabel", background=COLORS["bg"], foreground=COLORS["text"], font=("Segoe UI", 10))
        style.configure("TButton", background="#e0e0e0", foreground=COLORS["text"], font=("Segoe UI", 9))
        style.map("TButton", background=[("active", COLORS["hover"]), ("disabled", "#f5f5f5")])

        # Условие
        info = tk.Frame(root, bg=COLORS["panel"], padx=14, pady=10)
        info.pack(fill="x", padx=12, pady=(12, 6))
        tk.Label(info, text="УСЛОВИЕ ЗАДАЧИ", font=("Segoe UI", 12, "bold"),
                 bg=COLORS["panel"], fg=COLORS["accent"]).pack(anchor="w")
        tk.Label(info, text="• Разместить 8 звёзд так, чтобы они не били друг друга (как ферзи).\n"
                            "• Обе главные диагонали запрещены (☒).\n"
                            "• Кликни по клетке — программа найдёт все возможные расстановки.",
                 font=("Segoe UI", 9), bg=COLORS["panel"], fg=COLORS["text"],
                 justify="left", anchor="w").pack(anchor="w", pady=(4, 0))

        # Статус + кнопки
        top = ttk.Frame(root, padding=(12, 8))
        top.pack(fill="x")
        self.status = ttk.Label(top, text="Кликните по свободной клетке, чтобы поставить ★", font=("Segoe UI", 11))
        self.status.pack(side="left")
        self.btn_reset = ttk.Button(top, text="  Сбросить  ", command=self.reset)
        self.btn_reset.pack(side="right", padx=(6, 0))
        self.btn_show = ttk.Button(top, text="  Показать решение  ", command=self.show_solution, state="disabled")
        self.btn_show.pack(side="right", padx=4)

        # Доска
        board_outer = tk.Frame(root, bg=COLORS["border"], padx=3, pady=3)
        board_outer.pack(padx=16, pady=(4, 8))
        self.canvas = tk.Canvas(board_outer, width=N*CELL, height=N*CELL,
                                bg=COLORS["border"], highlightthickness=0, cursor="hand2")
        self.canvas.pack()

        self.rect_ids = [[None]*N for _ in range(N)]
        self.text_ids = [[None]*N for _ in range(N)]
        for r in range(N):
            for c in range(N):
                col, row = c+1, N-r
                x1, y1 = c*CELL, r*CELL
                is_light = (r+c) % 2 == 0
                if (col, row) in FORBIDDEN:
                    fill, text, tc = COLORS["forbidden"], "☒", COLORS["forbidden_fg"]
                else:
                    fill = COLORS["light"] if is_light else COLORS["dark"]
                    text, tc = "", "#000000"
                self.rect_ids[r][c] = self.canvas.create_rectangle(x1, y1, x1+CELL, y1+CELL,
                                                                   fill=fill, outline=COLORS["border"], width=1)
                self.text_ids[r][c] = self.canvas.create_text(x1+CELL//2, y1+CELL//2, text=text,
                                                              font=("Segoe UI Symbol", 22, "bold"), fill=tc)

        self.canvas.bind("<Button-1>", self.on_canvas_click)
        self.canvas.bind("<Motion>", self.on_motion)

        # Низ
        bottom = ttk.Frame(root, padding=(12, 6, 12, 12))
        bottom.pack(fill="x")
        self.result_label = ttk.Label(bottom, text="", font=("Segoe UI", 10))
        self.result_label.pack(side="left")
        nav = ttk.Frame(bottom)
        nav.pack(side="right")
        self.btn_prev = ttk.Button(nav, text=" ◀ ", command=self.prev_sol, state="disabled", width=3)
        self.btn_prev.pack(side="left", padx=2)
        self.sol_counter = ttk.Label(nav, text="", font=("Segoe UI", 10, "bold"))
        self.sol_counter.pack(side="left", padx=6)
        self.btn_next = ttk.Button(nav, text=" ▶ ", command=self.next_sol, state="disabled", width=3)
        self.btn_next.pack(side="left", padx=2)

    def _pos(self, event) -> Optional[Tuple[int, int]]:
        c, r = event.x // CELL, event.y // CELL
        return (c+1, N-r) if 0 <= c < N and 0 <= r < N else None

    def on_motion(self, event):
        if self.fixed:
            return
        pos = self._pos(event)
        if pos == self._last_hover:
            return
        if self._last_hover and self._last_hover not in FORBIDDEN:
            col, row = self._last_hover
            r, c = N-row, col-1
            fill = COLORS["light"] if (r+c) % 2 == 0 else COLORS["dark"]
            self.canvas.itemconfig(self.rect_ids[r][c], fill=fill)
        self._last_hover = pos
        if pos and pos not in FORBIDDEN:
            col, row = pos
            self.canvas.itemconfig(self.rect_ids[N-row][col-1], fill=COLORS["hover"])

    def on_canvas_click(self, event):
        pos = self._pos(event)
        if pos:
            self.on_click(*pos)

    def on_click(self, col: int, row: int):
        if self.fixed or (col, row) in FORBIDDEN:
            return
        self.fixed = (col, row)
        r, c = N-row, col-1
        self.canvas.itemconfig(self.rect_ids[r][c], fill=COLORS["star_fixed_bg"])
        self.canvas.itemconfig(self.text_ids[r][c], text="★", fill=COLORS["star_fixed"])
        self.status.config(text=f"Фиксированная звезда: ({col}, {row}). Идёт поиск…")
        self.root.update()

        self.solutions = self.solve(self.fixed)
        count = len(self.solutions)
        if count == 0:
            self.result_label.config(text=f"Решений нет при звезде в ({col}, {row})")
            self.status.config(text="Решений не найдено")
            messagebox.showinfo("Результат", "При такой позиции решений нет.")
        else:
            self.result_label.config(text=f"Найдено решений: {count}")
            self.status.config(text=f"Готово · {count} решений")
            self.btn_show.config(state="normal")
            st = "normal" if count > 1 else "disabled"
            self.btn_prev.config(state=st)
            self.btn_next.config(state=st)
            self.current_sol_idx = 0
            self.sol_counter.config(text=f"1 / {count}")
            self.show_solution()

    def reset(self):
        self.fixed = None
        self.solutions = []
        self.current_sol_idx = 0
        self._last_hover = None
        for r in range(N):
            for c in range(N):
                col, row = c+1, N-r
                is_light = (r+c) % 2 == 0
                if (col, row) in FORBIDDEN:
                    fill, text, tc = COLORS["forbidden"], "☒", COLORS["forbidden_fg"]
                else:
                    fill = COLORS["light"] if is_light else COLORS["dark"]
                    text, tc = "", "#000000"
                self.canvas.itemconfig(self.rect_ids[r][c], fill=fill)
                self.canvas.itemconfig(self.text_ids[r][c], text=text, fill=tc)
        self.status.config(text="Кликните по свободной клетке, чтобы поставить ★")
        self.result_label.config(text="")
        self.sol_counter.config(text="")
        self.btn_show.config(state="disabled")
        self.btn_prev.config(state="disabled")
        self.btn_next.config(state="disabled")

    def show_solution(self):
        if not self.solutions:
            return
        sol = self.solutions[self.current_sol_idx]
        for r in range(N):
            for c in range(N):
                col, row = c+1, N-r
                if (col, row) in FORBIDDEN:
                    continue
                is_light = (r+c) % 2 == 0
                base = COLORS["light"] if is_light else COLORS["dark"]
                if self.fixed == (col, row):
                    self.canvas.itemconfig(self.rect_ids[r][c], fill=COLORS["star_fixed_bg"])
                    self.canvas.itemconfig(self.text_ids[r][c], text="★", fill=COLORS["star_fixed"])
                else:
                    self.canvas.itemconfig(self.rect_ids[r][c], fill=base)
                    self.canvas.itemconfig(self.text_ids[r][c], text="", fill="#000000")
        for col_idx, row in enumerate(sol):
            col = col_idx + 1
            if row and self.fixed != (col, row):
                r, c = N-row, col-1
                self.canvas.itemconfig(self.rect_ids[r][c], fill=COLORS["star_sol_bg"])
                self.canvas.itemconfig(self.text_ids[r][c], text="★", fill=COLORS["star_sol"])
        self.sol_counter.config(text=f"{self.current_sol_idx+1} / {len(self.solutions)}")

    def prev_sol(self):
        if self.solutions:
            self.current_sol_idx = (self.current_sol_idx - 1) % len(self.solutions)
            self.show_solution()

    def next_sol(self):
        if self.solutions:
            self.current_sol_idx = (self.current_sol_idx + 1) % len(self.solutions)
            self.show_solution()

    def solve(self, fixed: Tuple[int, int]) -> List[List[int]]:
        solutions, board = [], [0]*N
        board[fixed[0]-1] = fixed[1]

        def is_safe(col, row):
            if (col, row) in FORBIDDEN:
                return False
            for c in range(1, col):
                r = board[c-1]
                if r and (r == row or abs(c-col) == abs(r-row)):
                    return False
            return True

        def bt(col):
            if col > N:
                solutions.append(board[:])
                return
            if col == fixed[0]:
                bt(col+1)
                return
            for row in range(1, N+1):
                if is_safe(col, row):
                    board[col-1] = row
                    bt(col+1)
                    board[col-1] = 0
        bt(1)
        return solutions


def main():
    root = tk.Tk()
    try:
        from ctypes import windll
        windll.shcore.SetProcessDpiAwareness(1)
    except Exception:
        pass
    StarsApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()