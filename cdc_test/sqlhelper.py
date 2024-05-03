import sqlalchemy
import cdc_test.value_generators as vg
import random as r

from cdc_test.connection_parameters import CONN_PARAMS

class SQLHelper:
    def __init__(self, insert_count: int = 0, update_count: int = 0, delete_count: int = 0):
        self.insert_count = insert_count
        self.update_count = update_count
        self.delete_count = delete_count

        print(f"Кол-во операций INSERT: {self.insert_count}")
        print(f"Кол-во операций UPDATE: {self.update_count}")
        print(f"Кол-во операций DELETE: {self.delete_count}")

    def run_transactions(self):
        self.insert_row()
        self.update_row()
        self.delete_row()
        print("Транзакции были проведены успешно.")

    def create_database(self):
        user_creds = f"{CONN_PARAMS['MYSQL_USER']}:{CONN_PARAMS['MYSQL_PASSWORD']}"
        db_creds = f"{CONN_PARAMS['MYSQL_HOST']}:{CONN_PARAMS['MYSQL_PORT']}"

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
        print("Произведена инициализация для тестирования CDC.")

    def create_mysql_engine(self):
        user_creds = f"{CONN_PARAMS['MYSQL_USER']}:{CONN_PARAMS['MYSQL_PASSWORD']}"
        db_creds = f"{CONN_PARAMS['MYSQL_HOST']}:{CONN_PARAMS['MYSQL_PORT']}"
        db = "cdc"
        extras = "charset=utf8mb4"
        engine = sqlalchemy.create_engine(f"mysql+mysqlconnector://{user_creds}@{db_creds}/{db}?{extras}")
        connection = engine.connect()

        return connection

    def execute_query(self, query: str):
        with self.create_mysql_engine() as conn:
            return conn.execute(query)

    def insert_row(self) -> None:
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

    def delete_row(self) -> None:
        for i in range(self.delete_count):
            query = f"""
                DELETE FROM test_table 
                WHERE id = {self.get_random_id()}
            """

            self.execute_query(query)

    def update_row(self) -> None:
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

    def get_random_id(self) -> int:
        min_max = (
            self.execute_query(f"""
                SELECT id
                FROM test_table
            """)
            .fetchall()
        )

        return int(*r.choice(min_max))