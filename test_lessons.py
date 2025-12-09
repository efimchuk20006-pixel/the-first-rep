import unittest
from datetime import date
from models import Lesson
from parser import LessonParser
from filters import parse_lesson, parse_multiple_lessons, create_lessons_map, filter_lessons_by_teacher


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
        expected = "Учебное занятие: дата=2025-03-15, аудитория=а-104, преподаватель=Иванов И.Е."
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


class TestLessonParserRoom(unittest.TestCase):
    """Тесты для парсинга аудиторий."""

    def test_parse_room_quoted(self):
        """Парсинг аудитории в кавычках."""
        result = LessonParser.parse_room_from_text('"а-104"')
        self.assertEqual(result, "а-104")

    def test_parse_room_pattern_cyrillic(self):
        """Парсинг аудитории в формате а-104."""
        result = LessonParser.parse_room_from_text("аудитория а-104")
        self.assertEqual(result, "а-104")

    def test_parse_room_pattern_latin(self):
        """Парсинг аудитории в формате A-104."""
        result = LessonParser.parse_room_from_text("room A-104")
        self.assertEqual(result, "A-104")

    def test_parse_room_keyword(self):
        """Парсинг аудитории по ключевому слову."""
        result = LessonParser.parse_room_from_text("аудитория: б-205")
        self.assertEqual(result, "б-205")

    def test_parse_room_invalid(self):
        """Проверка ошибки при неверной аудитории."""
        with self.assertRaises(ValueError):
            LessonParser.parse_room_from_text("no room info")


class TestLessonParserTeacher(unittest.TestCase):
    """Тесты для парсинга имён преподавателей."""

    def test_parse_teacher_quoted(self):
        """Парсинг имени в кавычках."""
        result = LessonParser.parse_teacher_from_text('"иванов и.е."')
        self.assertIn("Иванов", result)
        self.assertIn("И.Е.", result)

    def test_parse_teacher_fam_initials(self):
        """Парсинг фамилии и инициалов."""
        result = LessonParser.parse_teacher_from_text("петрова а в")
        self.assertIn("Петрова", result)
        self.assertIn("А.В.", result)

    def test_parse_teacher_initials_fam(self):
        """Парсинг инициалов и фамилии."""
        result = LessonParser.parse_teacher_from_text("и.о. сидоров")
        self.assertIn("Сидоров", result)

    def test_parse_teacher_english(self):
        """Парсинг английского имени."""
        result = LessonParser.parse_teacher_from_text("Smith J K")
        self.assertIn("Smith", result)

    def test_parse_teacher_invalid(self):
        """Проверка ошибки при неверном имени."""
        with self.assertRaises(ValueError):
            LessonParser.parse_teacher_from_text("123 456")


class TestLessonParserIntegration(unittest.TestCase):
    """Интеграционные тесты парсинга."""

    def test_parse_full_line_1(self):
        """Полный парсинг строки (формат 1)."""
        line = 'учебное занятие 2025.03.15 "а-104" "иванов и.е."'
        lesson = parse_lesson(line)
        self.assertEqual(lesson.date, date(2025, 3, 15))
        self.assertEqual(lesson.room, "а-104")
        self.assertIn("Иванов", lesson.teacher)

    def test_parse_full_line_2(self):
        """Полный парсинг строки (формат 2)."""
        line = 'учебное занятие 2025-04-20 "б-205" "петрова а.в."'
        lesson = parse_lesson(line)
        self.assertEqual(lesson.date, date(2025, 4, 20))
        self.assertEqual(lesson.room, "б-205")
        self.assertIn("Петрова", lesson.teacher)


class TestFilters(unittest.TestCase):
    """Тесты для функций фильтрации."""

    def setUp(self):
        """Подготовка тестовых данных."""
        self.test_lines = [
            'учебное занятие 2025.03.15 "а-104" "иванов и.е."',
            'учебное занятие 2025.04.20 "б-205" "петрова а.в."',
            'учебное занятие 2025.05.10 "в-301" "иванов п.о."',
        ]

    def test_parse_multiple_lessons(self):
        """Проверка парсинга множества строк."""
        lessons = parse_multiple_lessons(self.test_lines)
        self.assertEqual(len(lessons), 3)
        self.assertEqual(lessons[0].room, "а-104")
        self.assertEqual(lessons[1].room, "б-205")

    def test_create_lessons_map(self):
        """Проверка создания словаря по датам."""
        lessons_map = create_lessons_map(self.test_lines)
        self.assertEqual(len(lessons_map), 3)
        self.assertIn(date(2025, 3, 15), lessons_map)
        self.assertEqual(lessons_map[date(2025, 3, 15)].room, "а-104")

    def test_filter_lessons_by_teacher(self):
        """Проверка фильтрации по имени преподавателя."""
        filtered = filter_lessons_by_teacher(self.test_lines, "Иванов")
        self.assertEqual(len(filtered), 2)


class TestNormalizeInitials(unittest.TestCase):
    """Тесты для нормализации инициалов."""

    def test_normalize_initials_basic(self):
        """Нормализация простых инициалов."""
        result = LessonParser.normalize_initials("и.е.")
        self.assertEqual(result, "И.Е.")

    def test_normalize_initials_without_dots(self):
        """Нормализация инициалов без точек."""
        result = LessonParser.normalize_initials("ие")
        self.assertEqual(result, "И.Е.")

    def test_normalize_initials_mixed(self):
        """Нормализация смешанного формата."""
        result = LessonParser.normalize_initials("И.е")
        self.assertEqual(result, "И.Е.")


if __name__ == "__main__":
    unittest.main()
