import functools
import sqlite3 as sql

from Core.Decorators import singleton
from Files.Database.UserTableManager import UserTableManager


@singleton
class DatabaseManager:
    def __init__(self):
        self.connection = sql.connect('database.db',check_same_thread=False)
        self.connection.execute("PRAGMA encoding = \"UTF-8\"")
        self.userTableManager = UserTableManager()
        for manager in [self.userTableManager]:
            manager.initialize(self.connection)
            manager.create_tables()

    def close(self):
        self.connection.commit()
        self.connection.close()

def check_user_access(user_access):
    def wrapper_check_user(func):
        @functools.wraps(func)
        def wrapper_can_user_call(*args, **kwargs):
            if len(kwargs) < 1 and ("telegram_id" in kwargs) is False:
                message = "This function should be called with telegram_id parameter!"
                return None, message
            else:
                telegram_id = kwargs["telegram_id"]
                filter_result = DatabaseManager.DatabaseManager().userTableManager.select("Users", {"telegram_id": telegram_id})
                if filter_result.count() > 0:
                    user = filter_result[0]
                    if user.access == user_access:
                        result = func(*args, **kwargs)
                        return result, "Command is worked!"
                    else:
                        message = "This User {0} {1} can not run this method!".format(user.first_name,
                                                                                      user.last_name)
                        return None, message
                else:
                    return None, "This User doesnt registered yet!"

        return wrapper_can_user_call

    return wrapper_check_user
