import io
import os
from telegram import Update, Bot

from Core.TelegramBotManager import TelegramBotManager
from Core.Util.Util import Util
from Core.IMessageListener import IMessageListener


class MediaMessageListener(IMessageListener):
    @classmethod
    def handle(cls, update: Update):
        file_id, file_folder = cls.get_file_id(update)
        bot: Bot = TelegramBotManager().bot
        if file_id is not None:
            file = bot.get_file(file_id)
            cls.download_file(file, file_folder)
            bot.send_message(chat_id=update.message.chat_id, text="File is downloaded!")
            return True
        else:
            return False

    @staticmethod
    def get_file_id(update: Update):
        file_id = None
        folder = Util.get_abs_file_name('./')
        if update.message.photo:
            file_id = update.message.photo[-1]
            folder = Util.get_abs_file_name(Util.get_setting('photo', 'media'))
        elif update.message.video:
            file_id = update.message.video.file_id
            folder = Util.get_abs_file_name(Util.get_setting('video', 'media'))
        elif update.message.document:
            file_id = update.message.document[-1]
            folder = Util.get_abs_file_name(Util.get_setting('document', 'media'))
        elif update.message.audio:
            file_id = update.message.audio[-1]
            folder = Util.get_abs_file_name(Util.get_setting('audio', 'media'))
        return file_id, folder

    @staticmethod
    def download_file(file, file_folder):
        if not os.path.exists(file_folder):
            os.makedirs(file_folder)
        file_data = io.BytesIO()
        file.download(out=file_data)
        file_name = os.path.basename(file.file_path)
        file_data.seek(0)
        file = open(file_folder + file_name, 'wb')
        file.write(file_data.read())
        file.close()
        file_data.close()
