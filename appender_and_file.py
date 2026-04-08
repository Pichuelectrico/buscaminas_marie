from pathlib import Path


def build_game_file() -> None:
    base_dir = Path(__file__).resolve().parent
    bombgame_path = base_dir / "BombGame.mas"
    salida_path = base_dir / "salida_proyecto.txt"
    output_path = base_dir / "juego.mas"

    bombgame_content = bombgame_path.read_text(encoding="utf-8")
    salida_content = salida_path.read_text(encoding="utf-8")

    with output_path.open("w", encoding="utf-8", newline="") as output_file:
        output_file.write(bombgame_content)
        if not bombgame_content.endswith("\n"):
            output_file.write("\n")
        output_file.write(salida_content)


if __name__ == "__main__":
    build_game_file()
