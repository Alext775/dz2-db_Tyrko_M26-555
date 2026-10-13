import shlex

import prompt

from .constants import META_FILE
from .core import create_table, drop_table
from .utils import load_metadata, save_metadata


def print_help():
    print("\n***Процесс работы с таблицей***")
    print("Функции:")
    print("<command> create_table <имя_таблицы> <столбец1:тип> ... - создать таблицу")
    print("<command> list_tables - показать список всех таблиц")
    print("<command> drop_table <имя_таблицы> - удалить таблицу")
    print("<command> exit - выход из программы")
    print("<command> help - справочная информация")


def run():
    print("\nПервая попытка запустить проект!")
    print_help()

    while True:
        metadata = load_metadata(META_FILE)

        try:
            command = prompt.string(
                "Введите команду: "
            ).strip()
            print()

            args = shlex.split(command)

            if not args:
                continue

            action = args[0]
            params = args[1:]

            if action == "help":
                print_help()

            elif action == "exit":
                print("Выход из программы")
                break

            elif action == "create_table":
                if len(params) < 2:
                    raise ValueError("не указаны имя таблицы или столбцы")

                table_name = params[0]
                columns = params[1:]

                metadata = create_table(metadata, table_name, columns)
                save_metadata(META_FILE, metadata)

                table_columns = ", ".join(
                    f"{name}:{column_type}"
                    for name, column_type in metadata[table_name].items()
                )

                print(
                    f'Таблица "{table_name}" успешно создана '
                    f"со столбцами: {table_columns}"
                )

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

                metadata = drop_table(metadata, table_name)
                save_metadata(META_FILE, metadata)

                print(f'Таблица "{table_name}" успешно удалена')

            else:
                print(f"Команды {action} нет. Попробуйте снова")

        except KeyError as error:
            print(f"Ошибка: {error.args[0]}")

        except ValueError as error:
            print(f"Некорректное значение: {error}. Попробуйте снова")