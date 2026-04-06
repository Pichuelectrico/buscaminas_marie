from PIL import Image, ImageDraw, ImageFont
import random

# ─── CONFIG ───────────────────────────────────────────────────
BOARD_SIZE = 16
CELL_SIZE = 32
IMG_SIZE = BOARD_SIZE * CELL_SIZE
MINE_COUNT =22

# Direcciones base lógicas
BASE_REAL = 0x120
BASE_MINES = 0x220
BASE_COLORS = 0x320
BASE_VISIBLE = 0x420
BASE_NEIGHBORS = 0x520

# ─── COLORES RGB565 ───────────────────────────────────────────
COLOR_MAP = {
    "HIDDEN": {"hex": "39E7", "rgb": (68, 68, 68)},   # Gris oscuro
    "FLAG": {"hex": "FFE0", "rgb": (255, 255, 0)},    # Amarillo
    "MINE": {"hex": "0000", "rgb": (0, 0, 0)},        # Negro
    0: {"hex": "D6D6", "rgb": (211, 211, 211)},       # Gris claro
    1: {"hex": "001F", "rgb": (0, 0, 255)},           # Azul
    2: {"hex": "0300", "rgb": (0, 128, 0)},           # Verde
    3: {"hex": "7800", "rgb": (255, 0, 0)},           # Rojo
    4: {"hex": "001F", "rgb": (0, 0, 139)},           # Azul oscuro
    5: {"hex": "CA70", "rgb": (139, 0, 0)},           # Marrón
    6: {"hex": "0210", "rgb": (0, 255, 255)},         # Cian
    7: {"hex": "D69A", "rgb": (238, 130, 238)},       # Morado
    8: {"hex": "FFFF", "rgb": (255, 255, 255)},       # Blanco
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


# ─── TABLA DE VECINOS ─────────────────────────────────────────
def get_neighbors(index):
    r = index // BOARD_SIZE
    c = index % BOARD_SIZE
    neighbors = []

    for dr in [-1, 0, 1]:
        for dc in [-1, 0, 1]:
            if dr == 0 and dc == 0:
                continue

            nr = r + dr
            nc = c + dc

            if 0 <= nr < BOARD_SIZE and 0 <= nc < BOARD_SIZE:
                neighbors.append(nr * BOARD_SIZE + nc)

    while len(neighbors) < 8:
        neighbors.append(-1)

    return neighbors


# ─── MATRIZ LEGIBLE ───────────────────────────────────────────
def save_board_matrix(board, filename="tablero_matriz.txt"):
    lines = []
    lines.append("TABLERO REAL (16x16)")
    lines.append("'*' = mina")
    lines.append("")

    for row in board:
        line = " ".join(f"{'*' if v == -1 else v:>2}" for v in row)
        lines.append(line)

    with open(filename, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))


# ─── IMAGEN ───────────────────────────────────────────────────
def save_board_image(board, filename="tablero_real.png"):
    axis_margin = 28
    font = ImageFont.load_default()

    img = Image.new(
        "RGB",
        (IMG_SIZE + axis_margin, IMG_SIZE + axis_margin),
        (255, 255, 255)
    )
    draw = ImageDraw.Draw(img)

    # Etiquetas de columnas (0..15)
    for c in range(BOARD_SIZE):
        x = axis_margin + c * CELL_SIZE + CELL_SIZE // 2 - 4
        draw.text((x, 8), str(c), fill=(0, 0, 0), font=font)

    # Etiquetas de filas (0..15)
    for r in range(BOARD_SIZE):
        y = axis_margin + r * CELL_SIZE + CELL_SIZE // 2 - 4
        draw.text((8, y), str(r), fill=(0, 0, 0), font=font)

    for r in range(BOARD_SIZE):
        for c in range(BOARD_SIZE):
            val = board[r][c]
            color = COLOR_MAP["MINE"]["rgb"] if val == -1 else COLOR_MAP[val]["rgb"]

            x0 = axis_margin + c * CELL_SIZE
            y0 = axis_margin + r * CELL_SIZE
            x1 = axis_margin + (c + 1) * CELL_SIZE
            y1 = axis_margin + (r + 1) * CELL_SIZE

            draw.rectangle([x0, y0, x1, y1], fill=color, outline=(0, 0, 0))

            label = "*" if val == -1 else (str(val) if val > 0 else "")
            if label:
                text_color = (255, 255, 255) if color[0] + color[1] + color[2] < 300 else (0, 0, 0)
                tx = x0 + CELL_SIZE // 2 - 4
                ty = y0 + CELL_SIZE // 2 - 6
                draw.text((tx, ty), label, fill=text_color, font=font)

    img.save(filename)


# ─── BLOQUE MARIE LISTO PARA PEGAR ────────────────────────────
def build_marie_block(board):
    marie = ""
    neighbors_table = [get_neighbors(i) for i in range(BOARD_SIZE**2)]

    # 0x100 - 0x1FF → tablero real
    marie += "/ --- TABLERO REAL (0x100) ---\n"
    for r in range(BOARD_SIZE):
        for c in range(BOARD_SIZE):
            val = board[r][c]
            # En MARIE no usamos -1, usamos 9 como mina
            marie_val = 9 if val == -1 else val
            marie += f"DEC {marie_val}\n"

    # 0x200 - 0x2FF → minas
    marie += "/ --- MINAS (0x200) ---\n"
    for r in range(BOARD_SIZE):
        for c in range(BOARD_SIZE):
            marie += f"DEC {1 if board[r][c] == -1 else 0}\n"

    # 0x300 - 0x3FF → colores finales
    marie += "/ --- COLORES FINALES (0x300) ---\n"
    for r in range(BOARD_SIZE):
        for c in range(BOARD_SIZE):
            val = board[r][c]
            h = COLOR_MAP["MINE"]["hex"] if val == -1 else COLOR_MAP[val]["hex"]
            marie += f"HEX {h}\n"

    # 0x400 - 0x4FF → visible
    marie += "/ --- ESTADO VISIBLE (0x400) ---\n"
    for _ in range(BOARD_SIZE * BOARD_SIZE):
        marie += "DEC 0\n"

    # 0x500 en adelante → vecinos
    marie += "/ --- TABLA DE VECINOS (0x500) ---\n"
    for nlist in neighbors_table:
        for v in nlist:
            marie += f"DEC {v}\n"

    return marie


# ─── MAIN ─────────────────────────────────────────────────────
def main():
    board = build_board()

    # 1. Imagen
    save_board_image(board, "tablero_real.png")

    # 2. Matriz legible
    save_board_matrix(board, "tablero_matriz.txt")

    # 3. Bloque listo para pegar en MARIE
    marie_block = build_marie_block(board)
    with open("salida_proyecto.txt", "w", encoding="utf-8") as f:
        f.write(marie_block)

    print("Generados:")
    print("- tablero_real.png")
    print("- tablero_matriz.txt")
    print("- salida_proyecto.txt")


if __name__ == "__main__":
    main()