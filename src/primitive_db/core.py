import json

from .constants import ID_COLUMN, VALID_TYPES
from .decorators import (
    confirm_action,
    create_cacher,
    handle_db_errors,
    log_time,
)
from .utils import load_table_data

_select_cache = create_cacher()


@handle_db_errors
def create_table(metadata, table_name, columns):
    if not table_name.isidentifier():
        raise ValueError(table_name)

    if table_name in metadata:
        raise KeyError(f'Таблица "{table_name}" уже существует.')

    if not columns:
        raise ValueError("не указаны столбцы")

    schema = {ID_COLUMN: "int"}
    explicit_id = False

    for column in columns:
        if column.count(":") != 1:
            raise ValueError(column)

        column_name, column_type = column.split(":")

        if not column_name.isidentifier():
            raise ValueError(column_name)

        if column_type not in VALID_TYPES:
            raise ValueError(column_type)

        if column_name == ID_COLUMN:
            if column_type != "int" or explicit_id:
                raise ValueError(column)

            explicit_id = True
            continue

        if column_name in schema:
            raise ValueError(f"повторяющийся столбец {column_name}")

        schema[column_name] = column_type

    if len(schema) == 1:
        raise ValueError("не указаны столбцы кроме ID")

    metadata[table_name] = schema
    return metadata


@handle_db_errors
@confirm_action("удаление таблицы")
def drop_table(metadata, table_name):
    if table_name not in metadata:
        raise KeyError(f'Таблица "{table_name}" не существует.')

    del metadata[table_name]
    return metadata


def validate_value(value, column_type):
    expected_types = {"int": int, "str": str, "bool": bool}

    if type(value) is not expected_types[column_type]:
        raise ValueError(f"{value!r} не соответствует типу {column_type}")

    return value


@handle_db_errors
@log_time
def insert(metadata, table_name, values):
    if table_name not in metadata:
        raise KeyError(f'Таблица "{table_name}" не существует.')

    schema = metadata[table_name]
    columns = [name for name in schema if name != ID_COLUMN]

    if len(values) != len(columns):
        raise ValueError(f"ожидалось {len(columns)} значений, получено {len(values)}")

    row = {
        name: validate_value(value, schema[name])
        for name, value in zip(columns, values, strict=True)
    }

    data = load_table_data(table_name)
    next_id = max((record[ID_COLUMN] for record in data), default=0) + 1
    data.append({ID_COLUMN: next_id, **row})
    return data


@handle_db_errors
@log_time
def select(table_data, where_clause=None):
    key = json.dumps(
        {"data": table_data, "where": where_clause},
        ensure_ascii=False,
        sort_keys=True,
    )

    def find_rows():
        return [
            row.copy()
            for row in table_data
            if where_clause is None
            or all(row.get(name) == value for name, value in where_clause.items())
        ]

    cached_rows = _select_cache(key, find_rows)
    return [row.copy() for row in cached_rows]


@handle_db_errors
def update(table_data, set_clause, where_clause):
    if not where_clause:
        raise ValueError("не указано условие where")

    if ID_COLUMN in set_clause:
        raise ValueError("нельзя изменять ID")

    for row in table_data:
        if all(row.get(name) == value for name, value in where_clause.items()):
            row.update(set_clause)

    return table_data


@handle_db_errors
@confirm_action("удаление записи")
def delete(table_data, where_clause):
    if not where_clause:
        raise ValueError("не указано условие where")

    return [
        row
        for row in table_data
        if not all(row.get(name) == value for name, value in where_clause.items())
    ]
