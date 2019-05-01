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
        self.send_started_message()
        self.user_history = {}
        UdpServer().start()
        ServiceManager.load_services()
        ServiceManager.start_services()

    def send_started_message(self):
        filter_result = BotDatabase().filter(Tables.USERS,
                                             lambda row: row[UsersTableMap.ACCESS] == UsersAccessMode.ADMIN)
        if filter_result.count > 0:
            for admin in filter_result.rows:
                if UsersTableMap.CHAT_ID in admin:
                    chat_id = admin[UsersTableMap.CHAT_ID]
                    self.bot.send_message(chat_id=chat_id, text="Bot has been Started!")
