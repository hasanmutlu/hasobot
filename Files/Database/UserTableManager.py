import logging

from Core.DbManager.DbTable import Table, Field
from Core.DbManager.ITableManager import ITableManager
from Core.Util.Util import Object


class UserAccessMode:
    USER = 0
    ADMIN = 1
    BOT = 2
    COUNT = 3


class UserTableManager(ITableManager):

    def __init__(self):
        super(UserTableManager, self).__init__()
        user_table = Table("Users", [Field('id', int, is_primary_key=True),
                                     Field('access', int),  # 0:User, 1:Admin, 2:Bot,
                                     Field('chat_id', int),
                                     Field('first_name', str),
                                     Field('last_name', str),
                                     Field('telegram_id', int),
                                     ])
        self.add_table(user_table)

    def insert_user(self, data: Object):
        is_exist = self.record_is_exist("Users", "telegram_id", data.telegram_id)
        if is_exist:
            logging.warning(f"User {data.first_name} , {data.telegram_id} is already exist!")
        else:
            return self.insert_data('Users', data)

    def update_user(self, data: Object, _id: int):
        is_exist = self.record_is_exist("Users", "id", _id)
        if not is_exist:
            logging.warning(f"User {data.first_name} , {data.id} is not exist!")
        else:
            return self.update_data("Users", data, "id", _id)
