"""
Одновременный запуск сервера и нескольких клиентов.
"""

import subprocess


processes = []

while True:
    action = input('Выбирите действие: q - выход, s - запустить сервер и клиенты, x - завершить все процессы')

    if action == 'q':
        break
    elif action == 's':
        processes.append(subprocess.Popen('python server.py', creationflags=subprocess.CREATE_NEW_CONSOLE))

        for i in range(2):
            processes.append(subprocess.Popen('python client.py -m send', creationflags=subprocess.CREATE_NEW_CONSOLE))

        for i in range(2):
            processes.append(subprocess.Popen('python client.py -m listen',
                                              creationflags=subprocess.CREATE_NEW_CONSOLE))
    elif action == 'x':
        while processes:
            victim = processes.pop()
            victim.kill()
