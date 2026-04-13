from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import random

# ─── CONFIG ───────────────────────────────────────────────────
BOARD_SIZE = 16
CELL_SIZE = 32
IMG_SIZE = BOARD_SIZE * CELL_SIZE
MINE_COUNT = 22

# ─── COLORES RGB565 ───────────────────────────────────────────
COLOR_MAP = {
    "HIDDEN": {"hex": "39E7", "rgb": (68, 68, 68)},
    "FLAG": {"hex": "FFE0", "rgb": (255, 255, 0)},
    "MINE": {"hex": "0000", "rgb": (0, 0, 0)},
    0: {"hex": "D6D6", "rgb": (211, 211, 211)},
    1: {"hex": "001F", "rgb": (0, 0, 255)},
    2: {"hex": "0300", "rgb": (0, 128, 0)},
    3: {"hex": "7800", "rgb": (255, 0, 0)},
    4: {"hex": "001F", "rgb": (0, 0, 139)},
    5: {"hex": "CA70", "rgb": (139, 0, 0)},
    6: {"hex": "0210", "rgb": (0, 255, 255)},
    7: {"hex": "D69A", "rgb": (238, 130, 238)},
    8: {"hex": "FFFF", "rgb": (255, 255, 255)},
}


# ─── CONSTRUIR TABLERO ────────────────────────────────────────
def build_board():
    board = [[0] * BOARD_SIZE for _ in range(BOARD_SIZE)]

    mines = {
        (p // BOARD_SIZE, p % BOARD_SIZE)
        for p in random.sample(range(BOARD_SIZE ** 2), MINE_COUNT)
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
def save_board_matrix(board, filename: Path):
    lines = []
    lines.append("TABLERO REAL (16x16)")
    lines.append("'*' = mina")
    lines.append("")

    for row in board:
        line = " ".join(f"{'*' if v == -1 else v:>2}" for v in row)
        lines.append(line)

    filename.write_text("\n".join(lines), encoding="utf-8")


# ─── IMAGEN ───────────────────────────────────────────────────
def save_board_image(board, filename: Path):
    axis_margin = 28
    font = ImageFont.load_default()

    img = Image.new(
        "RGB",
        (IMG_SIZE + axis_margin, IMG_SIZE + axis_margin),
        (255, 255, 255)
    )
    draw = ImageDraw.Draw(img)

    for c in range(BOARD_SIZE):
        x = axis_margin + c * CELL_SIZE + CELL_SIZE // 2 - 4
        draw.text((x, 8), str(c), fill=(0, 0, 0), font=font)

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
    neighbors_table = [get_neighbors(i) for i in range(BOARD_SIZE ** 2)]

    marie += "/ --- TABLERO REAL (0x120) ---\n"
    for r in range(BOARD_SIZE):
        for c in range(BOARD_SIZE):
            val = board[r][c]
            marie_val = 9 if val == -1 else val
            marie += f"DEC {marie_val}\n"

    marie += "/ --- MINAS (0x220) ---\n"
    for r in range(BOARD_SIZE):
        for c in range(BOARD_SIZE):
            marie += f"DEC {1 if board[r][c] == -1 else 0}\n"

    marie += "/ --- COLORES FINALES (0x320) ---\n"
    for r in range(BOARD_SIZE):
        for c in range(BOARD_SIZE):
            val = board[r][c]
            h = COLOR_MAP["MINE"]["hex"] if val == -1 else COLOR_MAP[val]["hex"]
            marie += f"HEX {h}\n"

    marie += "/ --- ESTADO VISIBLE (0x420) ---\n"
    for _ in range(BOARD_SIZE * BOARD_SIZE):
        marie += "DEC 0\n"

    marie += "/ --- TABLA DE VECINOS (0x520) ---\n"
    for nlist in neighbors_table:
        for v in nlist:
            marie += f"DEC {v}\n"

    return marie


# ─── CONSTRUIR juego.mas FINAL ────────────────────────────────
def build_game_file(base_dir: Path, salida_content: str):
    bombgame_path = base_dir / "BombGame.mas"
    output_path = base_dir / "juego.mas"

    bombgame_content = bombgame_path.read_text(encoding="utf-8")
    bombgame_content = bombgame_content.replace(
        "__MINE_TOTAL__",
        str(MINE_COUNT)
    )

    with output_path.open("w", encoding="utf-8", newline="") as output_file:
        output_file.write(bombgame_content)
        if not bombgame_content.endswith("\n"):
            output_file.write("\n")
        output_file.write(salida_content)


# ─── MAIN ─────────────────────────────────────────────────────
def main():
    base_dir = Path(__file__).resolve().parent

    board = build_board()

    image_path = base_dir / "tablero_real.png"
    matrix_path = base_dir / "tablero_matriz.txt"
    salida_path = base_dir / "salida_proyecto.txt"

    save_board_image(board, image_path)
    save_board_matrix(board, matrix_path)

    marie_block = build_marie_block(board)
    salida_path.write_text(marie_block, encoding="utf-8")

    build_game_file(base_dir, marie_block)

    print("Generados:")
    print("- tablero_real.png")
    print("- tablero_matriz.txt")
    print("- salida_proyecto.txt")
    print("- juego.mas")


if __name__ == "__main__":
    main()