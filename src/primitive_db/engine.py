import prompt
from prettytable import PrettyTable

from .constants import ID_COLUMN, META_FILE
from .core import (
    create_table,
    delete,
    drop_table,
    insert,
    select,
    update,
    validate_value,
)
from .decorators import handle_db_errors
from .parser import parse_clause, parse_values, tokenize
from .utils import (
    load_metadata,
    load_table_data,
    remove_table_data,
    save_metadata,
    save_table_data,
)


def print_help():
    """Вывести список доступных команд"""
    print("\n***Операции с данными***")
    print("\nФункции:")
    print("<command> create_table <имя_таблицы> <столбец1:тип> ... - создать таблицу")
    print("<command> list_tables - показать список всех таблиц")
    print("<command> drop_table <имя_таблицы> - удалить таблицу")
    print(
        "<command> insert into <имя_таблицы> "
        "values (<значение1>, <значение2>, ...) - создать запись"
    )
    print(
        "<command> select from <имя_таблицы> "
        "where <столбец> = <значение> - прочитать записи по условию"
    )
    print("<command> select from <имя_таблицы> - прочитать все записи")
    print(
        "<command> update <имя_таблицы> set <столбец1> = <новое_значение1> "
        "where <столбец_условия> = <значение_условия> - обновить запись"
    )
    print(
        "<command> delete from <имя_таблицы> "
        "where <столбец> = <значение> - удалить запись"
    )
    print("<command> info <имя_таблицы> - вывести информацию о таблице")
    print("<command> exit - выход из программы")
    print("<command> help - справочная информация")
    print()


def get_schema(metadata, table_name):
    """Получить структуру указанной таблицы"""
    if table_name not in metadata:
        raise KeyError(f'Таблица "{table_name}" не существует.')

    return metadata[table_name]


def prepare_clause(metadata, table_name, clause, allow_id=True):
    """Проверить типы и подготовить условие запроса"""
    schema = get_schema(metadata, table_name)
    result = {}

    for column, value in clause.items():
        if column not in schema:
            raise KeyError(f'Столбец "{column}" не существует.')

        if column == ID_COLUMN and not allow_id:
            raise ValueError("нельзя изменять ID")

        result[column] = validate_value(value, schema[column])

    return result


def print_rows(metadata, table_name, rows):
    """Вывести записи в виде таблицы PrettyTable"""
    table = PrettyTable()
    table.field_names = list(get_schema(metadata, table_name))

    for row in rows:
        table.add_row([row[column] for column in table.field_names])

    print(table)


@handle_db_errors
def execute_command(command):
    """Разобрать и выполнить команду пользователя"""
    metadata = load_metadata(META_FILE)
    args = tokenize(command)

    if not args:
        return False

    action = args[0]
    params = args[1:]

    if action == "help":
        if params:
            raise ValueError("лишние аргументы")

        print_help()

    elif action == "exit":
        if params:
            raise ValueError("лишние аргументы")

        return True

    elif action == "create_table":
        if len(params) < 2:
            raise ValueError("не указаны имя таблицы или столбцы")

        table_name = params[0]
        result = create_table(metadata, table_name, params[1:])

        if result is not None:
            save_metadata(META_FILE, result)
            save_table_data(table_name, [])

            columns = ", ".join(
                f"{name}:{kind}" for name, kind in result[table_name].items()
            )

            print(f'Таблица "{table_name}" успешно создана со столбцами: {columns}')

    elif action == "list_tables":
        if params:
            raise ValueError("лишние аргументы")

        if metadata:
            for table_name in metadata:
                print(f"- {table_name}")
        else:
            print("Таблиц пока нет")

    elif action == "drop_table":
        if len(params) != 1:
            raise ValueError("укажите имя таблицы")

        table_name = params[0]
        get_schema(metadata, table_name)

        result = drop_table(metadata, table_name)

        if result is not None:
            save_metadata(META_FILE, result)
            remove_table_data(table_name)

            print(f'Таблица "{table_name}" успешно удалена')

    elif action == "insert":
        if len(args) < 7 or args[1] != "into" or args[3] != "values":
            raise ValueError("insert into <таблица> values (...)")

        table_name = args[2]
        values = parse_values(args[4:])
        data = insert(metadata, table_name, values)

        if data is not None:
            save_table_data(table_name, data)

            print(
                f"Запись с ID={data[-1][ID_COLUMN]} успешно "
                f'добавлена в таблицу "{table_name}".'
            )

    elif action == "select":
        if len(args) < 3 or args[1] != "from":
            raise ValueError("select from <таблица> [where ...]")

        table_name = args[2]
        get_schema(metadata, table_name)

        if len(args) == 3:
            where_clause = None

        elif len(args) == 7 and args[3] == "where":
            where_clause = prepare_clause(
                metadata,
                table_name,
                parse_clause(args[4:]),
            )

        else:
            raise ValueError("неверный синтаксис select")

        data = load_table_data(table_name)
        rows = select(data, where_clause)

        if rows is not None:
            print_rows(metadata, table_name, rows)

    elif action == "update":
        if len(args) != 10 or args[2] != "set" or args[6] != "where":
            raise ValueError("update <таблица> set <поле> = ... where ...")

        table_name = args[1]

        set_clause = prepare_clause(
            metadata,
            table_name,
            parse_clause(args[3:6]),
            allow_id=False,
        )

        where_clause = prepare_clause(
            metadata,
            table_name,
            parse_clause(args[7:10]),
        )

        data = load_table_data(table_name)
        matched_rows = select(data, where_clause)

        if matched_rows is not None:
            result = update(data, set_clause, where_clause)

            if result is not None:
                save_table_data(table_name, result)

                if len(matched_rows) == 1:
                    print(
                        f"Запись с ID={matched_rows[0][ID_COLUMN]} "
                        f'в таблице "{table_name}" успешно обновлена.'
                    )
                else:
                    print(f"Обновлено записей: {len(matched_rows)}")

    elif action == "delete":
        if len(args) != 7 or args[1] != "from" or args[3] != "where":
            raise ValueError("delete from <таблица> where <поле> = ...")

        table_name = args[2]

        where_clause = prepare_clause(
            metadata,
            table_name,
            parse_clause(args[4:]),
        )

        data = load_table_data(table_name)
        matched_rows = select(data, where_clause)

        if matched_rows is not None:
            result = delete(data, where_clause)

            if result is not None:
                save_table_data(table_name, result)

                if len(matched_rows) == 1:
                    print(
                        f"Запись с ID={matched_rows[0][ID_COLUMN]} "
                        f'успешно удалена из таблицы "{table_name}".'
                    )
                else:
                    print(f"Удалено записей: {len(matched_rows)}")

    elif action == "info":
        if len(params) != 1:
            raise ValueError("укажите имя таблицы")

        table_name = params[0]
        schema = get_schema(metadata, table_name)

        columns = ", ".join(f"{name}:{kind}" for name, kind in schema.items())

        print(f"Таблица: {table_name}")
        print(f"Столбцы: {columns}")
        print(f"Количество записей: {len(load_table_data(table_name))}")

    else:
        print(f"Команды {action} нет. Попробуйте снова")

    return False


def run():
    """Запустить основной цикл базы данных"""
    print_help()

    while True:
        try:
            command = prompt.string("Введите команду: ").strip()
            print()

            if execute_command(command):
                print("Выход из программы")
                break

        except (KeyboardInterrupt, EOFError):
            print("\nВыход из программы")
            break
