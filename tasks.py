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
        self.database_name = Chamber()["database"]["name"]

    def execute(self, operation, *args):
        self._connect()
        if callable(operation):
            result = operation(cursor=self.cursor, connection=self.connection, *args)
        else:
            result = self.cursor.execute(operation)
        self._close()
        return result

    def exists_database(self):
        def operation(cursor, connection):
            cursor.execute(f"SELECT 1 FROM pg_catalog.pg_database WHERE datname = '{self.database_name}'")
            return cursor.fetchone() is not None
        
        return self.execute(operation)

    def create_database(self):
        def operation(cursor, connection):
            try:
                cursor.execute(sql.SQL("CREATE DATABASE {}").format(sql.Identifier(f"{self.database_name}")))
                if self._is_pgvector_installed():
                    print("pgvector extension already installed")
                else:
                    self._install_pgvector()
                cursor.execute(sql.SQL("CREATE EXTENSION IF NOT EXISTS vector").format())
            except Exception as e:
                self.drop_database()
                raise e
        return self.execute(operation)

    def drop_database(self):
        return self.execute(sql.SQL("DROP DATABASE {}").format(sql.Identifier(f"{self.database_name}")))
        
    def _install_pgvector(self):
        print("Installing pgvector extension")
        return self.execute(sql.SQL("CREATE EXTENSION vector").format())
        
    def _is_pgvector_installed(self):
        def operation(cursor, connection):
            cursor.execute("SELECT 1 FROM pg_available_extensions WHERE name = 'pgvector' AND installed_version IS NOT NULL")
            return cursor.fetchone() is not None
        
        return self.execute(operation)
    
    def check(self):
        database_status = self.exists_database()
        pgvector_status = self._is_pgvector_installed()

        if database_status:
            print(f"✅ Database created")
        else:
            print(f"❌ Missing database")

        if pgvector_status:
            print(f"✅ PGVector extension installed")
        else:
            print(f"❌ Missing PGVector")

        return database_status and pgvector_status        


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

@task
def db_check(_ctx):
    if db.check():
        exit(0)
    else:
        exit(1)
