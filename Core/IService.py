import logging
from threading import Thread, Event

"""
    Telegram bot deals custom services with this interface
"""


class IService(Thread):
    def __init__(self, interval=None):
        super(IService, self).__init__()
        self.__interval__ = interval
        self.__is_stopped__ = Event()
        self.initialize()

    def stop(self):
        self.__is_stopped__.set()

    def initialize(self):
        raise NotImplementedError()

    def run(self):
        while True:
            try:
                self.run_service()
                if self.__interval__ is None or self.__is_stopped__.wait(self.__interval__):
                    break
            except Exception as e:
                logging.error(str(e))

    def run_service(self):
        raise NotImplementedError()
