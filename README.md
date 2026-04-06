# Buscaminas en MARIE
Joshua Reinoso, Karina Dahik y Gabriel Cazares

Este proyecto es una implementación del clásico juego **Buscaminas** desarrollado para la arquitectura **MARIE (Machine Architecture that is Really Intuitive and Easy)**. Utiliza una matriz de 16x16 y un sistema de visualización basado en colores para representar el estado del tablero.

## 🚀 Cómo funciona el proyecto

El proyecto se divide en dos componentes principales:

1.  **Generador de Datos (Python):** El script `python_map_gen.py` genera la lógica del tablero (minas, números de proximidad y colores) y exporta estos datos en un formato compatible con MARIE (`salida_proyecto.txt`).
2.  **Lógica del Juego (MARIE Assembly):** El archivo `BombGame.mas` contiene el código fuente en ensamblador que gestiona la interacción del usuario, la revelación de celdas, el manejo de vecinos y las condiciones de victoria o derrota.

### Mecánica del Juego
- **Tablero:** Una cuadrícula de 16x16 (256 celdas).
- **Entrada:** El usuario ingresa una coordenada o índice de celda.
- **Procesamiento:** El programa verifica si la celda contiene una mina. Si no, calcula y muestra el número de minas adyacentes.
- **Recursividad:** Si una celda tiene 0 minas vecinas, el juego expande automáticamente las celdas vacías (basado en la tabla de vecinos generada).

---

## 🎨 Sistema de Colores y Tablero

El juego utiliza códigos hexadecimales **RGB565** para representar visualmente el estado del tablero en el simulador.

### Tabla de Referencia de Colores

| Estado / Valor | Representación Visual | Hexadecimal | Color (RGB) |
| :--- | :--- | :--- | :--- |
| **Oculto** | Celda no revelada | `4208` | Gris Oscuro |
| **Mina (*)** | Bomba detectada | `0000` | Negro |
| **0** | Vacío (Sin minas cerca) | `D6D6` | Gris Claro |
| **1** | 1 Mina cerca | `07DF` | Azul |
| **2** | 2 Minas cerca | `0300` | Verde |
| **3** | 3 Minas cerca | `7800` | Rojo |
| **4+** | 4 a 8 Minas cerca | Varios | Azul Oscuro, Marrón, etc. |
| **Bandera** | Marca de usuario | `FFE0` | Amarillo |

### Visualización del Tablero Real
![Tablero Real](img/tablero_real.png)
*Ejemplo del tablero generado donde se aprecian las minas (negro) y los números de proximidad (colores).*

---

## 🛠 Estructura de Memoria en MARIE

Para que el juego funcione, la memoria se organiza en bloques específicos:

-   **0x100 - 0x1FF:** Valores lógicos del tablero (0-8 para números, 9 para minas).
-   **0x200 - 0x2FF:** Mapa binario de minas (1 si hay mina, 0 si no).
-   **0x300 - 0x3FF:** Tabla de colores finales (HEX).
-   **0x400 - 0x4FF:** Estado de visibilidad (determina si la celda ya fue clickeada).
-   **0x500 en adelante:** Tabla de adyacencia (cada celda apunta a sus 8 vecinos posibles).

---

## 📋 Requisitos e Instalación

1.  Cargar el contenido de `salida_proyecto.txt` al final de tu código en el simulador de MARIE.
2.  Ensamblar y ejecutar el archivo `BombGame.mas` en https://marie.js.org/
3.  Utilizar el display del simulador para ver el progreso del juego.
