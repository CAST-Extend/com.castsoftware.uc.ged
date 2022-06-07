"""
    Read and validate configuartion json file
"""
from logger import Logger
from json import load
from json import JSONDecodeError


__author__ = "Nevin Kaplan"
__copyright__ = "Copyright 2022, CAST Software"
__email__ = "n.kaplan@castsoftware.com"

class Config(Logger):

    def __init__(self, config):
        super().__init__("Config")

        #do all required fields contain data
        try:
            with open(config, 'rb') as config_file:
                self.__config = load(config_file)

            for v in ['report_path','AIP','NEO4J','CSS','IMAGING']:
                if v not in self.__config or len(self.__config[v]) == 0:
                    raise ValueError(f"Required field '{v}' is missing from config.json")

            for v in ['NEO4J','CSS']:
                json = self.__config[v]
                for p in ["host","port","user","password"]:
                    if p not in json or len(p) == 0:
                        raise ValueError(f"Required field '{p}' is missing from '{v}' in config.json")




        except JSONDecodeError as e:
            msg = str(e)
            self.error('Configuration file must be in a JSON format')
            print(msg)
            exit()

        except ValueError as e:
            msg = str(e)
            self.error(msg)
            print(msg)
            exit()

    @property
    def aip_name(self):
        return self.__config['aip_name']
    
    @property
    def aip_triplet_prefix(self):
        return self.__config['aip_triplet_prefix']
    
    @property
    def aip_rest_url(self):
        return self.__config['aip_rest_url']
    
    @property
    def aip_rest_user(self):
        return self.__config['aip_rest_user']
    
    @property
    def aip_rest_password(self):
        return self.__config['aip_rest_password']

    @property
    def report_path(self):
        return self.__config['report_path']

    @property
    def neo4j_host(self):
        return self.__config['neo4j_host']

    @property
    def neo4j_port(self):
        return self.__config['neo4j_port']

    @property
    def neo4j_user(self):
        return self.__config['neo4j_user']
    
    @property
    def neo4j_password(self):
        return self.__config['neo4j_password']
    
    @property
    def css_host(self):
        return self.__config['css_host']

    @property
    def css_port(self):
        return self.__config['css_port']

    @property
    def css_user(self):
        return self.__config['css_user']
    
    @property
    def css_password(self):
        return self.__config['css_password']
    
    @property
    def imaging_rest_url(self):
        return self.__config['imaging_rest_url']
    
    @property
    def imaging_rest_api_key(self):
        return self.__config['imaging_rest_api_key']

