def get_clickhouse_ddl() -> str:
	return """
        CREATE TABLE IF NOT EXISTS cdc.`test_table_log` (
            id Int32,
            int_val Int32,
            str_val Varchar(20),
            double_val Decimal(10, 2),
            inserted_at DateTime,
            updated_at Nullable(DateTime),
            delivered_at DateTime DEFAULT now(),
            __deleted BOOLEAN DEFAULT false
        ) 
        ENGINE=MergeTree
        ORDER BY id
        SETTINGS index_granularity = 8192;
    """

def get_mysql_ddl() -> str:
	return """
	    CREATE TABLE IF NOT EXISTS test_table(
	        id int NOT NULL AUTO_INCREMENT,
	        int_val int NOT NULL,
	        str_val VARCHAR(20),
	        double_val DECIMAL(10, 2),
	        inserted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
	        updated_at TIMESTAMP DEFAULT NULL ON UPDATE CURRENT_TIMESTAMP,
	        PRIMARY KEY (`id`)
	    )
	    ENGINE=InnoDB 
	    DEFAULT CHARSET=utf8mb4;
	"""