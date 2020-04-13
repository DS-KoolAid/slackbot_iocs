import requests as req
import logging
import string
import re
import responses
import enviroment


logger=logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
logger.addHandler(logging.StreamHandler())


def format_domains(ioc):
        return '{"url":"'+ioc+'"}'

class Actions:

    def __init__(self,message_txt):
        self.message=message_txt
        self.channel=message_txt['channel']
        self.user=message_txt['user']
        self.text=message_txt.get('blocks')[0].get('elements')[0].get('elements')[1].get('text')
        logger.debug(message_txt.get('elements'))
        if "addioc" in self.text:
            self.command= "addioc"
        elif "bulkadd" in self.text:
            self.command="bulkadd"
        elif "hi" in self.text or "help" in self.text or "hello" in self.text:
            self.command="help"
            responses.send_help(self.channel,self.user)
        else:
            self.command="unknown"
            responses.send_unknown(channel)
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
            responses.send_success_message(self.channel)
        else:
            responses.send_failure(self.channel)
    
    def bulkadd(self,tc_url):
        f=self.files
        iocs=""
        file_down_fail=False
        for i in f:
            logger.debug('URL DOWNLOAD: '+i['url_private_download'])
            res=req.get(i['url_private_download'], headers={"Authorization": "Bearer "+enviroment.TOKEN})
            if res.text not in iocs:
                iocs+=res.text
            if res.status_code!=200:
                responses.send_failure(self.channel)
                return
        ioc_array=iocs.split('\n')
        logger.debug('Attempting to submit '+str(len(ioc_array))+' IOCS...')
        responses.send_ioc_count(self.channel,len(ioc_array))
        count=0
        for i in ioc_array:
            res=req.post(tc_url,data=i)
            if res.status_code!=200:
                logger.debug("Upload Failure:\n"+res.text)
                responses.send_failure(self.channel)
                return
            count+=1
        logger.debug('Number of IOCs submitted: '+str(count))
        responses.send_success_message(self.channel)

