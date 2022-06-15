'''
    Run database sql queries 
'''
__author__ = "Héctor Luis Rodriguez"
__copyright__ = "Copyright 2022, CAST Software"
__credits__ = ["Héctor Luis Rodriguez","Nevin Kaplan"]

from operator import le
from pandas import read_sql_query, DataFrame
from psycopg2 import OperationalError
from sqlalchemy import create_engine
from sqlalchemy.exc import OperationalError
from logger import Logger
from logging import WARN,INFO,DEBUG

class CssConnection():

    def __init__(self, host, port, user, password, logger_level = INFO):
        self.__uri = 'postgresql+psycopg2://{0}:{1}@{2}:{3}/postgres'.format(user,password,host,port)
        self.__engine = create_engine(self.__uri)
        self.log=Logger("CssConnection",level=logger_level)
        
    def getEngine(self):
        return self.__engine
    
    def dfquery(self, sql):
        df = DataFrame()
        try: 
            df = read_sql_query(sql, self.__engine)
        except OperationalError as e:
            self.log.error(f"Query failed: {e._message}")
        except Exception as e:
            self.log.error(f"General Exception {e.message}")
        return df
    
    def disposeEngine(self):
        self.__engine.dispose()