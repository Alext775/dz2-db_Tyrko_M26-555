## Управление таблицами

Приложение позволяет создавать, просматривать и удалять таблицы.

### Запуск

```bash
uv sync
uv run database
```

### Команды

| Команда | Описание |
|---|---|
| `create_table <имя> <столбец:тип> ...` | Создание таблицы |
| `list_tables` | Просмотр списка таблиц |
| `drop_table <имя>` | Удаление таблицы |
| `help` | Справка |
| `exit` | Выход |

Поддерживаемые типы данных: `int`, `str`, `bool`.

При создании таблицы автоматически добавляется столбец `ID:int`.

### Пример

```text
>>>Введите команду: create_table users name:str age:int
Таблица "users" успешно создана со столбцами: ID:int, name:str, age:int

>>>Введите команду: list_tables
- users

>>>Введите команду: drop_table users
Таблица "users" успешно удалена.
```

Структура таблиц сохраняется в файле `db_meta.json`.

[![Демонстрация](https://asciinema.org/a/zXI4XMRIWgWFK1QK.svg)](https://asciinema.org/a/zXI4XMRIWgWFK1QK)