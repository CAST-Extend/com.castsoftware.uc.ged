import reports
import argparse
import os

from config import Config
from imagingNeo4j import Neo4jConnection
from aipCSS import CssConnection
from aipRest import AipRestCall
from imagingRestCall import ImagingApi

if __name__ == '__main__':
    
    print('\nAutomated Reports Tool')
    print('Copyright (c) 2022 CAST Software Inc.\n')
    
    parser = argparse.ArgumentParser(description='AT&T - SDS - Modernization - Report Generation Tool')
    parser.add_argument('-c','--config', required=True, help='Configuration properties file')
    args = parser.parse_args()
    c = Config(args.config)
    
    connNeo4j = Neo4jConnection(c.neo4j_host, c.neo4j_port, c.neo4j_user, c.neo4j_password)
    connCSS = CssConnection(c.css_host, c.css_port, c.css_user, c.css_password)
    connAipRest = AipRestCall(c.aip_rest_url, c.aip_rest_user, c.aip_rest_password)
    connImagingRest = ImagingApi(c.imaging_rest_url, c.imaging_rest_api_key)

    cypherDir = c.report_path + '/Cypher'
    postgresDir = c.report_path + '/Postgres'
    edDir = c.report_path + '/Engineering_Dashboard'
    imagingDir = c.report_path + '/Imaging_Reports'
    
    if not os.path.exists(cypherDir):
        os.makedirs(cypherDir)
    if not os.path.exists(postgresDir):
        os.makedirs(postgresDir)
    if not os.path.exists(edDir):
        os.makedirs(edDir)
    if not os.path.exists(imagingDir):
        os.makedirs(imagingDir)
                    
    try:

        # Imaging Reports Generation 
        reports.GenerateAllImagingReportsAsync(c.aip_name, connImagingRest)
 
        # Cypher reports
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
        reports.ASPProjectInformation(c.aip_name, c.aip_triplet_prefix, postgresDir, connCSS)
        reports.AssemblyInformation(c.aip_name, c.aip_triplet_prefix, postgresDir, connCSS)
        reports.CppProjectInformation(c.aip_name, c.aip_triplet_prefix, postgresDir, connCSS)
        reports.NetProjectInformation(c.aip_name, c.aip_triplet_prefix, postgresDir, connCSS)
        reports.JavaProjectInformation(c.aip_name, c.aip_triplet_prefix, postgresDir, connCSS)
        reports.Repository_Technology(c.aip_name, c.aip_triplet_prefix, postgresDir, connCSS)
        reports.Technology_LOC(c.aip_name, c.aip_triplet_prefix, postgresDir, connCSS)
        
        # Project BOM
        
        # Summary Information
        
        # Engineering Dashboard reports
        reports.GenerateActionPlanRulesReports(c.aip_name, c.aip_triplet_prefix, edDir, connAipRest)
        reports.GenerateRulesByKeywordReports(c.aip_name, c.aip_triplet_prefix, edDir, connAipRest, 'hard')
        reports.GenerateRulesByKeywordReports(c.aip_name, c.aip_triplet_prefix, edDir, connAipRest, 'storing')
        
        # Imaging Reports Download
        reports.GetAllImagingReportsAsync(c.aip_name, imagingDir, connImagingRest)
        reports.DBObjects(c.aip_name, imagingDir, connImagingRest)
        reports.APIInteractions(c.aip_name, imagingDir, connImagingRest)

    finally:
        connNeo4j.close()
        connCSS.disposeEngine()
        
    print('\nAutomated Reports Generation Finished')
