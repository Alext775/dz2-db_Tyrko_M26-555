from .constants import ID_COLUMN, VALID_TYPES


def create_table(metadata, table_name, columns):
    if not table_name.isidentifier():
        raise ValueError(table_name)

    if table_name in metadata:
        raise KeyError(
            f'Таблица "{table_name}" уже существует'
        )

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
            raise ValueError(
                f"повторяющийся столбец {column_name}"
            )

        schema[column_name] = column_type

    if len(schema) == 1:
        raise ValueError("не указаны столбцы кроме ID")

    metadata[table_name] = schema
    return metadata


def drop_table(metadata, table_name):
    if table_name not in metadata:
        raise KeyError(
            f'Таблица "{table_name}" не существует'
        )

    del metadata[table_name]
    return metadata