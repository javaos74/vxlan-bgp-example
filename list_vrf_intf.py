#!/usr/bin/env python
# -*- coding: utf-8 -*-


import json
import requests
import sys
import util
import os
from prettytable import PrettyTable


def list_vrf_interface_by_host( hostip, userid, passwd):
	print hostip
	vrf_map = {}
	resp = requests.post( util.get_nxapi_endpoint( hostip), data=json.dumps( util.get_payload( "show vrf interface")), headers=util.myheaders,auth=(userid,passwd)).json()
	outputs = resp['ins_api']['outputs']
	if not 'Success' in outputs['output']['msg']:
		return
	for row in outputs['output']['body']['TABLE_if']['ROW_if']:
		if vrf_map.has_key( row['vrf_name']):
			vrf_map[row['vrf_name']].add( row['if_name'])
		else:
			vrf_map[row['vrf_name']] = set()
			vrf_map[row['vrf_name']].add( row['if_name'])
	pt = PrettyTable(["vrf-name", "interface"])
	pt.align["vrf-name"] = "l" # Left align city names
	pt.padding_width = 1 # One space between column edges and contents (default)	
	for n in vrf_map.keys():
		pt.add_row( [ n, ",".join( vrf_map.get(n))])	
	print pt

if __name__ == "__main__":
	hosts = util.load_config( sys.argv[1]) #hosts.yaml 
	allhosts = hosts['spine'];
	allhosts.extend( hosts['leaf'])
	allhosts.extend( hosts['router'])
	for host in allhosts:
		list_vrf_interface_by_host( host, os.environ['NEXUS_USER'], os.environ['NEXUS_PASSWD'])
