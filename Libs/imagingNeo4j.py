'''
Created on 24 may 2022

@author: HLR
'''

from neo4j import GraphDatabase
from pandas import DataFrame

class Neo4jConnection(object):
    
    def __init__(self, host, port, user, password):
        self.__uri = "bolt://{0}:{1}".format(host,port)
        self.__user = user
        self.__pwd = password
        self.__driver = None
        try:
            self.__driver = GraphDatabase.driver(self.__uri, auth=(self.__user, self.__pwd))
        except Exception as e:
            print("Failed to create the driver: {0}".format(e))
        
    def close(self):
        if self.__driver is not None:
            self.__driver.close()
        
    def query(self, query, db="neo4j"):
        session = None
        response = None
        try: 
            session = self.__driver.session(database=db) if db is not None else self.__driver.session() 
            response = list(session.run(query))
        except Exception as e:
            print("Query failed: {0}".format(e))
        finally: 
            if session is not None:
                session.close()
        return response
    
    def dfquery(self, sentence):
        return DataFrame([dict(_) for _ in self.query(sentence)])