import requests as req
import logging
import string
import re
import json
import responses
import time
import environment
from db_actions import DBActions
from tc_api import tc_api

logger=logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
logger.addHandler(logging.StreamHandler())


class Action:

    def __init__(self, channel, user, command, command_arguments, files=None):
        self._channel = channel
        self._user = user
        self._command = command
        self._command_arguments = command_arguments
        self._files = files


    def execute(self):
        if self._command in ('hi', 'hello', 'help'):
            self._help()
        elif self._command == 'addioc':
            self._addioc()
        elif self._command =='falsepositive':
            self._falsepositive()
        elif self._command == 'bulkadd':
            self._bulkadd()
        elif self._command == 'getnewioc':
            self._getIOC()
        elif self._command == 'checkmyiocs':
            self._checkIOCs()
        elif self._command == 'submitioc':
            self._submitIOC()
        else:
            self._unknown_command()

    def _check_existing_iocs(self,db_conn,ioc_array):
        for ioc in ioc_array:
            logger.debug(f'CHECKING IOC:\t{ioc}')
            found= db_conn.check_if_ioc_exists(ioc['id'])
            if not found:
                logger.debug('IOC IS BEING ASSIGNED')
                ass_ioc=ioc
                return ioc
        return None

    def _getIOC(self):
        db_conn=DBActions()
        if db_conn.check_number_of_iocs(self._user) >=10:
            responses.send_message_to_slack(self._channel,'You currently have the max number of IOCs checked out\n\n You can view your IOCs with the `checkmyiocs` command')
            return 
        if 'url' in self._command_arguments:
            try:
                
                ioc_type='URL'
                # ioc = req.get('THREATCONNECT ENDPOINT')
                tc=tc_api()
                ioc_array=tc.get_iocs()
                page=1
                found=False
                ioc=None
                while True:
                    ioc=self._check_existing_iocs(db_conn,ioc_array) 
                    if ioc:
                        break
                    page+=1
                    ioc_array=tc.get_iocs(page=page)
                    if not ioc_array:
                        raise Exception("No IOCs returned from ThreatConnect")
                logger.debug(f'IOC being passed to db object {ioc}')
                db_conn.add_to_tracker(self._user,ioc,ioc_type)
                responses.send_ioc(self._channel,ioc)
            except:
                responses.send_failure(self._channel)
        else:
            responses.send_message_to_slack(self._channel,'We are sorry, but we currently only support URLs for the queue')
    
    def _checkIOCs(self):
        try:
            db_conn=DBActions()
            iocs=db_conn.get_user_iocs(self._user)
            if not iocs:
                responses.send_message_to_slack(self._channel, "You do not have any IOCs assigned to you at this time")
            else:
                responses.send_ioc_list(self._channel,iocs)
        except:
                responses.send_failure(self._channel)

    def _submitIOC(self):
        try:
            if self._command_arguments[0].isdigit() and (self._command_arguments[1] == 'vetted' or self._command_arguments[1] == 'unvetted'):
                db_conn=DBActions()
                iocs=db_conn.get_user_iocs(self._user)
                belong_to_user=False
                ioc_type=''
                indicator=''
                for i in iocs:
                    if int(i['id']) == int(self._command_arguments[0]):
                        belong_to_user = True
                        ioc_type=i['IOC_type']
                        indicator=i['ioc']
                        break
                if belong_to_user:
                    logger.debug('IOC belongs to user... submitting...')
                    tc=tc_api()
                    succ=tc.submit_ioc(indicator,self._command_arguments[1],ioc_type)
                    if not succ: 
                        logger.debug('**WARNING*** submitting ioc failed')
                        raise
                    succ = tc.delete_need_analysis(indicator,ioc_type)
                    if not succ:
                        logger.debug('**WARNING** failed to delete tag')
                        raise
                    succ = db_conn.remove_ioc(self._command_arguments[0])
                    if not succ:
                        raise
                    responses.send_thankyou(self._channel,self._user)

                else:
                    responses.send_message_to_slack(self._channel,"It seems that this IOC was not assigned to you. You can only submit ioc analysis for iocs assinged to you.")
            else: 
                responses.send_message_to_slack(self._channel, 'The format for this command is `submitioc <id> <vetted|unvetted>`')
        except:
            responses.send_failure(self._channel)



    def _help(self):
        responses.send_help(self._channel, self._user)


    def _unknown_command(self):
        responses.send_unknown(self._channel)


    def _addioc(self):
        tc_url = environment.DOMAIN_TC
        count=0
        for ioc in self._command_arguments:
            if "http" not in ioc and "hxxp" not in ioc:
                continue
            if '[.]' in ioc:
                ioc=ioc.replace('[.]','.')

            ioc=ioc.strip('<')
            ioc=ioc.strip('>')
            logger.debug('IOC: '+ioc)

            res = req.post(tc_url, data=ioc)
            count+=1
            if res.ok:
                responses.send_success_message(self._channel)
            else:
                responses.send_failure(self._channel)
        if count==0:
            responses.send_failure(self._channel)


    def _bulkadd(self):
        tc_url = environment.DOMAIN_TC
        f = self._files
        iocs=''

        for i in f:
            logger.debug(f"URL DOWNLOAD: {i['url_private_download']}")
            res = req.get(i['url_private_download'], headers={'Authorization': f'Bearer {environment.TOKEN}'})
            if not res.ok:
                responses.send_failure(self._channel)
                return

            if res.text not in iocs:
                iocs += res.text
        ioc_array = iocs.split('\n')
        if len(ioc_array)>100:
            responses.send_message_to_slack(self._channel, 'Due to limitations at the current time, we are only allowing 100 IOCs to be pushed at once. Sorry for the inconvience.')
            return
        logger.debug(f'Attempting to submit {str(len(ioc_array))} IOCS...')
        responses.send_ioc_count(self._channel,len(ioc_array))
        count=0

        for i in ioc_array:
            res = req.post(tc_url, data=i)
            logger.debug(f"Result status code: {res.status}")
            if not res.ok:
                logger.debug(f'Upload Failure:\n {res.text}')
                responses.send_failure(self._channel)
                return
            count += 1
            logger.debug(f'Uploaded: {i}')
            time.sleep(10)

        logger.debug(f'Number of IOCs submitted: {str(count)}')
        responses.send_success_message(self._channel)


    def _falsepositive(self):
        tc_url = environment.FALSE_POSITIVE_THREAT_CONNECT

        for fp_ioc in self._command_arguments:
            if '[.]' in fp_ioc:
                fp_ioc = fp_ioc.replace('[.]','.')

            fp_ioc = fp_ioc.strip('<')
            fp_ioc = fp_ioc.strip('>')

            data = {
                'channel_name': self._channel,
                'user_name': self._user,
                'text': fp_ioc
            }

            logger.debug(f'False PositiveIOC: {json.dumps(data)}')
            res=req.post(tc_url, json=data)
            if res.ok:
                responses.send_message_to_slack(self._channel, 'False Positive was submitted!')
            else:
                responses.send_message_to_slack(self._channel, f'Failed to submit false positive. Received status code {res.status_code}')