"""Модели предметной области."""

from __future__ import annotations

import datetime as dt
from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class Lesson:
    """Модель учебного занятия."""

    date: dt.date
    room: str
    teacher: str

    def __str__(self) -> str:
        return (
            f"Учебное занятие: дата={self.date}, аудитория={self.room}, "
            f"преподаватель={self.teacher}"
        )
