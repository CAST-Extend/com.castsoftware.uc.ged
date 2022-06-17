'''
    Run cypher queries 
'''
__author__ = "Héctor Luis Rodriguez"
__copyright__ = "Copyright 2022, CAST Software"
__credits__ = ["Héctor Luis Rodriguez","Nevin Kaplan"]

from neo4j import GraphDatabase 
from neo4j.exceptions import ServiceUnavailable
from pandas import DataFrame,json_normalize
from logger import Logger
from logging import WARN,INFO,DEBUG

class Neo4jConnection(object):
    
    def __init__(self, host, port, user, password,log_level=INFO):
        self.__log = Logger(level=log_level)
        self.__uri = "bolt://{0}:{1}".format(host,port)
        self.__user = user
        self.__pwd = password
        self.__driver = None
        try:
            self.__driver = GraphDatabase.driver(self.__uri, auth=(self.__user, self.__pwd))
        except Exception as e:
            self.__log.error(f"Failed to create the driver: {e}")
        
    def close(self):
        if self.__driver is not None:
            self.__driver.close()
        
    def query(self, query, db="neo4j"):
        session = None
        response = None
        try: 
            session = self.__driver.session(database=db) if db is not None else self.__driver.session() 
            response = list(session.run(query))
        finally: 
            if session is not None:
                session.close()
        return response
    
    def dfquery(self, sentence):
        df = DataFrame()
        try: 
            df = DataFrame([dict(_) for _ in self.query(sentence)])
            if df.empty:
                self.__log.warning("Query ran successfuly but return no results")
        except ServiceUnavailable as e:
            self.__log.error(f'Connection Error: {e}')
        except ValueError as e:
            self.__log.error(f"Query failed: {e}")
        except Exception as e:
            self.__log.error(f"Query failed: {e.message}")

        return df
