'''
Created on 1 jun 2022

@author: HLR
'''

import urllib.parse

from requests import get
from requests import post
from requests import exceptions
from requests import codes

from logger import Logger
from logging import INFO
from pandas import DataFrame
from time import perf_counter, ctime

class ImagingRestCall(Logger):

    _base_url = None
    _api_key = None
    _time_tracker_df  = DataFrame()
    _track_time = True

    def __init__(self, base_url, api_key, track_time=False,log_level=INFO):
        super().__init__(level=log_level)
        if base_url[-1]=='/': 
            base_url=base_url[:-1]
        self._base_url = base_url
        self._track_time = track_time
        self._api_key = api_key

    def get(self, url = ""):
        start_dttm = ctime()
        start_tm = perf_counter()
        headers = {'accept': 'application/json;charset=utf-8', 'x-api-key': self._api_key}
        
        try:
            if len(url) > 0 and url[0] != '/':
                url='/{0}'.format(url)
            u = urllib.parse.quote('{0}{1}'.format(self._base_url,url),safe='/:&?=')
            resp = get(url= u, headers=headers)
                      
            # Save the duration, if enabled.
            if (self._track_time):
                end_tm = perf_counter()
                end_dttm = ctime()
                duration = end_tm - start_tm

                #print(f'Request completed in {duration} ms')
                self._time_tracker_df = self._time_tracker_df.append({'Application': 'ALL', 'URL': url, 'Start Time': start_dttm \
                                                            , 'End Time': end_dttm, 'Duration': duration}, ignore_index=True)
            if resp.status_code == codes['ok']:
                return resp.status_code, resp.json()
            else:
                return resp.status_code,""

        except exceptions.ConnectionError:
            self.error('Unable to connect to host {0}'.format(self._base_url))
        except exceptions.Timeout:
            #TODO Maybe set up for a retry, or continue in a retry loop
            self.error('Timeout while performing api request using: {0}'.format(url))
        except exceptions.TooManyRedirects:
            #TODO Tell the user their URL was bad and try a different one
            self.error('TooManyRedirects while performing api request using: {0}'.format(url))
        except exceptions.RequestException as e:
            # catastrophic error. bail.
            self.error('General Request exception while performing api request using: {0}'.format(url), e)

        return 0, "{}"
    
    def post(self, url = "", data = ""):
        start_dttm = ctime()
        start_tm = perf_counter()
        headers = {'accept': 'application/json;charset=utf-8', 'x-api-key': self._api_key, 'Content-Type': 'application/json'}
         
        try:
            if len(url) > 0 and url[0] != '/':
                url='/{0}'.format(url)
            u = urllib.parse.quote('{0}{1}'.format(self._base_url,url),safe='/:&?=')

            resp = post(url= u, headers=headers, data=data)

            # Save the duration, if enabled.
            if (self._track_time):
                end_tm = perf_counter()
                end_dttm = ctime()
                duration = end_tm - start_tm

                #print(f'Request completed in {duration} ms')
                self._time_tracker_df = self._time_tracker_df.append({'Application': 'ALL', 'URL': url, 'Start Time': start_dttm \
                                                            , 'End Time': end_dttm, 'Duration': duration}, ignore_index=True)
            if resp.status_code == codes['ok']:
                return resp.status_code, resp.json()
            else:
                return resp.status_code,""

        except exceptions.ConnectionError:
            self.error('Unable to connect to host {0}'.format(self._base_url))
        except exceptions.Timeout:
            #TODO Maybe set up for a retry, or continue in a retry loop
            self.error('Timeout while performing api request using: {0}'.format(url))
        except exceptions.TooManyRedirects:
            #TODO Tell the user their URL was bad and try a different one
            self.error('TooManyRedirects while performing api request using: {0}'.format(url))
        except exceptions.RequestException as e:
            # catastrophic error. bail.
            self.error('General Request exception while performing api request using: {0}'.format(url), e)

        return 0, "{}"
    
    def getText(self, url = ""):
        start_dttm = ctime()
        start_tm = perf_counter()
        headers = {'accept': 'application/json;charset=utf-8', 'x-api-key': self._api_key}
        
        try:
            if len(url) > 0 and url[0] != '/':
                url='/{0}'.format(url)
            u = urllib.parse.quote('{0}{1}'.format(self._base_url,url),safe='/:&?=')
            resp = get(url= u, headers=headers)
            
            # Save the duration, if enabled.
            if (self._track_time):
                end_tm = perf_counter()
                end_dttm = ctime()
                duration = end_tm - start_tm

                #print(f'Request completed in {duration} ms')
                self._time_tracker_df = self._time_tracker_df.append({'Application': 'ALL', 'URL': url, 'Start Time': start_dttm \
                                                            , 'End Time': end_dttm, 'Duration': duration}, ignore_index=True)
            if resp.status_code == codes['ok']:
                return resp.status_code, resp.text
            else:
                return resp.status_code,""

        except exceptions.ConnectionError:
            self.error('Unable to connect to host {0}'.format(self._base_url))
        except exceptions.Timeout:
            #TODO Maybe set up for a retry, or continue in a retry loop
            self.error('Timeout while performing api request using: {0}'.format(url))
        except exceptions.TooManyRedirects:
            #TODO Tell the user their URL was bad and try a different one
            self.error('TooManyRedirects while performing api request using: {0}'.format(url))
        except exceptions.RequestException as e:
            # catastrophic error. bail.
            self.error('General Request exception while performing api request using: {0}'.format(url), e)

        return 0, "{}"
    
    def postText(self, url = "", data = ""):
        start_dttm = ctime()
        start_tm = perf_counter()
        headers = {'accept': 'application/json;charset=utf-8', 'x-api-key': self._api_key, 'Content-Type': 'application/json'}
        
        try:
            if len(url) > 0 and url[0] != '/':
                url='/{0}'.format(url)
            u = urllib.parse.quote('{0}{1}'.format(self._base_url,url),safe='/:&?=')

            resp = post(url= u, headers=headers, data=data)

            # Save the duration, if enabled.
            if (self._track_time):
                end_tm = perf_counter()
                end_dttm = ctime()
                duration = end_tm - start_tm

                #print(f'Request completed in {duration} ms')
                self._time_tracker_df = self._time_tracker_df.append({'Application': 'ALL', 'URL': url, 'Start Time': start_dttm \
                                                            , 'End Time': end_dttm, 'Duration': duration}, ignore_index=True)
            if resp.status_code == codes['ok']:
                return resp.status_code, resp.text
            else:
                return resp.status_code,""

        except exceptions.ConnectionError:
            self.error('Unable to connect to host {0}'.format(self._base_url))
        except exceptions.Timeout:
            #TODO Maybe set up for a retry, or continue in a retry loop
            self.error('Timeout while performing api request using: {0}'.format(url))
        except exceptions.TooManyRedirects:
            #TODO Tell the user their URL was bad and try a different one
            self.error('TooManyRedirects while performing api request using: {0}'.format(url))
        except exceptions.RequestException as e:
            # catastrophic error. bail.
            self.error('General Request exception while performing api request using: {0}'.format(url), e)

        return 0, "{}"
