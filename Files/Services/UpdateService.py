import logging
import os
import sys
import shutil
import zipfile

import requests
from bs4 import BeautifulSoup
from Core.IService import IService
from Core.ServiceManager import ServiceManager
from Core.TelegramBotManager import TelegramBotManager
from Core.Util.Util import Util
from Files.Database.BotDatabase import BotDatabase, Tables
from Files.Database.TableMaps import UsersTableMap, UsersAccessMode


class UpdateService(IService):

    def __init__(self):
        update_interval = Util.get_setting('update_interval', cls=int)
        if update_interval is None:
            update_interval = 60 * 60 * 24  # check updates daily
        super(UpdateService, self).__init__(update_interval)

    @staticmethod
    def get_server_commit_number():
        page_content = requests.get(Util.get_setting('repository_url', 'update'))
        page_content = BeautifulSoup(page_content.content)
        commit_element = page_content.select('.commits a .num')
        if len(commit_element) <= 0:
            return None
        else:
            try:
                return int(commit_element[0].text.strip())
            except ValueError as e:
                logging.error("Error : " + str(e))
                return None

    @staticmethod
    def download_and_extract_update(path):
        update_zip = requests.get(Util.get_setting('update_file_url', 'update'))
        if os.path.exists(path) is False:
            os.mkdir(path)
        update_file = open(f'{path}/update.zip', 'wb')
        update_file.write(update_zip.content)
        update_file.close()
        update_file = zipfile.ZipFile(f'{path}/update.zip', 'r')
        update_file.extractall(f'{path}/')
        os.remove(f'{path}/update.zip')

    @staticmethod
    def update_program():
        folder_update = '../.hasobot_update'
        UpdateService.download_and_extract_update(folder_update)
        folder_path = os.path.dirname(os.path.abspath(sys.argv[0]))
        Util.copytree(folder_update + '/hasobot-master', folder_path)
        shutil.rmtree(folder_update)
        os.chdir(folder_path)

    @staticmethod
    def check_and_update():
        server_version = UpdateService.get_server_commit_number()
        current_version = Util.get_setting('current_version', 'update', int)
        if server_version != current_version:
            filter_result = BotDatabase().filter(Tables.USERS,
                                                 lambda row: row[UsersTableMap.ACCESS] == UsersAccessMode.ADMIN)
            if filter_result.count > 0:
                for admin in filter_result.rows:
                    if UsersTableMap.CHAT_ID in admin:
                        chat_id = admin[UsersTableMap.CHAT_ID]
                        message = 'Bot is updating to new version!'
                        TelegramBotManager().bot.send_message(chat_id=chat_id, text=message)
            ServiceManager().stop_services()
            UpdateService.update_program()
            Util.set_setting(server_version, 'current_version', 'update')
            print('Program is updated!')
            Util.restart_program()

    def initialize(self):
        print("Update Service is initialized!")

    def run_service(self):
        enable_auto_update = Util.get_setting('enable_auto_update', 'general', bool)
        if enable_auto_update is True:
            print("Update Service is running!")
            UpdateService.check_and_update()
