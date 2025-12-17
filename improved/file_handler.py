"""Утилиты для чтения и записи текстовых файлов."""

from __future__ import annotations

from pathlib import Path
from typing import List


def read_lines_from_file(path: str = "test.txt") -> List[str]:
    """Прочитать строки из файла.

    Args:
        path: Путь к файлу.

    Returns:
        Список строк (с символами перевода строки) либо пустой список,
        если файл не найден.
    """
    try:
        with Path(path).open("r", encoding="utf-8") as file:
            return file.readlines()
    except FileNotFoundError:
        return []


def append_line_to_file(line: str, path: str = "test.txt") -> None:
    """Добавить строку в конец файла.

    Args:
        line: Строка для записи.
        path: Путь к файлу.

    Notes:
        Если строка не заканчивается символом "\n", он добавляется
        автоматически.
    """
    to_write = line if line.endswith("\n") else f"{line}\n"
    with Path(path).open("a", encoding="utf-8") as file:
        file.write(to_write)
