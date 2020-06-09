import requests as req
import logging
import environment
import time
import schedule
import time


logger=logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
logger.addHandler(logging.StreamHandler())


tc_url = environment.DOMAIN_TC

def job():
    with open('to_submit.txt','r') as f:
        for i in f:
            count=0
            res = req.post(tc_url, data=i)
            logger.debug(f"Result status code: {res.status_code}")
            if not res.ok:
                logger.debug(f'Upload Failure:\n {res.text}')
                return
            count += 1
            logger.debug(f'Uploaded: {i}')
            time.sleep(1)
    open('to_submit.txt','w').close()

schedule.every(10).minutes.do(job)


while 1:
    schedule.run_pending()
    time.sleep(1)
