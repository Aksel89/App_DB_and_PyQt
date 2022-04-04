"""
1. Написать функцию host_ping(), в которой с помощью утилиты ping будет проверяться доступность сетевых узлов.
Аргументом функции является список, в котором каждый сетевой узел должен быть представлен именем хоста
или ip-адресом.
В функции необходимо перебирать ip-адреса и проверять их доступность с выводом соответствующего
сообщения («Узел доступен», «Узел недоступен»).
При этом ip-адрес сетевого узла должен создаваться с помощью функции ip_address().
"""
from ipaddress import ip_address
from subprocess import Popen, PIPE


def host_ping(ip_address_list, timeout=300):

    result = {
        'Узел доступен': '',
        'Узел не доступен': '',
    }

    for ip_addr in ip_address_list:
        ping_ip = Popen(f'ping {ip_addr} -w {timeout}', stdout=PIPE)
        ping_ip.wait()
        if ping_ip.returncode == 0:
            result['Узел доступен'] += f'{str(ip_addr)} \n'
            res_info = f'{ip_addr} Узел доступен'
        else:
            result['Узел не доступен'] += f'{str(ip_addr)} \n'
            res_info = f'{ip_addr} Узел не доступен'
        print(res_info)
    return result


if __name__ == '__main__':
    list_ip = ['192.168.1.1', '192.168.16.230', '10.0.0.2', '87.250.250.242', 'ya.ru', 'localhost', '192.168.50.1',
               '192.168.50.88', '127.0.0.1']
    print(host_ping(list_ip))
