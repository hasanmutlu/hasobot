from telegram import Update
from Files.Database.TableMaps import UsersTableMap, UsersAccessMode


class BotUtil:
    @staticmethod
    def get_telegram_id(update: Update):
        return update.message.from_user.id

    @staticmethod
    def get_message(update: Update):
        return str(update.message.text)

    @staticmethod
    def get_message_command(update: Update):
        message = BotUtil.get_message(update)
        return message.split(' ')[0]

    @staticmethod
    def get_message_arguments(update: Update):
        message = BotUtil.get_message(update)
        command = BotUtil.get_message_command(update)
        return message.replace(command + ' ', '')

    @staticmethod
    def get_user_data(update: Update):
        _result = {UsersTableMap.TELEGRAM_ID: update.message.from_user.id,
                   UsersTableMap.FIRST_NAME: update.message.from_user.first_name,
                   UsersTableMap.LAST_NAME: update.message.from_user.last_name,
                   UsersTableMap.IS_BOT: update.message.from_user.is_bot,
                   UsersTableMap.CHAT_ID: update.message.chat_id,
                   UsersTableMap.ACCESS: UsersAccessMode.USER}
        return _result
