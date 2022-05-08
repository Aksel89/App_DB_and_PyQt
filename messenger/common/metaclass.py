import dis


# Метакласс, выполняющий базовую проверку класса «Сервер»
class ServerVerifier(type):
    def __init__(self, classname, bases, clsdict):
        """
        :param classname: экземпляр метакласса Server
        :param bases: кортеж базовых классов
        :param clsdict: словарь методов и атрибутов экземпляра метакласса
        """

        # Список методов, используемых функциями класса
        methods = []

        # Атрибуты, используемые функциями класса
        attributes = []

        # Перебираем ключи словаря с методами и атрибутами
        for func in clsdict:
            try:
                # Возвращает итератор по инструкциям в предоставленной функции,
                # методе, строке исходного кода или объекте кода.
                ret = dis.get_instructions(clsdict[func])
            except TypeError:
                # Если функция не найдена ловим мсключение
                pass
            else:
                # Если функция найдена, то получаем методы и атрибуты
                for i in ret:
                    print(i)
                    if i.opname == 'LOAD_GLOBAL':
                        if i.argval not in methods:
                            # Заполняем список методами
                            methods.append(i.argval)
                    elif i.opname == 'LOAD_ATTR':
                        if i.argval not in attributes:
                            # Заполняем список атрибутами
                            attributes.append(i.argval)

        if 'connect' in methods:
            raise TypeError('Недопустимо использовать метод "connect" в '
                            'серверном классе')

        if not ('SOCK_STREAM' in attributes and 'AF_INET' in attributes):
            raise TypeError('Некорректная инициализация сокета')

        super().__init__(classname, bases, clsdict)


# Метакласс, выполняющий базовую проверку класса «Клиент»
class ClientVerifier(type):
    def __init__(self, classname, bases, clsdict):
        # Список методов, используемых функциями класса
        methods = []
        for func in clsdict:
            try:
                # Возвращает итератор по инструкциям в предоставленной функции,
                # методе, строке исходного кода или объекте кода.
                ret = dis.get_instructions(clsdict[func])
            except TypeError:
                # Если функция не найдена ловим мсключение
                pass
            else:
                # Если функция найдена, то получаем методы
                for i in ret:
                    print(i)
                    if i.opname == 'LOAD_GLOBAL':
                        if i.argval not in methods:
                            # Заполняем список методами
                            methods.append(i.argval)

        for command in ('accept', 'listen', 'socket'):
            if command in methods:
                raise TypeError('Присутствует недопустимый, '
                                'для данного класса, метод')

        if 'get_message' in methods or 'send_message' in methods:
            pass
        else:
            raise TypeError('Отсутствует функция сокета')
        super().__init__(classname, bases, clsdict)
