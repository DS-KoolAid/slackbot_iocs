from slack import WebClient

import environment

token=environment.TOKEN

slack_client=WebClient(token)


def send_message_to_slack(channel, text):
    slack_client.chat_postMessage(channel=channel,text=text)

def send_success_message(channel):
    slack_client.chat_postMessage(channel=channel,text='IOC was submitted!')

def send_failure(channel):
    slack_client.chat_postMessage(channel=channel,text='Error submitting IOC')

def send_ioc_count(channel,count):
    slack_client.chat_postMessage(channel=channel,text=f'Attempting to submit {str(count)} IOCs')


def send_unknown(channel):
    slack_client.chat_postMessage(channel=channel,text='Sorry I do not understand your command, try asking me for help to see avaliable commands')

def send_ioc_list(channel,ioc_array):
    message="IOCs:\n"
    for i in ioc_array:
        message+=f"IOC Type: {i['type']}\tIOC: {i['ioc']}\n"
    slack_client.chat_postMessage(channel=channel,text=message)
    


def send_help(channel,user):
     slack_client.chat_postMessage(channel=channel,blocks=[
            {
                "type":"section",
                "text":{
                    "type":"mrkdwn",
                    "text":"Hello <@"+user+">! I am the threatconnect bot! :robot_face:"
                    }
            },
            {
                "type": "divider"
            },
            {
                "type":"section",
                "text": {
                    "type":"mrkdwn",
                    "text":"""Here are the commands we currently support
                    ```help```
                    ```addioc `<domain>` ```
                    ```bulkadd (attach text file with domains to this message)```
                    ```falsepositive `<domain>` ```
                    """
                }

            }])