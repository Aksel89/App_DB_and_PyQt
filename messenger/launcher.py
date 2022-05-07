"""
Одновременный запуск сервера и нескольких клиентов.
"""

import subprocess


def main():
    processes = []

    while True:
        action = input('Выбирите действие: q - выход, s - запустить сервер, k - запустить клиенты, '
                       'x - завершить все процессы')

        if action == 'q':
            break
        elif action == 's':
            # Запускаем сервер!
            processes.append(
                subprocess.Popen(
                    'python server.py',
                    creationflags=subprocess.CREATE_NEW_CONSOLE))
        elif action == 'k':
            print('Убедитесь, что на сервере зарегистрировано необходимо количество клиентов с паролем 123456.')
            print('Первый запуск может быть достаточно долгим из-за генерации ключей!')
            clients_count = int(
                input('Введите количество тестовых клиентов для запуска: '))
            # Запускаем клиентов:
            for i in range(clients_count):
                processes.append(
                    subprocess.Popen(
                        f'python client.py -n user_{i + 1} -p 123456',
                        creationflags=subprocess.CREATE_NEW_CONSOLE))
        elif action == 'x':
            while processes:
                processes.pop().kill()


if __name__ == '__main__':
    main()
