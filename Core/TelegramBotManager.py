from telegram import Bot
from telegram.ext import Updater, MessageHandler, Filters
from Core.Decorators import singleton
from Core.ServiceManager import ServiceManager
from Core.UdpServer import UdpServer
from Core.Util.Util import Util
from Files.Database.BotDatabase import BotDatabase, Tables
from Files.Database.TableMaps import UsersTableMap, UsersAccessMode
from Core.MessageManager import MessageManager


@singleton
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
        self.send_broadcast_message("Bot is started!", UsersAccessMode.ADMIN)

    def send_broadcast_message(self, text, user_access=UsersAccessMode.USER):
        # send user_access as None to send messages to all users
        if user_access is None:
            filter_result = BotDatabase().filter(Tables.USERS)
        else:
            filter_result = BotDatabase().filter(Tables.USERS,
                                                 lambda row: row[UsersTableMap.ACCESS] == user_access)
        if filter_result.count > 0:
            for user in filter_result.rows:
                if UsersTableMap.CHAT_ID in user:
                    chat_id = user[UsersTableMap.CHAT_ID]
                    self.bot.send_message(chat_id=chat_id, text=text)
