'''
Created on 27 may 2022

@author: HLR
'''

from restAPI import RestCall
from requests import codes
import pandas as pd

class AipRestCall(RestCall):
    
    def get_domain(self, schema_name):
        domain_id = "0"
        (status,json) = self.get()
        if status == codes["ok"]:
            try: 
                domain_id = list(filter(lambda x:x["schema"].lower()==schema_name.lower(),json))[0]['name']
            except IndexError:
                self.error('Domain not found for schema {0}'.format(schema_name))
        if status == 0:
            domain_id = "-1" 
        return domain_id
    
    def get_latest_snapshot(self, domain_id):
        snapshot = {}
        (status,json) = self.get('{0}/applications/3/snapshots'.format(domain_id))
        if status == codes["ok"] and len(json) > 0:
            snapshot['id'] = json[0]['href'].split('/')[-1]  
            snapshot['name'] = json[0]['name']
            snapshot['technology'] = json[0]['technologies']
            snapshot['module_href'] = json[0]['moduleSnapshots']['href']
            snapshot['result_href'] = json[0]['results']['href'] 
        return snapshot
    
    def get_action_plan_rules(self, aip_triplet_prefix):
        schema_name = '{0}_central'.format(aip_triplet_prefix)
        rules = set({})
        
        domain_id = self.get_domain(schema_name)
        if domain_id != "0" and domain_id != "-1":
            latest_snapshot = self.get_latest_snapshot(domain_id)
            if len(latest_snapshot) > 0:
                latest_snapshot_id = ["id"]
                url = '{0}/applications/3/snapshots/{1}/action-plan/issues?startRow=1&nbRows=10000'.format(domain_id,latest_snapshot_id)
                
                (status, json) = self.get(url)
                if status == codes['ok'] and len(json) > 0:
                    for violation in json:
                        rules.add((violation['rulePattern']['href'].split('/')[2], violation['rulePattern']['name'])) 
        return rules
    
    def get_rules_by_keyword(self, aip_triplet_prefix, keyword):
        schema_name = '{0}_central'.format(aip_triplet_prefix)
        rules = set({})
        
        domain_id = self.get_domain(schema_name)
        if domain_id != "0" and domain_id != "-1":
            latest_snapshot = self.get_latest_snapshot(domain_id)
            if len(latest_snapshot) > 0:
                latest_snapshot_id = latest_snapshot["id"]
                url = '{0}/configuration/snapshots/{1}/quality-rules'.format(domain_id,latest_snapshot_id)
                
                (status, json) = self.get(url)
                if status == codes['ok'] and len(json) > 0:
                    for rule in json:
                        if keyword.lower() in rule['name'].lower():
                            rules.add((rule['key'],rule['name']))
        return rules
    
    def get_rule_violations(self, aip_triplet_prefix, rule_id):
        schema_name = '{0}_central'.format(aip_triplet_prefix)
        
        domain_id = self.get_domain(schema_name)
        latest_snapshot_id = self.get_latest_snapshot(domain_id)["id"]
        url = '{0}/applications/3/snapshots/{1}/violations?rule-pattern={2}'.format(domain_id,latest_snapshot_id,rule_id)
        zipped = []

        (status, json) = self.get(url)
        if status == codes['ok'] and len(json) > 0:
            self.debug('Status OK and results not empty')
        
            ruleName = []
            objectFullName = []
            objectPath = []
            lineNumber = []
                        
            for violation in json:
                bookmark = 'N/A'
                path = 'N/A'
                ruleName.append(violation['rulePattern']['name'])
                objectFullName.append(violation['component']['name'])
                
                (st,js) = self.get(violation['component']['sourceCodes']['href'])
                if st == codes['ok'] and len(js) > 0:
                    path = (js[0]['file']['name'])
                    bookmark = js[0]['startLine']
                objectPath.append(path)
                
                (st2,js2) = self.get(violation['diagnosis']['findings']['href'])
                if st2 == codes['ok'] and len(js2['bookmarks']) > 0:
                    lineNumber.append(js2['bookmarks'][0][0]['codeFragment']['startLine'])
                    if len(js2['bookmarks']) > 1:
                        for i in range(1,len(js2['bookmarks'])):
                            ruleName.append(violation['rulePattern']['name'])
                            objectFullName.append(violation['component']['name'])
                            objectPath.append(path)
                            lineNumber.append(js2['bookmarks'][i][0]['codeFragment']['startLine'])
                else:
                    lineNumber.append(bookmark)

            zipped = list(zip(ruleName, objectFullName, objectPath, lineNumber))
        
        return pd.DataFrame(zipped, columns=['Rule Name','Object Full Name','Object Path','Line Number'])
        
        