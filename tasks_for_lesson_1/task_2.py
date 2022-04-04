"""
2. Написать функцию host_range_ping() для перебора ip-адресов из заданного диапазона.
Меняться должен только последний октет каждого адреса.
По результатам проверки должно выводиться соответствующее сообщение.
"""

from ipaddress import ip_address
from task_1 import host_ping


def host_range_ping():

    while True:

        ip_address_start = input('Введите первый ip адрес, с которого начнется проверка: ')
        las_oct = int(ip_address_start.split('.')[3])
        if las_oct > 254:
            print('Последний октет не может быть больше 254')
            continue
        else:
            break
    while True:

        range_ip = input('Сколько ip адресов по порядку проверить?: ')
        if not range_ip.isnumeric():
            print('Необходимо ввести число: ')
        else:
            if (las_oct+int(range_ip)) > 254:
                print(f"Доступное число ip адресов для проверки: {254-las_oct}")
            else:
                break

    host_list = []

    [host_list.append(str(ip_address(ip_address_start)+x)) for x in range(int(range_ip))]

    return host_ping(host_list)


if __name__ == "__main__":
    host_range_ping()
