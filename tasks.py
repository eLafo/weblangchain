# tasks.py
from invoke import task
import psycopg2
from psycopg2 import sql
from psycopg2.extensions import connection, cursor
from lib.chamber_py import Chamber

Chamber.load()

class Database():
    connection: connection = None
    cursor: cursor = None
    database_name = None
    autcommit = True
    
    def _connect(self):
        self.connection = psycopg2.connect(**Chamber()["database"]["connection"])
        self.connection.autocommit = self.autocommit
        self.cursor = self.connection.cursor()

    def _close(self):
        self.cursor.close()
        self.connection.close()

    def __init__(self, autocommit: bool = True):
        self.autocommit = autocommit
        # self.cursor = self.connection.cursor()
        self.database_name = Chamber()["database"]["name"]

    def execute(self, operation, *args):
        self._connect()
        if callable(operation):
            result = operation(cursor=self.cursor, connection=self.connection, *args)
        else:
            result = self.cursor.execute(operation)
        # result = operation(cursor=self.cursor, connection=self.connection, *args)
        self._close()
        return result

    def exists_database(self):
        def operation(cursor, connection):
            cursor.execute(f"SELECT 1 FROM pg_catalog.pg_database WHERE datname = '{self.database_name}'")
            return cursor.fetchone() is not None
        
        return self.execute(operation)

    def create_database(self):
        self.execute(sql.SQL("CREATE DATABASE {}").format(sql.Identifier(f"{self.database_name}")))

    def drop_database(self):
        self.execute(sql.SQL("DROP DATABASE {}").format(sql.Identifier(f"{self.database_name}")))

db = Database()

@task
def db_create(_ctx):
    if db.exists_database():
        print("Database already exists")
    else:
        db.create_database()
        print("Database created")


@task
def db_drop(_ctx):
    db.drop_database()
    print("Database dropped")

# @task
# def db_create_db(ctx):
#     # Connect to the
#     conn = psycopg2.connect(**Chamber()["database"]["connection"])
#     conn.autocommit = True  # Enable autocommit to create a new database
#     cursor = conn.cursor()

#     database_name = Chamber()["database"]["name"]
#     cursor.execute(f"SELECT 1 FROM pg_catalog.pg_database WHERE datname = '{database_name}'")
#     exists = cursor.fetchone()

#     # Create a new database
#     if not exists:
#         cursor.execute(sql.SQL("CREATE DATABASE {}").format(sql.Identifier(f"{database_name}")))
#     else:
#         print("Database already exists")

#     # Close the cursor and connection
#     cursor.close()
#     conn.close()
