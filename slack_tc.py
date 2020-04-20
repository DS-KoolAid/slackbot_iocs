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

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
logger.addHandler(logging.StreamHandler())

class IOCSlackBot:

    def __init__(self):
        self._channel = None
        self._user = None

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
    ssl_context = ssl_lib.create_default_context(cafile=certifi.where())
    application.run(port=5000, host='0.0.0.0')