from typing import List, Dict
from datetime import date
from parser import LessonParser
from models import Lesson


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
    import re
    lessons = parse_multiple_lessons(lines)
    pattern = re.compile(teacher_pattern)
    filtered = filter(lambda l: pattern.search(l.teacher), lessons)
    return {lesson.teacher: lesson for lesson in filtered}
