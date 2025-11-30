Tetris Galáctico es una versión extendida y temática del clásico Tetris,
donde los bloques son fragmentos cósmicos, meteoritos y satélites
que caen sobre un tablero espacial. El jugador debe alinearlos
para evitar el colapso energético del universo.

Desarrollado por:

Iván Andrés Gómez

Jesús Casadiegos

Implementado en Python, con un motor de juego propio que gestiona
la lógica, la renderización en consola y la lectura de teclas en tiempo real.

El juego utiliza un sistema de configuración externo (config_tetris.ast)
inspirado en lenguajes de dominio específico (DSL) y versiones en Prolog,
permitiendo definir reglas, controles y fragmentos cósmicos de forma modular.

                 CÓMO JUGAR

Abre una terminal en la carpeta principal del proyecto.

Ejecuta el archivo principal:

python runtime.py

Asegúrate de tener el archivo de configuración
config_tetris.ast en la misma carpeta.

Durante la partida, controla la caída de los fragmentos cósmicos
usando las siguientes teclas:

1 → Mover izquierda
2 → Bajar
3 → Mover derecha
4 → Descanso cósmico (pausa de 7 segundos)
5 → Impulso (caída rápida)
6 → Activar poder especial
7 → Rotar figura actual
0 → Finalizar juego

Para salir, presiona 0 o cierra la ventana de la terminal.

            MECÁNICAS Y REGLAS

Alineación perfecta: cuando una fila se completa, se desintegra
y otorga puntos cósmicos al jugador.

Rotación de figuras: con la tecla 7, puedes rotar la figura
actual para mejorar su encaje antes del impacto.

Descanso cósmico: con la tecla 4, el jugador detiene el tiempo
durante 7 segundos, permitiendo planear su próxima jugada.

Poder especial: puede usarse una vez al alcanzar 1000 puntos.
Limpia completamente el tablero.

Game Over: ocurre cuando los fragmentos alcanzan la parte superior
del tablero o se acumulan 10,000 gemas espaciales.

           CONFIGURACIÓN DEL JUEGO

Toda la lógica y los parámetros se definen en el archivo:

  config_tetris.ast

Este archivo contiene:

Nombre y versión del juego.

Dimensiones del tablero (ancho y alto).

Velocidad de caída inicial (energia_descendente).

Reglas especiales para alineación, meteoritos y niveles.

Controles configurables.

Definición de todos los fragmentos cósmicos:
(satelite, cubo, triángulo, serpiente, rayo, meteorito).

También se incluye una versión alternativa en formato Prolog,
que representa las mismas reglas como base de conocimiento lógico.

            DETALLES TÉCNICOS

Motor principal: GameRuntime
Juego base: BaseGame
Implementación: TetrisGame