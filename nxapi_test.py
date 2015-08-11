#!/usr/bin/env python
# -*- coding: utf-8 -*-

import requests
import json

"""
Modify these please
"""
url='http://10.72.86.58/ins'
switchuser='admin'
switchpassword='1234Qwer'

myheaders={'content-type':'application/json'}
payload={
  "ins_api": {
    "version": "1.0",
    "type": "cli_show",
    "chunk": "0",
    "sid": "1",
    "input": "show hostname",
    "output_format": "json"
  }
}
print payload
response = requests.post(url,data=json.dumps(payload), headers=myheaders,auth=(switchuser,switchpassword)).json()
print response