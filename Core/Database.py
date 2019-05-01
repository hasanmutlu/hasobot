import json
import logging
import os
import sys
from threading import Lock


class LastIdsTableMap:
    TABLE = "table"
    LAST_ID = "last_id"
    TABLE_NAME = "Last_Ids"


class Database:
    __LOCK__ = Lock()

    def __init__(self, file_name=None):
        self.__file_name__ = file_name
        self.__tables__ = {}
        if self.__file_name__ is not None:
            try:
                Database.__LOCK__.acquire()
                file_name = file_name
                if os.path.isfile(file_name):
                    file = open(file_name)
                    data = file.read()  # .replace('\n', '').replace('\r', '')
                    self.__tables__ = json.loads(data)
                    file.close()
            finally:
                Database.__LOCK__.release()

    # return table according to given table name.
    # overwrites [] operator
    def __getitem__(self, item):
        if type(item) is str:
            return self.__tables__[item]
        else:
            return None

    # return if given item name in tables or not
    # overwrites in operator
    def __contains__(self, item):
        return item in self.__tables__

    # filters given table's data according with given function
    def filter(self, table_name: str, func):
        _result = FilterResult()
        try:
            table = self[table_name]
            _result.indexes = [i for i in range(0, len(table)) if func(table[i]) is True]
            _result.rows = [table[i] for i in _result.indexes]
            _result.count = len(_result.indexes)
        except Exception as e:
            logging.error(str(e))
            print("Unexpected error:", sys.exc_info()[0])
        return _result

    # creates table with given name
    def create_table(self, name, force=False):
        if name not in self or force is True:
            self.__tables__[name] = []
            if LastIdsTableMap.TABLE_NAME not in self:
                last_id_table = [{LastIdsTableMap.TABLE: table_name, LastIdsTableMap.LAST_ID: len(table) + 1} for
                                 table_name, table in self.__tables__.items()]
                self.__tables__[LastIdsTableMap.TABLE_NAME] = last_id_table

    # saves database to file in json format
    def save(self, file_name=None):
        if file_name is None and self.__file_name__ is None:
            file_name = "database.db"
        else:
            file_name = self.__file_name__
        try:
            Database.__LOCK__.acquire()
            output = json.dumps(self.__tables__, indent=4, sort_keys=True, )
            file = open(file_name, "w")
            file.write(output)
            file.close()
        finally:
            Database.__LOCK__.release()

    # returns last id of given table_name
    def get_last_id(self, table_name: str):
        filter_result = self.filter(LastIdsTableMap.TABLE_NAME,
                                    lambda row: row[LastIdsTableMap.TABLE] == table_name)
        if filter_result.count > 0:
            last_id = filter_result.rows[0][LastIdsTableMap.LAST_ID]
            return int(last_id)
        else:
            self[LastIdsTableMap.TABLE_NAME].append({LastIdsTableMap.TABLE: table_name, LastIdsTableMap.LAST_ID: 1})
            return 1

    def increment_last_id(self, table_name: str):
        try:
            last_id = self.get_last_id(table_name) + 1
            records = self.filter(LastIdsTableMap.TABLE_NAME,
                                  lambda row: row[LastIdsTableMap.TABLE] == table_name)
            data_index = records.indexes[0]
            data = records.rows[0]
            data[LastIdsTableMap.LAST_ID] = last_id
            self.__tables__[LastIdsTableMap.TABLE_NAME][data_index] = data
            self.save()
        except Exception as e:
            logging.debug("{0} increment_last_id error \n\n{1} ".format(table_name, str(e)))

    # reconsider save
    def insert(self, table_name: str, data):
        data['id'] = self.get_last_id(table_name)
        self[table_name].append(data)
        self.increment_last_id(table_name)
        self.save()

    def get_by_index(self, table_name: str, index: int):
        try:
            return self.__tables__[table_name][index]
        except Exception as e:
            logging.error(e)
            return None

    def update(self, table_name: str, index: int, new_data):
        try:
            self.__tables__[table_name][index] = new_data
            self.save()
        except Exception as e:
            logging.error(e)

    def delete(self, table_name, filter_function):
        if table_name in self:
            self.__tables__[table_name] = [item for item in self[table_name] if filter_function(item) is False]
            self.save()
        else:
            logging.error('Table {0} is not exist\n'.format(table_name))

    def print(self):
        print(self.__tables__)


class FilterResult:
    def __init__(self):
        self.count = 0
        self.rows = []
        self.indexes = []
