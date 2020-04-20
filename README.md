# IOC Slackbot

This project is being used to support the pushing of IOCs from slack to threatconnect. This tool is built on the python flask, nginx and gunicorn. 

The current functionality of this tool include:

- Pushing singular IOCs to a ThreatConnect endpoint.
- Pushing multiple IOCs to a ThreatConnect endpoint. 

## Commands

- `@bot help` or `hi` 
- `@bot addioc <ioc to add>`
- `@bot bulkadd` (attach file with IOCs to message)

## Setup

To get the backend of the slackbot up and running, there are a few things that must be done. 

### Run the setup script

`chmod +x setup.sh`

`./setup.sh`

This script will install the necessary packages for the application. 

### Install the nginx config

While the bot will work without nginx, it is not suggested that you run this applicaiton without some sort of WSGI server. (Flask is good for development, but needs help when it comes to production)

The configuration file for nginx is in this repo callend 'nginx'. 

To install the nginx config follow these steps: 

`sudo cp nginx /etc/nginx/sites-enabled/`

`sudo unlink /etc/nginx/sites-enabled/default`

`sudo nginx -s reload`

### Install the service

For convenience sake, lets install this as a service. 

`sudo cp slackbot-ioc.service /etc/systemd/system/`

`sudo systemctl daemon-reload`

### Configure your environment variables

Modify the environment variables in `environment.py` for your needs. 

## Run the Application

`sudo systemctl start slackbot-ioc.service`


