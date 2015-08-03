#!/usr/bin/env python
# -*- coding: utf-8 -*-


import sys
import requests
import json
import util


def update_cdp(hostip, userid, passwd):
	retval = True
	target_cmd = "python bootflash:update_cdp.py"
	target_cmd = util.remove_last_semicolon(target_cmd)
	resp = requests.post( util.get_nxapi_endpoint( hostip), data=json.dumps( util.get_conf_payload( target_cmd)), headers=util.myheaders,auth=(userid,passwd)).json()
	outputs = resp['ins_api']['outputs']['output']
	#print outputs
	if not 'Success' in outputs['msg']:
		retval = False
	print 'update_cdp on %s is %s' %(hostip, retval)
	return retval

if __name__ == '__main__':
	role  = util.load_config( sys.argv[1]) #hosts.yaml
	for host in role['leaf']:
		update_cdp( host, 'admin', '1234Qwer')
	for host in role['spine']:
		update_cdp( host, 'admin', '1234Qwer')