from sqlite3 import Connection
from Entities import DbTable
from Entities.DbTable import Table


class ITableManager:

    def __init__(self):
        self.connection: Connection = None
        self.tables = {}

    def initialize(self, connection: Connection):
        self.connection = connection

    def add_table(self, table: Table):
        if table.name in self.tables:
            raise RuntimeError('given table is already exist')
        else:
            self.tables[table.name] = table

    def create_tables(self):
        for table in self.tables:
            table: Table = self.tables[table]
            create_query = table.get_create_table_query()
            self.connection.execute(create_query)
        self.connection.commit()

    def update_tables(self):
        raise NotImplementedError

    def record_is_exist(self, table_name: str, field: str, value):
        if table_name in self.tables is False:
            raise RuntimeError('given table is not exist!')
        sql_is_exist = f'SELECT COUNT({field}) FROM {table_name} Where {field} = ?;'
        count = self.connection.execute(sql_is_exist, [value]).fetchmany(1)[0][0]
        return True if count >= 1 else False

    def get_id(self, table_name: str, field: str, value, id_field='Id'):
        if table_name in self.tables is False:
            raise RuntimeError('given table is not exist!')
        sql_get = f'SELECT {id_field} FROM {table_name} Where {field} = ?;'
        result = self.connection.execute(sql_get, [value]).fetchall()
        return None if len(result) <= 0 else result[0][0]

    def select(self, table_name, _filter: dict = None):
        if table_name in self.tables is False:
            raise RuntimeError('given table is not exist!')
        sql, parameter_list = self.tables[table_name].get_select_query(_filter)
        sql_result_list = self.connection.execute(sql, parameter_list).fetchall()
        result_list = [DbTable.map_tuple_to_table_object(self.tables[table_name], row_data) for row_data in
                       sql_result_list]
        return result_list

    def insert_data(self, table_name, data):
        # data can be a dictionary or Object
        sql, parameter_list = self.tables[table_name].get_insert_query(data)
        cursor = self.connection.cursor()
        cursor.execute(sql, parameter_list)
        return cursor.lastrowid
