import requests as req
import logging
import string

logger=logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
logger.addHandler(logging.StreamHandler())


def format_domains(ioc):
        return '{"url":"'+ioc+'"}'

class Actions:

    def __init__(self,message_txt):
        self.text=message_txt.get('text')
        c_pos=self.text.find(' ')
        c_pos2=self.text.find(' ',c_pos+1)
        if c_pos2==(-1):
            c_pos2=len(self.text)
        self.command = self.text[c_pos+1:c_pos2]
        self.command_end_pos=c_pos2
        logger.debug('COMMAND: '+self.command)
        if "files" in message_txt:
            self.files=message_txt['files']
    
    def addioc(self,tc_url):
        pos1=self.text.find('<',self.command_end_pos)
        pos2=self.text.find('>',self.command_end_pos)
        ioc=self.text[pos1+1:pos2]
        if "[.]" in ioc:
            ioc=ioc.replace("[.]",".")
        ioc=ioc.strip('<')
        ioc=ioc.strip('>')
        tc_sub='['+format_domains(ioc)+']'
        logger.debug("IOC: "+str(tc_sub))
        res=req.post(tc_url,data=tc_sub)
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
        tc_sub='['
        count=0
        for i in ioc_array:
            if count==len(ioc_array)-1:
                tc_sub+=format_domains(i)
            else:
                tc_sub+=format_domains(i)+','
            count+=1
        tc_sub+=']'
        logger.info('IOC COUNT: '+str(count))
        logger.debug('IOC SUBMISSION:\n'+str(tc_sub))
        if file_down_fail==False:
            res=req.post(tc_url,data=tc_sub)
            if res.status_code==200:
                return True
            else:
                return False


