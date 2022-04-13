from sqlalchemy import create_engine, Table, Column, Integer, String, MetaData, ForeignKey, DateTime
from sqlalchemy.orm import mapper, sessionmaker
from common.variables import SERVER_DATABASE
import datetime


# Серверная база данных
class ServerStorage:
    # Все пользователи
    class AllUsers:
        def __init__(self, username):
            self.id = None
            self.name = username
            self.last_login = datetime.datetime.now()

    # Активные пользователи
    class ActiveUsers:
        def __init__(self, user_id, ip_address, port, login_time):
            self.user = user_id
            self.ip_address = ip_address
            self.port = port
            self.login_time = login_time
            self.id = None

    # Истории входов
    class LoginHistory:
        def __init__(self, name, date, ip_address, port):
            self.id = None
            self.name = name
            self.date_time = date
            self.ip_address = ip_address
            self.port = port

    def __init__(self):
        self.database_engine = create_engine(SERVER_DATABASE, echo=False, pool_recycle=7200)
        self.metadata = MetaData()

        # Создаем таблицу для всех пользователей
        users_table = Table('Users', self.metadata,
                            Column('id', Integer, primary_key=True),
                            Column('name', String, unique=True),
                            Column('last_login', DateTime)
                            )

        # Создаем таблицу, где будут отображаться активные пользователи
        active_users_table = Table('Active_users', self.metadata,
                                   Column('id', Integer, primary_key=True),
                                   Column('user', ForeignKey('Users.id'), unique=True),
                                   Column('ip_address', String),
                                   Column('port', Integer),
                                   Column('login_time', DateTime)
                                   )

        # Создаем таблицу с историей входов пользователей
        user_login_history = Table('Login_history', self.metadata,
                                   Column('id', Integer, primary_key=True),
                                   Column('name', ForeignKey('Users.id')),
                                   Column('date_time', DateTime),
                                   Column('ip_address', String),
                                   Column('port', Integer)
                                   )

        # Создание таблиц
        self.metadata.create_all(self.database_engine)

        # Связывание классов с таблицами
        mapper(self.AllUsers, users_table)
        mapper(self.ActiveUsers, active_users_table)
        mapper(self.LoginHistory, user_login_history)

        # Создание сессии
        Session = sessionmaker(bind=self.database_engine)
        self.session = Session()

        # Очищаем таблицу активных пользователей после установки соединения
        self.session.query(self.ActiveUsers).delete()
        self.session.commit()

    # Функция записи входа пользователя в базу
    def user_login(self, username, ip_address, port):
        print(username, ip_address, port)

        # Проверяем наличие пользователя в базе
        res = self.session.query(self.AllUsers).filter_by(name=username)

        # Если пользователь с таким именем есть, то обновляем время входа, иначе создаем нового
        if res.count():
            user = res.first()
            user.last_login = datetime.datetime.now()
        else:
            user = self.AllUsers(username)
            self.session.add(user)
            self.session.commit()

        # Создаем запись в таблице активных пользователей
        new_active_user = self.ActiveUsers(user.id, ip_address, port, datetime.datetime.now())
        self.session.add(new_active_user)

        # Записываем историю входа пользователя
        history = self.LoginHistory(user.id, datetime.datetime.now(), ip_address, port)
        self.session.add(history)

        # Сохраняем все изменения
        self.session.commit()

    # Функция записи выхода пользователя
    def user_logout(self, username):
        user = self.session.query(self.AllUsers).filter_by(name=username).first()

        # Удаляем пользователя из таблицы активных
        self.session.query(self.ActiveUsers).filter_by(user=user.id).delete()

        # Применяем изменения
        self.session.commit()

    # Функция возвращает всех пользователей с указанием времени последнего входа
    def users_list(self):
        query = self.session.query(self.AllUsers.name, self.AllUsers.last_login,)
        return query.all()

    # Функция возвращает всех активных, на данный момент, пользователей
    def active_users_list(self):
        query = self.session.query(
            self.AllUsers.name,
            self.ActiveUsers.ip_address,
            self.ActiveUsers.port,
            self.ActiveUsers.login_time
        ).join(self.AllUsers)
        return query.all()

    # Функция возвращает историю входа пользователей
    def login_history(self, username=None):
        query = self.session.query(self.AllUsers.name,
                                   self.LoginHistory.date_time,
                                   self.LoginHistory.ip_address,
                                   self.LoginHistory.port
                                   ).join(self.AllUsers)
        if username:
            query = query.filter(self.AllUsers.name == username)
        return query.all()


if __name__ == '__main__':
    test_db = ServerStorage()
    test_db.user_login('user1', '192.168.50.10', 5550)
    test_db.user_login('user2', '192.168.50.88', 5555)
    test_db.user_login('user3', '192.168.1.132', 4556)
    # выводим список кортежей - активных пользователей
    print(test_db.active_users_list())
    # выполянем 'отключение' пользователя
    test_db.user_logout('user2')
    # выводим список активных пользователей
    print(test_db.active_users_list())
    # запрашиваем историю входов по пользователю
    test_db.login_history('user3')
    # выводим список известных пользователей
    print(test_db.users_list())
