from db.db_module import Database
import os
from dotenv import load_dotenv
load_dotenv()

# dbconfig = os.getenv("MARIADB_LOCAL_DB_CONFIG")
dbconfig = {
    "host": os.getenv("MARIADB_LOCAL_HOST"),
    "user": os.getenv("MARIADB_LOCAL_USER"),
    "password": os.getenv("MARIADB_LOCAL_PASSWORD"),
    "database": os.getenv("MARIADB_LOCAL_DATABASE")
}
# Database 인스턴스 생성
db = Database(dbconfig)

def fetch_all_data(query):
    return db.execute_query(query)

def insert_data(query, values):
    db.execute_query(query, values)
