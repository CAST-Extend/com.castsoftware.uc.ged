import reports
import argparse
import os

from config import Config
from imagingNeo4j import Neo4jConnection
from aipCSS import CssConnection
from aipRest import AipRestCall
from imagingRestCall import ImagingApi
from hlRest import HighlightRestCall

if __name__ == '__main__':
    
    print('\nAutomated Reports Tool')
    print('Copyright (c) 2022 CAST Software Inc.\n')
    
    parser = argparse.ArgumentParser(description='AT&T - SDS - Modernization - Report Generation Tool')
    parser.add_argument('-c','--config', required=True, help='Configuration properties file')
    args = parser.parse_args()
    c = Config(args.config)

    try:
        # Cypher reports
        if c.NEO4J:
            connNeo4j = Neo4jConnection(c.neo4j_host, c.neo4j_port, c.neo4j_user, c.neo4j_password)
            cypherDir = c.report_path + '/Cypher'
            if not os.path.exists(cypherDir):
                os.makedirs(cypherDir)
            
            reports.ApiRepository(c.aip_name, cypherDir, connNeo4j)
            reports.ApiName(c.aip_name, cypherDir, connNeo4j)
            reports.CloudReady(c.aip_name, cypherDir, connNeo4j)
            reports.ComplexObjects(c.aip_name, cypherDir, connNeo4j)
            reports.Containerization(c.aip_name, cypherDir, connNeo4j)
            reports.CppRepo(c.aip_name, cypherDir, connNeo4j)
            reports.DeadCode(c.aip_name, cypherDir, connNeo4j)
            reports.MainCallingShellProgram(c.aip_name, cypherDir, connNeo4j)
            reports.ObjectLOC(c.aip_name, cypherDir, connNeo4j)
            reports.ShellProgram(c.aip_name, cypherDir, connNeo4j)
       
        # Postgres reports
        if c.CSS:
            connCSS = CssConnection(c.css_host, c.css_port, c.css_user, c.css_password)
            postgresDir = c.report_path + '/Postgres'
            if not os.path.exists(postgresDir):
                os.makedirs(postgresDir)
            reports.ASPProjectInformation(c.aip_name, c.aip_triplet_prefix, postgresDir, connCSS)
            reports.AssemblyInformation(c.aip_name, c.aip_triplet_prefix, postgresDir, connCSS)
            reports.CppProjectInformation(c.aip_name, c.aip_triplet_prefix, postgresDir, connCSS)
            reports.NetProjectInformation(c.aip_name, c.aip_triplet_prefix, postgresDir, connCSS)
            reports.JavaProjectInformation(c.aip_name, c.aip_triplet_prefix, postgresDir, connCSS)
            reports.Repository_Technology(c.aip_name, c.aip_triplet_prefix, postgresDir, connCSS)
            reports.Technology_LOC(c.aip_name, c.aip_triplet_prefix, postgresDir, connCSS)
           
        # Project BOM report
        if c.NEO4J and c.CSS and c.HIGHLIGHT:
            connHL = HighlightRestCall(c.hl_url, c.hl_user, c.hl_password)
            projectBomDir = c.report_path + '/Project_BOM'
            if not os.path.exists(projectBomDir):
                os.makedirs(projectBomDir)
            
            reports.ProjectBOM(c.hl_domain_id, c.hl_application_name, projectBomDir, connHL, c.aip_name, c.aip_triplet_prefix, connCSS)
        
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
            numberOfRetries = 10
            timeBetweenRetries = 5 
            reports.GenerateImagingReportsAsync(c.aip_name, imagingDir, standardReportsList, connImagingRest, numberOfRetries, timeBetweenRetries)

    finally:
        connNeo4j.close()
        connCSS.disposeEngine()
        
    print('\nAutomated Reports Generation Finished')
