# master_game.py
import os
import sys
import time
import random
import json

# colorama para colores en consola
from colorama import init as colorama_init, Fore, Style
colorama_init()

# intento de inicializar sonido con pygame; si falla, sigue sin sonido
try:
    import pygame
    pygame.mixer.init()
    PYGAME_AVAILABLE = True
except Exception:
    PYGAME_AVAILABLE = False

class MasterGame:
    """
    Clase única que contiene TODO: menú, Tetris (completo) y Snake (completo).
    Mantiene la lógica original lo más fiel posible.
    """

    def __init__(self):
        # Rutas de sonido (opcionales)
        self.sonido_tetris_path = "click.wav"
        self.sonido_snake_path = "eat.wav"
        self.sonido_tetris = None
        self.sonido_snake = None
        if PYGAME_AVAILABLE:
            try:
                if os.path.exists(self.sonido_tetris_path):
                    self.sonido_tetris = pygame.mixer.Sound(self.sonido_tetris_path)
                if os.path.exists(self.sonido_snake_path):
                    self.sonido_snake = pygame.mixer.Sound(self.sonido_snake_path)
            except Exception:
                self.sonido_tetris = None
                self.sonido_snake = None

        # Detectar plataforma y establecer lectura de teclas (función)
        self._setup_leer_tecla()

        # Variables auxiliares
        self._stop_requested = False

    # -----------------------------
    #  Detección de teclas (configurada en init)
    # -----------------------------
    def _setup_leer_tecla(self):
        # Definimos self.leer_tecla() para Windows o Unix
        try:
            import msvcrt
            def leer_tecla_windows():
                if msvcrt.kbhit():
                    try:
                        return msvcrt.getch().decode("latin-1")
                    except:
                        return None
                return None
            self.leer_tecla = leer_tecla_windows
            self._msvcrt = msvcrt
            self._use_msvcrt = True
        except ImportError:
            # Unix-like
            import termios, tty, select
            def leer_tecla_unix():
                dr, dw, de = select.select([sys.stdin], [], [], 0)
                if dr:
                    return sys.stdin.read(1)
                return None
            self.leer_tecla = leer_tecla_unix
            self._use_msvcrt = False

    # =============================
    #  Motor de juego general (leer config y seleccionar juego)
    # =============================
    def run_runtime_from_config(self, config_file):
        if not os.path.exists(config_file):
            print(f"No se encontró el archivo: {config_file}")
            sys.exit(1)

        with open(config_file, "r", encoding="utf-8") as f:
            config = json.load(f)

        nombre = config.get("nombre_juego", "").lower()

        if "tetris" in nombre:
            juego = self.TetrisGame(self, config)
        elif "snake" in nombre:
            juego = self.SnakeGame(self, config)
        else:
            print("No se reconoce el tipo de juego en la configuración.")
            sys.exit(1)

        juego.run()

    # =============================
    #  IMPLEMENTACIÓN DEL TETRIS (como clase interna pero referenciando self.master)
    # =============================
    class TetrisGame:
        def __init__(self, master, config):
            self.master = master  # referencia a MasterGame
            self.config = config
            self.ancho = config.get("ancho", 8)
            self.alto = config.get("alto", 12)
            self.velocidad = config.get("velocidad", 0.5)
            self.puntaje = 0
            self.poder_usado = False
            self.juego_activo = True

            # Colores disponibles para las piezas (colorama)
            self.colores = [Fore.RED, Fore.GREEN, Fore.YELLOW, Fore.CYAN, Fore.MAGENTA, Fore.BLUE, Fore.LIGHTWHITE_EX]

            # Figuras Tetris con sus colores (idénticas a tu código)
            self.figuras = [
                ([[ "█", "█" ],
                  [ "█", "█" ]], Fore.YELLOW),  # O

                ([[ "█" ],
                  [ "█" ],
                  [ "█" ],
                  [ "█" ]], Fore.CYAN),  # I

                ([[ " ", "█" ],
                  [ "█", "█" ],
                  [ "█", " " ]], Fore.GREEN),  # S

                ([[ "█", " " ],
                  [ "█", "█" ],
                  [ " ", "█" ]], Fore.RED),  # Z

                ([[ "█", " " ],
                  [ "█", " " ],
                  [ "█", "█" ]], Fore.MAGENTA),  # L

                ([[ " ", "█" ],
                  [ " ", "█" ],
                  [ "█", "█" ]], Fore.BLUE),  # J

                ([[ " ", "█", " " ],
                  [ "█", "█", "█" ]], Fore.LIGHTWHITE_EX)  # T
            ]

            # Tablero vacío
            self.tablero = [[" " for _ in range(self.ancho)] for _ in range(self.alto)]

            # Crear primera pieza
            self.nueva_pieza()

            # Ajustar consola
            if os.name == "nt":
                try:
                    os.system("mode con: cols=80 lines=25")
                except Exception:
                    pass

        # ------------------------------
        def nueva_pieza(self):
            figura, color = random.choice(self.figuras)
            self.pieza = figura
            self.color_pieza = color
            self.pieza_y = 0
            self.pieza_x = random.randint(0, self.ancho - len(self.pieza[0]))

        # ------------------------------
        def mostrar_tablero(self):
            os.system("cls" if os.name == "nt" else "clear")
            print(Fore.CYAN + f"{self.config['nombre_juego']} | Puntaje: {self.puntaje}")
            print(Fore.CYAN + "╔" + "═" * (self.ancho * 2) + "╗")
            for y in range(self.alto):
                fila = ""
                for x in range(self.ancho):
                    celda = self.tablero[y][x]
                    # Dibujar pieza actual
                    dentro = False
                    for fy, f_row in enumerate(self.pieza):
                        for fx, val in enumerate(f_row):
                            if val == "█" and y == self.pieza_y + fy and x == self.pieza_x + fx:
                                fila += self.color_pieza + "█" * 2
                                dentro = True
                                break
                        if dentro:
                            break
                    else:
                        fila += celda * 2
                print(Fore.CYAN + "║" + fila + "║")
            print(Fore.CYAN + "╚" + "═" * (self.ancho * 2) + "╝")
            print(Style.RESET_ALL + "Controles: 1=Izq 2=Bajar 3=Der 4=Descanso 5=Impulso 6=Poder 7=Rotar 0=Salir")

        # ------------------------------
        def mover_pieza(self, dx, dy):
            nuevo_x = self.pieza_x + dx
            nuevo_y = self.pieza_y + dy

            for fy, fila in enumerate(self.pieza):
                for fx, celda in enumerate(fila):
                    if celda == "█":
                        x = nuevo_x + fx
                        y = nuevo_y + fy
                        if x < 0 or x >= self.ancho or y >= self.alto:
                            return self.fijar_pieza()
                        if y >= 0 and self.tablero[y][x] != " ":
                            return self.fijar_pieza()

            self.pieza_x, self.pieza_y = nuevo_x, nuevo_y
            return True

        # ------------------------------
        def fijar_pieza(self):
            for fy, fila in enumerate(self.pieza):
                for fx, celda in enumerate(fila):
                    if celda == "█":
                        x = self.pieza_x + fx
                        y = self.pieza_y + fy
                        if 0 <= y < self.alto:
                            self.tablero[y][x] = self.color_pieza + "█" + Style.RESET_ALL

            self.limpiar_filas()

            if any(self.tablero[0][x] != " " for x in range(self.ancho)):
                self.mostrar_tablero()
                print(Fore.RED + "💀 ¡Game Over! El tablero está lleno.")
                self.juego_activo = False
                time.sleep(2)
                return False

            self.nueva_pieza()
            self.puntaje += 50
            return False

        # ------------------------------
        def limpiar_filas(self):
            nuevas = [fila for fila in self.tablero if any(c == " " for c in fila)]
            eliminadas = self.alto - len(nuevas)
            for _ in range(eliminadas):
                nuevas.insert(0, [" "] * self.ancho)
            self.tablero = nuevas
            if eliminadas > 0:
                print(Fore.GREEN + f"✅ {eliminadas} fila(s) eliminadas!")
                self.puntaje += eliminadas * 100
                time.sleep(0.5)

        # ------------------------------
        def rotar_pieza(self):
            nueva = [list(fila) for fila in zip(*self.pieza[::-1])]
            for fy, fila in enumerate(nueva):
                for fx, celda in enumerate(fila):
                    if celda == "█":
                        x = self.pieza_x + fx
                        y = self.pieza_y + fy
                        if x < 0 or x >= self.ancho or y >= self.alto:
                            return
                        if y >= 0 and self.tablero[y][x] != " ":
                            return
            self.pieza = nueva

        # ------------------------------
        def activar_poder(self):
            if self.puntaje >= 1000 and not self.poder_usado:
                self.tablero = [[" " for _ in range(self.ancho)] for _ in range(self.alto)]
                self.poder_usado = True
                print(Fore.LIGHTMAGENTA_EX + "💥 ¡Poder activado! Todos los bloques fueron eliminados.")
                time.sleep(1)
            elif self.poder_usado:
                print(Fore.YELLOW + "⚠️ Ya utilizaste el poder especial. Solo se puede usar una vez.")
                time.sleep(1)
            else:
                print(Fore.RED + "❌ Puntaje insuficiente (mínimo 1000).")
                time.sleep(1)

        # ------------------------------
        def run(self):
            print(Fore.CYAN + "Iniciando Tetris... Presiona 0 para salir.")
            time.sleep(1)

            while self.juego_activo:
                tecla = self.master.leer_tecla()
                if tecla == "0":
                    print(Fore.YELLOW + "Juego terminado por el usuario.")
                    self.juego_activo = False
                    break
                elif tecla == "1":
                    self.mover_pieza(-1, 0)
                elif tecla == "2":
                    self.mover_pieza(0, 1)
                elif tecla == "3":
                    self.mover_pieza(1, 0)
                elif tecla == "4":
                    print(Fore.LIGHTBLACK_EX + "😴 Descanso activado... pausa de 7 segundos.")
                    time.sleep(7)
                elif tecla == "5":
                    while self.mover_pieza(0, 1) and self.juego_activo:
                        pass
                    self.mostrar_tablero()
                    time.sleep(0.1)
                    continue
                elif tecla == "6":
                    self.activar_poder()
                elif tecla == "7":
                    self.rotar_pieza()

                # Reproducir sonido por tecla si está disponible (cada pulsación)
                try:
                    if tecla and self.master.sonido_tetris:
                        self.master.sonido_tetris.play()
                except Exception:
                    pass

                # Caída automática
                self.mover_pieza(0, 1)
                self.mostrar_tablero()
                time.sleep(self.velocidad)

    # =============================
    #  IMPLEMENTACIÓN DEL SNAKE
    # =============================
    class SnakeGame:
        COLOR_ROJO = "\033[91m"
        COLOR_VERDE = "\033[92m"
        COLOR_RESET = "\033[0m"

        def __init__(self, master, config):
            self.master = master
            self.config = config
            self.ancho = config.get("ancho", 40)
            self.alto = config.get("alto", 30)
            self.velocidad = config.get("velocidad", 5)
            self.longitud_inicial = config.get("longitud_inicial", 3)
            self.comidas = config.get("comidas", [])
            self.color_serpiente = config.get("color_serpiente", "verde")
            self.controles = config.get("controles", {
                "mover_izquierda": "a",
                "mover_derecha": "d",
                "mover_arriba": "w",
                "mover_abajo": "s"
            })
            # Inicial snake centrada
            self.snake = [(self.ancho // 2, self.alto // 2)]
            self.direccion = "derecha"
            self.puntaje = 0
            self.fruta = None

            # Truco para habilitar colores ANSI en la consola de Windows moderna
            os.system("")
            self.generar_fruta()
            try:
                if os.name == "nt":
                    os.system("mode con: cols=80 lines=30")
            except Exception:
                pass

            # Si estamos en Windows, usaremos la función msvcrt específica dentro de este objeto
            self._msvcrt = getattr(self.master, "_msvcrt", None)

        # Mostrar tablero casi idéntico al original
        def mostrar_tablero(self):
            print("\033[H", end="")
            print(f"{self.config.get('nombre_juego', 'Snake')} | Puntaje: {self.puntaje}")
            print("╔" + "═" * self.ancho + "╗")
            for y in range(self.alto):
                fila = ""
                for x in range(self.ancho):
                    if (x, y) in self.snake:
                        fila += f"{self.COLOR_VERDE}O{self.COLOR_RESET}"
                    elif self.fruta and self.fruta["pos"] == (x, y):
                        caracter = "+" if self.fruta["tipo"] == "bonus" else "*"
                        fila += f"{self.COLOR_ROJO}{caracter}{self.COLOR_RESET}"
                    else:
                        fila += " "
                print("║" + fila + "║")
            print("╚" + "═" * self.ancho + "╝")
            print("Usa W, A, S, D para moverte. Presiona Q para salir.")

        # Leer tecla adaptada (usa msvcrt cuando existe para leer teclas especiales)
        def leer_tecla(self):
            if self._msvcrt:
                if self._msvcrt.kbhit():
                    tecla = self._msvcrt.getch()
                    try:
                        t = tecla.decode("latin-1").lower()
                        if t in ["w", "a", "s", "d", "q"]:
                            return t
                    except:
                        if tecla == b'\xe0':
                            k = self._msvcrt.getch()
                            if k == b'H': return "w"
                            elif k == b'P': return "s"
                            elif k == b'K': return "a"
                            elif k == b'M': return "d"
            else:
                # usar la función global del master para unix
                return self.master.leer_tecla()
            return None

        def actualizar_direccion(self, tecla):
            if tecla == "w" and self.direccion != "abajo":
                self.direccion = "arriba"
            elif tecla == "s" and self.direccion != "arriba":
                self.direccion = "abajo"
            elif tecla == "a" and self.direccion != "derecha":
                self.direccion = "izquierda"
            elif tecla == "d" and self.direccion != "izquierda":
                self.direccion = "derecha"

        def mover_snake(self):
            cabeza_x, cabeza_y = self.snake[0]
            if self.direccion == "arriba": cabeza_y -= 1
            elif self.direccion == "abajo": cabeza_y += 1
            elif self.direccion == "izquierda": cabeza_x -= 1
            elif self.direccion == "derecha": cabeza_x += 1

            nueva_cabeza = (cabeza_x, cabeza_y)

            if (nueva_cabeza in self.snake or
                cabeza_x < 0 or cabeza_x >= self.ancho or
                cabeza_y < 0 or cabeza_y >= self.alto):
                os.system("cls")
                print("¡Game Over!")
                print(f"Puntaje final: {self.puntaje}")
                time.sleep(2)
                sys.exit(0)

            self.snake.insert(0, nueva_cabeza)

            # Si come la fruta
            if self.fruta and self.fruta["pos"] == nueva_cabeza:
                puntos = self.fruta.get("puntos", 10)
                incremento = self.fruta.get("incremento", 1)
                self.puntaje += puntos
                for _ in range(abs(incremento)):
                    # añadir copia del último segmento
                    self.snake.append(self.snake[-1])
                self.generar_fruta()

                # Reproducir sonido de comer si está disponible
                try:
                    if self.master.sonido_snake:
                        self.master.sonido_snake.play()
                except Exception:
                    pass
            else:
                self.snake.pop()

        def generar_fruta(self):
            if not self.comidas:
                self.comidas = [{"nombre": "normal", "puntos": 10, "incremento": 1}]
            fruta_tipo = random.choice(self.comidas)
            while True:
                pos = (random.randint(0, self.ancho - 1), random.randint(0, self.alto - 1))
                if pos not in self.snake:
                    break
            fruta_instancia = dict(fruta_tipo)
            fruta_instancia["tipo"] = fruta_tipo["nombre"]
            fruta_instancia["pos"] = pos
            self.fruta = fruta_instancia

        def run(self):
            os.system("cls")
            print("Iniciando Snake... Presiona Q para salir.")
            time.sleep(1)
            while True:
                tecla = self.leer_tecla()
                if tecla == "q":
                    print("Juego terminado por el usuario.")
                    break
                if tecla:
                    self.actualizar_direccion(tecla)
                self.mover_snake()
                self.mostrar_tablero()
                time.sleep(1 / self.velocidad)

    # =============================
    #  MENU PRINCIPAL / EJECUCIÓN
    # =============================
    def start(self):
        # Menú simple en consola igual que el original pero con opción para sonar
        while True:
            os.system("cls" if os.name == "nt" else "clear")
            print("🎮 Selecciona el juego que quieres ejecutar:")
            print("1. Tetris")
            print("2. Snake")
            print("3. Salir")
            opcion = input("Opción: ").strip()
            if opcion == "1":
                # buscar archivo de config por defecto
                cfg = "config_tetris.ast"
                if not os.path.exists(cfg):
                    print(f"No se encontró {cfg}. Creando configuración por defecto...")
                    default = {
                        "nombre_juego": "Tetris",
                        "ancho": 8,
                        "alto": 12,
                        "velocidad": 0.5
                    }
                    with open(cfg, "w", encoding="utf-8") as f:
                        json.dump(default, f, ensure_ascii=False, indent=2)
                    time.sleep(1)
                # ejecutar runtime
                try:
                    self.run_runtime_from_config(cfg)
                except KeyboardInterrupt:
                    print("Interrupción por teclado. Volviendo al menú.")
                    time.sleep(1)
            elif opcion == "2":
                cfg = "config_snake.ast"
                if not os.path.exists(cfg):
                    print(f"No se encontró {cfg}. Creando configuración por defecto...")
                    default = {
                        "nombre_juego": "Snake",
                        "ancho": 40,
                        "alto": 30,
                        "velocidad": 5,
                        "longitud_inicial": 3,
                        "comidas": [{"nombre": "normal", "puntos": 10, "incremento": 1}]
                    }
                    with open(cfg, "w", encoding="utf-8") as f:
                        json.dump(default, f, ensure_ascii=False, indent=2)
                    time.sleep(1)
                try:
                    self.run_runtime_from_config(cfg)
                except KeyboardInterrupt:
                    print("Interrupción por teclado. Volviendo al menú.")
                    time.sleep(1)
            elif opcion == "3":
                print("Saliendo...")
                break
            else:
                print("Opción no válida. Intenta de nuevo.")
                time.sleep(1)


# =============================
#  EJECUCIÓN DIRECTA
# =============================
if __name__ == "__main__":
    game = MasterGame()
    game.start()
