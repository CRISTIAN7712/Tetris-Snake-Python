# 🕹️ MasterGame -- Tetris & Snake

Dos juegos clásicos integrados en una misma aplicación gráfica hecha con
**Tkinter** y **Pygame**.\
Incluye sonidos, interfaz unificada, controles intuitivos y un modo
POWER especial para Tetris.

## 📸 Características principales

### 🎮 Tetris

-   Controles por teclado numérico (1--7)
-   Caída suave y caída instantánea
-   Rotación de piezas
-   Sistema de puntaje
-   **POWER** especial (tecla 6):
    -   Con 1000 puntos → limpia el tablero
    -   Si no puedes activarlo → mensaje de advertencia + efecto visual

### 🐍 Snake

-   Movimiento clásico con **WASD** o **Flechas**
-   Sonido al comer
-   Puntaje visible
-   Salida rápida con `Q`

### 🔊 Sonidos

-   Sonido de teclado
-   Sonido al comer
-   Integración con pygame

### 🖥️ Interfaz (Tkinter)

-   Menú de selección
-   Canvas dedicado
-   Mensajes informativos
-   Adaptación al tamaño de ventana

## 🚀 Instalación

### 1. Clonar proyecto

    git clone https://github.com/CRISTIAN7712/Tetris-Snake-Python.git
    cd mastergame

### 2. Entorno virtual

    python -m venv venv

### 3. Instalar dependencias

    pip install -r requirements.txt

### 4. Ejecutar

    python main.py

## 📦 Requirements

    pygame>=2.5
    pillow>=10.0

## 🎮 Controles

### Tetris

  Acción      Tecla
  ----------- -------
  Izquierda   1
  Abajo       2
  Derecha     3
  Pausa       4
  Drop        5
  POWER       6
  Rotar       7
  Salir       0

### Snake

  Acción      Tecla
  ----------- -------
  Arriba      W / ↑
  Abajo       S / ↓
  Izquierda   A / ←
  Derecha     D / →
  Salir       Q

## 🔊 Sonidos esperados

    keyboard.wav
    eating.wav

## 📁 Estructura

    mastergame/
    │── main.py
    │── requirements.txt
    │── README.md
    │── keyboard.wav
    │── eating.wav

## 🧩 Compatibilidad

-   Python 3.9+
-   Windows / Linux / Mac

---

## 👨‍⚕️ Autor

Desarrollado por **Ing. Cristian Díaz**  
Diseño adaptado y optimizado para propósitos médicos y clínicas.

---

<p align="center">
  <img width="300" src="https://i.imgur.com/YYf2LgH.png" alt="Logo del autor">
</p>
