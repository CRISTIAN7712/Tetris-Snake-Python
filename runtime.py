# master_game_gui_b.py
import tkinter as tk
from tkinter import messagebox
import random
import time
import sys
import os

# Sonido opcional: pygame si está disponible
try:
    import pygame
    pygame.mixer.init()
    PYGAME = True
except Exception:
    PYGAME = False

class MasterGame:
    """
    MasterGame: una sola clase que contiene:
    - GUI (Tkinter) con selección de juego.
    - Tetris gráfico en canvas.
    - Snake gráfico en canvas.
    - Ambos juegos dibujados y controlados por teclado.
    """

    def __init__(self, width=800, height=600):
        # --- GUI base ---
        self.root = tk.Tk()
        self.root.title("MasterGame — Tetris + Snake (Gráfico)")
        self.root.protocol("WM_DELETE_WINDOW", self._on_quit)

        # Maximizar ventana (Windows + Linux)
        self.root.state("zoomed")
        try:
            self.root.attributes("-zoomed", True)
        except:
            pass

        # sonido opcional
        self.snd_tetris = None
        self.snd_snake = None
        if PYGAME:
            try:
                if os.path.exists("click.wav"):
                    self.snd_tetris = pygame.mixer.Sound("click.wav")
                if os.path.exists("eat.wav"):
                    self.snd_snake = pygame.mixer.Sound("eat.wav")
            except Exception:
                self.snd_tetris = None
                self.snd_snake = None

        # estado del juego
        self.mode = None  # "tetris" or "snake" or None
        self.running = False

        # ---------------------------
        # LAYOUT RESPONSIVE (GRID)
        # ---------------------------
        self.root.rowconfigure(0, weight=1)
        self.root.columnconfigure(0, weight=0)
        self.root.columnconfigure(1, weight=1)

        # panel izquierdo
        self.left_w = 200
        self.left_frame = tk.Frame(self.root, width=self.left_w)
        self.left_frame.grid(row=0, column=0, sticky="ns", padx=6, pady=6)

        # área del canvas
        self.canvas_frame = tk.Frame(self.root)
        self.canvas_frame.grid(row=0, column=1, sticky="nsew", padx=6, pady=6)

        self.canvas_frame.rowconfigure(0, weight=1)
        self.canvas_frame.columnconfigure(0, weight=1)

        # canvas
        self.canvas = tk.Canvas(self.canvas_frame, bg="black")
        self.canvas.grid(row=0, column=0, sticky="nsew")

        # dimensiones base de ventana
        self.WIN_W = width
        self.WIN_H = height

        # redibujar al cambiar tamaño (responsive)
        self.canvas.bind("<Configure>", self._on_resize)

        # ---------------------------
        # Controles interiores (pack)
        # ---------------------------
        tk.Label(self.left_frame, text="MasterGame", font=("Arial", 16, "bold")).pack(pady=(6,12))
        tk.Button(self.left_frame, text="Jugar Tetris", width=18, command=self.start_tetris).pack(pady=4)
        tk.Button(self.left_frame, text="Jugar Snake", width=18, command=self.start_snake).pack(pady=4)
        tk.Button(self.left_frame, text="Parar / Volver al menú", width=18, command=self.stop_game).pack(pady=8)
        tk.Button(self.left_frame, text="Salir", width=18, command=self._on_quit).pack(pady=8)

        tk.Label(self.left_frame, text="Info / Controles", font=("Arial", 10, "bold")).pack(pady=(12,4))
        self.info_label = tk.Label(self.left_frame, text="", justify=tk.LEFT, wraplength=self.left_w-10)
        self.info_label.pack()

        # bind keys
        self.root.bind_all("<Key>", self._on_key)

        # clock
        self._after_id = None

        # parámetros Tetris
        self.t_width = 10
        self.t_height = 20
        self.cell = 24
        self.t_margin_x = 20
        self.t_margin_y = 20

        # parámetros Snake
        self.s_cols = 30
        self.s_rows = 20
        self.s_cell = 20

        # mostrar menú inicial
        self._show_menu_info()


        # Start mainloop if used as script; else call start()
    # end __init__
    # ---------------------------
    # Generic helpers and UI
    # ---------------------------
    def _show_menu_info(self):
        self.info_label.config(text=(
            "Selecciona un juego:\n\n"
            "Tetris: controles numéricos 1=Left 2=Down 3=Right 4=Pause 5=Drop 6=Power 7=Rotate\n"
            "Snake: WASD o flechas, Q para salir\n\n"
            "Nota: ambos juegos son gráficos (canvas)."
        ))
        self.canvas.delete("all")

        # Medidas del canvas (con fallback si aún no se ha dibujado)
        cw = self.canvas.winfo_width()
        ch = self.canvas.winfo_height()

        if cw < 50:
            cw = self.WIN_W - self.left_w - 20
        if ch < 50:
            ch = self.WIN_H - 20

        # Título
        self.canvas.create_text(
            cw // 2, ch // 2,
            text="MasterGame\nTetris & Snake",
            fill="white",
            font=("Arial", 30),
            justify="center"
        )

    def _on_resize(self, event):
        """Se ejecuta cada vez que el canvas cambia de tamaño."""
        
        # Redibujar menú
        if self.mode is None:
            self._show_menu_info()
            return

        # Reposicionar Tetris
        if self.mode == "tetris":
            new_w = event.width
            new_h = event.height

            # recalcular márgenes para centrar el tablero
            self.t_margin_x = (new_w - (self.t_width * self.cell)) // 2
            self.t_margin_y = (new_h - (self.t_height * self.cell)) // 2

            self._draw_tetris()
            return

        # Reposicionar Snake
        if self.mode == "snake":
            new_w = event.width
            new_h = event.height

            self.s_margin_x = (new_w - (self.s_cols * self.s_cell)) // 2
            self.s_margin_y = (new_h - (self.s_rows * self.s_cell)) // 2

            self._draw_snake()
            return

    def _on_quit(self):
        self.stop_game()
        try:
            if PYGAME:
                pygame.mixer.quit()
        except Exception:
            pass
        self.root.destroy()
        try:
            sys.exit(0)
        except Exception:
            pass

    def _on_key(self, event):
        k = event.keysym
        ch = event.char
        # pass to active mode handler
        if self.mode == "tetris":
            self._tetris_handle_key(k, ch)
        elif self.mode == "snake":
            self._snake_handle_key(k, ch)

    def start(self):
        self.root.mainloop()

    # ---------------------------
    # Stop game / return to menu
    # ---------------------------
    def stop_game(self):
        if self.running:
            self.running = False
            # cancel after
            if self._after_id:
                try:
                    self.canvas.after_cancel(self._after_id)
                except Exception:
                    pass
                self._after_id = None
            self.mode = None
            self.canvas.delete("all")
            self._show_menu_info()
    # =========================
    #  TETRIS implementation
    # =========================
    def start_tetris(self):
        if self.running:
            messagebox.showinfo("En ejecución", "Ya hay un juego en ejecución. Deténlo primero.")
            return
        self.mode = "tetris"
        self.running = True
        # board size
        cfg_w = 10
        cfg_h = 20
        self.t_width = cfg_w
        self.t_height = cfg_h
        self.cell = 24
        # compute margins to center board
        canvas_w = max(self.canvas.winfo_width(), (self.t_width*self.cell)+40)
        canvas_h = max(self.canvas.winfo_height(), (self.t_height*self.cell)+40)
        self.t_margin_x = (canvas_w - (self.t_width*self.cell))//2
        self.t_margin_y = (canvas_h - (self.t_height*self.cell))//2
        # init tetris state
        self.t_board = [[0 for _ in range(self.t_width)] for _ in range(self.t_height)]
        self.t_score = 0
        self.t_power_used = False
        self.t_speed = 500  # ms per fall step
        # pieces (tetrominoes) as matrix of 1/0
        self.t_pieces = [
            ([[1,1],
              [1,1]], "yellow"),  # O
            ([[1,1,1,1]], "cyan"),  # I
            ([[0,1,1],
              [1,1,0]], "green"),  # S
            ([[1,1,0],
              [0,1,1]], "red"),    # Z
            ([[1,0,0],
              [1,1,1]], "orange"), # L
            ([[0,0,1],
              [1,1,1]], "blue"),   # J
            ([[0,1,0],
              [1,1,1]], "magenta") # T
        ]
        self._spawn_t_piece()
        self._draw_tetris()
        # set info text
        self.info_label.config(text=f"Tetris — Puntaje: {self.t_score}")
        # schedule step
        self._tetris_schedule()

    def _spawn_t_piece(self):
        self.t_piece, self.t_piece_color = random.choice(self.t_pieces)
        # copy matrix
        self.t_piece = [list(row) for row in self.t_piece]
        self.t_piece_y = 0
        self.t_piece_x = random.randint(0, self.t_width - len(self.t_piece[0]))
        # ensure fit
        if self._tetris_collides(self.t_piece_x, self.t_piece_y, self.t_piece):
            # immediate game over
            self._tetris_game_over()
    def _rotate_matrix(self, m):
        return [list(row) for row in zip(*m[::-1])]

    def _tetris_collides(self, nx, ny, piece):
        for py, row in enumerate(piece):
            for px, val in enumerate(row):
                if val:
                    x = nx+px
                    y = ny+py
                    if x < 0 or x >= self.t_width or y < 0 or y >= self.t_height:
                        return True
                    if self.t_board[y][x]:
                        return True
        return False

    def _tetris_lock_piece(self):
        for py, row in enumerate(self.t_piece):
            for px, val in enumerate(row):
                if val:
                    x = self.t_piece_x+px
                    y = self.t_piece_y+py
                    if 0 <= y < self.t_height and 0 <= x < self.t_width:
                        self.t_board[y][x] = self.t_piece_color
        self._tetris_clear_lines()
        self.t_score += 50
        self._spawn_t_piece()

    def _tetris_clear_lines(self):
        new_board = [row for row in self.t_board if any(cell==0 for cell in row)]
        removed = self.t_height - len(new_board)
        for _ in range(removed):
            new_board.insert(0, [0]*self.t_width)
        if removed>0:
            self.t_board = new_board
            self.t_score += removed*100

    def _tetris_game_over(self):
        self.running = False
        self.mode = None
        self.canvas.create_text(self.WIN_W//2, 30, text="GAME OVER", fill="white", font=("Arial", 24))
        messagebox.showinfo("Game Over", f"Tetris terminó. Puntaje: {self.t_score}")

    def _draw_tetris(self):
        self.canvas.delete("all")
        bw = self.t_width * self.cell
        bh = self.t_height * self.cell
        x0 = self.t_margin_x
        y0 = self.t_margin_y

        # fondo del tablero
        self.canvas.create_rectangle(x0-2, y0-2, x0+bw+2, y0+bh+2,
                                    fill="#111", outline="#333")

        # bloques fijos
        for y in range(self.t_height):
            for x in range(self.t_width):
                cell = self.t_board[y][x]
                if cell:
                    self._draw_cell(x0 + x*self.cell, y0 + y*self.cell, self.cell, cell)

        # pieza activa
        for py, row in enumerate(self.t_piece):
            for px, val in enumerate(row):
                if val:
                    cx = x0 + (self.t_piece_x+px)*self.cell
                    cy = y0 + (self.t_piece_y+py)*self.cell
                    self._draw_cell(cx, cy, self.cell, self.t_piece_color)

        # líneas de cuadrícula
        for i in range(self.t_width+1):
            self.canvas.create_line(x0+i*self.cell, y0, x0+i*self.cell, y0+bh, fill="#222")
        for j in range(self.t_height+1):
            self.canvas.create_line(x0, y0+j*self.cell, x0+bw, y0+j*self.cell, fill="#222")

        # puntaje a la derecha
        self.canvas.create_text(
            x0 + bw + 80, y0 + 20,
            text=f"Puntaje: {self.t_score}",
            fill="white",
            font=("Arial", 12),
            anchor="w"
        )

        # ============================
        # BARRA DE COMANDOS INFERIOR
        # ============================
        bar_text = (
            "1=Izq | 2=Abajo | 3=Der | 4=Pausa | "
            "5=Drop | 6=Power | 7=Rotar | 0=Salir"
        )
        # --- NUEVO: usar el alto REAL DEL CANVAS ---
        cW = self.canvas.winfo_width()
        cH = self.canvas.winfo_height()

        self.canvas.create_rectangle(
            0, cH - 35, cW, cH,
            fill="#222", outline="#444"
        )
        self.canvas.create_text(
            cW // 2, cH - 18,
            text=bar_text,
            fill="white",
            font=("Arial", 11)
        )


    def _draw_cell(self, x, y, s, color_name):
        # map color names to hex
        cmap = {
            "yellow":"#FFD54A","cyan":"#4DD0E1","green":"#AED581",
            "red":"#EF5350","orange":"#FF8A65","blue":"#42A5F5","magenta":"#CE93D8"
        }
        c = cmap.get(color_name, "#FFFFFF")
        self.canvas.create_rectangle(x+1,y+1,x+s-1,y+s-1,fill=c,outline="#111")

    def _tetris_step(self):
        if not (self.running and self.mode=="tetris"):
            return
        # try move down
        if not self._tetris_collides(self.t_piece_x, self.t_piece_y+1, self.t_piece):
            self.t_piece_y += 1
        else:
            # cannot move down -> lock
            self._tetris_lock_piece()
        # redraw
        self._draw_tetris()
        self.info_label.config(text=f"Tetris — Puntaje: {self.t_score}")
        # schedule next
        self._after_id = self.canvas.after(self.t_speed, self._tetris_step)

    def _tetris_schedule(self):
        # start stepping
        if self._after_id:
            try:
                self.canvas.after_cancel(self._after_id)
            except Exception:
                pass
        self._after_id = self.canvas.after(self.t_speed, self._tetris_step)

    def _tetris_handle_key(self, keysym, char):
        # map keys to actions per original mapping
        # original: 1=left 2=down 3=right 4=rest 5=impulso(drop) 6=power 7=rotate 0=exit
        key = None
        # accept numeric keypad keys and characters
        if char and char.isdigit():
            key = char
        elif keysym in ("KP_1","KP_2","KP_3","KP_4","KP_5","KP_6","KP_7","KP_0"):
            key = keysym[-1]
        elif keysym=="Escape":
            key = "0"
        if not key:
            return
        # actions
        if key=="0":
            self.stop_game()
            return
        if key=="1":
            if not self._tetris_collides(self.t_piece_x-1, self.t_piece_y, self.t_piece):
                self.t_piece_x -= 1
        elif key=="2":
            if not self._tetris_collides(self.t_piece_x, self.t_piece_y+1, self.t_piece):
                self.t_piece_y += 1
        elif key=="3":
            if not self._tetris_collides(self.t_piece_x+1, self.t_piece_y, self.t_piece):
                self.t_piece_x += 1
        elif key == "4":
            if not self.running:
                return

            self.running = False
            if self._after_id:
                try:
                    self.canvas.after_cancel(self._after_id)
                except:
                    pass

            # obtener tamaño REAL del canvas
            cw = self.canvas.winfo_width()
            ch = self.canvas.winfo_height()

            # mensaje de pausa
            self.pause_msg = self.canvas.create_text(
                cw//2, 50,
                text="PAUSA (7 seg)",
                fill="yellow",
                font=("Arial", 24, "bold")
            )

            self.canvas.update()
            self.canvas.after(7000, self._resume_after_pause)
            return
        elif key=="5":
            # impulso: drop until collision
            while not self._tetris_collides(self.t_piece_x, self.t_piece_y+1, self.t_piece):
                self.t_piece_y += 1
            self._tetris_lock_piece()
        elif key == "6":
            # POWER ok
            if self.t_score >= 1000 and not self.t_power_used:

                for y in range(self.t_height):
                    for x in range(self.t_width):
                        self.t_board[y][x] = 0

                self.t_power_used = True

                cw = self.canvas.winfo_width()
                ch = self.canvas.winfo_height()

                msg = self.canvas.create_text(
                    cw//2, ch//2,
                    text="POWER ACTIVADO",
                    fill="yellow",
                    font=("Arial", 26, "bold")
                )
                self.canvas.update()
                self.canvas.after(900)
                self.canvas.delete(msg)

            else:
                # falla del power: puntaje insuficiente o ya usado
                cw = self.canvas.winfo_width()
                ch = self.canvas.winfo_height()

                if self.t_power_used:
                    texto = "El POWER ya fue usado"
                else:
                    texto = "Necesitas 1000 puntos"

                # parpadeo rojo
                self.canvas.create_rectangle(0,0,cw,ch, fill="#550000")
                self.canvas.update()
                self.canvas.after(60)

                # mensaje de error
                msg = self.canvas.create_text(
                    cw//2, ch//2,
                    text=texto,
                    fill="red",
                    font=("Arial", 24, "bold")
                )
                self.canvas.update()
                self.canvas.after(900)
                self.canvas.delete(msg)
        elif key == "7":
            # Rotación con validación de bordes
            newp = self._rotate_matrix(self.t_piece)

            # Si choca, intenta corregir moviendo 1 a la izquierda o derecha
            if not self._tetris_collides(self.t_piece_x, self.t_piece_y, newp):
                self.t_piece = newp
            elif not self._tetris_collides(self.t_piece_x - 1, self.t_piece_y, newp):
                self.t_piece_x -= 1
                self.t_piece = newp
            elif not self._tetris_collides(self.t_piece_x + 1, self.t_piece_y, newp):
                self.t_piece_x += 1
                self.t_piece = newp
            # Si no se pudo corregir → no se rota (validación)
        # play sound per key
        try:
            if self.snd_tetris:
                self.snd_tetris.play()
        except Exception:
            pass
        # redraw
        self._draw_tetris()
    def _resume_after_pause(self):
        # borrar texto si existe
        if hasattr(self, "pause_msg"):
            self.canvas.delete(self.pause_msg)

        self.running = True
        self._tetris_schedule()
    # =========================
    #  SNAKE implementation
    # =========================
    def start_snake(self):
        if self.running:
            messagebox.showinfo("En ejecución", "Ya hay un juego en ejecución. Deténlo primero.")
            return
        self.mode = "snake"
        self.running = True
        # grid
        self.s_cols = 30
        self.s_rows = 20
        self.s_cell = 20
        # position canvas margin
        canvas_w = max(self.canvas.winfo_width(), (self.s_cols*self.s_cell)+40)
        canvas_h = max(self.canvas.winfo_height(), (self.s_rows*self.s_cell)+40)
        self.s_margin_x = (canvas_w - (self.s_cols*self.s_cell))//2
        self.s_margin_y = (canvas_h - (self.s_rows*self.s_cell))//2
        # snake state
        self.s_snake = [(self.s_cols//2, self.s_rows//2)]
        self.s_dir = (1,0)
        self.s_speed = 120  # ms per step
        self.s_score = 0
        self._place_food()
        self._draw_snake()
        self.info_label.config(text=f"Snake — Puntaje: {self.s_score}")
        # schedule
        self._after_id = self.canvas.after(self.s_speed, self._snake_step)

    def _place_food(self):
        while True:
            x = random.randint(0, self.s_cols-1)
            y = random.randint(0, self.s_rows-1)
            if (x,y) not in self.s_snake:
                self.s_food = (x,y)
                break

    def _draw_snake(self):
        self.canvas.delete("all")
        # background
        grid_w = self.s_cols*self.s_cell
        grid_h = self.s_rows*self.s_cell
        x0 = self.s_margin_x
        y0 = self.s_margin_y
        self.canvas.create_rectangle(x0-2,y0-2,x0+grid_w+2,y0+grid_h+2,fill="#111",outline="#333")
        # draw food
        fx,fy = self.s_food
        self.canvas.create_rectangle(x0+fx*self.s_cell+2, y0+fy*self.s_cell+2,
                                     x0+(fx+1)*self.s_cell-2, y0+(fy+1)*self.s_cell-2,
                                     fill="#ff3333", outline="#111")
        # draw snake
        for i,(sx,sy) in enumerate(self.s_snake):
            color = "#66ff66" if i==0 else "#009933"
            self.canvas.create_rectangle(x0+sx*self.s_cell+2, y0+sy*self.s_cell+2,
                                         x0+(sx+1)*self.s_cell-2, y0+(sy+1)*self.s_cell-2,
                                         fill=color, outline="#111")
        # score
        self.canvas.create_text(x0+grid_w+80, y0+20, text=f"Puntaje: {self.s_score}", fill="white", font=("Arial",12), anchor="w")

    def _snake_step(self):
        if not (self.running and self.mode=="snake"):
            return
        # compute new head
        hx,hy = self.s_snake[0]
        dx,dy = self.s_dir
        nx,ny = hx+dx, hy+dy
        # collision
        if nx<0 or nx>=self.s_cols or ny<0 or ny>=self.s_rows or (nx,ny) in self.s_snake:
            # game over
            messagebox.showinfo("Game Over", f"Snake terminó. Puntaje: {self.s_score}")
            self.running = False
            self.mode = None
            self._show_menu_info()
            return
        # move
        self.s_snake.insert(0,(nx,ny))
        if (nx,ny)==self.s_food:
            self.s_score += 10
            self._place_food()
            try:
                if self.snd_snake:
                    self.snd_snake.play()
            except Exception:
                pass
        else:
            self.s_snake.pop()
        self._draw_snake()
        self.info_label.config(text=f"Snake — Puntaje: {self.s_score}")
        self._after_id = self.canvas.after(self.s_speed, self._snake_step)

    def _snake_handle_key(self, keysym, char):
        # map WASD and arrows to directions
        key = char.lower() if char else keysym
        if key in ("w","Up","W","Up"):
            if self.s_dir!=(0,1):
                self.s_dir=(0,-1)
        elif key in ("s","Down","S","Down"):
            if self.s_dir!=(0,-1):
                self.s_dir=(0,1)
        elif key in ("a","Left","A","Left"):
            if self.s_dir!=(1,0):
                self.s_dir=(-1,0)
        elif key in ("d","Right","D","Right"):
            if self.s_dir!=(-1,0):
                self.s_dir=(1,0)
        elif key in ("q","Q"):
            self.stop_game()

# ============================
# Ejecutar la app
# ============================
if __name__ == "__main__":
    app = MasterGame()
    app.start()
