"""
Maze Solver Animasi - BFS & DFS
================================
Jalankan: python maze_solver.py

Kontrol:
    Tombol BFS   = Jalankan BFS
    Tombol DFS   = Jalankan DFS
    Tombol Reset = Reset maze
    Slider       = Atur kecepatan
"""

import tkinter as tk
from collections import deque

# ── Maze (persis dari PDF) ──────────────────────────────────────────────────
MAZE_RAW = [
    "################",
    "#S..#....#.....#",
    "###.#.##.#.###.#",
    "#.....##...#.#.#",
    "#.########.#...#",
    "#.#......#.#####",
    "#.#.####.#....##",
    "#...#.##.####.##",
    "###.#.##....#..#",
    "#.#.#.#####.##.#",
    "#.#.......#..#.#",
    "#.#######.####.#",
    "#.....##.......#",
    "#####.########E#",
    "################",
]

ROWS = len(MAZE_RAW)
COLS = len(MAZE_RAW[0])
maze = [list(row) for row in MAZE_RAW]

# ── Warna ────────────────────────────────────────────────────────────────────
C_BG       = "#0f1937"
C_WALL     = "#122350"
C_PATH     = "#ebedfa"
C_FRONTIER = "#5DCAA5"
C_VISITED  = "#e6dca8"
C_SOLUTION = "#1D9E75"
C_START    = "#1D9E75"
C_END      = "#e09016"
C_TEXT     = "#ffffff"
C_PANEL    = "#0a1230"

# ── Ukuran ───────────────────────────────────────────────────────────────────
CELL    = 42
PAD     = 14
PANEL_H = 90

WIN_W = COLS * CELL + PAD * 2
WIN_H = ROWS * CELL + PAD * 2 + PANEL_H


def find_pos(ch):
    for r in range(ROWS):
        for c in range(COLS):
            if maze[r][c] == ch:
                return (r, c)
    return None


def get_neighbors(r, c):
    result = []
    for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
        nr, nc = r + dr, c + dc
        if 0 <= nr < ROWS and 0 <= nc < COLS and maze[nr][nc] != '#':
            result.append((nr, nc))
    return result


def build_path(came_from, end):
    path = set()
    cur = end
    while cur is not None:
        path.add(cur)
        cur = came_from.get(cur)
    return path


class MazeSolver:
    def __init__(self, root):
        self.root = root
        self.root.title("Maze Solver – BFS & DFS")
        self.root.configure(bg=C_BG)
        self.root.resizable(False, False)

        self.start_pos = find_pos('S')
        self.end_pos   = find_pos('E')

        self.visited   = set()
        self.frontier  = set()
        self.solution  = set()
        self.came_from = {}
        self.struct    = []
        self.state     = "idle"   # idle | searching | found | not_found
        self.algo      = "bfs"
        self.after_id  = None

        self._build_ui()
        self.draw_maze()

    # ── UI ───────────────────────────────────────────────────────────────────

    def _build_ui(self):
        # Canvas maze
        self.canvas = tk.Canvas(
            self.root,
            width=WIN_W, height=ROWS * CELL + PAD * 2,
            bg=C_BG, highlightthickness=0
        )
        self.canvas.pack()

        # Panel bawah
        panel = tk.Frame(self.root, bg=C_PANEL, height=PANEL_H)
        panel.pack(fill="x")
        panel.pack_propagate(False)

        # Baris tombol
        btn_frame = tk.Frame(panel, bg=C_PANEL)
        btn_frame.pack(pady=(10, 4))

        style = dict(
            font=("Courier", 11, "bold"),
            fg=C_TEXT, bg="#1a3060",
            activeforeground=C_TEXT, activebackground="#254080",
            relief="flat", padx=16, pady=5, cursor="hand2",
            bd=0
        )

        self.btn_bfs = tk.Button(btn_frame, text="▶  BFS",
                                 command=lambda: self.start_search("bfs"), **style)
        self.btn_bfs.pack(side="left", padx=6)

        self.btn_dfs = tk.Button(btn_frame, text="▶  DFS",
                                 command=lambda: self.start_search("dfs"), **style)
        self.btn_dfs.pack(side="left", padx=6)

        self.btn_reset = tk.Button(btn_frame, text="↺  Reset",
                                   command=self.reset, **style)
        self.btn_reset.pack(side="left", padx=6)

        # Slider kecepatan
        spd_frame = tk.Frame(panel, bg=C_PANEL)
        spd_frame.pack()

        tk.Label(spd_frame, text="Kecepatan:", font=("Courier", 10),
                 fg="#8899cc", bg=C_PANEL).pack(side="left", padx=(0, 6))

        self.speed_var = tk.IntVar(value=3)
        slider = tk.Scale(
            spd_frame, from_=1, to=6, orient="horizontal",
            variable=self.speed_var, length=140,
            bg=C_PANEL, fg="#8899cc", troughcolor="#1a2a50",
            highlightthickness=0, showvalue=False, bd=0
        )
        slider.pack(side="left")

        self.spd_label = tk.Label(spd_frame, text="Normal",
                                  font=("Courier", 10), fg="#8899cc", bg=C_PANEL, width=12)
        self.spd_label.pack(side="left", padx=4)
        slider.config(command=self._update_speed_label)

        # Label status
        self.status_var = tk.StringVar(value="Tekan BFS atau DFS untuk mulai")
        self.status_lbl = tk.Label(
            panel, textvariable=self.status_var,
            font=("Courier", 10), fg="#aabbdd", bg=C_PANEL
        )
        self.status_lbl.pack()

    def _update_speed_label(self, _=None):
        names = ["", "Lambat", "Pelan", "Normal", "Cepat", "Sangat Cepat", "Max"]
        self.spd_label.config(text=names[self.speed_var.get()])

    def _get_delay(self):
        delays = [0, 250, 120, 50, 18, 5, 1]
        return delays[self.speed_var.get()]

    # ── Draw ─────────────────────────────────────────────────────────────────

    def draw_maze(self):
        self.canvas.delete("all")
        ox, oy = PAD, PAD

        for r in range(ROWS):
            for c in range(COLS):
                ch = maze[r][c]
                x1 = ox + c * CELL + 1
                y1 = oy + r * CELL + 1
                x2 = x1 + CELL - 2
                y2 = y1 + CELL - 2

                if ch == '#':
                    color = C_WALL
                elif ch == 'S':
                    color = C_START
                elif ch == 'E':
                    color = C_END
                elif (r, c) in self.solution:
                    color = C_SOLUTION
                elif (r, c) in self.frontier:
                    color = C_FRONTIER
                elif (r, c) in self.visited:
                    color = C_VISITED
                else:
                    color = C_PATH

                self.canvas.create_rectangle(
                    x1, y1, x2, y2,
                    fill=color, outline="", tags="cell"
                )

                if ch == 'S':
                    self.canvas.create_text(
                        (x1+x2)//2, (y1+y2)//2,
                        text="·", fill=C_TEXT,
                        font=("Courier", int(CELL * 0.6), "bold")
                    )
                elif ch == 'E':
                    self.canvas.create_text(
                        (x1+x2)//2, (y1+y2)//2,
                        text="E", fill=C_TEXT,
                        font=("Courier", int(CELL * 0.5), "bold")
                    )

        # Grid lines
        for r in range(ROWS + 1):
            self.canvas.create_line(
                ox, oy + r * CELL,
                ox + COLS * CELL, oy + r * CELL,
                fill="#1a2e60", width=1
            )
        for c in range(COLS + 1):
            self.canvas.create_line(
                ox + c * CELL, oy,
                ox + c * CELL, oy + ROWS * CELL,
                fill="#1a2e60", width=1
            )

    # ── Search ───────────────────────────────────────────────────────────────

    def start_search(self, algo):
        self.reset(keep_algo=False)
        self.algo    = algo
        self.state   = "searching"
        self.struct  = [self.start_pos]
        self.frontier = {self.start_pos}
        name = "BFS (Breadth-First)" if algo == "bfs" else "DFS (Depth-First)"
        self.status_var.set(f"Menjalankan {name}...")
        self._step()

    def _step(self):
        if self.state != "searching":
            return

        if not self.struct:
            self.state = "not_found"
            self.status_var.set("Tidak ada jalan keluar!")
            self.draw_maze()
            return

        cur = self.struct.pop(0) if self.algo == "bfs" else self.struct.pop()
        self.frontier.discard(cur)
        self.visited.add(cur)

        if cur == self.end_pos:
            self.solution = build_path(self.came_from, self.end_pos)
            self.state = "found"
            self.draw_maze()
            self.status_var.set(
                f"✓ Jalan ditemukan!  Panjang: {len(self.solution)} langkah  |  "
                f"Dikunjungi: {len(self.visited)} sel"
            )
            return

        for nb in get_neighbors(cur[0], cur[1]):
            if nb not in self.visited and nb not in self.frontier:
                self.came_from[nb] = cur
                self.frontier.add(nb)
                self.struct.append(nb)

        self.draw_maze()
        algo_name = "BFS" if self.algo == "bfs" else "DFS"
        self.status_var.set(
            f"{algo_name}  |  Dikunjungi: {len(self.visited)}  |  Antrian: {len(self.struct)}"
        )

        self.after_id = self.root.after(self._get_delay(), self._step)

    def reset(self, keep_algo=True):
        if self.after_id:
            self.root.after_cancel(self.after_id)
            self.after_id = None
        self.visited   = set()
        self.frontier  = set()
        self.solution  = set()
        self.came_from = {}
        self.struct    = []
        self.state     = "idle"
        self.status_var.set("Tekan BFS atau DFS untuk mulai")
        self.draw_maze()


if __name__ == "__main__":
    root = tk.Tk()
    app = MazeSolver(root)
    root.mainloop()