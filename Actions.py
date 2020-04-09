import requests as req
class Actions:

    def __init__(self,message_txt):
        self.text=message_txt.get('text')
        c_pos=self.text.find(' ')
        c_pos2=self.text.find(' ',c_pos+1)
        if c_pos2==(-1):
            c_pos2=len(self.text)
        self.command = self.text[c_pos+1:c_pos2]
        if "files" in message_txt:
            self.files=message_txt['files']
    
    def addioc(self,tc_url):
        pos1=self.text.find('`')
        pos2=self.text.find('`',pos1+1)
        ioc=self.text[pos1+1:pos2]
        if "[.]" in ioc:
            ioc=ioc.replace("[.]",".")
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
            res=req.get(i['url_private_download'], headers={"Authorization": "Bearer "+token})
            iocs+=res.txt
            if res.status_code!=200:
                return False
        if file_down_fail==False:
            res=req.post(self.tc_url,data=iocs)
            if res.status_code==200:
                return True
            else:
                return False