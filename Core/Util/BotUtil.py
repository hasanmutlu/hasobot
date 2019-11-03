from telegram import Update
from Files.Database.UserTableManager import UserAccessMode


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
        _result = {"telegram_id": update.message.from_user.id,
                   "first_name": update.message.from_user.first_name,
                   "last_name": update.message.from_user.last_name,
                   "chat_id": update.message.chat_id,
                   "access": UserAccessMode.BOT if update.message.from_user.is_bot else UserAccessMode.USER}
        return _result
