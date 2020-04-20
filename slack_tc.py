from slackeventsapi import SlackEventAdapter
from flask import Flask, request
import certifi
import requests as req
import ssl as ssl_lib
import logging
import environment
from Actions import Action
import responses

application = Flask(__name__)
slack_events_adapter=SlackEventAdapter(environment.SECRET,'/slack/events',application)
domain_tc_endpoint=environment.DOMAIN_TC


class IOCSlackBot:

    def __init__(self):
        self._channel = None
        self._user = None

    # @slack_events_adapter.on('app_mention')
    # def app_mention(event_data):
    #     message_txt = event_data['event']
    #     logger.debug("WOW")
    #     logger.debug(message_txt)
    #     text = message_txt.get('blocks')[0].get('elements')[0].get('elements')[1].get('text')
    #     act = Actions(message_txt,text)
    #     if 'addioc' == act.command or 'addio' == act.command:
    #         ioc = message_txt.get('blocks')[0].get('elements')[0].get('elements')[2].get('url')
    #         act.addioc(environment.DOMAIN_TC, ioc)
    #     elif 'bulkad' == act.command or 'bulkadd' == act.command:
    #         act.bulkadd(environment.DOMAIN_TC)
    #     elif 'falsepositive' == act.command:
    #         # TODO pass Threat connect endpoint
    #         fp_ioc = message_txt.get('blocks')[0].get('elements')[0].get('elements')[2].get('url')
    #         act.falsepositive(fp_ioc)


    # @slack_events_adapter.on('message')
    # def message(event_data):
    #     message_txt = event_data['event']
    #     logger.debug("MOM")
    #     logger.debug(event_data)
    #     if 'bot_id' not in message_txt:
    #         text = message_txt.get('blocks')[0].get('elements')[0].get('elements')[0].get('text')
    #         act = Actions(message_txt,text)
    #         # resp = response(message_txt['channel'],message_txt['user'])
    #         if 'addioc' == act.command or 'addio' == act.command:
    #             ioc = message_txt.get('blocks')[0].get('elements')[0].get('elements')[1].get('url')
    #             act.addioc(environment.DOMAIN_TC, ioc)
    #         elif 'bulkad' == act.command or 'bulkadd' == act.command:
    #             act.bulkadd(environment.DOMAIN_TC)
    #         elif 'falsepositive' == act.command:
    #             # TODO pass Threat connect endpoint
    #             fp_ioc = message_txt.get('blocks')[0].get('elements')[0].get('elements')[1].get('url')
    #             act.falsepositive(fp_ioc)

@slack_events_adapter.on('app_mention')
@slack_events_adapter.on('message')
def parse_event(event):
    import pprint
    # Ignore messages from the bot
    if 'bot_id' in event['event']:
        return

    pprint.pprint(event)
    logger.debug('----------------------------------------------------------')

    channel = event['event']['channel']
    user = event['event']['user']

    command = ''
    command_arguments = []
    message = event['event']['blocks'][0]['elements'][0]['elements']
    for element in message:
        if element['type'] == 'text':
            # text can contain multiple words
            words = element['text'].strip().split()
            for word in words:
                # skip extra spaces
                if not word:
                    continue
                # first word we see is the command
                if not command:
                    command = word.lower()
                # any other words are arguments for the command
                else:
                    command_arguments.append(word.lower())
        elif element['type'] == 'link':
            command_arguments.append(element['url'])

    data = {
        'channel': channel,
        'user': user,
        'command': command,
        'command_arguments': command_arguments
    }

    if 'files' in event['event']:
        data['files'] = event['event']['files']
    pprint.pprint(data)


    action = Action(**data)
    action.execute()


if __name__ == '__main__':
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)
    logger.addHandler(logging.StreamHandler())

    ssl_context = ssl_lib.create_default_context(cafile=certifi.where())
    application.run(port=5000, host='0.0.0.0')