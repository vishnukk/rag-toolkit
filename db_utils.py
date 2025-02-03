import os

import oracledb

oracledb.init_oracle_client()
connection = oracledb.connect(user=os.getenv("DB_USER"), password=os.getenv("DB_PASSWORD"),
                              dsn=os.getenv("DB_DSN"))
cursor = connection.cursor()
