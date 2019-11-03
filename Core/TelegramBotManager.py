import logging

from telegram import Bot
from telegram.ext import Updater, MessageHandler, Filters

from Core import Decorators
from Core.ServiceManager import ServiceManager
from Core.UdpServer import UdpServer
from Core.Util.Util import Util
from Core.MessageManager import MessageManager
from Files.Database.DatabaseManager import DatabaseManager
from Files.Database.UserTableManager import UserAccessMode


@Decorators.singleton
class TelegramBotManager:
    def initialize(self):
        token = Util.get_setting('token')
        updater = Updater(token=token)
        dispatcher = updater.dispatcher
        MessageManager.initialize()
        command_handler = MessageHandler(Filters.all, MessageManager.handle_messages)
        dispatcher.add_handler(command_handler)
        updater.start_polling()
        self.bot: Bot = updater.bot
        UdpServer().start()
        ServiceManager.load_services()
        ServiceManager.start_services()
        self.send_started_message()

    def send_started_message(self):
        self.send_broadcast_message("Bot is started!", UserAccessMode.ADMIN)

    def send_broadcast_message(self, text, user_access=UserAccessMode.USER):
        try:
            # send user_access as None to send messages to all users
            if user_access is None:
                filter_result = DatabaseManager().userTableManager.select("Users")
            else:
                filter_result = DatabaseManager().userTableManager.select("Users", {"access": user_access})
            if len(filter_result) > 0:
                for user in filter_result:
                    if user.chat_id != 0:
                        self.bot.send_message(chat_id=user.chat_id, text=text)
        except Exception as e:
            logging.error(str(e))
