import os
import sys
import time
import random
import json
from colorama import init, Fore, Style


# ==============================
#  DETECCIÓN DE TECLAS (Windows/Linux)
# ==============================
try:
    import msvcrt
    def leer_tecla():
        if msvcrt.kbhit():
            return msvcrt.getch().decode("latin-1")
        return None
except ImportError:
    import termios, tty, select
    def leer_tecla():
        dr, dw, de = select.select([sys.stdin], [], [], 0)
        if dr:
            return sys.stdin.read(1)
        return None


# ==============================
#  CLASE BASE DE JUEGO
# ==============================
class BaseGame:
    def __init__(self, config):
        self.config = config

    def run(self):
        raise NotImplementedError


# ==============================
#  MOTOR DE JUEGO GENERAL
# ==============================
class GameRuntime:
    def __init__(self, config_file):
        if not os.path.exists(config_file):
            print(f"No se encontró el archivo: {config_file}")
            sys.exit(1)

        with open(config_file, "r", encoding="utf-8") as f:
            self.config = json.load(f)

        nombre = self.config.get("nombre_juego", "").lower()

        if "tetris" in nombre:
            self.juego = TetrisGame(self.config)
        elif "snake" in nombre:
            self.juego = SnakeGame(self.config)
        else:
            print("No se reconoce el tipo de juego en la configuración.")
            sys.exit(1)

    def run(self):
        self.juego.run()


# ==============================
#  IMPLEMENTACIÓN DEL TETRIS
# ==============================
class TetrisGame(BaseGame):
    def __init__(self, config):
        super().__init__(config)
        self.ancho = config.get("ancho", 8)
        self.alto = config.get("alto", 12)
        self.velocidad = config.get("velocidad", 0.5)
        self.puntaje = 0
        self.poder_usado = False
        self.juego_activo = True

        # Colores disponibles para las piezas
        self.colores = [Fore.RED, Fore.GREEN, Fore.YELLOW, Fore.CYAN, Fore.MAGENTA, Fore.BLUE, Fore.LIGHTWHITE_EX]

        # Figuras Tetris con sus colores
        self.figuras = [
            ([[ "█", "█" ],
              [ "█", "█" ]], Fore.YELLOW),  # Cuadrado (O)

            ([[ "█" ],
              [ "█" ],
              [ "█" ],
              [ "█" ]], Fore.CYAN),  # Línea (I)

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
            os.system("mode con: cols=80 lines=25")

    # ------------------------------
    # CREAR NUEVA PIEZA
    # ------------------------------
    def nueva_pieza(self):
        figura, color = random.choice(self.figuras)
        self.pieza = figura
        self.color_pieza = color
        self.pieza_y = 0
        self.pieza_x = random.randint(0, self.ancho - len(self.pieza[0]))

    # ------------------------------
    # DIBUJAR TABLERO
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
    # MOVER PIEZA
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
    # FIJAR PIEZA
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
    # LIMPIAR FILAS
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
    # ROTAR PIEZA
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
    # PODER ESPECIAL
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
    # BUCLE PRINCIPAL
    # ------------------------------
    def run(self):
        print(Fore.CYAN + "Iniciando Tetris... Presiona 0 para salir.")
        time.sleep(1)

        while self.juego_activo:
            tecla = leer_tecla()
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

            # Caída automática
            self.mover_pieza(0, 1)
            self.mostrar_tablero()
            time.sleep(self.velocidad)


# ==============================
#  IMPLEMENTACIÓN DEL SNAKE
# ==============================
class SnakeGame(BaseGame): 
    
    # Códigos de colores ANSI
    COLOR_ROJO = "\033[91m"
    COLOR_VERDE = "\033[92m"
    COLOR_RESET = "\033[0m"

    def __init__(self, config):
        super().__init__(config)
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
        self.snake = [(self.ancho // 2, self.alto // 2)]
        self.direccion = "derecha"
        self.puntaje = 0
        self.fruta = None
        
        # Truco para habilitar colores ANSI en la consola de Windows moderna
        os.system("") 
        
        self.generar_fruta()
        os.system("mode con: cols=80 lines=30")

    def mostrar_tablero(self):
        # Mueve el cursor al inicio en lugar de borrar todo (cls) para evitar parpadeo
        # Si ves caracteres raros, cambia esto de nuevo a os.system("cls")
        print("\033[H", end="") 
        
        print(f"{self.config.get('nombre_juego', 'Snake')} | Puntaje: {self.puntaje}")
        print("╔" + "═" * self.ancho + "╗")
        
        for y in range(self.alto):
            fila = ""
            for x in range(self.ancho):
                if (x, y) in self.snake:
                    # AQUI SE PONE LA SERPIENTE VERDE
                    fila += f"{self.COLOR_VERDE}O{self.COLOR_RESET}"
                elif self.fruta and self.fruta["pos"] == (x, y):
                    # AQUI SE PONE LA FRUTA ROJA O BONUS
                    caracter = "+" if self.fruta["tipo"] == "bonus" else "*"
                    fila += f"{self.COLOR_ROJO}{caracter}{self.COLOR_RESET}"
                else:
                    fila += " "
            print("║" + fila + "║")
        print("╚" + "═" * self.ancho + "╝")
        print("Usa W, A, S, D para moverte. Presiona Q para salir.")

    def leer_tecla(self):
        if msvcrt.kbhit():
            tecla = msvcrt.getch()
            try:
                t = tecla.decode("latin-1").lower()
                if t in ["w", "a", "s", "d", "q"]:
                    return t
            except:
                if tecla == b'\xe0':
                    k = msvcrt.getch()
                    if k == b'H': return "w"
                    elif k == b'P': return "s"
                    elif k == b'K': return "a"
                    elif k == b'M': return "d"
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
        
        if self.fruta and self.fruta["pos"] == nueva_cabeza:
            puntos = self.fruta.get("puntos", 10)
            incremento = self.fruta.get("incremento", 1)
            self.puntaje += puntos
            for _ in range(abs(incremento)):
                self.snake.append(self.snake[-1])
            self.generar_fruta()
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


# ==============================
#  EJECUCIÓN PRINCIPAL
# ==============================
if __name__ == "__main__":
    print("🎮 Selecciona el juego que quieres ejecutar:")
    print("1. Tetris")
    print("2. Snake")

    opcion = input("Opción: ")

    if opcion == "1":
        runtime = GameRuntime("config_tetris.ast")
    elif opcion == "2":
        runtime = GameRuntime("config_snake.ast")
    else:
        print("Opción no válida. Saliendo...")
        sys.exit(0)

    runtime.run()