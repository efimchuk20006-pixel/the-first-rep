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


def parse_lesson(line: str) -> Lesson:
    """
    функция разбора текстовой строки и создания объекта lesson.
    используется регулярное выражение для парсинга.

    ожидаемый формат строки:
        учебныезанятия 2025.03.15 "а-104" "иванов и.е."
    """
    text = line.strip()

    def parse_date_from_text(s: str) -> date:
        # популярные форматы: yyyy.mm.dd, yyyy-mm-dd, dd.mm.yyyy, dd/mm/yyyy, yyyy/mm/dd
        # ищем сначала варианты с годом впереди, затем варианты с годом в конце.
        # возвращаем объект date при первом успешном совпадении.
        # год-первый
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

        # попробуем неполные/прочие: yyyymmdd
        m = re.search(r"\b(\d{4})(\d{2})(\d{2})\b", s)
        if m:
            y, mo, d = m.groups()
            try:
                return datetime(int(y), int(mo), int(d)).date()
            except ValueError:
                pass

        raise ValueError(f"не удалось распознать дату в строке: {s}")

    def parse_room_from_text(s: str) -> str:
        # типичные обозначения аудитории: a-104, а104, а-104, аудитория 104, "а-104"
        # ищем буквенно-цифровое обозначение с буквой и цифрами
        m = re.search(r"\b[АA]-?\d{1,4}\b", s, flags=re.IGNORECASE)
        if m:
            return m.group(0)

        # по ключевому слову 'аудитория' или 'room'
        m = re.search(r"(?:аудитори(?:я|и)|auditorium|room)[:\s\"]+([A-Za-zА-Яа-я0-9\-]+)", s, flags=re.IGNORECASE)
        if m:
            return m.group(1)

        # в кавычках: "а-104"
        m = re.search(r'"([^\"]+)"', s)
        if m:
            candidate = m.group(1)
            # если внутри кавычек видим цифры или букву+цифры — считаем аудиторией
            if re.search(r"[0-9]", candidate):
                return candidate

        raise ValueError(f"не удалось распознать аудиторию в строке: {s}")

    def parse_teacher_from_text(s: str) -> str:
        # пробуем сначала извлечь текст из кавычек — часто имя даётся в кавычках
        def normalize_initials(a: str) -> str:
            # привести инициалы к формату и.е.
            chars = re.findall(r"([A-Za-zА-Яа-яЁё])", a)
            if len(chars) >= 2:
                i1 = chars[0].upper()
                i2 = chars[1].upper()
                return f"{i1}.{i2}."
            return a

        # содержимое в кавычках (двойных и одинарных)
        quoted = re.findall(r'"([^\"]+)"|\'([^\']+)\'', s)
        # quoted — список кортежей; приводим к простому списку непустых
        qlist = [q[0] or q[1] for q in quoted if q[0] or q[1]]

        def try_parse_segment(seg: str):
            # фамилия + инициалы (в разных регистрах и с пробелами)
            m = re.search(r"([А-ЯЁа-яё]+)\s+([А-ЯЁа-яё])\.?\s*([А-ЯЁа-яё])\.?", seg, flags=re.IGNORECASE)
            if m:
                fam, a1, a2 = m.groups()
                fam = fam.strip().capitalize()
                initials = f"{a1.upper()}.{a2.upper()}."
                return f"{fam} {initials}"

            # фамилия + инициалы слитно (иванов и.е.)
            m = re.search(r"([А-ЯЁа-яё]+)\s+([А-ЯЁа-яё]\.[А-ЯЁа-яё]\.)", seg, flags=re.IGNORECASE)
            if m:
                fam, initials = m.groups()
                fam = fam.strip().capitalize()
                initials = normalize_initials(initials)
                return f"{fam} {initials}"

            # инициалы перед фамилией
            m = re.search(r"([А-ЯЁа-яё]\.?\s*[А-ЯЁа-яё]\.?)\s*([А-ЯЁа-яё]+)", seg, flags=re.IGNORECASE)
            if m:
                initials, fam = m.groups()
                fam = fam.strip().capitalize()
                initials = normalize_initials(initials)
                return f"{fam} {initials}"

            # только инициалы
            m = re.search(r"\b([А-ЯЁа-яё])\.?\s*([А-ЯЁа-яё])\.?\b", seg, flags=re.IGNORECASE)
            if m:
                a1, a2 = m.groups()
                return f"{a1.upper()}.{a2.upper()}."

            # англ. варианты
            m = re.search(r"([A-Z][a-z]+)\s+([A-Z])\.?\s*([A-Z])\.?", seg)
            if m:
                fam, a1, a2 = m.groups()
                return f"{fam} {a1}.{a2}."

            return None

        # пробуем сначала сегменты в кавычках
        for seg in qlist:
            res = try_parse_segment(seg)
            if res:
                return res

        # если в кавычках ничего нет
        res = try_parse_segment(s)
        if res:
            return res

        raise ValueError(f"не удалось распознать преподавателя в строке: {s}")

    # выполняем извлечение
    dt = parse_date_from_text(text)
    room = parse_room_from_text(text)
    teacher = parse_teacher_from_text(text)

    return Lesson(dt, room, teacher)


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
    # словарь: дата -> объект lesson
    return {lesson.date: lesson for lesson in lessons}


def filter_lessons_by_teacher(lines: List[str], teacher_pattern: str) -> Dict[str, Lesson]:
    """
    фильтрация занятий по имени преподавателя, используя регулярное выражение.
    словарь (map): имя преподавателя -> объект lesson
    """
    lessons = parse_multiple_lessons(lines)
    # компиляция регулярного выражения один раз
    pattern = re.compile(teacher_pattern)
    # map для фильтрации
    filtered = filter(lambda l: pattern.search(l.teacher), lessons)
    # map по имени преподавателя
    return {lesson.teacher: lesson for lesson in filtered}


def main():
    print("введите описание учебного занятия в одной строке.")
    print('формат: учебное занятие гггг.мм.дд "аудитория" "фамилия и.е."')
    print('например: учебное занятие 2025.03.15 "а-104" "иванов и.е."')
    print()

    line = input("строка: ")

    # объект на основании строки
    lesson = parse_lesson(line)

    print()
    print("сформированный объект:")
    print(lesson)


if __name__ == "__main__":
    main()
