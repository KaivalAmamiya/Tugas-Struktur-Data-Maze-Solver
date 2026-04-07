# 🧩 Maze Solver – BFS & DFS Animasi

Visualisasi animasi pencarian jalan keluar dari labirin menggunakan algoritma **BFS** dan **DFS**, dibuat dengan Python dan Tkinter (tidak perlu install library tambahan).

---

## 📄 Penjelasan

Program ini mensimulasikan dua algoritma pencarian jalur pada sebuah labirin:

- **BFS (Breadth-First Search)** — menjelajah sel secara melebar, menjamin jalur terpendek
- **DFS (Depth-First Search)** — menjelajah sel secara mendalam, menemukan jalur lebih cepat tapi tidak selalu terpendek

**Warna visualisasi:**

| Warna | Keterangan |
|---|---|
| 🟩 Hijau muda | Frontier (sel yang sedang dalam antrian) |
| 🟨 Kuning muda | Visited (sel yang sudah dikunjungi) |
| 🟢 Hijau tua | Jalur solusi |
| 🟦 Navy | Dinding (wall) |
| 🟠 Oranye | Titik Exit (E) |

---

## 🖥️ Kode

```python
def _step(self):
    if self.state != "searching":
        return

    cur = self.struct.pop(0) if self.algo == "bfs" else self.struct.pop()
    self.frontier.discard(cur)
    self.visited.add(cur)

    if cur == self.end_pos:
        self.solution = build_path(self.came_from, self.end_pos)
        self.state = "found"
        return

    for nb in get_neighbors(cur[0], cur[1]):
        if nb not in self.visited and nb not in self.frontier:
            self.came_from[nb] = cur
            self.frontier.add(nb)
            self.struct.append(nb)

    self.after_id = self.root.after(self._get_delay(), self._step)
```

**Struktur data:**
- BFS menggunakan `list` sebagai **queue** → `pop(0)`
- DFS menggunakan `list` sebagai **stack** → `pop()`

---

## 🗺️ Maze

Maze diambil langsung dari soal praktikum (15×16 grid):

```
################
#S..#....#.....#
###.#.##.#.###.#
#.....##...#.#.#
#.########.#...#
#.#......#.#####
#.#.####.#....##
#...#.##.####.##
###.#.##....#..#
#.#.#.#####.##.#
#.#.......#..#.#
#.#######.####.#
#.....##.......#
#####.########E#
################
```

- `S` = titik start (pojok kiri atas)
- `E` = titik exit (pojok kanan bawah)
- `#` = dinding
- `.` = jalur

---

## 🟩 Contoh Output

**BFS:**
```
✓ Jalan ditemukan!  Panjang: 30 langkah  |  Dikunjungi: 89 sel
```

**DFS:**
```
✓ Jalan ditemukan!  Panjang: 57 langkah  |  Dikunjungi: 104 sel
```

> BFS selalu menemukan jalur terpendek, sedangkan DFS menemukan jalur lebih cepat tapi panjangnya tidak optimal.

---

## ✅ Kesimpulan

Dari implementasi di atas dapat disimpulkan bahwa:

- ✅ BFS menjamin jalur **terpendek** karena menjelajah level per level
- ✅ DFS lebih **hemat memori** karena hanya menyimpan satu jalur di stack
- ✅ Kedua algoritma berhasil menemukan jalan keluar dari labirin
- ✅ Visualisasi animasi memudahkan pemahaman cara kerja masing-masing algoritma

---

## 🚀 Cara Menjalankan

### 1. Clone Repository

```bash
git clone https://github.com/username/maze-solver.git
cd maze-solver
```

### 2. Jalankan Program

```bash
python maze_solver.py
```

> Tidak perlu install library apapun — Tkinter sudah built-in di Python!

### 3. Kontrol Program

| Tombol | Fungsi |
|---|---|
| `▶ BFS` | Jalankan animasi BFS |
| `▶ DFS` | Jalankan animasi DFS |
| `↺ Reset` | Reset maze ke kondisi awal |
| Slider | Atur kecepatan animasi (Lambat → Max) |
