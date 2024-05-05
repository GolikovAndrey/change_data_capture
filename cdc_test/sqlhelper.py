import datetime
import time

import sqlalchemy
import random as r
import pandas as pd
from clickhouse_driver import Client
from clickhouse_sqlalchemy import make_session
import cdc_test.value_generators as vg

from cdc_test.connection_parameters import CONN_PARAMS

class SQLHelper:
    def __init__(self, insert_count: int = 0, update_count: int = 0, delete_count: int = 0, count_log: bool = True):
        self.insert_count = insert_count
        self.update_count = update_count
        self.delete_count = delete_count
        self.count_log = count_log
        self.conn_params = CONN_PARAMS

        if self.count_log:
            print(f"Кол-во операций INSERT: {self.insert_count}")
            print(f"Кол-во операций UPDATE: {self.update_count}")
            print(f"Кол-во операций DELETE: {self.delete_count}")

    def run_transactions(self):
        if self.insert_count > 0:
            self.insert_row()
        if self.update_count > 0:
            self.update_row()
        if self.delete_count > 0:
            self.delete_row()
        print("Транзакции были проведены успешно.")

    def create_mysql_table(self):
        user_creds = f"{self.conn_params['MYSQL_USER']}:{self.conn_params['MYSQL_PASSWORD']}"
        db_creds = f"{self.conn_params['MYSQL_HOST']}:{self.conn_params['MYSQL_PORT']}"

        engine = sqlalchemy.create_engine(f"mysql+mysqlconnector://{user_creds}@{db_creds}")

        with engine.connect() as conn:
            conn.execute("CREATE DATABASE IF NOT EXISTS cdc;")
            conn.execute("USE cdc;")
            conn.execute("""
                CREATE TABLE IF NOT EXISTS test_table(
                    id int NOT NULL AUTO_INCREMENT,
                    int_val int NOT NULL,
                    str_val VARCHAR(20),
                    double_val DECIMAL(10, 2),
                    datetime_val TIMESTAMP NOT NULL,
                    PRIMARY KEY (`id`)
                )
                ENGINE=InnoDB 
                DEFAULT CHARSET=utf8mb4;
            """)
        print("Создана таблица в MySQL.")

    def create_clickhouse_table(self):
        client = Client(
            host=self.conn_params['CH_HOST'],
            user=self.conn_params['CH_USER'],
            password=self.conn_params['CH_PASSWORD']
        )

        client.execute("CREATE DATABASE IF NOT EXISTS cdc;")
        client.execute("USE cdc;")
        client.execute("""
            CREATE TABLE IF NOT EXISTS cdc.`test_table` (
                id Int32,
                int_val Int32,
                str_val Varchar(20) DEFAULT NULL,
                double_val Decimal(10, 2) DEFAULT NULL,
                datetime_val DateTime,
                created_at DateTime DEFAULT now(),
                is_deleted UInt8 DEFAULT 0
            ) 
            ENGINE=ReplacingMergeTree(created_at, is_deleted)
            ORDER BY id
            SETTINGS index_granularity = 8192;
        """)

        print("Создана таблица в ClickHouse")

    def create_tables(self):
        self.create_mysql_table()
        self.create_clickhouse_table()

    def get_mysql_connection(self):
        user_creds = f"{self.conn_params['MYSQL_USER']}:{self.conn_params['MYSQL_PASSWORD']}"
        db_creds = f"{self.conn_params['MYSQL_HOST']}:{self.conn_params['MYSQL_PORT']}"
        db = "cdc"
        extras = "charset=utf8mb4"
        engine = sqlalchemy.create_engine(f"mysql+mysqlconnector://{user_creds}@{db_creds}/{db}?{extras}")
        connection = engine.connect()

        return connection

    def execute_query(self, query: str):
        with self.get_mysql_connection() as conn:
            return conn.execute(query)

    def insert_row(self) -> None:
        start = datetime.datetime.now()
        print(f"Начало транзакций (INSERT): {start}")
        for i in range(self.insert_count):
            query = f"""
                INSERT INTO test_table(
                    int_val, 
                    str_val, 
                    double_val,
                    datetime_val
                )
                VALUES (
                    {vg.generate_int_value()},
                    '{vg.generate_str_value()}',
                    {vg.generate_double_value()},
                    '{vg.generate_timestamp_value()}'
                )
            """

            self.execute_query(query)

        end = datetime.datetime.now()
        print(f"Конец транзакций (INSERT): {end}")
        print(f"Транзакции были выполнены за {(end - start).seconds} секунд {(start - end).microseconds} миллисекунд.")

    def delete_row(self) -> None:
        start = datetime.datetime.now()
        print(f"Начало транзакций (DELETE): {start}")
        for i in range(self.delete_count):
            query = f"""
                DELETE FROM test_table 
                WHERE id = {self.get_random_id()}
            """

            self.execute_query(query)

        end = datetime.datetime.now()
        print(f"Конец транзакций (DELETE): {end}")
        print(f"Транзакции были выполнены за {(end - start).seconds} секунд {(start - end).microseconds} миллисекунд.")

    def update_row(self) -> None:
        start = datetime.datetime.now()
        print(f"Начало транзакций (UPDATE): {start}")

        for i in range(self.update_count):
            query = f"""
                UPDATE test_table
                SET int_val = {vg.generate_int_value()},
                    str_val = '{vg.generate_str_value()}',
                    double_val = {vg.generate_double_value()},
                    datetime_val = '{vg.generate_timestamp_value()}'
                WHERE id = {self.get_random_id()}
            """

            self.execute_query(query)

        end = datetime.datetime.now()
        print(f"Конец транзакций (UPDATE): {end}")
        print(f"Транзакции были выполнены за {(end - start).seconds} секунд {(start - end).microseconds} миллисекунд.")

    def get_random_id(self) -> int:
        min_max = (
            self.execute_query(f"""
                SELECT id
                FROM test_table
            """)
            .fetchall()
        )

        return int(*r.choice(min_max))

    def read_clickhouse_table(self, query: str) -> pd.DataFrame:
        ch_session = self.get_clickhouse_session()

        with ch_session.connection() as ch_connection:
            dataframe = pd.read_sql(
                sql=query,
                con=ch_connection
            )

        return dataframe

    def get_clickhouse_session(self):
        user_creds = f"{self.conn_params['CH_USER']}:{self.conn_params['CH_PASSWORD']}"
        db_creds = f"{self.conn_params['CH_HOST']}:{self.conn_params['CH_PORT']}/{self.conn_params['CH_DATABASE']}"
        extras = "connect_timeout=300&send_receive_timeout=300&sync_request_timeout=300"

        engine = sqlalchemy.create_engine(f"clickhouse+native://{user_creds}@{db_creds}?{extras}")
        session = make_session(engine=engine)

        return session

    def read_mysql_table(self, query) -> pd.DataFrame:

        with self.get_mysql_connection() as mysql_conn:
            dataframe = pd.read_sql(
                sql=query,
                con=mysql_conn
            )

        return dataframe