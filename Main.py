import os
import logging
from Core.Util.Util import Util
from Core.TelegramBotManager import TelegramBotManager

if __name__ == '__main__':
    try:
        program_path = os.path.dirname(__file__)
        if program_path is not '':
            os.chdir(program_path)
        logging.basicConfig(filename=Util.get_abs_file_name("hasobot.log"),
                            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                            level=logging.INFO)
        TelegramBotManager().initialize()
    except Exception as e:
        logging.error(str(e))
