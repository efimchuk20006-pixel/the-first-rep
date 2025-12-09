from typing import List


def read_lines_from_file(path: str = "test.txt") -> List[str]:
    """Чтение строк из файла."""
    try:
        with open(path, "r", encoding="utf-8") as f:
            return f.readlines()
    except FileNotFoundError:
        return []


def append_line_to_file(line: str, path: str = "test.txt") -> None:
    """Добавление строки в файл."""
    with open(path, "a", encoding="utf-8") as f:
        if not line.endswith("\n"):
            line = line + "\n"
        f.write(line)
