"""Набор модульных тестов для программы работы 3."""

# pylint: disable=missing-function-docstring
# pylint: disable=missing-module-docstring
import tempfile
import unittest
from datetime import date
from pathlib import Path

from filters import (
    create_lessons_map,
    filter_lessons_by_teacher,
    parse_lesson,
    parse_multiple_lessons,
)
from lesson_parser import LessonParser
from models import Lesson
from file_handler import append_line_to_file, read_lines_from_file


class TestLesson(unittest.TestCase):
    """Тесты для класса Lesson."""

    def test_lesson_creation(self):
        """Проверка создания объекта Lesson."""
        lesson = Lesson(date(2025, 3, 15), "а-104", "Иванов И.Е.")
        self.assertEqual(lesson.date, date(2025, 3, 15))
        self.assertEqual(lesson.room, "а-104")
        self.assertEqual(lesson.teacher, "Иванов И.Е.")

    def test_lesson_str(self):
        """Проверка строкового представления Lesson."""
        lesson = Lesson(date(2025, 3, 15), "а-104", "Иванов И.Е.")
        expected = (
            "Учебное занятие: дата=2025-03-15, аудитория=а-104, "
            "преподаватель=Иванов И.Е."
        )
        self.assertEqual(str(lesson), expected)


class TestLessonParserDate(unittest.TestCase):
    """Тесты для парсинга дат."""

    def test_parse_date_yyyy_mm_dd_dots(self):
        """Парсинг даты в формате yyyy.mm.dd."""
        result = LessonParser.parse_date_from_text("2025.03.15")
        self.assertEqual(result, date(2025, 3, 15))

    def test_parse_date_yyyy_mm_dd_dashes(self):
        """Парсинг даты в формате yyyy-mm-dd."""
        result = LessonParser.parse_date_from_text("2025-04-20")
        self.assertEqual(result, date(2025, 4, 20))

    def test_parse_date_dd_mm_yyyy(self):
        """Парсинг даты в формате dd.mm.yyyy."""
        result = LessonParser.parse_date_from_text("15.03.2025")
        self.assertEqual(result, date(2025, 3, 15))

    def test_parse_date_yyyymmdd(self):
        """Парсинг даты в формате yyyymmdd."""
        result = LessonParser.parse_date_from_text("20250315")
        self.assertEqual(result, date(2025, 3, 15))

    def test_parse_date_invalid(self):
        """Проверка ошибки при неверной дате."""
        with self.assertRaises(ValueError):
            LessonParser.parse_date_from_text("invalid date")


class TestLessonParserOther(unittest.TestCase):
    """Тесты для парсинга аудитории и преподавателя."""

    def test_parse_room(self):
        text = 'учебное занятие 2025.03.15 "а-104" "иванов и.е."'
        room = LessonParser.parse_room_from_text(text)
        self.assertEqual(room, "а-104")

    def test_parse_teacher(self):
        text = 'учебное занятие 2025.03.15 "а-104" "иванов и.е."'
        teacher = LessonParser.parse_teacher_from_text(text)
        self.assertEqual(teacher, "Иванов И.Е.")


class TestParseLesson(unittest.TestCase):
    """Тесты для функции parse_lesson()."""

    def test_parse_lesson_ok(self):
        lesson = parse_lesson('учебное занятие 2025.03.15 "а-104" "иванов и.е."')
        self.assertEqual(lesson.date, date(2025, 3, 15))
        self.assertEqual(lesson.room, "а-104")
        self.assertIn("Иванов", lesson.teacher)

    def test_parse_lesson_bad(self):
        with self.assertRaises(ValueError):
            parse_lesson("какая-то неправильная строка")


class TestFilters(unittest.TestCase):
    """Тесты для функций фильтрации."""

    def setUp(self):
        self.test_lines = [
            'учебное занятие 2025.03.15 "а-104" "иванов и.е."',
            'учебное занятие 2025.04.20 "б-205" "петрова а.в."',
            'учебное занятие 2025.05.10 "в-301" "иванов п.о."',
        ]

    def test_parse_multiple_lessons(self):
        lessons = parse_multiple_lessons(self.test_lines)
        self.assertEqual(len(lessons), 3)
        self.assertEqual(lessons[0].room, "а-104")
        self.assertEqual(lessons[1].room, "б-205")

    def test_create_lessons_map(self):
        lessons_map = create_lessons_map(self.test_lines)
        self.assertEqual(len(lessons_map), 3)
        self.assertIn(date(2025, 3, 15), lessons_map)
        self.assertEqual(lessons_map[date(2025, 3, 15)].room, "а-104")

    def test_filter_lessons_by_teacher(self):
        filtered = filter_lessons_by_teacher(self.test_lines, "Иванов")
        self.assertEqual(len(filtered), 2)


class TestNormalizeInitials(unittest.TestCase):
    """Тесты для нормализации инициалов."""

    def test_normalize_initials_basic(self):
        result = LessonParser.normalize_initials("и.е.")
        self.assertEqual(result, "И.Е.")

    def test_normalize_initials_without_dots(self):
        result = LessonParser.normalize_initials("ие")
        self.assertEqual(result, "И.Е.")

    def test_normalize_initials_mixed(self):
        result = LessonParser.normalize_initials("И.е")
        self.assertEqual(result, "И.Е.")


class TestFileHandler(unittest.TestCase):
    """Тесты для чтения/записи файла."""

    def test_read_missing_file(self):
        with tempfile.TemporaryDirectory() as tmp:
            missing = Path(tmp) / "missing.txt"
            self.assertEqual(read_lines_from_file(str(missing)), [])

    def test_append_and_read(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "data.txt"
            append_line_to_file('line1', str(path))
            append_line_to_file('line2\n', str(path))
            lines = read_lines_from_file(str(path))
            self.assertEqual(lines, ["line1\n", "line2\n"])


if __name__ == "__main__":
    unittest.main()
