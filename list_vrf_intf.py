#!/usr/bin/env python
# -*- coding: utf-8 -*-


import json
import requests
import sys
import util


def list_vrf_interface_by_host( hostip, userid, passwd):
	print hostip
	vrf_map = {}
	resp = requests.post( util.get_nxapi_endpoint( hostip), data=json.dumps( util.get_payload( "show vrf interface")), headers=util.myheaders,auth=(userid,passwd)).json()
	outputs = resp['ins_api']['outputs']
	if not 'Success' in outputs['output']['msg']:
		return
	for row in outputs['output']['body']['TABLE_if']:
		if vrf_map.has_key() :
			vrf_map[row['ROW_if']['vrf_name']] = 
		else:
			vrf_map[row['ROW_if']['vrf_name']] = set()
			vrf_map[row['ROW_if']['vrf_name']].add( row['ROW_if']['if_name'])
			print " - ", row['ROW_intf']['intf-name'], row['ROW_intf']['prefix']


if __name__ == "__main__":
	hosts = util.load_config( sys.argv[1])
	allhosts = hosts['spine'];
	allhosts.extend( hosts['leaf'])
	for host in allhosts:
		list_interface_by_host( host, 'admin', '1234Qwer')
