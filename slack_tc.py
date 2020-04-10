from slack import WebClient
from slackeventsapi import SlackEventAdapter
from flask import Flask
import certifi
import requests as req
import ssl as ssl_lib
import logging
import enviroment
from Actions import Actions

application = Flask(__name__)

slack_events_adapter=SlackEventAdapter(enviroment.SECRET,"/slack/events",application)

token=enviroment.TOKEN

slack_client=WebClient(token)

domain_tc_endpoint=enviroment.DOMAIN_TC

@slack_events_adapter.on("app_mention")
def message(event_data):
    message_txt=event_data["event"]
    act=Actions(message_txt)
    # resp=response(message_txt['channel'],message_txt['user'])
    if "addioc" ==act.command or "addio"==act.command:
        succ=act.addioc(enviroment.DOMAIN_TC)
        if succ:
            slack_client.chat_postMessage(channel=message_txt['channel'],text='IOC was submitted!')
        else:
            slack_client.chat_postMessage(channel=message_txt['channel'],text='Error submitting IOC')
        #send request
    elif "bulkad" == act.command or "bulkadd"==act.command:
        succ=act.bulkadd(enviroment.DOMAIN_TC,token)
        if succ:
            slack_client.chat_postMessage(channel=message_txt['channel'],text='IOC was submitted!')
        else:
            slack_client.chat_postMessage(channel=message_txt['channel'],text='Error submitting IOC')
    elif "hello" == act.command or "hi" == act.command or "help" == act.command:
        slack_client.chat_postMessage(channel=message_txt['channel'],blocks=[
            {
                "type":"section",
                "text":{
                    "type":"mrkdwn",
                    "text":"Hello <@"+message_txt["user"]+">! I am the threatconnect bot! :robot_face:"
                    }
            },
            {
                "type": "divider"
            },
            {
                "type":"section",
                "text": {
                    "type":"mrkdwn",
                    "text":"Here are the commands we currently support \n\n```help```\n\n```addioc `<domain>` ```\n\n```bulkadd (attach text file with domains to this message)```\n"
                }

            }])
    else:
        slack_client.chat_postMessage(channel=message_txt['channel'],text='Sorry I do not understand your command, try asking me for help to see avaliable commands')



if __name__ == "__main__":
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)
    logger.addHandler(logging.StreamHandler())
    ssl_context = ssl_lib.create_default_context(cafile=certifi.where())
    application.run(port=5000,host='0.0.0.0')