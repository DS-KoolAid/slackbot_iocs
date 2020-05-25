from datetime import datetime 
import logging
import base64
import hmac
import hashlib
import requests as req
import time
import sys
import json

logger=logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
logger.addHandler(logging.StreamHandler())



try:
    import ConfigParser
except:
    import configparser as ConfigParser


config = ConfigParser.RawConfigParser()
config.read('./tc.ini')

try:
    api_access_id = config.get('threatconnect', 'api_access_id')
    api_secret_key = config.get('threatconnect', 'api_secret_key')
    api_default_org = config.get('threatconnect', 'api_default_org')
    api_base_url = config.get('threatconnect', 'api_base_url')
    api_ioc_uri_feed = config.get('threatconnect', 'api_ioc_uri_feed')
    api_tag = config.get('threatconnect','api_tag')

except ConfigParser.NoOptionError:
    print('Could not read configuration file.')
    sys.exit(1)

class tc_api():

    def __init__(self, api_aid=api_access_id, api_sec=api_secret_key, api_org=api_default_org, api_url=api_base_url, api_token=None, api_token_expires=None):
        """ """
        # logger
        self.log_level = {
            'debug': logging.DEBUG,
            'info': logging.INFO,
            'warning': logging.WARNING,
            'error': logging.ERROR,
            'critical': logging.CRITICAL}
        self.formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s (%(funcName)s:%(lineno)d)')
        self.tcl = logging.getLogger('TC_API')
        self.tcl.addHandler(logging.StreamHandler())

        self.api_ioc_uri_feed = api_ioc_uri_feed

        self.api_tag = api_tag

        # debugging
        self._memory_monitor = True

        # credentials
        self._api_aid = api_aid
        self._api_sec = api_sec
        self._api_token = api_token
        self._api_token_expires = api_token_expires

        # user defined values
        self._api_org = api_org
        self._api_url = api_url
        self._api_result_limit = 200

        # default values
        self._activity_log = False
        self._api_request_timeout = 30
        self._api_retries = 5  # maximum of 5 minute window
        self._api_sleep = 59  # seconds
        self._bulk_on_demand = False
        self._enable_report = False

        self._proxies = {'https': None}


        # config items
        self._report = []
        self._verify_ssl = False


    def _api_request_headers(self,uri,method):
        """ """
        timestamp = int(time.time())
        if self._api_token is not None and self._api_token_expires is not None:
            window_padding = 15  # bcs - possible configuration option
            current_time = int(time.time()) - window_padding
            if (int(self._api_token_expires) < current_time):
                self._renew_token()
            authorization = 'TC-Token {0}'.format(self._api_token)

        elif self._api_aid is not None and self._api_sec is not None:
            path_url=uri
            signature = "{0}:{1}:{2}".format(path_url, method, timestamp)
            # python 2.7, does not work on 3.x and not tested on 2.6
            # hmac_signature = hmac.new(self._api_sec, signature, digestmod=hashlib.sha256).digest()
            # authorization = 'TC {0}:{1}'.format(self._api_aid, base64.b64encode(hmac_signature))
            # python 3.x
            hmac_signature = hmac.new(self._api_sec.encode(), signature.encode(), digestmod=hashlib.sha256).digest()
            authorization = 'TC {0}:{1}'.format(self._api_aid, base64.b64encode(hmac_signature).decode())
        self.tcl.debug(timestamp)
        self.tcl.debug(authorization)
        return timestamp,authorization
        # ro.add_header('Timestamp', timestamp)
        # ro.add_header('Authorization', authorization)

    def get_iocs(self,page=1):
        uri=self.api_ioc_uri_feed
        method="GET"
        ioc_array=[]
        if page==1:
            ts,auth=self._api_request_headers(uri,method)
            r=req.get(f'{self._api_url}{uri}',headers={'Timestamp':str(ts),'Authorization':str(auth)})
            jd=json.loads(r.text)
            for i in jd['data']['indicator']:
                d={'id':i['id'],'ioc':i['summary']}
                ioc_array.append(d)
            return ioc_array
            
        else:
            strt=str(page*100)
            uri+="?resultStart="+strt+"&resultLimit=100"
            ts,auth=self._api_request_headers(uri,method)
            r=req.get(f'{self._api_url}{uri}',headers={'Timestamp':str(ts),'Authorization':str(auth)})
            jd=json.loads(r.text)
            for i in jd['data']['indicator']:
                d={'id':i['id'],'ioc':i['summary']}
                ioc_array.append(d)
            return ioc_array

    def submit_ioc(self,ioc,status,ioc_type):
        method="POST"
        ioc_type=ioc_type.replace(' ','')
        uri=self.api_tag
        uri=uri.replace('{indicatorType}',ioc_type)
        uri=uri.replace("{indicator}",ioc)
        uri=uri.replace('{tagName}',status)
        ts,auth=self._api_request_headers(uri,method)
        logger.debug(f'URI for submitting: {uri}')
        r=req.get(f'{self._api_url}{uri}',headers={'Timestamp':str(ts),'Authorization':str(auth)})
        jd=json.loads(r.text)
        if jd['status'] == 'Success':
            return True
        else:
            return False

    def delete_need_analysis(self,ioc,ioc_type):
        method="DELETE"
        tag='Needs%20Review'
        ioc_type=ioc_type.replace(' ','')
        uri=self.api_tag
        uri=uri.replace('{indicatorType}',ioc_type)
        uri=uri.replace("{indicator}",ioc)
        uri=uri.replace('{tagName}',tag)
        ts,auth=self._api_request_headers(uri,method)
        logger.debug(f'Delete need review tag: {uri}')
        r=req.get(f'{self._api_url}{uri}',headers={'Timestamp':str(ts),'Authorization':str(auth)})
        jd=json.loads(r.text)
        if jd['status'] == 'Success':
            return True
        else:
            return False