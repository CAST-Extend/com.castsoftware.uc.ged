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
    writer = pd.ExcelWriter(outputFile, engine='xlsxwriter')
    
    repoNames = []
    frameworkList = []
    associatedFrameworks = []
    projectInformation = ProjectsInformation(schema_prefix, connCSS)
    projectPaths = ''
    if not projectInformation.empty and len(componentsMapping) > 0:
        for projectName, projectPath in zip(projectInformation['Project Name'], projectInformation['Project Path']):
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
            for i in range(repoIndex, lastFolderIndex):
                projectFolder = projectFolder + '/' + referenceSplit[i] 
            projectFolder = projectFolder + '/'
            projectPaths = projectPaths + '|' + projectPath
            
            for component in componentsMapping:
                frameworkPath = component.get("Framework Path").replace("\\","/")
                if projectFolder in frameworkPath:
                    frameworkName = component.get("Framework Name")
                    frameworkVersion = component.get("Framework Version")
                    fwListRow = {}
                    fwListRow["Repository Name"] = repositoryName
                    fwListRow["Project Name"] = projectName
                    fwListRow["Project Path"] = projectPath
                    fwListRow["Framework Name"] = frameworkName
                    fwListRow["Framework Version"] = frameworkVersion
                    fwListRow["Framework Path"] = frameworkPath
                    frameworkList.append(fwListRow)
                    associatedFrameworks.append(frameworkName)

    orphanFrameworks = []
    for component in componentsMapping:
        if component.get("Framework Name") not in associatedFrameworks: orphanFrameworks.append(component) #.get("Framework Path"))
    remainingOrphanFrameworks = orphanFrameworks[:]

    uaProjectInformation = UAProjectsInformation(schema_prefix, connCSS)
    if not uaProjectInformation.empty and len(orphanFrameworks) > 0:
        projectInformation = pd.concat([projectInformation, uaProjectInformation])
        for uaProjectName, uaProjectPath, uaTechnology in zip(uaProjectInformation['Project Name'], uaProjectInformation['Project Path'], uaProjectInformation['Technology']):
            repoNames.append("N/A")
       
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
                    cppRepoList.append(cppProject)
    
    if len(cppRepoList) > 0: 
        cppRepoDf = pd.DataFrame(cppRepoList).drop_duplicates()
        projectInformation = pd.concat([projectInformation, cppRepoDf]) 

    frameworkDf = pd.DataFrame(frameworkList)
    add_tab(writer, frameworkDf, "Project_BOM(Bill of Material)", 30)
    add_tab(writer, projectInformation, "Project_TechnologyVersion", 30)
    orphanFrameworkDf = pd.DataFrame(remainingOrphanFrameworks)
    add_tab(writer, orphanFrameworkDf, "Orphan Frameworks", 40)
    writer.save()
    log.info('Successfully generated {0}'.format(outputFile))
    
def add_tab(writer, data, name, width):
        data.to_excel(writer, index=False, sheet_name=name, startrow=1,header=False)

        workbook = writer.book
        header_format = workbook.add_format({'text_wrap':True,'align': 'center'})

        worksheet = writer.sheets[name]
        rows = len(data)
        cols = len(data.columns)-1
        
        columns=[]
        for col_num, value in enumerate(data.columns.values):
            columns.append({'header': value})

        table_options={
                    'columns':columns,
                    'header_row':True,
                    'autofilter':True,
                    'banded_rows':True
                    }
        worksheet.add_table(0, 0, rows, cols,table_options)

        for col_num, value in enumerate(data.columns.values):
            worksheet.write(0, col_num, value, header_format)
            worksheet.set_column(col_num, col_num, width)
        return worksheet
        
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
    From Engineering Dashboard Folder
    Reports based on specific rules results, including object path and bookmarks
'''
    
def GenericRuleResultsReport(rule_id, schema_prefix, connAipRest, outputFile):
    dtf_results = connAipRest.get_rule_violations(schema_prefix, rule_id) 
    if not dtf_results.empty:
        writer = pd.ExcelWriter(outputFile, engine='xlsxwriter')
        add_tab(writer, dtf_results, "Violations", 30)
        writer.save()
        log.info('Successfully generated {0}'.format(outputFile))
    else:
        log.warning('No results available')
        
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
            outputFile = f'{report_path}/{appName}_{CleanNameForReport(reportName)}'
            log.info(f'Generating Report ID {report_id} - {outputFile}')
            StandardImagingReport(appName, outputFile, report_id, CleanNameForReport(reportName), connImagingRest)
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

def StandardImagingReport(app_name, outputFile, report_id, reportName, connImagingRest):
    dtf_results = connImagingRest.GetReport(app_name, report_id)
    if not dtf_results.empty:
        generateImagingReport(dtf_results, outputFile, reportName)
        log.info('Successfully generated {0}'.format(outputFile))
    else:
        log.warning('No results available')

def DBObjects(app_name, report_path, connImagingRest):
    log.info('Starting DB Objects report generation...')
    outputFile = '{0}/{1}_DB_Objects'.format(report_path,app_name)
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
            generateImagingReport(dtf_results, outputFile, 'DB_Objects')
            log.info('Successfully generated {0}'.format(outputFile))
        else:
            log.warning('No results available')
    else:
        log.warning('No results available')

def APIInteractions(app_name, report_path, connImagingRest):
    log.info('Starting API Interactions report generation...')
    outputFile = '{0}/{1}_API_Interactions'.format(report_path,app_name)
    apiNodes = connImagingRest.APILevel5Nodes(app_name)
    dtf_results = connImagingRest.ExportView(app_name, apiNodes)
    if not dtf_results.empty:
        generateImagingReport(dtf_results, outputFile, 'API_Interactions')
        log.info('Successfully generated {0}'.format(outputFile))
    else:
        log.warning('No results available')
        
def generateImagingReport(data, outputFile, sheetName):
    excelMaxRows = 1048576
    if len(data.index) >=  excelMaxRows:
        log.warning(f'Too much rows for an Excel file for {outputFile} - Generating CSV version instead')
        outputFile = outputFile + '.csv'
        data.to_csv(outputFile, index = False)
    else:
        outputFile = outputFile + '.xlsx'
        writer = pd.ExcelWriter(outputFile, engine='xlsxwriter')
        add_tab(writer, data, sheetName, 20)
        writer.save()
    