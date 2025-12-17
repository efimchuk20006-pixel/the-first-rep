# Practical work 2.1.5 — Инструментальные средства анализа кода программ

Содержимое репозитория:
- `original/` — исходная версия программы
- `improved/` — улучшенная версия после анализа



## Быстрый запуск тестов и анализа

### Статический анализ
```bash
сd original/
flake8 . --max-line-length=88
pylint main.py models.py parser.py filters.py file_handler.py

сd improved/
flake8 . --max-line-length=88
pylint main.py models.py lesson_parser.py filters.py file_handler.py
```

### Динамический анализ
```bash

pytest -q
pytest --cov=. --cov-report=term-missing -q

