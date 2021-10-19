import os

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

#sqlite configuration

#SQLALCHEMY_DB_URL = 'sqlite:///data/database.db'

#engine = create_engine(SQLALCHEMY_DB_URL, connect_args={"check_same_thread":False})

#-------------------------------------------------------------------------------------
#SQL Server configuration

SERVER = '103.200.4.18, 1433' #PC Daffa
#SERVER = 'PPAKPIMONITORIN' #DEWAWEB
DATABASE = 'db1'
DRIVER = 'ODBC Driver 17 for SQL Server'
USERNAME = 'ADMIN'
PASSWORD = 'Admin123'
DATABASE_CONNECTION = f'mssql://{USERNAME}:{PASSWORD}@{SERVER}/{DATABASE}?driver={DRIVER}'

#Server=localhost\MSSQLSERVER01;Database=master;Trusted_Connection=True;

engine = create_engine(DATABASE_CONNECTION, connect_args={"check_same_thread":False})

SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()