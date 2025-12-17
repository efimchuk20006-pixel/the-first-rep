from datetime import datetime, date
import re
from models import Lesson

class LessonParser:
    """Класс для разбора строки и создания объекта Lesson."""
    @staticmethod
    def parse_date_from_text(s: str) -> date:
        """Разбор даты из текста."""
        m = re.search(r"(\d{4})[.\-/](\d{1,2})[.\-/](\d{1,2})", s)
        if m:
            y, mo, d = m.groups()
            try:
                return datetime(int(y), int(mo), int(d)).date()
            except ValueError:
                pass
        m = re.search(r"(\d{1,2})[.\-/](\d{1,2})[.\-/](\d{4})", s)
        if m:
            d, mo, y = m.groups()
            try:
                return datetime(int(y), int(mo), int(d)).date()
            except ValueError:
                pass
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
        m = re.search(r'["\']([^"\']+)["\']', s)
        if m:
            cand = m.group(1)
            if re.search(r"\d", cand):
                return cand
        m = re.search(r"\b[АA]-?\d{1,4}\b", s, flags=re.IGNORECASE)
        if m:
            return m.group(0)
        m = re.search(r"(?:аудитори(?:я|и)|auditorium|room)[:\s\"]+([A-Za-zА-Яа-я0-9\-]*\d[A-Za-zА-Яа-я0-9\-]*)", s, flags=re.IGNORECASE)
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
            r"([А-ЯЁа-яё]\.?*[А-ЯЁа-яё]\.?)\s*([А-ЯЁа-яё]+)",
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

    @staticmethod
    def normalize_initials(text: str) -> str:
        """Нормализация инициалов: 'и.е.' -> 'И.Е.'; 'ие' -> 'И.Е.'."""
        cleaned = re.sub(r"[^A-Za-zА-Яа-я]", "", text)
        if not cleaned:
            raise ValueError(f"инициалы не распознаны: {text}")

        letters = cleaned[:2].upper()
        if len(letters) == 1:
            return f"{letters}."
        return f"{letters[0]}.{letters[1]}."

    @staticmethod
    def parse_room_from_text(text: str) -> str:
        """Извлечь аудиторию из строки: сначала ищет в кавычках, если нет - ищет паттерн аудитории без кавычек."""
        match = re.search(r'"([^"]+)"', text)
        if match:
            return match.group(1).strip()
        # Попробуем найти аудиторию без кавычек (например, а17, а-104, б-205, в-301)
        match2 = re.search(r'\b[абвгд]-?\d{1,4}\b', text, re.IGNORECASE)
        if match2:
            return match2.group(0).strip()
        # Попробуем найти вариант без дефиса (например, а17)
        match3 = re.search(r'\b[абвгд]\d{1,4}\b', text, re.IGNORECASE)
        if match3:
            return match3.group(0).strip()
        raise ValueError(f"аудитория не найдена в строке: {text}")

    @staticmethod
    def parse_teacher_from_text(text: str) -> str:
        """Извлечь преподавателя (вторая пара кавычек или последние слова после аудитории)."""
        matches = re.findall(r'"([^"]+)"', text)
        if len(matches) >= 2:
            raw = matches[1].strip()
            parts = raw.split()
            surname = parts[0].capitalize() if parts else ""
            initials_raw = parts[1] if len(parts) > 1 else ""
            if not surname or not initials_raw:
                raise ValueError(f"преподаватель не распознан: {raw}")
            initials = LessonParser.normalize_initials(initials_raw)
            return f"{surname} {initials}"
        # Если кавычек нет, ищем фамилию и инициалы после аудитории
        # Удаляем дату и аудиторию
        # Пример: 2025-03-15 а17 жулькин и.А
        #         0          1   2       3
        tokens = text.strip().split()
        # ищем токен, похожий на аудиторию
        room_idx = -1
        for i, t in enumerate(tokens):
            if re.fullmatch(r'[абвгд]-?\d{1,4}', t, re.IGNORECASE) or re.fullmatch(r'[абвгд]\d{1,4}', t, re.IGNORECASE):
                room_idx = i
                break
        if room_idx != -1 and len(tokens) > room_idx + 2:
            surname = tokens[room_idx + 1].capitalize()
            initials_raw = tokens[room_idx + 2]
            initials = LessonParser.normalize_initials(initials_raw)
            return f"{surname} {initials}"
        raise ValueError(f"преподаватель не найден в строке: {text}")

    @staticmethod
    def parse(line: str) -> Lesson:
        """Разобрать строку и создать Lesson."""
        date_ = LessonParser.parse_date_from_text(line)
        room = LessonParser.parse_room_from_text(line)
        teacher = LessonParser.parse_teacher_from_text(line)
        return Lesson(date=date_, room=room, teacher=teacher)
