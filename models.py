from datetime import date


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
        return f"Учебное занятие: дата={self.date}, аудитория={self.room}, преподаватель={self.teacher}"
