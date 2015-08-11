#!/usr/bin/env python
# -*- coding: utf-8 -*-


import json
import requests
import sys
import util
import os


def list_interface_by_host( hostip, userid, passwd):
	print hostip
	resp = requests.post( util.get_nxapi_endpoint( hostip), data=json.dumps( util.get_payload( "show interface brief")), headers=util.myheaders,auth=(userid,passwd)).json()
	outputs = resp['ins_api']['outputs']
	if not 'Success' in outputs['output']['msg']:
		return
	try:
		for row in outputs['output']['body']['TABLE_interface']['ROW_interface']:
			if row['state'] == 'up':
				print " - ", row['interface'], row['vlan'] if row.has_key('vlan') else '--', row['portmode'] if row.has_key('portmode') else ''

	except Exception as e:
		print e


if __name__ == "__main__":
	hosts = util.load_config( sys.argv[1])
	allhosts = hosts['spine'];
	allhosts.extend( hosts['leaf'])
	allhosts.extend( hosts['router'])
	for host in allhosts:
		list_interface_by_host( host, os.environ['NEXUS_USER'], os.environ['NEXUS_PASSWD'])
