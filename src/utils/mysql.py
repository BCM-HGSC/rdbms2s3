import sqlalchemy
import pandas as pd
import pymysql

class mysql_retriever(object):
    def __init__(self, config, table_name):
        self.url = config.database.url
        self.schema = config.database.schema
        self.password = config.database.password
        self.table_name = table_name

    def retrieve_data(self):
        conn_str = f'mysql+pymysql://{self.schema}:{self.password}@{self.url}'
        conn = sqlalchemy.create_engine(conn_str)
        sql_str  = f"SELECT * FROM {self.table_name}"
        ref = pd.read_sql_query(sql_str, con=conn, chunksize=1000)
        df_list = [i for i in ref]
        df = pd.concat(df_list).reset_index(drop=True)
        return df



