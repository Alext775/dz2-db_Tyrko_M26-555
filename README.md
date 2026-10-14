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

## CRUD-операции

Программа поддерживает добавление, чтение, обновление и удаление записей.

### Добавление записи

```sql
insert into users values ("Sergei", 28, true)
```

ID генерируется автоматически. Указывать его при добавлении не нужно.

### Чтение записей

Вывод всех записей:

```sql
select from users
```

Вывод записей по условию:

```sql
select from users where age = 28
```

### Обновление записей

```sql
update users set age = 29 where name = "Sergei"
```

### Удаление записей

```sql
delete from users where ID = 1
```

### Информация о таблице

```text
info users
```

Пример вывода:

```text
Таблица: users
Столбцы: ID:int, name:str, age:int, is_active:bool
Количество записей: 0
```

### Хранение данных

Данные каждой таблицы сохраняются в отдельном JSON-файле
в директории `data/`.

Например, записи таблицы `users` хранятся в `data/users.json`.

Поддерживаемые типы данных:

- `int` — целые числа
- `str` — строки
- `bool` — логические значения

Все поля обязательны, кроме ID, который генерируется автоматически.

Строковые значения необходимо заключать в кавычки.

[![Демонстрация](https://asciinema.org/a/ZUmFmUbD4NvSxstF.svg)](https://asciinema.org/a/ZUmFmUbD4NvSxstF)