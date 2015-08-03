#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import requests
import json
import util
import os
from prettytable import PrettyTable




def show_nve_peers(hostip,userid,passwd):
	pt = PrettyTable(["if-name", "peer-ip","peer-state", "uptime", "router-mac"])
	pt.align["if-name"] = "l" # Left align city names
	pt.padding_width = 1 # One space between column edges and contents (default)

	resp = requests.post( util.get_nxapi_endpoint( hostip), data=json.dumps( util.get_payload( "show nve peers")), headers=util.myheaders,auth=(userid,passwd)).json()
	outputs = resp['ins_api']['outputs']
	if not 'Success' in outputs['output']['msg']:
		return
	for row in outputs['output']['body']['TABLE_nve_peers']['ROW_nve_peers']:
		pt.add_row([ row['if-name'], row['peer-ip'], row['peer-state'], row['uptime'], row['router-mac'] ])
	print pt

def show_nve_vni(hostip,userid,passwd):
	pt = PrettyTable(["if-name", "vni","mcast", "vni-state", "mode", "type"])
	pt.align["if-name"] = "l" # Left align city names
	pt.padding_width = 1 # One space between column edges and contents (default)

	resp = requests.post( util.get_nxapi_endpoint( hostip), data=json.dumps( util.get_payload( "show nve vni")), headers=util.myheaders,auth=(userid,passwd)).json()
	outputs = resp['ins_api']['outputs']
	if not 'Success' in outputs['output']['msg']:
		return
	for row in outputs['output']['body']['TABLE_nve_vni']['ROW_nve_vni']:
		pt.add_row([ row['if-name'], row['vni'], row['mcast'], row['vni-state'], row['mode'], row['type'] ])
	print pt

def show_mac_all(hostip,userid,passwd):
	pt = PrettyTable(["topo-id", "mac-addr","prod-type", "next-hop"])
	pt.align["topo-id"] = "l" # Left align city names
	pt.padding_width = 1 # One space between column edges and contents (default)

	resp = requests.post( util.get_nxapi_endpoint( hostip), data=json.dumps( util.get_payload( "show l2route evpn mac all")), headers=util.myheaders,auth=(userid,passwd)).json()
	outputs = resp['ins_api']['outputs']
	if not 'Success' in outputs['output']['msg']:
		return
	for row in outputs['output']['body']['TABLE_l2route_mac_all']['ROW_l2route_mac_all']:
		pt.add_row([ row['topo-id'], row['mac-addr'], row['prod-type'], row['next-hop'] ])
	print pt

def show_mac_ip_all(hostip,userid,passwd):
	pt = PrettyTable(["topo-id", "mac-addr","prod-type", "host-ip", "next-hop"])
	pt.align["topo-id"] = "l" # Left align city names
	pt.padding_width = 1 # One space between column edges and contents (default)

	resp = requests.post( util.get_nxapi_endpoint( hostip), data=json.dumps( util.get_payload( "show l2route evpn mac-ip all")), headers=util.myheaders,auth=(userid,passwd)).json()
	outputs = resp['ins_api']['outputs']
	if not 'Success' in outputs['output']['msg']:
		return
	for row in outputs['output']['body']['TABLE_l2route_mac_ip_all']['ROW_l2route_mac_ip_all']:
		pt.add_row([ row['topo-id'], row['mac-addr'], row['prod-type'], row['host-ip'], row['next-hop'] ])
	print pt




if __name__ == '__main__':
	hosts = []
	if len(sys.argv) != 3:
		print '#python mon_vxlan.py {nve_peer|nve_vni|mac_all|mac_ip_all} switch-model.yaml'
		sys.exit(0)

	cmd = sys.argv[1]
	model = util.load_model_config( sys.argv[2]) #switch-model.yaml 
	for h in model.keys():
		if model[h].has_key('role') :
			if model[h]['role'] == 'leaf':
				hosts.append( h)
	
	if cmd == 'nve_peer':
		for host in hosts:
			print '[switch] ' + host
			show_nve_peers( host, os.environ['NEXUS_USER'], os.environ['NEXUS_PASSWD'])
	elif cmd == 'nve_vni':
		for host in hosts:
			print '[switch] ' + host
			show_nve_vni( host, os.environ['NEXUS_USER'], os.environ['NEXUS_PASSWD'])
	elif cmd == 'mac_all':
		for host in hosts:
			print '[switch] ' + host
			show_mac_all( host, os.environ['NEXUS_USER'], os.environ['NEXUS_PASSWD'])
	elif cmd == 'mac_ip_all':
		for host in hosts:
			print '[switch] ' + host
			show_mac_ip_all( host, os.environ['NEXUS_USER'], os.environ['NEXUS_PASSWD'])

			

