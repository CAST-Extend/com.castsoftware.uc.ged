'''
Created on 24 may 2022

@author: HLR
'''
import pandas as pd

'''
    Reports from Neo4j Cypher Queries
'''

def GenericCypherReport(query, sheetName, connNeo4j, outputFile):
    dtf_results = connNeo4j.dfquery(query)
    if not dtf_results.empty:
        with pd.ExcelWriter(outputFile) as writer:
            dtf_results.to_excel(writer, sheet_name=f'{sheetName}', index=False)
        print('Successfully generated {0}'.format(outputFile))
    else: 
        print('No results available')
    
def ApiRepository(app_name, report_path, connNeo4j):
    print('Starting the API Repository report generation...')
    cypher = """  
        MATCH (m:Module:{0})-[:Contains]->(o1:Object)-[]-(o2:Object)<-[]-(l:Level5)
            WHERE l.Name CONTAINS "API"
            RETURN DISTINCT m.Name as `Repository Name`, COLLECT(DISTINCT l.Name) as `API Name`""".format(app_name)
    outputFile = '{0}/{1}_API_Repository.xlsx'.format(report_path,app_name)
    sheetName = 'API'
    GenericCypherReport(cypher, sheetName, connNeo4j, outputFile)    

def ApiName(app_name, report_path, connNeo4j): 
    print('Starting the API Name report generation...')
    cypher = """
        MATCH (m:Module:{0})-[:Contains]->(o1:Object)-[]-(o2:Object)<-[]-(l:Level5)
            WHERE l.Name CONTAINS "API"
            RETURN DISTINCT l.Name as `API Name`""".format(app_name)
    
    outputFile = '{0}/{1}_API_Name.xlsx'.format(report_path,app_name)
    sheetName = 'API Name'
    GenericCypherReport(cypher, sheetName, connNeo4j, outputFile)
    
def CloudReady(app_name, report_path, connNeo4j): 
    print('Starting the Cloud Ready report generation...')
    cypher = """
        MATCH (h:HighlightProperty)
        MATCH(o:{0})-[r:Property]->(op:ObjectProperty)
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
    print('Starting the Containerization report generation...')
    cypher = """
        MATCH (h:HighlightProperty)
        MATCH(o:GICECAP_22041)-[r:Property]->(op:ObjectProperty)
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
    print('Starting the Complex Objects report generation...')
    queryObjects = '''
        MATCH (o:Object:{0})-[r]->(p:ObjectProperty) 
            WHERE p.Description CONTAINS 'Cyclomatic Complexity' 
            RETURN DISTINCT 
                o.AipId as `object_id`,o.Type as `Object Type`, o.FullName as `Object Fullname`, 
                o.File as `Object Path`, o.Name as `Object Name`,r.value as `Complexity`;'''.format(app_name)
    querySubObjects = """
        MATCH (o:SubObject:{0})-[r]->(p:ObjectProperty) 
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
        print('Successfully generated {0}'.format(outputFile))
    else: 
        print('No results available')
        
def CppRepo(app_name, report_path, connNeo4j): 
    print('Starting the C++ Repo report generation...')
    cypher = """
        MATCH (o:Object:{0})
        WHERE o.Type="C/C++ File" 
        RETURN distinct o.Name as `Object Name`, o.FullName as `Object Fullname`, o.Type as `Object Type`""".format(app_name)
    outputFile = '{0}/{1}_C++Repo.xlsx'.format(report_path,app_name)
    sheetName = 'C++ Repo'
    GenericCypherReport(cypher, sheetName, connNeo4j, outputFile)

def DeadCode(app_name, report_path, connNeo4j):
    print('Starting the Complex Objects report generation...')
    cypher = """
        MATCH (o:Object:{0}) 
            WHERE Not (o)-[]-(:Object)
            RETURN DISTINCT o.Type, o.Name, o.File, o.FullName
        UNION ALL
        MATCH (o:SubObject:{0}) 
            WHERE Not (o)-[]-(:SubObject)
            RETURN DISTINCT o.Type, o.Name, o.File, o.FullName""".format(app_name)
    outputFile = '{0}/{1}_Dead_Code.xlsx'.format(report_path,app_name)
    sheetName = 'Dead Code'
    GenericCypherReport(cypher, sheetName, connNeo4j, outputFile)
    
def MainCallingShellProgram(app_name, report_path, connNeo4j): 
    print('Starting the MainCallingShellProgram report generation...')
    cypher = """
        MATCH (caller:Object:{0})-[:CALL]->(callee:Object:{0})
        WHERE caller.Type="SHELL Program" 
        AND NOT (()-[:CALL]->(caller))
        RETURN caller.Name,caller.FullName,caller.Type,callee.Name,callee.FullName,callee.Type""".format(app_name)
    outputFile = '{0}/{1}_MainCallingShellProgram.xlsx'.format(report_path,app_name)
    sheetName = 'MainCallingShellProgram'
    GenericCypherReport(cypher, sheetName, connNeo4j, outputFile)

def ObjectLOC(app_name, report_path, connNeo4j): 
    print('Starting the Object LOC report generation...')
    cypher = """
        MATCH (o:Object:{0})-[r]->(p:ObjectProperty) 
        WHERE p.Description CONTAINS "Number of code lines"
        RETURN DISTINCT o.AipId as `Object Id`,o.Type as `Object Type`, 
            o.FullName as `Object Fullname`, o.Name as `Object Name`,
            r.value as `Number of code lines`""".format(app_name)
    outputFile = '{0}/{1}_Object_LOC.xlsx'.format(report_path,app_name)
    sheetName = 'LinesOfCode'
    GenericCypherReport(cypher, sheetName, connNeo4j, outputFile)
    
def ShellProgram(app_name, report_path, connNeo4j): 
    print('Starting the Shell Program report generation...')
    cypher = """
        MATCH (o:Object:{0})
        WHERE o.Type="SHELL Program"   return distinct o.Name,o.FullName,o.Type""".format(app_name)
    outputFile = '{0}/{1}_Shell_Program.xlsx'.format(report_path,app_name)
    sheetName = 'ShellProgram_list'
    GenericCypherReport(cypher, sheetName, connNeo4j, outputFile)
    
'''
    Reports from Postgres SQL Queries
'''
    
def GenericSQLReport(query, sheetName, connCSS, outputFile):
    dtf_results = connCSS.dfquery(query)
    if not dtf_results.empty:
        with pd.ExcelWriter(outputFile) as writer:
            dtf_results.to_excel(writer, sheet_name=f'{sheetName}', index=False)
        print('Successfully generated {0}'.format(outputFile))
    else: 
        print('No results available')
    
def ASPProjectInformation(app_name, schema_prefix, report_path, connCSS):
    print('Starting the ASPProjectInformation report generation...')
    sql =f'''
        select object_name as "Project Name", rootpath as "Project Reference" from {schema_prefix}_mngt.cms_asp_project
        '''
    outputFile = '{0}/{1}_ASP_Project_Information.xlsx'.format(report_path,app_name) 
    sheetName = 'Results'  
    GenericSQLReport(sql, sheetName, connCSS, outputFile)
    
def AssemblyInformation(app_name, schema_prefix, report_path, connCSS):
    print('Starting the AssemblyInformation report generation...')
    sql =f'''
        select assemblypath as "Assembly Name" from {schema_prefix}_mngt.cms_net_assembly_file
        '''
    outputFile = '{0}/{1}_Assembly_Information.xlsx'.format(report_path,app_name) 
    sheetName = 'Results'  
    GenericSQLReport(sql, sheetName, connCSS, outputFile)
    
def CppProjectInformation(app_name, schema_prefix, report_path, connCSS):
    print('Starting the CppProjectInformation report generation...')
    sql =f'''
        select object_name as "Project Name", rootpath as "Project Reference" from {schema_prefix}_mngt.cms_cpp_project
        '''
    outputFile = '{0}/{1}_Cpp_Project_Information.xlsx'.format(report_path,app_name) 
    sheetName = 'Results'  
    GenericSQLReport(sql, sheetName, connCSS, outputFile)
    
def JavaProjectInformation(app_name, schema_prefix, report_path, connCSS):
    print('Starting the JavaProjectInformation report generation...')
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
    print('Starting the NetProjectInformation report generation...')
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
    print('Starting the Repository Technology report generation...')
    sql =f'''
        TODO
        '''
    outputFile = '{0}/{1}_Repository_Technology.xlsx'.format(report_path,app_name) 
    sheetName = 'Results'  
    #GenericSQLReport(sql, sheetName, connCSS, outputFile)
   
def Technology_LOC(app_name, schema_prefix, report_path, connCSS):
    print('Starting the Technology LOC report generation...')
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
    sql2 = 'Pending query for 2nd sheet'
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
        print('Successfully generated {0}'.format(outputFile))
    else:
        print('No results available')
        
def GenerateActionPlanRulesReports(app_name, schema_prefix, report_path, connAipRest):
    rules = connAipRest.get_action_plan_rules(schema_prefix)
    for (rule_id, rule_name) in rules:
        print('Starting report generation for rule: {0}'.format(rule_name))
        filename = CleanRuleNameForReport(rule_name)
        GenericRuleResultsReport(rule_id, schema_prefix, connAipRest, '{0}/{1}_{2}.xlsx'.format(report_path,app_name,filename))

def GenerateRulesByKeywordReports(app_name, schema_prefix, report_path, connAipRest, keyword):
    rules = connAipRest.get_rules_by_keyword(schema_prefix, keyword)
    for (rule_id, rule_name) in rules:
        print('Starting report generation for rule: {0}'.format(rule_name))
        filename = CleanRuleNameForReport(rule_name)
        GenericRuleResultsReport(rule_id, schema_prefix, connAipRest, '{0}/{1}_{2}.xlsx'.format(report_path,app_name,filename))

def CleanRuleNameForReport(rule_name):
    forbidden_chars = '"*\\/\'.|?:<>(),'
    space = ' '
    filename = ''.join([x if x not in forbidden_chars else '' for x in rule_name])
    filename = ''.join([x if x not in space else '_' for x in filename])
    if len(filename) >= 100:
        filename = filename[:100]
    return filename  
 
'''
    Reports from Imaging
'''
def GenerateAllImagingReportsAsync(app_name, connImagingRest):
    for report_id in range(1,12):
        connImagingRest.ReportsGeneration(app_name, report_id)

def StandardImagingReport(app_name, outputFile, report_id, connImagingRest):
    dtf_results = connImagingRest.GetReport(app_name, report_id)
    if not dtf_results.empty:
        dtf_results.to_csv(outputFile, index = False)
        print('Successfully generated {0}'.format(outputFile))
    else:
        print('No results available')

def RelationsBetweenObjectsAndDataSources(app_name, report_path, connImagingRest):
    report_id = '1'
    outputFile = '{0}/{1}_RelationsBetweenObjectsAndDataSources.xlsx'.format(report_path,app_name)
    StandardImagingReport(app_name, outputFile, report_id, connImagingRest)

def MostReferencedObjects(app_name, report_path, connImagingRest):
    report_id = '7'
    outputFile = '{0}/{1}_MostReferencedObjects.xlsx'.format(report_path,app_name)
    StandardImagingReport(app_name, outputFile, report_id, connImagingRest)

def ModulesComplexity(app_name, report_path, connImagingRest):
    report_id = '10'
    outputFile = '{0}/{1}_ModulesComplexity.xlsx'.format(report_path,app_name)
    StandardImagingReport(app_name, outputFile, report_id, connImagingRest)
    
def GetAllImagingReportsAsync(app_name, report_path, connImagingRest):
    reports = {
            ('1', 'ObjectsAndDataSources'),
            ('2', 'DBTablesAndDBObjects'),
            ('3', 'DataSourcesAndTransactions'),
            ('4', 'TransactionsAndObjects'),
            ('5', 'TransactionsAndDataSources'),
            ('6', 'TransactionComplexity'),
            ('7', 'MostReferencedObjects'),
            ('8', 'RelationBetweenModules'),
            ('9', 'ModulesAndTransactions'),
            ('10','ModulesComplexity'),
            ('11','ModulesAndObjects')
        }
    for (report_id, report_name) in reports:
        outputFile = '{0}/{1}_{2}.csv'.format(report_path,app_name,report_name)
        print('Starting download for report: {0}'.format(report_name))
        StandardImagingReport(app_name, outputFile, report_id, connImagingRest)
    
def DBObjects(app_name, report_path, connImagingRest):
    print('Starting DB Objects report generation...')
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
            print('Successfully generated {0}'.format(outputFile))
        else:
            print('No results available')
    else:
        print('No results available')

def APIInteractions(app_name, report_path, connImagingRest):
    print('Starting API Interactions report generation...')
    outputFile = '{0}/{1}_API_Interactions.csv'.format(report_path,app_name)
    apiNodes = connImagingRest.APILevel5Nodes(app_name)
    dtf_results = connImagingRest.ExportView(app_name, apiNodes)
    if not dtf_results.empty:
        dtf_results.to_csv(outputFile, index = False)
        print('Successfully generated {0}'.format(outputFile))
    else:
        print('No results available')