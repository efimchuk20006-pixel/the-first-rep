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
