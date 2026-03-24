from PIL import Image, ImageDraw, ImageFont
import random

# ─── CONFIG ───────────────────────────────────────────────────
BOARD_SIZE = 16
CELL_SIZE = 32
IMG_SIZE = BOARD_SIZE * CELL_SIZE
MINE_COUNT = 3

# Direcciones base (sin múltiples ORG)
BASE_REAL = 0x100
BASE_MINES = 0x200
BASE_COLORS = 0x300

# ─── COLORES RGB565 ───────────────────────────────────────────
COLOR_MAP = {
    "HIDDEN": {"hex": "4208", "rgb": (68, 68, 68)},  # Gris oscuro
    "FLAG": {"hex": "FFE0", "rgb": (255, 255, 0)},  # Amarillo
    "MINE": {"hex": "0000", "rgb": (0, 0, 0)},  # Negro
    0: {"hex": "D6D6", "rgb": (211, 211, 211)},  # Gris claro
    1: {"hex": "07DF", "rgb": (0, 0, 255)},  # Azul
    2: {"hex": "0300", "rgb": (0, 128, 0)},  # Verde
    3: {"hex": "7800", "rgb": (255, 0, 0)},  # Rojo
    4: {"hex": "001F", "rgb": (0, 0, 139)},  # Azul oscuro
    5: {"hex": "CA70", "rgb": (139, 0, 0)},  # Marrón
    6: {"hex": "0210", "rgb": (0, 255, 255)},  # Cian
    7: {"hex": "D69A", "rgb": (238, 130, 238)},  # Morado
    8: {"hex": "FFFF", "rgb": (255, 255, 255)},  # Blanco
}


# ─── CONSTRUIR TABLERO ────────────────────────────────────────
def build_board():
    board = [[0] * BOARD_SIZE for _ in range(BOARD_SIZE)]
    mines = {
        (p // BOARD_SIZE, p % BOARD_SIZE)
        for p in random.sample(range(BOARD_SIZE**2), MINE_COUNT)
    }
    for r, c in mines:
        board[r][c] = -1
    for r in range(BOARD_SIZE):
        for c in range(BOARD_SIZE):
            if board[r][c] == -1:
                continue
            board[r][c] = sum(
                1
                for dr in [-1, 0, 1]
                for dc in [-1, 0, 1]
                if (dr or dc)
                and 0 <= r + dr < BOARD_SIZE
                and 0 <= c + dc < BOARD_SIZE
                and board[r + dr][c + dc] == -1
            )
    return board


board = build_board()

# ─── 1. IMAGEN ────────────────────────────────────────────────
AXIS_MARGIN = 28
font = ImageFont.load_default()

img = Image.new(
    "RGB", (IMG_SIZE + AXIS_MARGIN, IMG_SIZE + AXIS_MARGIN), (255, 255, 255)
)
draw = ImageDraw.Draw(img)

# Etiquetas de columnas (0..15)
for c in range(BOARD_SIZE):
    x = AXIS_MARGIN + c * CELL_SIZE + CELL_SIZE // 2 - 4
    draw.text((x, 8), str(c), fill=(0, 0, 0), font=font)

# Etiquetas de filas (0..15)
for r in range(BOARD_SIZE):
    y = AXIS_MARGIN + r * CELL_SIZE + CELL_SIZE // 2 - 4
    draw.text((8, y), str(r), fill=(0, 0, 0), font=font)

for r in range(BOARD_SIZE):
    for c in range(BOARD_SIZE):
        val = board[r][c]
        color = COLOR_MAP["MINE"]["rgb"] if val == -1 else COLOR_MAP[val]["rgb"]
        draw.rectangle(
            [
                AXIS_MARGIN + c * CELL_SIZE,
                AXIS_MARGIN + r * CELL_SIZE,
                AXIS_MARGIN + (c + 1) * CELL_SIZE,
                AXIS_MARGIN + (r + 1) * CELL_SIZE,
            ],
            fill=color,
            outline=(0, 0, 0),
        )
img.save("tablero_real.png")

# ─── 2. BLOQUE C++ ────────────────────────────────────────────
cpp_out = "// Pegar en loadBoard() del C++\n"
cpp_out += "int real[16][16] = {\n"
for row in board:
    cpp_out += "    { " + ", ".join(f"{v:>3}" for v in row) + " },\n"
cpp_out += "};\n"

# ─── 3. BLOQUE MARIE (UN SOLO ORG 100) ───────────────────────
marie = ""

# ── 3a. ORG 100: Tablero real (valores -1 a 8)
marie += "ORG 100\n"
for r in range(BOARD_SIZE):
    for c in range(BOARD_SIZE):
        val = board[r][c]
        # MARIE no acepta DEC negativo, mina = 9 como valor especial
        marie_val = 9 if val == -1 else val
        marie += f"DEC {marie_val}\n"

# ── 3b. Relleno hasta 0x200 (ya estamos en 0x200 exacto, 256 celdas después)
# 0x100 + 256 = 0x200, no necesita relleno

# ── 3c. Minas lineales (0x200 - 0x2FF)
marie += "/ --- MINAS (0x200) ---\n"
for r in range(BOARD_SIZE):
    for c in range(BOARD_SIZE):
        marie += f"DEC {1 if board[r][c] == -1 else 0}\n"

# ── 3d. Colores finales (0x300 - 0x3FF)
marie += "/ --- COLORES FINALES (0x300) ---\n"
for r in range(BOARD_SIZE):
    for c in range(BOARD_SIZE):
        val = board[r][c]
        h = COLOR_MAP["MINE"]["hex"] if val == -1 else COLOR_MAP[val]["hex"]
        marie += f"HEX {h}\n"

# ─── GUARDAR ──────────────────────────────────────────────────
with open("salida_proyecto.txt", "w", encoding="utf-8") as f:
    f.write("=== BLOQUE C++ ===\n")
    f.write(cpp_out + "\n")
    f.write("=== BLOQUE MARIE (pegar desde ORG 100) ===\n")
    f.write(marie + "\n")

print("Generados: tablero_real.png  |  salida_proyecto.txt")
