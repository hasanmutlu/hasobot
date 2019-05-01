import requests
from bs4 import BeautifulSoup
from telegram import Update

from Core.Decorators import singleton
from Core.IMessageListener import IMessageListener
from Core.TelegramBotManager import TelegramBotManager
from Files.MessageListeners.HelpMessageListener import bot_help


class ExchangeDataMap:
    NAME = "isim"
    BUYING = "forexbuying"
    SELLING = "forexselling"


@singleton
class ExchangeMessageListener(IMessageListener):
    @staticmethod
    def get_first_tag_value(soup_data: BeautifulSoup, tag):
        res = soup_data.find(tag)
        return res.contents[0] if len(res) > 0 else ""

    def get_exchange_data(self):
        xml_data = requests.get("http://www.tcmb.gov.tr/kurlar/today.xml")
        soup = BeautifulSoup(xml_data.content, 'lxml')
        data = [item for item in soup.find_all("currency")]
        data = ["{0}  {1}  {2} ".format(
            self.get_first_tag_value(item, ExchangeDataMap.NAME),
            self.get_first_tag_value(item, ExchangeDataMap.BUYING),
            self.get_first_tag_value(item, ExchangeDataMap.SELLING)
        ) for item in data]
        text = '\n'.join(data)
        return text

    @staticmethod
    @bot_help("this command returns current exchange information")
    def handle_exchange(self, update: Update):
        result = self.get_exchange_data()
        TelegramBotManager().bot.send_message(chat_id=update.message.chat_id, text=result)
