from file_handler import read_lines_from_file, append_line_to_file
from filters import parse_lesson
def show_raw_data(path: str = "test.txt") -> None:
    """Вывод сырых строк из файла."""
    lines = read_lines_from_file(path)
    if not lines:
        print(f"файл {path} пуст или не найден")
        return
    print(f"Сырые строки в {path}:")
    for i, l in enumerate(lines, 1):
        print(f"{i}: {l.rstrip()}")
def show_parsed_data(path: str = "test.txt") -> None:
    """Вывод распарсенных записей."""
    lines = read_lines_from_file(path)
    if not lines:
        print(f"файл {path} пуст или не найден")
        return
    print("Распарсенные записи:")
    for i, l in enumerate(lines, 1):
        try:
            lesson = parse_lesson(l)
            print(f"{i}: {lesson}")
        except Exception as e:
            print(f"{i}: ошибка парсинга: {e}")
def main():
    """Главная функция с интерактивным меню."""
    menu = (
        "1) Внести данные",
        "2) Показать сырые данные (test.txt)",
        "3) Показать распарсенные данные",
        "4) Выход",
    )
    map = {
        "1": {"desc": "Внести данные", "func": None},
        "2": {"desc": "Показать сырые данные", "func": show_raw_data},
        "3": {"desc": "Показать распарсенные данные", "func": show_parsed_data},
        "4": {"desc": "Выход", "func": None},
    }
    while True:
        print("\n" + "="*50)
        print("МЕНЮ")
        print("="*50)
        for option in menu:
            print(option)
        print("="*50)
        choice = input("Выберите опцию (1-4): ").strip()
        if choice not in map:
            print("✗ Неверный выбор. Введите 1, 2, 3 или 4.")
            continue
        if choice == "1":
            print('Введите строку в формате: учебное занятие гггг.мм.дд "аудитория" "фамилия и.е."')
            line = input("Строка (или пусто для отмены): ").strip()
            if line:
                append_line_to_file(line)
                print("✓ Запись добавлена в test.txt")
            else:
                print("✗ Отменено")
        elif choice == "4":
            print("До свидания!")
            break
        else:
            func = map[choice]["func"]
            if func:
                func()
if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print('\nПрограмма прервана пользователем')
