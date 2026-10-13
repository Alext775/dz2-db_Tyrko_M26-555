import prompt


def print_help():
    print("<command> exit - выйти из программы")
    print("<command> help - справочная информация")


def welcome():
    print("\nПервая попытка запустить проект!")
    print("\n***")
    print_help()

    while True:
        command = prompt.string(
            "Введите команду: "
        ).strip()
        print()

        if command == "help":
            print_help()

        elif command == "exit":
            print("Выход из программы")
            break

        else:
            print(
                f"Команды {command} нет. "
                "Попробуйте снова."
            )