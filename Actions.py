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
        elif self._command == 'getIOCFromQueue':
            self._getIOC()
        elif self._command == 'checkMyIOCs':
            self._checkIOCs()
        else:
            self._unknown_command()

    def _getIOC(self):
        if 'URL' in self._command_arguments:
            try:
                db_conn=DBActions()
                ioc_type='URL'
                # ioc = req.get('THREATCONNECT ENDPOINT')
                tc=tc_api()
                ioc_array=tc.get_user_iocs()
                ioc=None
                page=1
                while True:
                    ioc= db_conn.check_if_ioc_exists(ioc_array)
                    if ioc:
                        break
                    else:
                        page+=1
                        ioc_array=tc.get_user_iocs(page=page)
                        if not ioc_array:
                            responses.send_failure(self._channel)
                            return
                db_conn.add_to_tracker(self._user,ioc_type,ioc)
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



    def _help(self):
        responses.send_help(self._channel, self._user)


    def _unknown_command(self):
        responses.send_unknown(self._channel)


    def _addioc(self):
        tc_url = environment.DOMAIN_TC

        for ioc in self._command_arguments:
            if '[.]' in ioc:
                ioc=ioc.replace('[.]','.')

            ioc=ioc.strip('<')
            ioc=ioc.strip('>')
            logger.debug('IOC: '+ioc)

            res = req.post(tc_url, data=ioc)
            if res.ok:
                responses.send_success_message(self._channel)
            else:
                responses.send_failure(self._channel)


    def _bulkadd(self):
        tc_url = environment.DOMAIN_TC
        f = self._files
        iocs=''

        for i in f:
            logger.debug(f"URL DOWNLOAD: {i['url_private_download']}")
            res = req.get(i['url_private_download'], headers={'Authorization': f'Bearer {environment.TOKEN}'})
            if res.text not in iocs:
                iocs += res.text

            if res.ok:
                responses.send_failure(self._channel)
                return

        ioc_array = iocs.split('\n')
        if len(ioc_array)>100:
            responses.send_message_to_slack(self._channel, 'Due to limitations at the current time, we are only allowing 100 IOCs to be pushed at once. Sorry for the inconvience.')
            return
        logger.debug(f'Attempting to submit {str(len(ioc_array))} IOCS...')
        responses.send_ioc_count(self._channel,len(ioc_array))
        count=0

        for i in ioc_array:
            res = req.post(tc_url, data=i)
            if res.ok:
                logger.debug(f'Upload Failure:\n {res.text}')
                responses.send_failure(self._channel)
                return
            count += 1
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