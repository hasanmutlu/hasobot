from inspect import signature
from telegram import Update
from Core.Util.BotUtil import BotUtil

"""
    Telegram bot deals custom listeners with this interface
"""


class IMessageListener:

    def handle(self, update: Update):
        command = BotUtil.get_message_command(update).lower()
        function_name = "handle_" + command
        if command is not None:
            handler_function = getattr(self.__class__, function_name, None)
            if handler_function is None:
                return False
            else:
                args = signature(handler_function).parameters
                if 'self' in args:
                    handler_function(self, update)
                else:
                    handler_function(update)
                return True
