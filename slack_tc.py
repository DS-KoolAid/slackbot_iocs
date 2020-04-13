from slackeventsapi import SlackEventAdapter
from flask import Flask, request
import certifi
import requests as req
import ssl as ssl_lib
import logging
import enviroment
from Actions import Actions
import responses

application = Flask(__name__)

slack_events_adapter=SlackEventAdapter(enviroment.SECRET,"/slack/events",application)

domain_tc_endpoint=enviroment.DOMAIN_TC

@slack_events_adapter.on("app_mention")
def message(event_data):
    message_txt=event_data["event"]
    text=message_txt.get('blocks')[0].get('elements')[0].get('elements')[1].get('text')
    act=Actions(message_txt,text)
    if "addioc" ==act.command or "addio"==act.command:
        ioc=message_txt.get('blocks')[0].get('elements')[0].get('elements')[2].get('url')
        succ=act.addioc(enviroment.DOMAIN_TC)
    elif "bulkad" == act.command or "bulkadd"==act.command:
        succ=act.bulkadd(enviroment.DOMAIN_TC)

@slack_events_adapter.on("message")
def message(event_data):
    message_txt=event_data["event"]
    if "bot_id" not in message_txt:
        text=message_txt.get('blocks')[0].get('elements')[0].get('elements')[0].get('text')
        act=Actions(message_txt,text)
        # resp=response(message_txt['channel'],message_txt['user'])
        if "addioc" ==act.command or "addio"==act.command:
            ioc=message_txt.get('blocks')[0].get('elements')[0].get('elements')[1].get('url')
            succ=act.addioc(enviroment.DOMAIN_TC,ioc)
        elif "bulkad" == act.command or "bulkadd"==act.command:
            succ=act.bulkadd(enviroment.DOMAIN_TC)

if __name__ == "__main__":
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)
    logger.addHandler(logging.StreamHandler())
    ssl_context = ssl_lib.create_default_context(cafile=certifi.where())
    application.run(port=5000,host='0.0.0.0')