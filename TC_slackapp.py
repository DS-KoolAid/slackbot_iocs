from slack import WebClient
from slackeventsapi import SlackEventAdapter
from flask import Flask
import certifi
import requests as req
import ssl as ssl_lib
from Responses import Responses
import logging
import enviroment

app = Flask(__name__)

slack_events_adapter=SlackEventAdapter(enviroment.SECRET,"/slack/events",app)

token=enviroment.TOKEN

slack_client=WebClient(token)

domain_tc_endpoint=enviroment.DOMAIN_TC

@slack_events_adapter.on("app_mention")
def message(event_data):
    message_txt=event_data["event"]
    logger.debug(event_data["event"])
    text = message_txt.get('text')
    c_pos=text.find(' ')
    c_pos2=text.find(' ',c_pos+1)
    if c_pos2==(-1):
        c_pos2=len(text)
    logger.debug(c_pos)
    logger.debug(c_pos2)
    command = text[c_pos+1:c_pos2]
    logger.debug(command)
    if "addioc" ==command or "addio"==command:
        ioc=text[c_pos2+1:]
        res=req.post(domain_tc_endpoint,data=ioc)
        if res.status_code==200:
            slack_client.chat_postMessage(channel=message_txt['channel'],text='IOC was submitted!')
        else:
            slack_client.chat_postMessage(channel=message_txt['channel'],text='Error submitting IOC')
        #send request
    elif "bulkad" == command or "bulkadd"==command:
        f=message_txt['files']
        iocs=""
        file_down_fail=False
        for i in f:
            logger.debug(i['url_private_download'])
            res=req.get(i['url_private_download'], headers={"Authorization": "Bearer "+token})
            logger.debug(res.text)
            iocs+=res.txt
            if res.status_code!=200:
                slack_client.chat_postMessage(channel=message_txt['channel'],text='Error reading file.')
                file_down_fail=True
                break
        if file_down_fail==False:
            res=req.post(domain_tc_endpoint,data=iocs)
            if res.status_code==200:
                slack_client.chat_postMessage(channel=message_txt['channel'],text='IOC was submitted!')
            else:
                slack_client.chat_postMessage(channel=message_txt['channel'],text='Error submitting IOC')
    elif "hello" == command or "hi" == command or "help" == command:
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
                    "text":"Here are the commands we currently support \n\n`help`\n\n`addioc <domain>`\n\n`bulkadd (attach text file with domains to this message)`\n"
                }

            }])
    else:
        slack_client.chat_postMessage(channel=message_txt['channel'],text='Sorry I do not understand your command, try asking me for help to see avaliable commands')



if __name__ == "__main__":
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)
    logger.addHandler(logging.StreamHandler())
    ssl_context = ssl_lib.create_default_context(cafile=certifi.where())
    app.run(port=3000,host='0.0.0.0')