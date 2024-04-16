import os
import sqlalchemy
import cdc_test.value_generators as vg

CONN_PARAMS = {
    'MYSQL_USER': os.environ['MYSQL_USER'],
    'MYSQL_PASSWORD': os.environ['MYSQL_PASSWORD'],
    'MYSQL_HOST': os.environ['MYSQL_HOST'],
    'MYSQL_PORT': os.environ['MYSQL_PORT'],
    'MYSQL_DATABASE': os.environ['MYSQL_DATABASE']
}

class SQLHelper:

    def ___init___(self):
        user_creds = f"{CONN_PARAMS['MYSQL_USER']}:{CONN_PARAMS['MYSQL_PASSWORD']}"
        db_creds = f"{CONN_PARAMS['MYSQL_HOST']}:{CONN_PARAMS['MYSQL_PORT']}"
        extras = "charset=utf8mb4"

        engine = sqlalchemy.create_engine(f"mysql+mysqlconnector://{user_creds}@{db_creds}?{extras}")

        with engine.connect() as conn:
            conn.exectute("""
                CREATE DATABASE IF NOT EXISTS cdc_test;
                
                USE cdc_test;
                
                CREATE TABLE IF NOT EXISTS test_table(
                    id int NOT NULL AUTO_INCREMENT,
                    int_val int NOT NULL,
                    str_val VARCHAR(20),
                    double_val DECIMAL(14, 12),
                    datetime_val TIMESTAMP NOT NULL,
                    json_val JSON NOT NULL
                    PRIMARY KEY (id)
                );
            """)
        print("Произведена инициализация для тестирования CDC.")

    def create_mysql_engine(self):
        user_creds = f"{CONN_PARAMS['MYSQL_USER']}:{CONN_PARAMS['MYSQL_PASSWORD']}"
        db_creds = f"{CONN_PARAMS['MYSQL_HOST']}:{CONN_PARAMS['MYSQL_PORT']}"
        db = CONN_PARAMS['MYSQL_DATABASE']
        extras = "charset=utf8mb4"

        return sqlalchemy.create_engine(f"mysql+mysqlconnector://{user_creds}@{db_creds}/{db}?{extras}")

    def execute_query(self, query: str):
        with self.create_mysql_engine() as conn:
            print("Будет проведена следующая операция:")
            print(query)
            return conn.execute(query)

    def insert_row(self):
        
        query = f"""
            INSERT INTO test_table(
                int_val, 
                str_val, 
                double_val, 
                json_val, 
                array_val
            )
            VALUES (
                {vg.generate_int_value()},
                {vg.generate_str_value()},
                {vg.generate_double_value()},
                {vg.generate_timestamp_value()},
                {vg.genarate_array()}
            )
        """
        
        self.execute_query(query)

    def delete_row(self):

        query = f"""
            DELETE FROM test_table 
            WHERE id = {self.get_random_int()}
        """
        
        self.execute_query(query)

    def update_row(self):

        query = f"""
            UPDATE test_table
            SET int_val = {vg.generate_int_value()},
                str_val = {vg.generate_str_value()},
                double_val = {vg.generate_double_value()},
                json_val = {vg.generate_timestamp_value()},
                array = {vg.genarate_array()}
            WHERE id = {self.get_random_int()}
        """

        self.execute_query(query)

    def get_random_int(self):
        return self.execute_query("SELECT id FROM test_table LIMIT 1")