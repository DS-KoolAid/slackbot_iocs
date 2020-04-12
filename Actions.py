import requests as req
import logging
import string
import re

logger=logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
logger.addHandler(logging.StreamHandler())


def format_domains(ioc):
        return '{"url":"'+ioc+'"}'

class Actions:

    def __init__(self,message_txt):
        self.message=message_txt
        self.text=message_txt.get('blocks')[0].get('elements')[0].get('elements')[1].get('text')
        logger.debug(message_txt.get('elements'))
        if "addioc" in self.text:
            self.command= "addioc"
        elif "bulkadd" in self.text:
            self.command="bulkadd"
        elif "hi" in self.text or "help" in self.text or "hello" in self.text:
            self.command="help"
        else:
            self.command="unknown"
        logger.debug('COMMAND: '+self.command)
        if "files" in message_txt:
            self.files=message_txt['files']
    
    def addioc(self,tc_url):
        ioc=self.message.get('blocks')[0].get('elements')[0].get('elements')[2].get('url')
        if "[.]" in ioc:
            ioc=ioc.replace("[.]",".")
        ioc=ioc.strip('<')
        ioc=ioc.strip('>')
        logger.debug("IOC: "+ioc)
        res=req.post(tc_url,data=ioc)
        if res.status_code==200:
            return True
        else:
            return False
    
    def bulkadd(self,tc_url,token):
        f=self.files
        iocs=""
        file_down_fail=False
        for i in f:
            logger.debug('URL DOWNLOAD: '+i['url_private_download'])
            res=req.get(i['url_private_download'], headers={"Authorization": "Bearer "+token})
            iocs+=res.text
            
            if res.status_code!=200:
                return False
        logger.debug('IOCS:\n'+iocs)
        ioc_array=iocs.split('\n')
        if file_down_fail:
            return False
        count=0
        for i in ioc_array:
            logger.debug("IOC: "+i)
            res=req.post(tc_url,data=i)
            if res.status_code!=200:
                return False
            count+=1
        logger.info('IOC COUNT: '+str(count))
        return True


