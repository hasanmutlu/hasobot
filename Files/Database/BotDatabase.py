from Core.Database import Database, LastIdsTableMap
from Core.Decorators import singleton
from Core.Util.Util import Util


class Tables:
    USERS = "Users"


@singleton
class BotDatabase(Database):
    def __init__(self, file_name: str = "BotDB.db"):
        super().__init__(Util.get_abs_file_name(file_name))
        self.create_table(Tables.USERS)
        self.create_table(LastIdsTableMap.TABLE_NAME)
