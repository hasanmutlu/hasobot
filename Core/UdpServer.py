import logging

from Core import TelegramBotManager
from threading import Thread
import socket
from Core.Util.Util import Util
from Files.Database.UserTableManager import UserAccessMode


class UdpServer(Thread):

    def __init__(self):
        super(UdpServer, self).__init__()
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        self.port = Util.get_setting('udp_port', cls=int)
        self.port_bc = Util.get_setting('udp_broadcast_port', cls=int)

    def run(self):
        udp_enabled = Util.get_setting('udp_enabled', cls=bool)
        if udp_enabled is False or self.port is None:
            return
        self.socket.settimeout(10)
        self.socket.bind(('', self.port))
        while True:
            self.read_package()
            self.send_broadcast_message()

    def send_broadcast_message(self):
        message = f'TelegramBot is running on port:{self.port}'
        self.socket.sendto(message.encode(), ('<broadcast>', self.port_bc))

    def read_package(self):
        try:
            data, address = self.socket.recvfrom(1024)
            message = f'udp package is received from {address} and data is {data}'
            print("Message is", message)
            TelegramBotManager.TelegramBotManager().send_broadcast_message(message, UserAccessMode.ADMIN)
        except Exception as e:
            logging.error(e)
            pass
