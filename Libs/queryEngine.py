"""
    Read and validate configuration json file
"""
from ast import Str
from imagingNeo4j import Neo4jConnection
from aipCSS import CssConnection

from logging import WARN,INFO,DEBUG
from logger import Logger
from json import load,JSONDecodeError,dump
from os import makedirs
from sqlalchemy import true
from pandas import ExcelWriter

import os
import inspect

__author__ = "Nevin Kaplan"
__copyright__ = "Copyright 2022, CAST Software"
__credits__ = ["Nevin Kaplan","Héctor Luis Rodriguez" ]
__email__ = "n.kaplan@castsoftware.com"

class QueryEngine():
    def __init__(self, config, log_level=INFO):
        self.log = Logger(level=log_level)
        self.log.debug("NEO4J Cypher is active, generating reports")
        self.__config=config
        
        self.connNeo4j = Neo4jConnection(config.neo4j_host, config.neo4j_port, config.neo4j_user, config.neo4j_password)
        self.connCSS = CssConnection(config.css_host, config.css_port, config.css_user, config.css_password)

        try:
            with open("query.json", 'rb') as query_file:
                self.__data = load(query_file)
            
            self.__query_modified = False

            self.log.debug("Done")
        except JSONDecodeError as e:
            msg = str(e)
            self.log.error(f'Configuration file error: {msg}')
            raise ValueError("Invalid JSon Format in query.json")

        except ValueError as e:
            msg = str(e)
            self.log.error(msg)

    def run(self):
        for rpt in self.__data:
            if 'ouputFolder' not in rpt:
                self.log.error('Missing report ouputFolder')
                continue
            output_folder = f"{self.__config.report_path}/{rpt['ouputFolder']}"
            
            if not os.path.exists(output_folder):
                makedirs(output_folder)

            filename = rpt['report'].replace('{config.aip_name}',self.__config.aip_name)
            filename = f'{output_folder}/{filename}.xlsx'
            self.log.info(f'Working on {filename}')

            # Create a Pandas Excel writer using XlsxWriter as the engine.
            writer = ExcelWriter(filename, engine='xlsxwriter')

            tab_df=[]
            for tab in rpt['tabs']:
                any_tabs = False

                if 'queryName' not in tab:
                    self.log.error(f'Missing queryName for {filename}')
                    continue
                tab_name = tab['queryName']

                if 'queryType' not in tab:
                    self.log.error(f'Missing queryType for {filename}/{tab_name}')
                    continue
                query_type = tab['queryType']

                self.log.info(f'Running {query_type} query for {tab_name}')
                query =" ".join( tab['query'])
                query=query.replace('{config.aip_name}',self.__config.aip_name)
                query=query.replace('{config.aip_triplet_prefix}',self.__config.aip_triplet_prefix)

                #what type of query are we making?
                #curently there are 2 choices, cypher and css
                if query_type == 'cypher':
                    df = self.connNeo4j.dfquery(query)
                elif query_type == 'css':
                    df = self.connCSS.dfquery(query)
                else:
                    raise self.log.error(f'Missing query_type for {filename}/{tab_name}')

                if not df.empty:
                    any_tabs = True
                    columns = None
                    if not 'formating' in tab:
                        tab['formating'] = {}
                    self._add_tab(writer,df,tab_name,tab['formating'])

            if any_tabs:
                writer.save()
            else:
                writer.close()
                os.remove(filename)
    
    def _add_tab(self,writer,data,name,formatting):
        data.to_excel(writer, index=False, sheet_name=name, startrow=1,header=False)

        workbook = writer.book
        header_format = workbook.add_format({'text_wrap':True,'align': 'center'})

        worksheet = writer.sheets[name]
        rows = len(data)
        cols = len(data.columns)-1
        
        columns=[]
        for col_num, value in enumerate(data.columns.values):
            if value not in formatting:
                fmt={}
                fmt['width']=20
                formatting[value]=fmt
                self.__query_modified = True
    
            columns.append({'header': value})

        table_options={
                    'columns':columns,
                    'header_row':True,
                    'autofilter':True,
                    'banded_rows':True
                    }
        worksheet.add_table(0, 0, rows, cols,table_options)

        for col_num, value in enumerate(data.columns.values):
            fmt = formatting[value]
            worksheet.write(0, col_num, value, header_format)
            worksheet.set_column(col_num, col_num, fmt['width'])

        return worksheet

    # def updateQueryFile(self):
    #     if self.__query_modified:
    #         with open("query.json", 'w') as query_file:
    #             dump(self.__data,query_file, ensure_ascii=False, indent=4)


# import argparse
# from config import Config

# log = Logger()
# parser = argparse.ArgumentParser(description='AT&T - SDS - Modernization - Report Generation Tool')
# parser.add_argument('-c','--config', required=True, help='Configuration properties file')
# args = parser.parse_args()
# c = Config(args.config)

# cypher = QueryEngine(c,log_level=INFO)
# cypher.run()
# #cypher.updateQueryFile()
