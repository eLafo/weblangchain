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
    database = None
    autocommit = True
    
    def _connect(self, default_database: bool = False):
        db_settings = {k: Chamber()["database"][k] for k in ('user', 'host', 'password', 'port')}
        if not default_database:
            db_settings.update({'database': self.database})
        self.connection = psycopg2.connect(**db_settings)
        self.connection.autocommit = self.autocommit
        self.cursor = self.connection.cursor()

    def _close(self):
        self.cursor.close()
        self.connection.close()

    def __init__(self, autocommit: bool = True):
        self.autocommit = autocommit
        self.database = Chamber()["database"]["database"]

    def execute(self, operation, default_database: bool = False, *args):
        self._connect(default_database=default_database)
        if callable(operation):
            result = operation(cursor=self.cursor, connection=self.connection, *args)
        else:
            result = self.cursor.execute(operation)
        self._close()
        return result

    def exists_database(self):
        def operation(cursor, connection):
            cursor.execute(f"SELECT 1 FROM pg_catalog.pg_database WHERE datname = '{self.database}'")
            return cursor.fetchone() is not None
        
        return self.execute(operation, default_database=True)

    def create_database(self):
        def operation(cursor, connection):
            try:
                cursor.execute(sql.SQL("CREATE DATABASE {}").format(sql.Identifier(f"{self.database}")))
            except Exception as e:
                self.drop_database()
                raise e
        return self.execute(operation, default_database=True)

    def drop_database(self):
        return self.execute(sql.SQL("DROP DATABASE {}").format(sql.Identifier(f"{self.database}")))
        
    def install_pgvector(self):
        print("Installing pgvector extension")
        return self.execute(sql.SQL("CREATE EXTENSION IF NOT EXISTS vector").format(sql.Identifier(f"{self.database}")))
        
    def is_pgvector_installed(self):
        def operation(cursor, connection):
            cursor.execute("SELECT 1 FROM pg_available_extensions WHERE name = 'vector' AND installed_version IS NOT NULL")
            return cursor.fetchone() is not None
        
        return self.execute(operation)
    
    def check(self):
        database_status = self.exists_database()
        pgvector_status = self.is_pgvector_installed()

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
    db.install_pgvector()

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
        
@task
def db_install_pgvector(_ctx):
    db.install_pgvector()

