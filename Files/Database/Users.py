import functools
from Files.Database.BotDatabase import BotDatabase, Tables
from Files.Database.TableMaps import UsersTableMap


class Users:

    @staticmethod
    def get_user(telegram_id):
        records = BotDatabase().filter(Tables.USERS,
                                       lambda row: row[UsersTableMap.TELEGRAM_ID] == telegram_id)
        if records.count > 0:
            return records.rows[0]
        else:
            return None

    @staticmethod
    def is_user_exist(telegram_id):
        return True if Users.get_user(telegram_id) is not None else False

    @staticmethod
    def add_new_user(user_data):
        telegram_id = user_data[UsersTableMap.TELEGRAM_ID]
        if Users.is_user_exist(telegram_id) is False:
            BotDatabase().insert(Tables.USERS, user_data)


def check_user(user_access):
    def wrapper_check_user(func):
        @functools.wraps(func)
        def wrapper_can_user_call(*args, **kwargs):
            if len(kwargs) < 1 and ("telegram_id" in kwargs) is False:
                message = "This function should be called with telegram_id parameter!"
                return None, message
            else:
                telegram_id = kwargs["telegram_id"]
                user = Users.get_user(telegram_id)
                if user is not None:
                    if UsersTableMap.ACCESS in user and user[UsersTableMap.ACCESS] == user_access:
                        result = func(*args, **kwargs)
                        return result, "Command is worked!"
                    else:
                        message = "This User {0} {1} can not run this method!".format(user[UsersTableMap.FIRST_NAME],
                                                                                      user[UsersTableMap.LAST_NAME])
                        return None, message
                else:
                    return None, "This User doesnt registered yet!"

        return wrapper_can_user_call

    return wrapper_check_user
