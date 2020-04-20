import requests as req
import logging
import string
import re
import json
import responses
import environment

logger=logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
logger.addHandler(logging.StreamHandler())

# def format_domains(ioc):
#         return f'{'url':''+ioc+''}'

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
        else:
            self._unknown_command()


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
            if res.status_code == req.status_codes.codes.okay:
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

            if res.status_code != req.status_codes.codes.okay:
                responses.send_failure(self._channel)
                return

        ioc_array = iocs.split('\n')
        logger.debug(f'Attempting to submit {str(len(ioc_array))} IOCS...')
        responses.send_ioc_count(self._channel,len(ioc_array))
        count=0

        for i in ioc_array:
            res = req.post(tc_url, data=i)
            if res.status_code != req.status_codes.codes.okay:
                logger.debug(f'Upload Failure:\n {res.text}')
                responses.send_failure(self._channel)
                return
            count += 1

        logger.debug(f'Number of IOCs submitted: {str(count)}')
        responses.send_success_message(self._channel)


    def _falsepositive(self):
        tc_url = environment.DOMAIN_TC

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
            responses.send_message_to_slack(self._channel, 'False Positive was submitted!')
            # res=req.post(data=ioc)
            # if res.status_code==200:
            #     responses.send_success_message(self._channel)
            # else:
            #     responses.send_failure(self._channel)
