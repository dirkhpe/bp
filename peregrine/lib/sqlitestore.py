"""
This module consolidates Database access for the lkb project.
"""

import logging
import os
import sqlite3
from sqlalchemy import Column, Integer, Text, create_engine, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship


Base = declarative_base()


class Table(Base):
    """
    Table containing the information of the database.
    """
    __tablename__ = "table_inv"
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(Text, nullable=False, unique=True)
    rows = Column(Integer)
    reserved = Column(Integer)
    data = Column(Integer)
    index_size = Column(Integer)
    unused = Column(Integer)


class TableName(Base):
    __tablename__ = "table_names"
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(Text, nullable=False, unique=True)
    fields = relationship('FieldName', back_populates='tablename')


class FieldName(Base):
    __tablename__ = "field_names"
    id = Column(Integer, primary_key=True, autoincrement=True)
    table_id = Column(Integer, ForeignKey('table_names.id'), nullable=False)
    fieldname = Column(Text, nullable=False)
    tablename = relationship('TableName', back_populates='fields')


class Recdata(Base):
    __tablename__ = "recdata"
    id = Column(Integer, primary_key=True, autoincrement=True)
    field_id = Column(Integer, ForeignKey('field_names.id'), nullable=False)
    recnr = Column(Integer, nullable=False)
    value = Column(Text, nullable=False)
    fieldname = relationship('FieldName')


class DirectConn:
    """
    This class will set up a direct connection to the database. It allows to reset the database,
    in which case the database will be dropped and recreated, including all tables.
    """

    def __init__(self, config):
        """
        To drop a database in sqlite3, you need to delete the file.
        """
        self.db = config['Main']['inv_db']
        self.dbConn, self.cur = self._connect2db()

    def _connect2db(self):
        """
        Internal method to create a database connection and a cursor. This method is called during object
        initialization.
        Note that sqlite connection object does not test the Database connection. If database does not exist, this
        method will not fail. This is expected behaviour, since it will be called to create databases as well.
        :return: Database handle and cursor for the database.
        """
        logging.debug("Creating Datastore object and cursor")
        if os.path.isfile(self.db):
            db_conn = sqlite3.connect(self.db)
            # db_conn.row_factory = sqlite3.Row
            logging.debug("Datastore object and cursor are created")
            return db_conn, db_conn.cursor()
        else:
            return False, False

    def rebuild(self):
        # A drop for sqlite is a remove of the file
        if self.dbConn:
            self.dbConn.close()
            os.remove(self.db)
        # Reconnect to the Database
        self.dbConn, self.cur = self._connect2db()
        # Use SQLAlchemy connection to build the database
        conn_string = "sqlite:///{db}".format(db=self.db)
        engine = set_engine(conn_string=conn_string)
        Base.metadata.create_all(engine)

    def res_query(self, query):
        """
        This function will return the result of the query as a list of records. Each record is represented as a
        dictionary.

        :param query:

        :return: list of records in dictionary format.
        """
        res_set = []
        self.cur.execute(query)
        field_names = [i[0] for i in self.cur.description]
        for rec in self.cur:
            res_dict = {}
            for cnt in range(len(field_names)):
                res_dict[field_names[cnt]] = rec[cnt]
            res_set.append(res_dict)
        return res_set


def init_session(db, echo=False):
    """
    This function configures the connection to the database and returns the session object.
    :param db: Name of the sqlite3 database.
    :param echo: True / False, depending if echo is required. Default: False
    :return: session object.
    """
    conn_string = "sqlite:///{db}".format(db=db)
    engine = set_engine(conn_string, echo)
    session = set_session4engine(engine)
    return session


def set_engine(conn_string, echo=False):
    engine = create_engine(conn_string, echo=echo)
    return engine


def set_session4engine(engine):
    session_class = sessionmaker(bind=engine)
    session = session_class()
    return session
