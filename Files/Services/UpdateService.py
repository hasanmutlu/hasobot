import logging
import os
import sys
import shutil
import zipfile

import requests
from bs4 import BeautifulSoup
from Core.IService import IService
from Core.ServiceManager import ServiceManager
from Core.Util.Util import Util


class UpdateService(IService):

    def __init__(self):
        super(UpdateService, self).__init__(60 * 60 * 24)

    def get_server_commit_number(self):
        page_content = requests.get(Util.get_setting('repository_url', 'update'))
        page_content = BeautifulSoup(page_content.content, 'lxml')
        commit_element = page_content.select('.commits a .num')
        if len(commit_element) <= 0:
            return None
        else:
            try:
                return int(commit_element[0].text.strip())
            except ValueError as e:
                logging.error("Error : " + str(e))
                return None

    def download_and_extract_update(self, path):
        update_zip = requests.get(Util.get_setting('update_file_url', 'update'))
        if os.path.exists(path) is False:
            os.mkdir(path)
        update_file = open(f'{path}/update.zip', 'wb')
        update_file.write(update_zip.content)
        update_file.close()
        update_file = zipfile.ZipFile(f'{path}/update.zip', 'r')
        update_file.extractall(f'{path}/')
        os.remove(f'{path}/update.zip')

    def update_program(self):
        folder_update = '../.hasobot_update'
        self.download_and_extract_update(folder_update)
        folder_path = os.path.dirname(os.path.abspath(sys.argv[0]))
        Util.copytree(folder_update + '/hasobot-master', folder_path)
        shutil.rmtree(folder_update)
        os.chdir(folder_path)

    def check_and_update(self):
        server_version = self.get_server_commit_number()
        current_version = Util.get_setting('current_version', 'update', int)
        if server_version != current_version:
            ServiceManager().stop_services()
            self.update_program()
            Util.set_setting(server_version, 'current_version', 'update')
            print('Program is updated!')
            Util.restart_program()

    def initialize(self):
        print("Update Service is initialized!")

    def run_service(self):
        enable_auto_update = Util.get_setting('enable_auto_update', 'general', bool)
        if enable_auto_update is True:
            print("Update Service is running!")
            self.check_and_update()