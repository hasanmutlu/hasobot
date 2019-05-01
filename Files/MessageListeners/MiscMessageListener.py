import time
import pyttsx3
import requests
import telegram
from bs4 import BeautifulSoup
from telegram import Update, Bot

from Core.Decorators import singleton
from Core.TelegramBotManager import TelegramBotManager
from Core.Util.BotUtil import BotUtil
from Core.Util.Util import Util
from Files.Database.BotDatabase import BotDatabase
from Files.Database.TableMaps import UsersTableMap, UsersAccessMode
from Files.Database.Users import check_user, Users
from Core.IMessageListener import IMessageListener
from Files.MessageListeners.HelpMessageListener import bot_help


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
        if Users.is_user_exist(telegram_id) is False:
            message = "You are new user"
            _user = BotUtil.get_user_data(update)
            Users.add_new_user(_user)
            BotDatabase().save()
        else:
            _user = Users.get_user(telegram_id)
            message = "Welcome back {0} {1}!!".format(_user[UsersTableMap.FIRST_NAME],
                                                      _user[UsersTableMap.LAST_NAME])
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
        func_result, bot_result = exec_cmd_bot(telegram_id=telegram_id, command=command)
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
    def handle_capture(update: Update):
        # Define the duration (in seconds) of the video capture here
        capture_duration = 10

        cap = cv2.VideoCapture(0)

        # Define the codec and create VideoWriter object
        fourcc = cv2.VideoWriter_fourcc(*'XVID')
        out = cv2.VideoWriter('output.avi', fourcc, 30.0, (640, 480))

        start_time = time.time()
        while (int(time.time() - start_time) < capture_duration):
            ret, frame = cap.read()
            if ret == True:
                frame = cv2.flip(frame, 0)

                # write the flipped frame
                out.write(frame)

                cv2.imshow('frame', frame)
                # if cv2.waitKey(1) & 0xFF == ord('q'):
                #    break
            else:
                break

        # Release everything if job is finished
        cap.release()
        out.release()
        cv2.destroyAllWindows()
        telegram_id = BotUtil.get_telegram_id(update)
        func_result, bot_result = get_file_stream(telegram_id=telegram_id, file_name="output.avi")
        TelegramBotManager().bot.send_video(chat_id=update.message.chat_id, video=func_result)


@check_user(UsersAccessMode.ADMIN)
def get_file_stream(*, telegram_id, file_name):
    return open(file_name, 'rb')


@check_user(UsersAccessMode.ADMIN)
def exec_cmd_bot(*, telegram_id, command):
    res, output, error = Util.execute(command)
    if len(output) == 0:
        output = "Empty"
    return output


@check_user(UsersAccessMode.ADMIN)
def reboot_bot(*, telegram_id):
    Util.execute("reboot")


@check_user(UsersAccessMode.ADMIN)
def shutdown_bot(*, telegram_id):
    Util.execute("shutdown now -h")


@check_user(UsersAccessMode.ADMIN)
def exec_python(*, telegram_id, cmd):
    exec(cmd)


@check_user(UsersAccessMode.ADMIN)
def speak_bot(*, telegram_id, text):
    MiscMessageListener().speak(text)
