from imagingRestAPI import ImagingRestCall
from requests import codes
from io import StringIO

import pandas as pd

class ImagingApi(ImagingRestCall):
    
    _tenantName = 'default'
    
    def ReportsGeneration(self, appName, report_id):
        file_type = 'csv'
        tenantName = self._tenantName
        url = '/imaging/api/domains/{0}/apps/{1}/reports?reportid={2}&filetype={3}'.format(tenantName,appName,report_id,file_type)
        (status, json) = self.post(url)
        report_uuid = ''
        if status == codes['ok']:
            print('Report generation requested for report {0}. Code: {1}. Body: {2}'.format(report_id,status,json))
            report_uuid = json['success']['uuid']
        else:
            print('Error requesting generation of report {0}. Code: {1}. Body: {2}'.format(report_id,status,json))
        return report_uuid
    
    def ReportStatus(self):
        statuses = ''
        url = '/imaging/api/reports/status'
        (status, json) = self.get(url)
        if status == codes['ok']:
            statuses = json
        return(statuses)  
        
    def GetReport(self, appName, report_id):
        report = ''
        tenantName = self._tenantName
        url = '/imaging/api/domains/{0}/apps/{1}/reports?reportid={2}'.format(tenantName,appName,report_id)
        (status, text) = self.getText(url)
        if status == codes['ok']:
            report = text
        if len(report) > 0:
            return pd.read_csv(StringIO(report))
        else:
            return pd.DataFrame()
        
    def GetDBObjects(self, appName):
        dbObjects = ''
        tenantName = self._tenantName
        report_id = '1'
        url = '/imaging/api/domains/{0}/apps/{1}/dbobjects?reportid={2}'.format(tenantName,appName,report_id)
        (status, json) = self.get(url)
        if status == codes['ok']:
            dbObjects = json
        return dbObjects
    
    def APILevel5Nodes(self, app_name):
        apiNodes = ''
        tenantName = self._tenantName
        url = '/imaging/api/domains/{0}/apps/{1}/apilevel5?viewName=_externallibraries'.format(tenantName, app_name)
        (status, allNodes) = self.get(url)
        if status == codes['ok'] and len(allNodes) > 0:
            nodes = []
            for node in allNodes['success']['graph']['nodes']:
                nodes.append(node['id'])
            edges = []
            for edge in allNodes['success']['graph']['edges']:
                edges.append(edge['id'])
            apiNodes = '{' + '"nodes" : {0},"edges" : {1}'.format(nodes,edges) + '}'
        return apiNodes
    
    def ExportView(self, appName, jsonData):
        report = ''
        tenantName = self._tenantName
        url = '/imaging/api/domains/{0}/apps/{1}/export'.format(tenantName,appName)
        (status, text) = self.postText(url, jsonData)
        if status == codes['ok']:
            report = text
        if len(report) > 0:
            return pd.read_csv(StringIO(report))
        else:
            return pd.DataFrame()
        