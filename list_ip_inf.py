#!/usr/bin/env python
# -*- coding: utf-8 -*-


import json
import requests
import sys
import util


def list_interface_by_host( hostip, userid, passwd):
	print hostip
	resp = requests.post( util.get_nxapi_endpoint( hostip), data=json.dumps( util.get_payload( "show ip interface brief")), headers=util.myheaders,auth=(userid,passwd)).json()
	outputs = resp['ins_api']['outputs']
	if not 'Success' in outputs['output']['msg']:
		return
	for row in outputs['output']['body']['TABLE_intf']:
		if row['ROW_intf']['link-state'] == 'up':
			print " - ", row['ROW_intf']['intf-name'], row['ROW_intf']['prefix']


if __name__ == "__main__":
	hosts = util.load_config( sys.argv[1])
	allhosts = hosts['spine'];
	allhosts.extend( hosts['leaf'])
	for host in allhosts:
		list_interface_by_host( host, 'admin', '1234Qwer')
