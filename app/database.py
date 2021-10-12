import os

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

#sqlite configuration

#SQLALCHEMY_DB_URL = 'sqlite:///data/database.db'

#engine = create_engine(SQLALCHEMY_DB_URL, connect_args={"check_same_thread":False})

#-------------------------------------------------------------------------------------
#SQL Server configuration

#SERVER = 'DESKTOP-RR8SR4K' #PC Daffa
SERVER = 'PPAKPIMONITORIN' #DEWAWEB
DATABASE = 'master'
DRIVER = 'ODBC Driver 17 for SQL Server'
DATABASE_CONNECTION = f'mssql://@{SERVER}/{DATABASE}?driver={DRIVER}'

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