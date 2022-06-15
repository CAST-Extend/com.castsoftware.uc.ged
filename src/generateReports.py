import reports
import argparse
import os
''' test lks
'''
from config import Config
from imagingNeo4j import Neo4jConnection
from aipCSS import CssConnection
from aipRest import AipRestCall
from imagingRestCall import ImagingApi
from hlRest import HighlightRestCall
from queryEngine import QueryEngine
from logging import INFO

if __name__ == '__main__':
    
    print('\nAutomated Reports Tool')
    print('Copyright (c) 2022 CAST Software Inc.\n')
    
    parser = argparse.ArgumentParser(description='Report Generation Tool')
    parser.add_argument('-c','--config', required=True, help='Configuration JSON file')
    parser.add_argument('-q','--query', required=True, help='Cypher and CSS queries JSON file')
    args = parser.parse_args()
    c = Config(args.config)
    
    connNeo4j = None
    connCSS = None
    connHL = None
    connAipRest = None
    connImagingRest = None
    
    try:
        # Cypher and Postgres reports
        if c.NEO4J and c.CSS:
            queryEng = QueryEngine(c, args.query, log_level=INFO)
            queryEng.run()
            
        # Project BOM and Summary Information reports
        if c.NEO4J and c.CSS:
            projectBomDir = c.report_path + '/Project_BOM'
            summaryInfoDir = c.report_path + '/Summary_Information'
            
            connNeo4j = Neo4jConnection(c.neo4j_host, c.neo4j_port, c.neo4j_user, c.neo4j_password)
            connCSS = CssConnection(c.css_host, c.css_port, c.css_user, c.css_password)
            
            if not os.path.exists(projectBomDir):
                os.makedirs(projectBomDir)
            if not os.path.exists(summaryInfoDir):
                os.makedirs(summaryInfoDir)
            
            if c.HIGHLIGHT:
                connHL = HighlightRestCall(c.hl_url, c.hl_user, c.hl_password)
                reports.ProjectBOMfromHighLight(c.hl_domain_id, c.hl_application_name, projectBomDir, connHL, c.aip_name, c.aip_triplet_prefix, connCSS, connNeo4j)
            elif c.LOCAL_BOM_REPORT:             
                reports.ProjectBOMfromLocalFile(c.bom_path, projectBomDir, c.aip_name, c.aip_triplet_prefix, connCSS, connNeo4j)
        
        # Engineering Dashboard reports
        if c.AIP:
            connAipRest = AipRestCall(c.aip_rest_url, c.aip_rest_user, c.aip_rest_password)
            edDir = c.report_path + '/Engineering_Dashboard'
            if not os.path.exists(edDir):
                os.makedirs(edDir)
            reports.GenerateActionPlanRulesReports(c.aip_name, c.aip_triplet_prefix, edDir, connAipRest)
            reports.GenerateRulesByKeywordReports(c.aip_name, c.aip_triplet_prefix, edDir, connAipRest, 'hard')
            reports.GenerateRulesByKeywordReports(c.aip_name, c.aip_triplet_prefix, edDir, connAipRest, 'storing')
        
        # Imaging Reports 
        if c.IMAGING:
            connImagingRest = ImagingApi(c.imaging_rest_url, c.imaging_rest_api_key)
            imagingDir = c.report_path + '/Imaging_Reports'
            if not os.path.exists(imagingDir):
                    os.makedirs(imagingDir)
            reports.DBObjects(c.aip_name, imagingDir, connImagingRest)
            reports.APIInteractions(c.aip_name, imagingDir, connImagingRest)
            '''
            Possible values:
                'Relation between Objects And DataSources',
                'Relation between DBTables And DBObjects',
                'Relation between DataSources And Transactions',
                'Relation between Transactions And Objects',
                'Relation between Transactions And DataSources',
                'Transactions Complexity',
                'Most Referenced Objects',
                'Relation between Modules',
                'Relation between Modules and Transactions',
                "Modules' Complexity",
                'Relation between Modules and Objects'
            '''
            standardReportsList = [
                'Most Referenced Objects',
                "Modules' Complexity",
            ]
            numberOfRetries = 30
            timeBetweenRetries = 10
            reports.GenerateImagingReportsAsync(c.aip_name, imagingDir, standardReportsList, connImagingRest, numberOfRetries, timeBetweenRetries)
            
    finally:
        connNeo4j.close()
        connCSS.disposeEngine()
        
    print('\nAutomated Reports Generation Finished')
