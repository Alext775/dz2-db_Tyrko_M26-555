import shlex


def tokenize(command):
    lexer = shlex.shlex(command, posix=False, punctuation_chars="(),=")
    lexer.whitespace_split = True
    lexer.commenters = ""
    tokens = []

    for token in lexer:
        if all(char in "(),=" for char in token):
            tokens.extend(token)
        else:
            tokens.append(token)

    return tokens


def parse_value(token):
    if len(token) >= 2 and token[0] == token[-1] and token[0] in ("'", '"'):
        return token[1:-1]

    if token.lower() == "true":
        return True

    if token.lower() == "false":
        return False

    try:
        return int(token)
    except ValueError as error:
        raise ValueError(f"строка {token} должна быть в кавычках") from error


def parse_values(tokens):
    if len(tokens) < 3 or tokens[0] != "(" or tokens[-1] != ")":
        raise ValueError("неверный формат values")

    values = []

    for index, token in enumerate(tokens[1:-1]):
        if index % 2 == 0:
            if token in ("(", ")", ",", "="):
                raise ValueError("некорректный список значений")

            values.append(parse_value(token))

        elif token != ",":
            raise ValueError("между значениями должна быть запятая")

    if not values or len(tokens[1:-1]) != len(values) * 2 - 1:
        raise ValueError("некорректный список значений")

    return values


def parse_clause(tokens):
    if len(tokens) != 3 or tokens[1] != "=":
        raise ValueError("ожидается условие вида столбец = значение")

    column = tokens[0]

    if not column.isidentifier():
        raise ValueError(column)

    return {column: parse_value(tokens[2])}
