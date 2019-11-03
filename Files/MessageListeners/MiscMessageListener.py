import pyttsx3
import requests
import telegram
from bs4 import BeautifulSoup
from telegram import Update

from Core.Decorators import singleton
from Core.TelegramBotManager import TelegramBotManager
from Core.Util.BotUtil import BotUtil
from Core.Util.Util import Util
from Core.IMessageListener import IMessageListener
from Files.Database.DatabaseManager import DatabaseManager, check_user_access
from Files.Database.UserTableManager import UserAccessMode
from Files.MessageListeners.HelpMessageListener import bot_help
from Files.Services.UpdateService import UpdateService


@singleton
class MiscMessageListener(IMessageListener):
    def __init__(self, language='turkish', rate=120):
        self.__speak_engine__ = pyttsx3.init()
        voices = self.__speak_engine__.getProperty('voices')
        self.__speak_engine__.setProperty('rate', rate)
        for voice in voices:
            if voice.id == language:
                self.__speak_engine__.setProperty('voice', voice.id)
                break

    def speak(self, text):
        self.__speak_engine__.say(text)
        self.__speak_engine__.runAndWait()

    @bot_help("If calling user have admin access, this command converts given message to speech ")
    def handle_speak(self, update: Update):
        telegram_id = BotUtil.get_telegram_id(update)
        message = BotUtil.get_message_arguments(update)
        # func_result, bot_result = self.speak(telegram_id=telegram_id, text=message)
        # bot.send_message(chat_id=update.message.chat_id, text=bot_result)
        self.speak(message)

    @staticmethod
    def handle_register(update: Update):
        telegram_id = BotUtil.get_telegram_id(update)
        if DatabaseManager().userTableManager.record_is_exist("Users", "telegram_id", telegram_id) is False:
            message = "You are new user"
            _user = BotUtil.get_user_data(update)
            DatabaseManager().userTableManager.insert_data("Users", _user)
        else:
            _user = DatabaseManager().userTableManager.select("Users", {"telegram_id": telegram_id})[0]
            message = "Welcome back {0} {1}!!".format(_user.first_name,
                                                      _user.last_name)
        TelegramBotManager().bot.send_message(chat_id=update.message.chat_id, text=message)

    @staticmethod
    @bot_help("this command returns current temperature of server")
    def handle_temperature(update: Update):
        res, output, error = Util.execute("vcgencmd measure_temp")
        TelegramBotManager().bot.send_message(chat_id=update.message.chat_id, text=output)

    @staticmethod
    @bot_help("If calling user have admin access, this command restarts server ")
    def handle_reboot(update: Update):
        telegram_id = BotUtil.get_telegram_id(update)
        func_result, bot_result = reboot_bot(telegram_id=telegram_id)
        TelegramBotManager().bot.send_message(chat_id=update.message.chat_id, text=bot_result)

    @staticmethod
    @bot_help("If calling user have admin access, this command shutdowns server ")
    def handle_shutdown(update: Update):
        telegram_id = BotUtil.get_telegram_id(update)
        func_result, bot_result = shutdown_bot(telegram_id=telegram_id)
        TelegramBotManager().bot.send_message(chat_id=update.message.chat_id, text=bot_result)

    @staticmethod
    @bot_help("If calling user have admin access, this command execs given python command on server")
    def handle_python(update: Update):
        telegram_id = BotUtil.get_telegram_id(update)
        cmd = BotUtil.get_message_arguments(update)
        func_result, bot_result = exec_python(telegram_id=telegram_id, cmd=cmd)
        TelegramBotManager().bot.send_message(chat_id=update.message.chat_id, text=bot_result)

    @staticmethod
    @bot_help("this command runs given command and returns result")
    def handle_exec(update: Update):
        telegram_id = BotUtil.get_telegram_id(update)
        command = BotUtil.get_message_arguments(update)
        try:
            func_result, bot_result = exec_cmd_bot(telegram_id=telegram_id, command=command)
        except Exception as e:
            print(e)
        TelegramBotManager().bot.send_message(chat_id=update.message.chat_id, text=func_result)

    @staticmethod
    def handle_getfile(update: Update):
        telegram_id = BotUtil.get_telegram_id(update)
        file_name = BotUtil.get_message_arguments(update)
        func_result, bot_result = get_file_stream(telegram_id=telegram_id, file_name=file_name)
        TelegramBotManager().bot.send_document(chat_id=update.message.chat_id, document=func_result)

    @staticmethod
    def handle_getvideo(update: Update):
        telegram_id = BotUtil.get_telegram_id(update)
        video_len = int(BotUtil.get_message_arguments(update))
        Util.capture_video(video_len)
        func_result, bot_result = get_file_stream(telegram_id=telegram_id, file_name='out.avi')
        TelegramBotManager().bot.send_document(chat_id=update.message.chat_id, document=func_result)

    @staticmethod
    def handle_news(update: Update):
        rss_data = requests.get("http://www.haberturk.com/rss/manset.xml".strip())
        soup = BeautifulSoup(rss_data.content, 'lxml')
        descriptions = soup.find_all("description")
        descriptions = [descriptions[i].string for i in range(len(descriptions)) if i > 0 and i < 4]
        text = "\n\n".join(descriptions)
        # text = map(lambda x: str(x)+"\n\n", descriptions)
        TelegramBotManager().bot.send_message(chat_id=update.message.chat_id, text=str(text))

    @staticmethod
    def handle_test44(update: Update):
        custom_keyboard = [['top-left', 'top-right'], ['bottom-left', 'bottom-right']]
        reply_markup = telegram.ReplyKeyboardMarkup(custom_keyboard)
        TelegramBotManager().bot.send_message(chat_id=update.message.chat_id, text="Custom Keyboard Test",
                                              reply_markup=reply_markup)

    @staticmethod
    def handle_update(update: Update):
        # starts updating manually
        UpdateService.check_and_update()

    @staticmethod
    @bot_help('Returns current public ip of bot')
    def handle_get_ip(update: Update):
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.113 Safari/537.36',
        }
        data = requests.get('https://ip-adresim.net/', headers=headers)

        data = BeautifulSoup(data.content)
        data = data.select('.mycurrentip')[0].text
        TelegramBotManager().bot.send_message(chat_id=update.message.chat_id, text=f'Ip Address:{data}')


@check_user_access(UserAccessMode.ADMIN)
def get_file_stream(*, telegram_id, file_name):
    return open(file_name, 'rb')


@check_user_access(UserAccessMode.ADMIN)
def exec_cmd_bot(*, telegram_id, command):
    res, output, error = Util.execute(command)
    if len(output) == 0:
        output = "Empty"
    return output


@check_user_access(UserAccessMode.ADMIN)
def reboot_bot(*, telegram_id):
    Util.execute("reboot")


@check_user_access(UserAccessMode.ADMIN)
def shutdown_bot(*, telegram_id):
    Util.execute("shutdown now -h")


@check_user_access(UserAccessMode.ADMIN)
def exec_python(*, telegram_id, cmd):
    exec(cmd)


@check_user_access(UserAccessMode.ADMIN)
def speak_bot(*, telegram_id, text):
    MiscMessageListener().speak(text)
