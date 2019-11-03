from Core.Util.Util import Util, Object


class Field:

    def __init__(self, name: str, field_type: type, length=0, is_primary_key=False):
        self.name = name
        self.is_primary_key = is_primary_key
        self.field_type = field_type
        self.length = length
        if is_primary_key and field_type != int:
            raise RuntimeError('only integer data types can be primary key!!')

    def __get_integer_create_query_string__(self) -> str:
        result = f"{self.name} INTEGER"
        if self.is_primary_key:
            result += " PRIMARY KEY"
        return result

    def __get_text_create_query_string__(self) -> str:
        result = f"{self.name}"
        if 0 < self.length <= 255:
            result += f" VARCHAR({self.length})"
        else:
            result += " TEXT"
        return result

    def __get_real_create_query_string__(self) -> str:
        return f"{self.name} DECIMAL"

    def get_create_query_string(self) -> str:
        if self.field_type == int:
            return self.__get_integer_create_query_string__()
        elif self.field_type == str:
            return self.__get_text_create_query_string__()
        elif self.field_type == float:
            return self.__get_real_create_query_string__()
        else:
            raise RuntimeError("unknown field type")


class Table:

    def __init__(self, name, attributes: []):
        self.name = name
        if Util.check_list_type(attributes, Field) is False:
            print("given attributes type should be TableField")
            raise RuntimeError()
        else:
            self.attributes = attributes

    def __get_attributes_create_query_string(self):
        result = ""
        for _field in self.attributes:
            result += _field.get_create_query_string() + ",\n"
        result = result[0:len(result) - 2]  # added to remove last ,
        return result

    def get_create_table_query(self):
        attributes_query_str = self.__get_attributes_create_query_string()
        result = f"CREATE TABLE IF NOT EXISTS {self.name}(\n{attributes_query_str});"
        return result

    def get_insert_query(self, data: Object):
        field_list = [field.name for field in self.attributes if field.is_primary_key is False and field.name in data]
        parameter_list = [data[field] for field in field_list]
        if len(field_list) > 0:
            parameters_str = ','.join('?' * len(field_list))
            result = f"INSERT INTO {self.name}({','.join(field_list)}) VALUES({parameters_str});"
            return result, parameter_list
        else:
            raise RuntimeError('Given Data is not suitable!')

    def get_update_query(self, data: Object, filter_field, filter_value):
        field_list = [field.name for field in self.attributes if field.is_primary_key is False and field.name in data]
        parameter_list = [data[field] for field in field_list]
        if len(field_list) > 0:
            result = f"UPDATE {self.name} SET{' = ?,'.join(field_list)} WHERE {filter_field} = ?;"
            parameter_list.append(filter_value)
            return result, parameter_list
        else:
            raise RuntimeError('Given Data is not suitable!')

    def get_select_query(self, _filter: Object = None, selected_fields: list = None):
        if selected_fields is None:
            select_list = '*'
        else:
            select_list = [field.name for field in self.attributes if field.name in selected_fields]
            select_list = ','.join(select_list)
        if _filter is not None:
            field_list = [field.name for field in self.attributes if field.name in _filter]
            parameter_list = [_filter[field] for field in field_list]
            field_list = [f'{field} = ?' for field in field_list]
            field_list = ' AND '.join(field_list)
            result = f"SELECT {select_list} FROM {self.name} WHERE {field_list};"
            return result, parameter_list
        else:
            result = f"SELECT {select_list} FROM {self.name};"
            return result, []


def map_tuple_to_table_object(table: Table, data: ()):
    if len(table.attributes) != len(data):
        raise RuntimeError('Given tuple is not match given table attributes!')
    result = Object()
    index = 0
    for attribute in table.attributes:
        result[attribute.name] = data[index]
        index += 1
    return result
