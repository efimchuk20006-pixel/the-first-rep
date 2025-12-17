"""Функции разбора и фильтрации учебных занятий."""

from __future__ import annotations

import re
from datetime import date
from typing import Dict, List

from lesson_parser import LessonParser
from models import Lesson


def parse_lesson(line: str) -> Lesson:
    """Разбор одной строки и создание объекта Lesson."""
    return LessonParser.parse(line)


def parse_multiple_lessons(lines: List[str], *, strict: bool = True) -> List[Lesson]:
    """Парсинг набора строк.

    strict=True: при первой ошибке выбрасывается исключение.
    strict=False: некорректные строки пропускаются.
    """
    lessons: List[Lesson] = []
    for line in lines:
        try:
            lessons.append(parse_lesson(line))
        except ValueError:
            if strict:
                raise
    return lessons


def create_lessons_map(lines: List[str], *, strict: bool = True) -> Dict[date, Lesson]:
    """Создание словаря: дата -> занятие."""
    lessons = parse_multiple_lessons(lines, strict=strict)
    return {lesson.date: lesson for lesson in lessons}


def filter_lessons_by_teacher(
    lines: List[str], teacher_pattern: str, *, strict: bool = True
) -> Dict[str, Lesson]:
    """Фильтрация занятий по имени преподавателя (regex).

    Возвращает словарь: teacher -> Lesson.
    """
    pattern = re.compile(teacher_pattern, flags=re.IGNORECASE)
    lessons = parse_multiple_lessons(lines, strict=strict)
    filtered = (lesson for lesson in lessons if pattern.search(lesson.teacher))
    return {lesson.teacher: lesson for lesson in filtered}
