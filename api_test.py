import requests as req
import time, subprocess
import logging,json
from TC_API import TC_API


logger=logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
logger.addHandler(logging.StreamHandler())



tc = TC_API()
d=tc.make_request('/api/v2/tags/Needs%20Review/indicators?resultStart=100','GET')
jd=json.loads(d)
for i in range(0,100):
    print(json.dumps(jd['data']['indicator'][0],indent=4))
# print(json.dumps(jd,indent=4))


