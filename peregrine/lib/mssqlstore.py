"""
The datastore script consolidates methods to connect to the CMDB traditional data store.
"""

import pyodbc


class DataStore:

    def __init__(self, cfg):
        """
        Datastore initialization. Connection to the database is configured. A cursor is created.
        :param cfg: Ini file object.
        :return:
        """
        server = cfg['MSSql']['server']
        database = cfg['MSSql']['database']
        username = cfg['MSSql']['username']
        password = cfg['MSSql']['password']
        conndriver = 'DRIVER={ODBC Driver 13 for SQL Server};'
        connstr = 'SERVER={s};DATABASE={db};UID={u};PWD={p}'.format(s=server, db=database, u=username, p=password)
        self.conn = pyodbc.connect(conndriver + connstr)
        self.cursor = self.conn.cursor()

    def close(self):
        self.conn.close()

    def res_query(self, query):
        """
        This function will return the result of the query as a list of records. Each record is represented as a
        dictionary.

        :param query:

        :return: list of records in dictionary format.
        """
        res_set = []
        self.cursor.execute(query)
        field_names = [i[0] for i in self.cursor.description]
        for rec in self.cursor:
            res_dict = {}
            for cnt in range(len(field_names)):
                res_dict[field_names[cnt]] = rec[cnt]
            res_set.append(res_dict)
        return res_set

    def get_fields(self, tablename):
        fieldnames = []
        query = "SELECT TOP(1) * FROM {tn}".format(tn=tablename)
        self.cursor.execute(query)
        for field in self.cursor.description:
            name = field[0]
            form = field[1]
            size = field[3]
            if str(form) == "<class 'str'>" and size <= 4096:
                fieldnames.append(name)
        return fieldnames
