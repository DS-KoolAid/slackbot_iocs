import requests as req
import time, subprocess
import logging,json
from tc_api import tc_api


logger=logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
logger.addHandler(logging.StreamHandler())



tc = tc_api()
d=tc.get_iocs(page=2)
for i in d:
    print(d)
# print(json.dumps(d['data']['indicator']))
# for i in d['data']['indicator']:
#     print(json.dumps(i['summary'],indent=4))



