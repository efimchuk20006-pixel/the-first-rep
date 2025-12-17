"""Точка входа CLI-программы (меню, ввод и вывод данных)."""

from __future__ import annotations

from typing import Callable, Dict, Optional

from file_handler import append_line_to_file, read_lines_from_file
from filters import parse_lesson


def show_raw_data(path: str = "test.txt") -> None:
    """Вывод сырых строк из файла."""
    lines = read_lines_from_file(path="improved/test.txt")
    if not lines:
        print(f"файл {path} пуст или не найден")
        return

    print(f"Сырые строки в {path}:")
    for i, line in enumerate(lines, 1):
        print(f"{i}: {line.rstrip()}")


def show_parsed_data(path: str = "test.txt") -> None:
    """Вывод распарсенных записей (с диагностикой ошибок)."""
    lines = read_lines_from_file(path="improved/test.txt")
    if not lines:
        print(f"файл {path} пуст или не найден")
        return

    print("Распарсенные записи:")
    for i, line in enumerate(lines, 1):
        try:
            lesson = parse_lesson(line)
            print(f"{i}: {lesson}")
        except ValueError as exc:
            print(f"{i}: ошибка парсинга: {exc}")


def main() -> None:
    """Главная функция с интерактивным меню."""
    menu = (
        "1) Внести данные",
            "2) Показать сырые данные (improved/test.txt)",
        "3) Показать распарсенные данные",
        "4) Выход",
    )

    actions: Dict[str, Dict[str, Optional[Callable[[], None]]]] = {
        "1": {"desc": "Внести данные", "func": None},
        "2": {"desc": "Показать сырые данные", "func": show_raw_data},
        "3": {"desc": "Показать распарсенные данные", "func": show_parsed_data},
        "4": {"desc": "Выход", "func": None},
    }

    while True:
        print("\n" + "=" * 50)
        print("МЕНЮ")
        print("=" * 50)
        for item in menu:
            print(item)

        choice = input("Выберите пункт: ").strip()

        if choice not in actions:
            print("Некорректный выбор")
            continue

        if choice == "1":
            print(
                "Введите строку в формате: учебное занятие гггг.мм.дд "
                '"аудитория" "фамилия и.е."'
            )
            line = input("Строка (или пусто для отмены): ").strip()
            if line:
                    append_line_to_file(line, path="improved/test.txt")
                    print("✓ Запись добавлена в improved/test.txt")
            else:
                print("✗ Отменено")
            continue

        if choice == "4":
            print("До свидания!")
            break

        func = actions[choice]["func"]
        if func is not None:
            func()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nПрограмма прервана пользователем")
