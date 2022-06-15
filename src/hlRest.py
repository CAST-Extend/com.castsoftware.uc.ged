from restAPI import RestCall
from requests import codes

class HighlightRestCall(RestCall):
    
    def get_components_mapping(self, domainId, applicationId):
        components = []
        url = f'/domains/{domainId}/applications/{applicationId}/components/mapping'
        (status, json) = self.get(url)
        if status == codes['ok'] and len(json) > 0:
            for component in json:
                name = component.get('name')
                version = component.get('version')
                for file in component.get('files'):
                    localFilePath = file.get('localFilePath')
                    lfpSplited = localFilePath.replace("\\","/").split("/")
                    repo = lfpSplited[lfpSplited.index("Analyzed")+1]
                    components.append({
                        "Framework Name" : name,
                        "Framework Version" : version,
                        "Framework Path" : localFilePath,
                        "Repository Name" : repo
                    })
        else:
            print('Error returning components mapping')
        return components
        
    def get_all_applications(self, domainId):
        applicationIdList = {}
        url = f'/domains/{domainId}/applications'
        (status, json) = self.get(url)
        if status == codes['ok'] and len(json) > 0:
            for app in json:
                applicationIdList[app["name"]] = app["id"]
        return applicationIdList
        
    def get_application_id(self, domainId, appName):
        applicationIdList = self.get_all_applications(domainId)
        return applicationIdList[appName]
        