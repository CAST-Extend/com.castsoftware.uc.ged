from logging import WARN,INFO,DEBUG
from logger import Logger
import pandas as pd
import time

'''
    Generate Project BOM Report
'''

log = Logger(level=INFO)

def ProjectBOMfromLocalFile(bom_path, report_path, aip_name, schema_prefix, connCSS, connNeo4j):
    log.info('Starting the Project BOM report generation...')
    componentsMapping = []
    logsDf = pd.read_excel(io= bom_path, header = 5, sheet_name ='Logs', usecols = "B:D")
    for name,version,localPath in zip(logsDf["Name"],logsDf["Version"],logsDf["Local Path"]):
        lpSplited = localPath.replace("\\","/").split("/")
        repo = lpSplited[lpSplited.index("Analyzed")+1]
        componentsMapping.append({
                "Repository Name" : repo,
                "Framework Name" : name,
                "Framework Version" : version,
                "Framework Path" : localPath                
            })
    GenerateProjectBOM(componentsMapping, report_path, aip_name, schema_prefix, connCSS, connNeo4j)

def ProjectBOMfromHighLight(domainId, hl_app_name, report_path, connHL, aip_name, schema_prefix, connCSS, connNeo4j):
    componentsMapping = ApplicationComponentsMapping(domainId, hl_app_name, connHL)
    GenerateProjectBOM(componentsMapping, report_path, aip_name, schema_prefix, connCSS, connNeo4j)

def GenerateProjectBOM(componentsMapping, report_path, aip_name, schema_prefix, connCSS, connNeo4j):   
    outputFile = f'{report_path}/{aip_name}_Project_BOM.xlsx'
    writer = pd.ExcelWriter(outputFile)
    
    repoNames = []
    frameworkList = []
    associatedFrameworks = []
    #auSheetList = {}
    projectInformation = ProjectsInformation(schema_prefix, connCSS)
    projectPaths = ''
    if not projectInformation.empty and len(componentsMapping) > 0:
        for projectName, projectPath in zip(projectInformation['Project Name'], projectInformation['Project Path']):
            #log.info(f'Project path: {projectPath}')
            referenceSplit = projectPath.split("\\")
            repoIndex = referenceSplit.index("Analyzed")+1
            repositoryName = referenceSplit[repoIndex]
            repoNames.append(repositoryName)
            projectFolder = 'Analyzed'
            lastFolderIndex = 0
            if "." in referenceSplit[len(referenceSplit)-1]:
                lastFolderIndex = len(referenceSplit)-1
            else:
                lastFolderIndex = len(referenceSplit)
            #log.info(referenceSplit)
            #log.info(f"Last Folder: {referenceSplit[lastFolderIndex-1]} - {repoIndex} - {lastFolderIndex}")
            for i in range(repoIndex, lastFolderIndex):
                projectFolder = projectFolder + '/' + referenceSplit[i] 
            #log.info(f'Project folder: {projectFolder}')
            projectFolder = projectFolder + '/'
            projectPaths = projectPaths + '|' + projectPath
            
            #projectFolder = '/' + referenceSplit[len(referenceSplit)-2] + '/'
            #auList = []
            for component in componentsMapping:
                frameworkPath = component.get("Framework Path").replace("\\","/")
                if projectFolder in frameworkPath:
                    #log.info(f'Framework Path: {frameworkPath}')
                    frameworkName = component.get("Framework Name")
                    frameworkVersion = component.get("Framework Version")
                    '''
                    auDfRow = {}
                    auDfRow["Framework Name"] = frameworkName
                    auDfRow["Framework Version"] = frameworkVersion
                    auDfRow["Framework Path"] = frameworkPath
                    auList.append(auDfRow)
                    '''
                    fwListRow = {}
                    fwListRow["Repository Name"] = repositoryName
                    fwListRow["Project Name"] = projectName
                    fwListRow["Project Path"] = projectPath
                    fwListRow["Framework Name"] = frameworkName
                    fwListRow["Framework Version"] = frameworkVersion
                    fwListRow["Framework Path"] = frameworkPath
                    frameworkList.append(fwListRow)
                    associatedFrameworks.append(frameworkName)
            '''        
            if len(auList) > 0:
                auDf = pd.DataFrame(auList)
                if len(projectName)>30:
                    projectName = projectName[0:29]
                auSheetList.update({projectName : auDf})'''

    #log.info(f'Used frameworks: {associatedFrameworks}')
    orphanFrameworks = []
    for component in componentsMapping:
        if component.get("Framework Name") not in associatedFrameworks: orphanFrameworks.append(component) #.get("Framework Path"))
    remainingOrphanFrameworks = orphanFrameworks[:]
    #log.info(f'Orphan Frameworks: {orphanFrameworks}')
    uaProjectInformation = UAProjectsInformation(schema_prefix, connCSS)
    if not uaProjectInformation.empty and len(orphanFrameworks) > 0:
        projectInformation = pd.concat([projectInformation, uaProjectInformation])
        
        
        for uaProjectName, uaProjectPath, uaTechnology in zip(uaProjectInformation['Project Name'], uaProjectInformation['Project Path'], uaProjectInformation['Technology']):
            #log.info(f'UA Project path: {uaProjectPath}')
            #referenceSplit = uaProjectPath.split("\\")
            #repositoryName = referenceSplit[len(referenceSplit)-1]
            repoNames.append("N/A")
            '''
            for framework in orphanFrameworks:
                frameworkPath = framework.get("Framework Path")
                frameworkName = framework.get("Framework Name")
                frameworkVersion = framework.get("Framework Version")
                if uaTechnology == 'HTML5' and ('.js' in frameworkPath.lower() or '.html' in frameworkPath.lower() or '.ts' in frameworkPath.lower()):
                    #log.info(f'{uaTechnology} - {framework}')
                    fwListRow = {}
                    fwListRow["Repository Name"] = "N/A"
                    fwListRow["Project Name"] = uaProjectName
                    fwListRow["Project Path"] = uaProjectPath
                    fwListRow["Framework Name"] = frameworkName
                    fwListRow["Framework Version"] = frameworkVersion
                    fwListRow["Framework Path"] = frameworkPath
                    frameworkList.append(fwListRow)
                    remainingOrphanFrameworks.remove(framework)
                elif uaTechnology == 'Python' and '.py' in frameworkPath.lower():
                    #log.info(f'{uaTechnology} - {framework}')
                    fwListRow = {}
                    fwListRow["Repository Name"] = repositoryName
                    fwListRow["Project Name"] = uaProjectName
                    fwListRow["Project Path"] = uaProjectPath
                    fwListRow["Framework Name"] = frameworkName
                    fwListRow["Framework Version"] = frameworkVersion
                    fwListRow["Framework Path"] = frameworkPath
                    frameworkList.append(fwListRow)
                    remainingOrphanFrameworks.remove(framework)
                elif uaTechnology == 'SHELL' and ('.sh' in frameworkPath.lower() or '.ksh' in frameworkPath.lower()): 
                    #log.info(f'{uaTechnology} - {framework}')
                    fwListRow = {}
                    fwListRow["Repository Name"] = repositoryName
                    fwListRow["Project Name"] = uaProjectName
                    fwListRow["Project Path"] = uaProjectPath
                    fwListRow["Framework Name"] = frameworkName
                    fwListRow["Framework Version"] = frameworkVersion
                    fwListRow["Framework Path"] = frameworkPath
                    frameworkList.append(fwListRow)
                    remainingOrphanFrameworks.remove(framework)
                elif uaTechnology == 'PHP' and '.php' in frameworkPath.lower():
                    #log.info(f'{uaTechnology} - {framework}')
                    fwListRow = {}
                    fwListRow["Repository Name"] = repositoryName
                    fwListRow["Project Name"] = uaProjectName
                    fwListRow["Project Path"] = uaProjectPath
                    fwListRow["Framework Name"] = frameworkName
                    fwListRow["Framework Version"] = frameworkVersion
                    fwListRow["Framework Path"] = frameworkPath
                    frameworkList.append(fwListRow)
                    remainingOrphanFrameworks.remove(framework)
                elif uaTechnology == 'Perl' and '.pl' in frameworkPath.lower():
                    #log.info(f'{uaTechnology} - {framework}')
                    fwListRow = {}
                    fwListRow["Repository Name"] = repositoryName
                    fwListRow["Project Name"] = uaProjectName
                    fwListRow["Project Path"] = uaProjectPath
                    fwListRow["Framework Name"] = frameworkName
                    fwListRow["Framework Version"] = frameworkVersion
                    fwListRow["Framework Path"] = frameworkPath
                    frameworkList.append(fwListRow)
                    remainingOrphanFrameworks.remove(framework)
            '''
        
    projectInformation.insert(0,'Repository Name', repoNames, True)
    
    cppRepo = CppRepo(aip_name, connNeo4j)
    cppRepoList = []
    cppPathList = []
    if not cppRepo.empty:
        for fullname in cppRepo['Object Fullname']:
            if ".c" in fullname and "Analyzed" in fullname:
                fullnameSplit = fullname.split('\\')
                repo = fullnameSplit[fullnameSplit.index("Analyzed")+1]
                projectName = ''
                for i in range(fullnameSplit.index("Analyzed")+1,len(fullnameSplit)-1):
                    if projectName == '': projectName = fullnameSplit[i]
                    else: projectName = projectName + '\\' + fullnameSplit[i]
                projectPath = ''
                for i in range(0,len(fullnameSplit)-1):
                    if projectPath == '': projectPath = fullnameSplit[i]
                    else: projectPath = projectPath + '\\' + fullnameSplit[i]
                projectPath = projectPath.replace('[','')
                if not projectPath in projectPaths:
                    cppPathList.append(projectPath)
                    cppProject = {}
                    cppProject["Repository Name"] = repo
                    cppProject["Project Name"] = projectName
                    cppProject["Project Path"] = projectPath
                    cppProject["Technology"] = 'C++'
                    cppProject["Version"] = 'N/A'
                    #log.info(cppProject)
                    cppRepoList.append(cppProject)
    
    #log.info(cppRepoList)
    if len(cppRepoList) > 0: 
        cppRepoDf = pd.DataFrame(cppRepoList).drop_duplicates()
        projectInformation = pd.concat([projectInformation, cppRepoDf]) 

    frameworkDf = pd.DataFrame(frameworkList)
    frameworkDf.to_excel(writer, sheet_name="Project_BOM(Bill of Material)", index=False)
    projectInformation.to_excel(writer, sheet_name="Project_TechnologyVersion", index=False)
    orphanFrameworkDf = pd.DataFrame(remainingOrphanFrameworks)
    orphanFrameworkDf.to_excel(writer, sheet_name="Orphan Frameworks", index=False)
    '''
    for auSheet in auSheetList:
        sheetName = auSheet
        if len(sheetName)>30:
            sheetName = sheetName[0:29]
        auSheetList[auSheet].to_excel(writer, sheet_name=sheetName, index=False)
    '''                     
    writer.save()
    log.info('Successfully generated {0}'.format(outputFile))
        
def ApplicationComponentsMapping(domainId, hl_app_name, connHL):
    applicationId = connHL.get_application_id(domainId, hl_app_name)
    return connHL.get_components_mapping(domainId, applicationId)

def ProjectsInformation(schema_prefix, connCSS):
    sql = f"""
        select 
            object_name as "Project Name", rootpath as "Project Path", '.Net' as "Technology", frameworkversion as "Version"
        from {schema_prefix}_mngt.cms_net_project
        union
        select 
            object_name as "Project Name", rootpath as "Project Path", 'Java' as "Technology", coalesce(java_version, 'Unknown') as "Version"
        from {schema_prefix}_mngt.cms_j2ee_project
        union
        select 
            object_name as "Project Name", rootpath as "Project Path", 'C++' as "Technology", 
            case devenv_usage
                when 'DevEnvVC2003Console' then 'VC++ 2003 Console'
                when 'DevEnvVC2003Mfc' then 'VC++ 2003 Win32/Mfc'                
                when 'DevEnvVC2005Console' then 'VC++ 2005 Console'
                when 'DevEnvVC2005Mfc' then 'VC++ 2005 Win32/Mfc'
                when 'DevEnvVC2008Console' then 'VC++ 2008 Console'
                when 'DevEnvVC2008Mfc' then 'VC++ 2008 Win32/Mfc'
                when 'DevEnvVC2010Console' then 'VC++ 2010 Console'
                when 'DevEnvVC2010Mfc' then 'VC++ 2010 Win32/Mfc'
                when 'DevEnvVC2012Console' then 'VC++ 2012 Console'
                when 'DevEnvVC2012Mfc' then 'VC++ 2012 Win32/Mfc'
            else 'Unknown'
            end as "Version"
        from {schema_prefix}_mngt.cms_cpp_project
        union
        select 
            object_name as "Project Name", rootpath as "Project Path", 'ASP' as "Technology", 'Unknown' as "Version"
        from {schema_prefix}_mngt.cms_asp_project
        union
        select 
            object_name as "Project Name", rootpath as "Project Path", 'VB' as "Technology", 'Unknown' as "Version"
        from {schema_prefix}_mngt.cms_vb_project
        order by "Project Name"
    """
    return connCSS.dfquery(sql)

def UAProjectsInformation(schema_prefix, connCSS):
    sql = f"""
        select 
            languagesstr as "Project Name", rootpath as "Project Path", languagesstr as "Technology", 'Unknown' as "Version"
        from {schema_prefix}_mngt.cms_ua_project
        order by "Project Name"
    """
    return connCSS.dfquery(sql)

def CppRepo(aip_name, connNeo4j):
    cypher = """
        MATCH (o:Object:`{0}`)
        WHERE o.Type="C/C++ File" 
        RETURN distinct o.Name as `Object Name`, o.FullName as `Object Fullname`, o.Type as `Object Type`""".format(aip_name)
    return connNeo4j.dfquery(cypher)
    
'''
    Reports from Postgres SQL Queries
'''
    
def GenericSQLReport(query, sheetName, connCSS, outputFile):
    dtf_results = connCSS.dfquery(query)
    if not dtf_results.empty:
        with pd.ExcelWriter(outputFile) as writer:
            dtf_results.to_excel(writer, sheet_name=f'{sheetName}', index=False)
        log.info('Successfully generated {0}'.format(outputFile))
    else: 
        log.info('No results available')
    
def ASPProjectInformation(app_name, schema_prefix, report_path, connCSS):
    log.info('Starting the ASPProjectInformation report generation...')
    sql =f'''
        select object_name as "Project Name", rootpath as "Project Reference" from {schema_prefix}_mngt.cms_asp_project
        '''
    outputFile = '{0}/{1}_ASP_Project_Information.xlsx'.format(report_path,app_name) 
    sheetName = 'Results'  
    GenericSQLReport(sql, sheetName, connCSS, outputFile)
    
def AssemblyInformation(app_name, schema_prefix, report_path, connCSS):
    log.info('Starting the AssemblyInformation report generation...')
    sql =f'''
        select assemblypath as "Assembly Name" from {schema_prefix}_mngt.cms_net_assembly_file
        '''
    outputFile = '{0}/{1}_Assembly_Information.xlsx'.format(report_path,app_name) 
    sheetName = 'Results'  
    GenericSQLReport(sql, sheetName, connCSS, outputFile)
    
def CppProjectInformation(app_name, schema_prefix, report_path, connCSS):
    log.info('Starting the CppProjectInformation report generation...')
    sql =f'''
        select object_name as "Project Name", rootpath as "Project Reference" from {schema_prefix}_mngt.cms_cpp_project
        '''
    outputFile = '{0}/{1}_Cpp_Project_Information.xlsx'.format(report_path,app_name) 
    sheetName = 'Results'  
    GenericSQLReport(sql, sheetName, connCSS, outputFile)
    
def JavaProjectInformation(app_name, schema_prefix, report_path, connCSS):
    log.info('Starting the JavaProjectInformation report generation...')
    sql = """
        select object_name as "Project Name", rootpath as "Project Reference", codesize as "Code Size",
            apppath as "Application Path", web_descriptor as "Web Descriptor", java_version as "Java Version",
            hibernate_usage as "Hibernate Usage", struts_usage as "Struts Usage", spring_usage as "Spring Usage",
            jsf_usage as "JSF Usage", ejb_usage as "EJB Usage", wbs_usage as "WBS Usage"
        from {0}_mngt.cms_j2ee_project""".format(schema_prefix)
    outputFile = '{0}/{1}_Java_Project_Information.xlsx'.format(report_path,app_name) 
    sheetName = 'Results'  
    GenericSQLReport(sql, sheetName, connCSS, outputFile)
    
def NetProjectInformation(app_name, schema_prefix, report_path, connCSS):
    log.info('Starting the NetProjectInformation report generation...')
    sql =f'''
        select 
            object_name as "Project Name", rootpath as "Project Reference", codesize as "Code Size",
            frameworkversion as "Version", assemblyname as "Assembly Name", defaultnamespace as "Default Namespace"
        from {schema_prefix}_mngt.cms_net_project
        '''
    outputFile = '{0}/{1}_Net_Project_Information.xlsx'.format(report_path,app_name) 
    sheetName = 'Results'  
    GenericSQLReport(sql, sheetName, connCSS, outputFile)

   
def Repository_Technology(app_name, schema_prefix, report_path, connCSS):
    log.info('Starting the Repository Technology report generation...')
    """
    sql =f'''
        TODO
    '''
    outputFile = '{0}/{1}_Repository_Technology.xlsx'.format(report_path,app_name) 
    sheetName = 'Results'  
    GenericSQLReport(sql, sheetName, connCSS, outputFile)
    """
   
def Technology_LOC(app_name, schema_prefix, report_path, connCSS):
    log.info('Starting the Technology LOC report generation...')
    sql = """
        Select Languages as "Technology Name", SUM(LOC) as "LOC" 
        from ((select t3.object_language_name Languages, SUM(t4.InfVal) LOC 
                from {0}_local.cdt_objects t3, {0}_local.objfilref t2, {0}_local.refpath t1,  {0}_local.ObjInf t4  
                where t3.object_id = t4.IdObj and t4.InfTyp = 1 and  t4.InfSubTyp = 0 and  t2.idobj = t3.object_id and t1.idfilref = t2.idfilref 
                    and t3.object_language_name not 
                    like '%%N/A%%' and t3.object_language_name not like '%%Universal Analyzer Language%%' and t3.object_language_name not like 'COM' and 
                     t3.object_language_name not like '.NET' and object_type_Str not in ('File which contains source code')
                group by Languages order by 1 )
                UNION  ALL  
                (select  distinct t3.object_language_name as Languages, 0 LOC
                from {0}_local.cdt_objects t3   
                where   t3.object_language_name not 
                    like '%%N/A%%' and t3.object_language_name not like '%%Universal Analyzer Language%%' and t3.object_language_name not like 'COM' and 
                     t3.object_language_name not like '.NET' and object_type_Str not in ('File which contains source code') order by 1 )) temp 
        group by "Technology Name" order by 1""".format(schema_prefix)
    #sql2 = 'Pending query for 2nd sheet'
    outputFile = '{0}/{1}_Technology_LOC.xlsx'.format(report_path,app_name)  
    sheetName = 'Technology_LOC'  
    GenericSQLReport(sql, sheetName, connCSS, outputFile)

'''    
    From Engineering Dashboard Folder
    Reports based on specific rules results, including object path and bookmarks
'''
    
def GenericRuleResultsReport(rule_id, schema_prefix, connAipRest, outputFile):
    dtf_results = connAipRest.get_rule_violations(schema_prefix, rule_id) 
    if not dtf_results.empty:
        with pd.ExcelWriter(outputFile) as writer:
            dtf_results.to_excel(writer, sheet_name="Violations", index=False)
        log.info('Successfully generated {0}'.format(outputFile))
    else:
        log.info('No results available')
        
def GenerateActionPlanRulesReports(app_name, schema_prefix, report_path, connAipRest):
    rules = connAipRest.get_action_plan_rules(schema_prefix)
    for (rule_id, rule_name) in rules:
        log.info('Starting report generation for rule: {0}'.format(rule_name))
        filename = CleanNameForReport(rule_name)
        GenericRuleResultsReport(rule_id, schema_prefix, connAipRest, '{0}/{1}_{2}.xlsx'.format(report_path,app_name,filename))

def GenerateRulesByKeywordReports(app_name, schema_prefix, report_path, connAipRest, keyword):
    rules = connAipRest.get_rules_by_keyword(schema_prefix, keyword)
    for (rule_id, rule_name) in rules:
        log.info('Starting report generation for rule: {0}'.format(rule_name))
        filename = CleanNameForReport(rule_name)
        GenericRuleResultsReport(rule_id, schema_prefix, connAipRest, '{0}/{1}_{2}.xlsx'.format(report_path,app_name,filename))

def CleanNameForReport(complex_name):
    forbidden_chars = '"*\\/\'.|?:<>(),'
    space = ' '
    filename = ''.join([x if x not in forbidden_chars else '' for x in complex_name])
    filename = ''.join([x if x not in space else '_' for x in filename])
    if len(filename) >= 100:
        filename = filename[:100]
    return filename  
 
'''
    Reports from Imaging REST API
'''

def GenerateImagingReportsAsync(app_name, report_path, standardReportsList, connImagingRest, retriesNumber, retryTime):
    standardReportsUuid = []
    for report in standardReportsList:
        standardReportsUuid.append(connImagingRest.ReportsGeneration(app_name, GetReportId(report)))
    i = 0
    while i < retriesNumber and len(standardReportsUuid) > 0:
        standardReportsUuid = CheckStatusAndDownloadReport(app_name, report_path, connImagingRest, standardReportsUuid)
        if len(standardReportsUuid) > 0: time.sleep(retryTime)
        i = i + 1

def CheckStatusAndDownloadReport(appName, report_path, connImagingRest, standardReportsUuid):
    reportStatus = connImagingRest.ReportStatus()
    pendingReports = standardReportsUuid[:]
    log.debug(f'Pending reports: {pendingReports}')
    for report in pendingReports:
        status = reportStatus['success'][report]['Status']
        reportName = reportStatus['success'][report]['ReportName']
        log.debug(f'Report {report} Status {status} Name {reportName}')
        if status == 'Done':
            report_id = GetReportId(reportName)
            outputFile = f'{report_path}/{appName}_{CleanNameForReport(reportName)}.csv'
            log.info(f'Generating Report ID {report_id} - {outputFile}')
            StandardImagingReport(appName, outputFile, report_id, connImagingRest)
            standardReportsUuid.remove(report)
    return standardReportsUuid
    
def GetReportId(reportName):
        switcher = {
            'Relation between Objects And DataSources' : '1',
            'Relation between DBTables And DBObjects' : '2',
            'Relation between DataSources And Transactions' : '3',
            'Relation between Transactions And Objects' : '4',
            'Relation between Transactions And DataSources' : '5',
            'Transactions Complexity' : '6',
            'Most Referenced Objects' : '7',
            'Relation between Modules' : '8',
            'Relation between Modules and Transactions' : '9',
            "Modules' Complexity" : '10',
            'Relation between Modules and Objects' : '11'
            }
        return switcher.get(reportName, 0)    

def StandardImagingReport(app_name, outputFile, report_id, connImagingRest):
    dtf_results = connImagingRest.GetReport(app_name, report_id)
    if not dtf_results.empty:
        dtf_results.to_csv(outputFile, index = False)
        log.info('Successfully generated {0}'.format(outputFile))
    else:
        log.info('No results available')

def DBObjects(app_name, report_path, connImagingRest):
    log.info('Starting DB Objects report generation...')
    outputFile = '{0}/{1}_DB_Objects.csv'.format(report_path,app_name)
    dbObjects = connImagingRest.GetDBObjects(app_name)
    if len(dbObjects) > 0:
        nodes = []
        for node in dbObjects['success']['graph']['nodes']:
            nodes.append(node['id'])
        edges = []
        for edge in dbObjects['success']['graph']['edges']:
            edges.append(edge['id'])
        data = '"nodes" : {0},"edges" : {1}'.format(nodes,edges)
        jsonData = '{' + data + '}'
        dtf_results = connImagingRest.ExportView(app_name, jsonData)
        if not dtf_results.empty:
            dtf_results.to_csv(outputFile, index = False)
            log.info('Successfully generated {0}'.format(outputFile))
        else:
            log.info('No results available')
    else:
        log.info('No results available')

def APIInteractions(app_name, report_path, connImagingRest):
    log.info('Starting API Interactions report generation...')
    outputFile = '{0}/{1}_API_Interactions.csv'.format(report_path,app_name)
    apiNodes = connImagingRest.APILevel5Nodes(app_name)
    dtf_results = connImagingRest.ExportView(app_name, apiNodes)
    if not dtf_results.empty:
        dtf_results.to_csv(outputFile, index = False)
        log.info('Successfully generated {0}'.format(outputFile))
    else:
        log.info('No results available')

        
'''     
@deprecated: 

def GenerateMostReferencedObjects(app_name, connImagingRest):
    report_id = '7'
    connImagingRest.ReportsGeneration(app_name, report_id)
    
def GenerateModulesComplexity(app_name, connImagingRest):
    report_id = '10'
    connImagingRest.ReportsGeneration(app_name, report_id)

def RelationsBetweenObjectsAndDataSources(app_name, report_path, connImagingRest):
    report_id = '1'
    outputFile = '{0}/{1}_RelationsBetweenObjectsAndDataSources.csv'.format(report_path,app_name)
    StandardImagingReport(app_name, outputFile, report_id, connImagingRest)

def MostReferencedObjects(app_name, report_path, connImagingRest):
    report_id = '7'
    outputFile = '{0}/{1}_MostReferencedObjects.csv'.format(report_path,app_name)
    StandardImagingReport(app_name, outputFile, report_id, connImagingRest)

def ModulesComplexity(app_name, report_path, connImagingRest):
    report_id = '10'
    outputFile = '{0}/{1}_ModulesComplexity.csv'.format(report_path,app_name)
    StandardImagingReport(app_name, outputFile, report_id, connImagingRest)

def GenerateAllImagingReportsAsync(app_name, connImagingRest):
    for report_id in range(1,12):
        connImagingRest.ReportsGeneration(app_name, report_id) 
        
def GetAllImagingReportsAsync(app_name, report_path, connImagingRest, retriesNumber, retryTime):
    i = 0
    while i < retriesNumber:
        CheckStatusAndDownloadReport(app_name, report_path, connImagingRest)
        time.sleep(retryTime)
        i = i + 1
'''

'''
    @deprecated: 
    Reports from Neo4j Cypher Queries


def GenericCypherReport(query, sheetName, connNeo4j, outputFile):
    dtf_results = connNeo4j.dfquery(query)
    if not dtf_results.empty:
        with pd.ExcelWriter(outputFile) as writer:
            dtf_results.to_excel(writer, sheet_name=f'{sheetName}', index=False)
        log.info('Successfully generated {0}'.format(outputFile))
    else: 
        log.info('No results available')
    
def ApiRepository(app_name, report_path, connNeo4j):
    log.info('Starting the API Repository report generation...')
    cypher = """  
        MATCH (m:Module:`{0}`)-[:Contains]->(o1:Object)-[]-(o2:Object)<-[]-(l:Level5)
            WHERE l.Name CONTAINS "API"
            RETURN DISTINCT m.Name as `Repository Name`, COLLECT(DISTINCT l.Name) as `API Name`""".format(app_name)
    outputFile = '{0}/{1}_API_Repository.xlsx'.format(report_path,app_name)
    sheetName = 'API'
    GenericCypherReport(cypher, sheetName, connNeo4j, outputFile)    

def ApiName(app_name, report_path, connNeo4j): 
    log.info('Starting the API Name report generation...')
    cypher = """
        MATCH (m:Module:`{0}`)-[:Contains]->(o1:Object)-[]-(o2:Object)<-[]-(l:Level5)
            WHERE l.Name CONTAINS "API"
            RETURN DISTINCT l.Name as `API Name`""".format(app_name)
    
    outputFile = '{0}/{1}_API_Name.xlsx'.format(report_path,app_name)
    sheetName = 'API Name'
    GenericCypherReport(cypher, sheetName, connNeo4j, outputFile)
    
def CloudReady(app_name, report_path, connNeo4j): 
    log.info('Starting the Cloud Ready report generation...')
    cypher = """
        MATCH (h:HighlightProperty)
        MATCH(o:`{0}`)-[r:Property]->(op:ObjectProperty)
        WHERE op.Id STARTS WITH h.AipId
        AND op.Id ENDS WITH 'CloudReady'
        RETURN o.AipId AS AipId,o.FullName AS PATH,o.Type as Type, 
                r.value AS Value,op.Description AS Description,
                op.Doc as Doc_link,op.Tags as Tags, 
                o.InternalType as InternalType,o.Level as Level, 
                o.Mangling as Mangling, o.Parent as Parent, o.Module as Module""".format(app_name)
    outputFile = '{0}/{1}_CloudReady.xlsx'.format(report_path,app_name)
    sheetName = 'Cloud Ready'
    GenericCypherReport(cypher, sheetName, connNeo4j, outputFile)
    
def Containerization(app_name, report_path, connNeo4j): 
    log.info('Starting the Containerization report generation...')
    cypher = """
        MATCH (h:HighlightProperty)
        MATCH(o:`{0}`)-[r:Property]->(op:ObjectProperty)
        WHERE op.Id STARTS WITH h.AipId
        AND op.Id ENDS WITH 'Container'
        RETURN o.AipId AS AipId,o.FullName AS PATH,o.Type as Type, r.value AS Value,
                op.Description AS Description,op.Doc as Doc_link,op.Tags as Tags, 
                o.InternalType as InternalType,o.Level as Level, o.Mangling as Mangling, 
                o.Parent as Parent, o.Module as Module""".format(app_name)
    outputFile = '{0}/{1}_Containerization.xlsx'.format(report_path,app_name)
    sheetName = 'Containerization'
    GenericCypherReport(cypher, sheetName, connNeo4j, outputFile)
    
def ComplexObjects(app_name, report_path, connNeo4j):
    log.info('Starting the Complex Objects report generation...')
    queryObjects = """
        MATCH (o:Object:`{0}`)-[r]->(p:ObjectProperty) 
            WHERE p.Description CONTAINS 'Cyclomatic Complexity' 
            RETURN DISTINCT 
                o.AipId as `object_id`,o.Type as `Object Type`, o.FullName as `Object Fullname`, 
                o.File as `Object Path`, o.Name as `Object Name`,r.value as `Complexity`;""".format(app_name)
    querySubObjects = """
        MATCH (o:SubObject:`{0}`)-[r]->(p:ObjectProperty) 
            WHERE p.Description CONTAINS 'Cyclomatic Complexity' 
            RETURN DISTINCT 
                o.AipId as `object_id`,o.Type as `Object Type`, o.FullName as `Object Fullname`, 
                o.File as `Object Path`, o.Name as `Object Name`,r.value as `Complexity`;""".format(app_name)
    outputFile = '{0}/{1}_Complex_Objects.xlsx'.format(report_path,app_name)
    dtf_data_object = connNeo4j.dfquery(queryObjects)
    dtf_data_subobject = connNeo4j.dfquery(querySubObjects)
    if not(dtf_data_object.empty and dtf_data_subobject.empty):
        with pd.ExcelWriter(outputFile) as writer:
            dtf_data_object.to_excel(writer, sheet_name="Complex Objects", index=False)
            dtf_data_subobject.to_excel(writer, sheet_name="Complex SubObjects", index=False)    
        log.info('Successfully generated {0}'.format(outputFile))
    else: 
        log.info('No results available')
        
def CppRepo(app_name, report_path, connNeo4j): 
    log.info('Starting the C++ Repo report generation...')
    cypher = """
        MATCH (o:Object:`{0}`)
        WHERE o.Type="C/C++ File" 
        RETURN distinct o.Name as `Object Name`, o.FullName as `Object Fullname`, o.Type as `Object Type`""".format(app_name)
    outputFile = '{0}/{1}_C++Repo.xlsx'.format(report_path,app_name)
    sheetName = 'C++ Repo'
    GenericCypherReport(cypher, sheetName, connNeo4j, outputFile)

def DeadCode(app_name, report_path, connNeo4j):
    log.info('Starting the Complex Objects report generation...')
    cypher = """
        MATCH (o:Object:`{0}`) 
            WHERE Not (o)-[]-(:Object)
            RETURN DISTINCT o.Type, o.Name, o.File, o.FullName
        UNION ALL
        MATCH (o:SubObject:`{0}`) 
            WHERE Not (o)-[]-(:SubObject)
            RETURN DISTINCT o.Type, o.Name, o.File, o.FullName""".format(app_name)
    outputFile = '{0}/{1}_Dead_Code.xlsx'.format(report_path,app_name)
    sheetName = 'Dead Code'
    GenericCypherReport(cypher, sheetName, connNeo4j, outputFile)
    
def MainCallingShellProgram(app_name, report_path, connNeo4j): 
    log.info('Starting the MainCallingShellProgram report generation...')
    cypher = """
        MATCH (caller:Object:`{0}`)-[:CALL]->(callee:Object:`{0}`)
        WHERE caller.Type="SHELL Program" 
        AND NOT (()-[:CALL]->(caller))
        RETURN caller.Name,caller.FullName,caller.Type,callee.Name,callee.FullName,callee.Type""".format(app_name)
    outputFile = '{0}/{1}_MainCallingShellProgram.xlsx'.format(report_path,app_name)
    sheetName = 'MainCallingShellProgram'
    GenericCypherReport(cypher, sheetName, connNeo4j, outputFile)

def ObjectLOC(app_name, report_path, connNeo4j): 
    log.info('Starting the Object LOC report generation...')
    cypher = """
        MATCH (o:Object:`{0}`)-[r]->(p:ObjectProperty) 
        WHERE p.Description CONTAINS "Number of code lines"
        RETURN DISTINCT o.AipId as `Object Id`,o.Type as `Object Type`, 
            o.FullName as `Object Fullname`, o.Name as `Object Name`,
            r.value as `Number of code lines`""".format(app_name)
    outputFile = '{0}/{1}_Object_LOC.xlsx'.format(report_path,app_name)
    sheetName = 'LinesOfCode'
    GenericCypherReport(cypher, sheetName, connNeo4j, outputFile)
    
def ShellProgram(app_name, report_path, connNeo4j): 
    log.info('Starting the Shell Program report generation...')
    cypher = """
        MATCH (o:Object:`{0}`)
        WHERE o.Type="SHELL Program"   return distinct o.Name,o.FullName,o.Type""".format(app_name)
    outputFile = '{0}/{1}_Shell_Program.xlsx'.format(report_path,app_name)
    sheetName = 'ShellProgram_list'
    GenericCypherReport(cypher, sheetName, connNeo4j, outputFile)
'''