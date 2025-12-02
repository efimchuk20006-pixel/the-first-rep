from datetime import datetime, date
import re
from typing import List, Dict


class Lesson:
    """
    класс "учебное занятие".
    свойства:
        date-дата проведения занятия (тип date)
        room-название аудитории (строка)
        teacher-имя преподавателя (строка)
    """
    def __init__(self, date_: date, room: str, teacher: str):
        self.date = date_
        self.room = room
        self.teacher = teacher

    def __str__(self):
        # date выводится в формате гггг-мм-дд по умолчанию
        return f"Учебное занятие: дата={self.date}, аудитория={self.room}, преподаватель={self.teacher}"


class LessonParser:
    """Класс для разбора строки и создания объекта Lesson."""

    @staticmethod
    def parse_date_from_text(s: str) -> date:
        """Разбор даты из текста."""
        # популярные форматы: yyyy.mm.dd, yyyy-mm-dd, dd.mm.yyyy, dd/mm/yyyy, yyyy/mm/dd
        m = re.search(r"(\d{4})[.\-/](\d{1,2})[.\-/](\d{1,2})", s)
        if m:
            y, mo, d = m.groups()
            try:
                return datetime(int(y), int(mo), int(d)).date()
            except ValueError:
                pass

        # день-месяц-год
        m = re.search(r"(\d{1,2})[.\-/](\d{1,2})[.\-/](\d{4})", s)
        if m:
            d, mo, y = m.groups()
            try:
                return datetime(int(y), int(mo), int(d)).date()
            except ValueError:
                pass

        # неполные: yyyymmdd
        m = re.search(r"\b(\d{4})(\d{2})(\d{2})\b", s)
        if m:
            y, mo, d = m.groups()
            try:
                return datetime(int(y), int(mo), int(d)).date()
            except ValueError:
                pass

        raise ValueError(f"не удалось распознать дату в строке: {s}")

    @staticmethod
    def parse_room_from_text(s: str) -> str:
        """Разбор номера аудитории из текста."""
        # в кавычках: "а-104"
        m = re.search(r'["\']([^"\']+)["\']', s)
        if m:
            cand = m.group(1)
            if re.search(r"\d", cand):
                return cand

        # типичные обозначения: a-104, а-104
        m = re.search(r"\b[АA]-?\d{1,4}\b", s, flags=re.IGNORECASE)
        if m:
            return m.group(0)

        # по ключевому слову 'аудитория'
        m = re.search(r"(?:аудитори(?:я|и)|auditorium|room)[:\s\"]+([A-Za-zА-Яа-я0-9\-]+)", s, flags=re.IGNORECASE)
        if m:
            return m.group(1)

        raise ValueError(f"не удалось распознать аудиторию в строке: {s}")

    @staticmethod
    def normalize_initials(a: str) -> str:
        """Привести инициалы к формату и.е."""
        chars = re.findall(r"([A-Za-zА-Яа-яЁё])", a)
        if len(chars) >= 2:
            return f"{chars[0].upper()}.{chars[1].upper()}."
        return a

    @staticmethod
    def try_parse_segment(seg: str):
        """Попытка разбора сегмента как имени преподавателя."""
        patterns = [
            r"([А-ЯЁа-яё]+)\s+([А-ЯЁа-яё])\.?\s*([А-ЯЁа-яё])\.?",
            r"([А-ЯЁа-яё]+)\s+([А-ЯЁа-яё]\.[А-ЯЁа-яё]\.)",
            r"([А-ЯЁа-яё]\.?\s*[А-ЯЁа-яё]\.?)\s*([А-ЯЁа-яё]+)",
            r"([A-Z][a-z]+)\s+([A-Z])\.?\s*([A-Z])\.?",
        ]
        for pat in patterns:
            m = re.search(pat, seg, flags=re.IGNORECASE)
            if not m:
                continue
            groups = m.groups()
            if len(groups) == 3:
                fam, a1, a2 = groups
                return f"{fam.strip().capitalize()} {a1.upper()}.{a2.upper()}."
            if len(groups) == 2:
                g1, g2 = groups
                if "." in g2:
                    fam, initials = g1, g2
                    return f"{fam.strip().capitalize()} {LessonParser.normalize_initials(initials)}"
                else:
                    initials, fam = g1, g2
                    return f"{fam.strip().capitalize()} {LessonParser.normalize_initials(initials)}"
        m = re.search(r"\b([А-ЯЁа-яё])\.?\s*([А-ЯЁа-яё])\.?\b", seg, flags=re.IGNORECASE)
        if m:
            a1, a2 = m.groups()
            return f"{a1.upper()}.{a2.upper()}."
        return None

    @staticmethod
    def parse_teacher_from_text(s: str) -> str:
        """Разбор имени преподавателя из текста."""
        quoted = re.findall(r'"([^\"]+)"|\'([^\']+)\'', s)
        qlist = [q[0] or q[1] for q in quoted if q[0] or q[1]]
        for seg in qlist:
            res = LessonParser.try_parse_segment(seg)
            if res:
                return res
        res = LessonParser.try_parse_segment(s)
        if res:
            return res
        raise ValueError(f"не удалось распознать преподавателя в строке: {s}")

    @classmethod
    def parse(cls, line: str) -> Lesson:
        """Разбор строки и создание объекта Lesson."""
        text = line.strip()
        dt = cls.parse_date_from_text(text)
        room = cls.parse_room_from_text(text)
        teacher = cls.parse_teacher_from_text(text)
        return Lesson(dt, room, teacher)


def parse_lesson(line: str) -> Lesson:
    """
    функция разбора текстовой строки и создания объекта lesson.
    используется регулярное выражение для парсинга.

    ожидаемый формат строки:
        учебныезанятия 2025.03.15 "а-104" "иванов и.е."
    """
    return LessonParser.parse(line)


def parse_multiple_lessons(lines: List[str]) -> List[Lesson]:
    """
    функция для парсинга нескольких строк с использованием map().
    """
    return list(map(parse_lesson, lines))


def create_lessons_map(lines: List[str]) -> Dict[date, Lesson]:
    """
    создание словаря (map) с ключом по дате.
    используется регулярные выражения для парсинга и map() для обработки.
    """
    lessons = parse_multiple_lessons(lines)
    return {lesson.date: lesson for lesson in lessons}


def filter_lessons_by_teacher(lines: List[str], teacher_pattern: str) -> Dict[str, Lesson]:
    """
    фильтрация занятий по имени преподавателя, используя регулярное выражение.
    словарь (map): имя преподавателя -> объект lesson
    """
    lessons = parse_multiple_lessons(lines)
    pattern = re.compile(teacher_pattern)
    filtered = filter(lambda l: pattern.search(l.teacher), lessons)
    return {lesson.teacher: lesson for lesson in filtered}


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

    while True:
        print("\n" + "="*50)
        print("МЕНЮ")
        print("="*50)
        for option in menu:
            print(option)
        print("="*50)

        choice = input("Выберите опцию (1-4): ").strip()

        if choice == "1":
            print('Введите строку в формате: учебное занятие гггг.мм.дд "аудитория" "фамилия и.е."')
            line = input("Строка (или пусто для отмены): ").strip()
            if line:
                append_line_to_file(line)
                print("✓ Запись добавлена в test.txt")
            else:
                print("✗ Отменено")

        elif choice == "2":
            show_raw_data()

        elif choice == "3":
            show_parsed_data()

        elif choice == "4":
            print("До свидания!")
            break

        else:
            print("✗ Неверный выбор. Введите 1, 2, 3 или 4.")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print('\nПрограмма прервана пользователем')
