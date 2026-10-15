import time


def handle_db_errors(func):
    """Перехватывать ошибки при работе с базой данных"""

    def wrapper(*args, **kwargs):
        """Выполнить функцию с обработкой исключений"""
        try:
            return func(*args, **kwargs)

        except FileNotFoundError:
            print("Ошибка: файл данных не найден")

        except KeyError as error:
            print(f"Ошибка: {error.args[0]}")

        except ValueError as error:
            print(f"Некорректное значение: {error}. Попробуйте снова")

        return None

    wrapper.__name__ = func.__name__
    wrapper.__doc__ = func.__doc__
    return wrapper


def confirm_action(action_name):
    """Создать декоратор подтверждения опасных операций"""

    def decorator(func):
        """Обернуть функцию запросом подтверждения"""

        def wrapper(*args, **kwargs):
            """Запросить подтверждение перед выполнением функции"""
            answer = (
                input(f'Вы уверены, что хотите выполнить "{action_name}"? [y/n]: ')
                .strip()
                .lower()
            )

            if answer != "y":
                print("Операция отменена")
                return None

            return func(*args, **kwargs)

        wrapper.__name__ = func.__name__
        wrapper.__doc__ = func.__doc__
        return wrapper

    return decorator


def log_time(func):
    """Измерять время выполнения функции"""

    def wrapper(*args, **kwargs):
        """Выполнить функцию и вывести время её работы"""
        start = time.monotonic()

        try:
            return func(*args, **kwargs)

        finally:
            duration = time.monotonic() - start

            print(f"Функция {func.__name__} выполнилась за {duration:.3f} секунд")

    wrapper.__name__ = func.__name__
    wrapper.__doc__ = func.__doc__
    return wrapper


def create_cacher():
    """Создать замыкание для кэширования результатов"""
    cache = {}

    def cache_result(key, value_func):
        """Вернуть результат из кэша или вычислить новый"""
        if key not in cache:
            cache[key] = value_func()

        return cache[key]

    return cache_result
