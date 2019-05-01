from telegram import Update, Bot
from Core.Util.ImportUtil import ImportUtil


class MessageManager:
    __listener_list__ = []
    __initialized__ = False

    @staticmethod
    def initialize():
        class_list = ImportUtil.import_classes_from_folder("Files/MessageListeners")
        MessageManager.__listener_list__ = [class_[1]() for class_ in class_list]
        MessageManager.__initialized__ = True

    @staticmethod
    def handle_messages(bot: Bot, update: Update):
        if MessageManager.__initialized__ is False:
            MessageManager.initialize()
        _handled = False
        for listener in MessageManager.__listener_list__:
            listener_result = listener.handle(update)
            _handled |= False if listener_result is None else listener_result
        if _handled is False:
            bot.send_message(chat_id=update.message.chat_id, text="this message is not handled yet")
