#!/bin/bash

apt install gunicorn3

python3 -m venv env

source env/bin/activate

pip3 install wheel

pip3 install requests, slackeventsapi, slackclient, gunicorn

deactivate