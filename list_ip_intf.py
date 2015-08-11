#!/usr/bin/env python
# -*- coding: utf-8 -*-


import json
import requests
import sys
import util
import os
from prettytable import PrettyTable


def list_interface_by_host( hostip, userid, passwd):
	print hostip
	resp = requests.post( util.get_nxapi_endpoint( hostip), data=json.dumps( util.get_payload( "show ip interface vrf all")), headers=util.myheaders,auth=(userid,passwd)).json()
	outputs = resp['ins_api']['outputs']
	if not 'Success' in outputs['output']['msg']:
		return
	pt = PrettyTable(["intf-name", "vrf-name", "link-state", 'admin-stat', 'prefix', 'secondary'])
	pt.align["intf-name"] = "l" # Left align city names
	pt.padding_width = 1 # One space between column edges and contents (default)		
	try:
		if type(outputs['output']['body']['TABLE_intf']) == dict:
			for row in outputs['output']['body']['TABLE_intf']['ROW_intf']:
				#print 'dict %r' %row
				if row['link-state'].upper() == 'TRUE':
					pt.add_row( [ row['intf-name'], row['vrf-name-out'], 'up', 'up' if row['admin-state'].upper() == 'TRUE' else 'down', row['prefix'], row['TABLE_secondary_address']['ROW_secondary_address']['prefix1'] if row.has_key('TABLE_secondary_address') else '-' ])
		else :
			for idx,row in enumerate(outputs['output']['body']['TABLE_intf']):
				#print 'list %r' %row
				#print row['ROW_intf']['link-state']
				if row['ROW_intf']['link-state'] == 'up':
					pt.add_row( [ row['ROW_intf']['intf-name'], outputs['output']['body']['TABLE_vrf'][idx]['ROW_vrf']['vrf-name-out'], 'up', row['ROW_intf']['admin-state'], row['ROW_intf']['prefix'], row['ROW_intf']['TABLE_secondary_address']['ROW_secondary_address']['prefix1'] if row['ROW_intf'].has_key('TABLE_secondary_address') else '-' ])
	except Exception as e:
		print e
	print pt


if __name__ == "__main__":
	hosts = util.load_config( sys.argv[1])
	allhosts = hosts['spine'];
	allhosts.extend( hosts['leaf'])
	allhosts.extend( hosts['router'])
	for host in allhosts:
		list_interface_by_host( host, os.environ['NEXUS_USER'], os.environ['NEXUS_PASSWD'])
