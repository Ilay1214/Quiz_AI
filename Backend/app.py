# import database setup
from Database.database_setup import setup_database, DB_NAME, get_connection_config

# Database connection helper
def get_db_connection():
    config = get_connection_config()
    config["database"] = DB_NAME
    return mysql.connector.connect(**config)
