"""
    Read and validate configuartion json file
"""
from logging import WARN
from logger import Logger
from json import load
from json import JSONDecodeError

from sqlalchemy import true

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

            # AIP must always be active
            # self.__config['AIP']['active']=True

            for v in ['report_path','AIP','NEO4J','CSS','IMAGING','HIGHLIGHT','LOCAL_BOM_REPORT']:
                if v not in self.__config or len(self.__config[v]) == 0:
                    raise ValueError(f"Required field '{v}' is missing from config.json")

            for v in ['AIP','NEO4J','CSS','IMAGING','HIGHLIGHT','LOCAL_BOM_REPORT']:
                json = self.__config[v]
                if 'active' not in json or json['active'] == True:
                    self.__config[v]['active']=True
                    valid = True
                    if v in ['AIP']:
                        for p in ["name","triplet_prefix","url","user","password"]:
                            if p not in json or len(p) == 0:
                                valid=False
                                break
                    elif v in ['NEO4J','CSS']:
                        for p in ["host","port","user","password"]:
                            if p not in json or len(p) == 0:
                                valid=False
                                break
                    elif v in ['IMAGING']:
                        for p in ["url","api_key"]:
                            if p not in json or len(p) == 0:
                                valid=False
                                break
                    elif v in ['HIGHLIGHT']:
                        for p in ["application_name","domain_id","url","user","password"]:
                            if p not in json or len(p) == 0:
                                valid=False
                                break
                    elif v in ['LOCAL_BOM_REPORT']:
                        for p in ["report_path"]:
                            if p not in json or len(p) == 0:
                                valid=False
                                break
                    if not valid:
                        raise ValueError(f"Required field '{p}' is missing from '{v}' in config.json")
                else: 
                    self.__config[v]['active']=False
                    self.warning(f"{v} configuration is inactive")

        except JSONDecodeError as e:
            msg = str(e)
            self.error('Configuration file must be in a JSON format')
            exit()

        except ValueError as e:
            msg = str(e)
            self.error(msg)
            exit()

    @property
    def AIP(self):
        return self.__config['AIP']['active']

    @property
    def NEO4J(self):
        return self.__config['NEO4J']['active']

    @property
    def CSS(self):
        return self.__config['CSS']['active']

    @property
    def IMAGING(self):
        return self.__config['IMAGING']['active']
    
    @property
    def HIGHLIGHT(self):
        return self.__config['HIGHLIGHT']['active']
    
    @property
    def LOCAL_BOM_REPORT(self):
        return self.__config['LOCAL_BOM_REPORT']['active']

    @property
    def report_path(self):
        return self.__config['report_path']

    @property
    def aip_name(self):
        return self.__config['AIP']['name']
    
    @property
    def aip_triplet_prefix(self):
        return self.__config['AIP']['triplet_prefix']
    
    @property
    def aip_rest_url(self):
        return self.__config['AIP']['url']
    
    @property
    def aip_rest_user(self):
        return self.__config['AIP']['user']
    
    @property
    def aip_rest_password(self):
        return self.__config['AIP']['password']

    @property
    def neo4j_host(self):
        return self.__config['NEO4J']['host']

    @property
    def neo4j_port(self):
        return self.__config['NEO4J']['port']

    @property
    def neo4j_user(self):
        return self.__config['NEO4J']['user']
    
    @property
    def neo4j_password(self):
        return self.__config['NEO4J']['password']
    
    @property
    def css_host(self):
        return self.__config['CSS']['host']

    @property
    def css_port(self):
        return self.__config['CSS']['port']

    @property
    def css_user(self):
        return self.__config['CSS']['user']
    
    @property
    def css_password(self):
        return self.__config['CSS']['password']
    
    @property
    def imaging_rest_url(self):
        return self.__config['IMAGING']['url']
    
    @property
    def imaging_rest_api_key(self):
        return self.__config['IMAGING']['api_key']
    
    @property
    def hl_application_name(self):
        return self.__config['HIGHLIGHT']['application_name']
    
    @property
    def hl_domain_id(self):
        return self.__config['HIGHLIGHT']['domain_id']
    
    @property
    def hl_url(self):
        return self.__config['HIGHLIGHT']['url']
    
    @property
    def hl_user(self):
        return self.__config['HIGHLIGHT']['user']
    
    @property
    def hl_password(self):
        return self.__config['HIGHLIGHT']['password']
    
    @property
    def bom_path(self):
        return self.__config['LOCAL_BOM_REPORT']['report_path']

