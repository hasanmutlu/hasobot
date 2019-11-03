import functools

from telegram import Update

from Core.Decorators import singleton
from Core.IMessageListener import IMessageListener
from Core.TelegramBotManager import TelegramBotManager


def bot_help(description):
    help_obj = HelpMessageListener()

    def bot_help_decorator(func):
        func_name = func.__name__.replace('handle_', '')
        if func_name not in help_obj.__help__:
            help_obj.__help__[func_name] = description

        @functools.wraps(func)
        def _bot_help_decorator(*args, **kwargs):
            return func(*args, **kwargs)

        return _bot_help_decorator

    return bot_help_decorator


@singleton
class HelpMessageListener(IMessageListener):
    def __init__(self):
        self.__help__ = {}

    def handle_help(self, update: Update):
        result = ""
        for command in self.__help__:
            result += "<b>{0}</b> -> {1}\n\n".format(command, self.__help__[command])
        TelegramBotManager().bot.send_message(chat_id=update.message.chat_id, text=result, parse_mode='html')
