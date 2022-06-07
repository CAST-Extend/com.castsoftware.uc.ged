'''
Created on 25 may 2022

@author: HLR
'''

import pandas as pd

from logger import Logger
from sqlalchemy import create_engine

class CssConnection(Logger):

    def __init__(self, host, port, user, password):
        self.__uri = 'postgresql+psycopg2://{0}:{1}@{2}:{3}/postgres'.format(user,password,host,port)
        self.__engine = create_engine(self.__uri)
        
    def getEngine(self):
        return self.__engine
    
    def dfquery(self, sql):
        return pd.read_sql_query(sql, self.__engine)
    
    def disposeEngine(self):
        self.__engine.dispose()