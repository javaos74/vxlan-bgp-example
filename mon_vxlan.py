#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import requests
import json
import util
import os
from prettytable import PrettyTable



def get_func(key):
	if func_table.has_key(key):
		return func_table[key]
	else :
		print 'usage : python mon_vxlan.py {cmd} {switch-model.yaml}'
		print 'available cmd list : ',
		for k in func_table:
			print k,

def show_nve_peers(hostip,userid,passwd):
	pt = PrettyTable(["if-name", "peer-ip","peer-state", "uptime", "router-mac"])
	pt.align["if-name"] = "l" # Left align city names
	pt.padding_width = 1 # One space between column edges and contents (default)

	resp = requests.post( util.get_nxapi_endpoint( hostip), data=json.dumps( util.get_payload( "show nve peers")), headers=util.myheaders,auth=(userid,passwd)).json()
	outputs = resp['ins_api']['outputs']
	if not 'Success' in outputs['output']['msg']:
		return
	if type(outputs['output']['body']['TABLE_nve_peers']['ROW_nve_peers']) == list: 
		for row in outputs['output']['body']['TABLE_nve_peers']['ROW_nve_peers']:
			pt.add_row([ row['if-name'], row['peer-ip'], row['peer-state'], row['uptime'], row['router-mac'] ])
	else :
		row = outputs['output']['body']['TABLE_nve_peers']['ROW_nve_peers']
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
	if type(outputs['output']['body']) == dict:
		if type(outputs['output']['body']['TABLE_l2route_mac_all']['ROW_l2route_mac_all']) == list:
			for row in outputs['output']['body']['TABLE_l2route_mac_all']['ROW_l2route_mac_all']:
				pt.add_row([ row['topo-id'], row['mac-addr'], row['prod-type'], row['next-hop'] ])
		else:
			row = outputs['output']['body']['TABLE_l2route_mac_all']['ROW_l2route_mac_all']
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
	if type(outputs['output']['body']) == dict:
		if type(outputs['output']['body']['TABLE_l2route_mac_ip_all']['ROW_l2route_mac_ip_all']) == list:
			for row in outputs['output']['body']['TABLE_l2route_mac_ip_all']['ROW_l2route_mac_ip_all']:
				pt.add_row([ row['topo-id'], row['mac-addr'], row['prod-type'], row['host-ip'], row['next-hop'] ])
			else:
				row = outputs['output']['body']['TABLE_l2route_mac_ip_all']['ROW_l2route_mac_ip_all']
				pt.add_row([ row['topo-id'], row['mac-addr'], row['prod-type'], row['host-ip'], row['next-hop'] ])
	print pt


def show_ip_arp_suppression(hostip,userid,passwd):
	pt = PrettyTable(["ip-addr", "age","mac", "vlan", "physical-iod", "flag"])
	pt.align["ip-addr"] = "l" # Left align city names
	pt.padding_width = 1 # One space between column edges and contents (default)

	resp = requests.post( util.get_nxapi_endpoint( hostip), data=json.dumps( util.get_payload( "show ip arp suppression-cache detail")), headers=util.myheaders,auth=(userid,passwd)).json()
	outputs = resp['ins_api']['outputs']
	if not 'Success' in outputs['output']['msg']:
		return
	if type(outputs['output']['body']) == dict:	
		for row in outputs['output']['body']['TABLE_arp-suppression']['ROW_arp-suppression']['TABLE_entries']['ROW_entries']:
			pt.add_row([ row['ip-addr'], row['age'], row['mac'], row['vlan'], row['physical-iod'], row['flag'] ])
	print pt

def show_vxlan_interface(hostip,userid,passwd):
	pt = PrettyTable(["Interface", "Vlan","VPL Ifindex", "LTL", "HW VP" ])
	pt.align["Interface"] = "l" # Left align city names
	pt.padding_width = 1 # One space between column edges and contents (default)

	resp = requests.post( util.get_nxapi_endpoint( hostip), data=json.dumps( util.get_payload_ascii( "show vxlan interface")), headers=util.myheaders,auth=(userid,passwd)).json()
	outputs = resp['ins_api']['outputs']
	if not 'Success' in outputs['output']['msg']:
		return
	body = outputs['output']['body']
	items = body.split("\n")
	for item in items:
		vals = item.split(' ')
		#print vals
		if len(vals) == 7 and vals[0] != 'Interface':
			pt.add_row( [vals[0], vals[2], vals[3], vals[4], vals[6]])
	print pt	

def show_vmtracker(hostip,userid,passwd):
	pt = PrettyTable(["Interface", "Host","VMNIC","VM", "State", "PortGroup", "VLAN-Range" ])
	pt.align["Interface"] = "l" # Left align city names
	pt.padding_width = 1 # One space between column edges and contents (default)
	resp = requests.post( util.get_nxapi_endpoint( hostip), data=json.dumps( util.get_payload_ascii( "show vmtracker info detail")), headers=util.myheaders,auth=(userid,passwd)).json()
	outputs = resp['ins_api']['outputs']
	if not 'Success' in outputs['output']['msg']:
		return
	body = outputs['output']['body']
	items = body.split("\n")
	for item in items:
		vals = item.split(' ')
		if len(vals) == 27 and vals[0] != 'Interface' and vals[0][0] != '-' :
			pt.add_row( [vals[0], vals[1], vals[6], vals[8], vals[9], vals[13], vals[20] ])
	print pt


def show_interface_rate(hostip,userid,passwd):

	pt = PrettyTable(["Port", "Intvl","Rx Mbps","Rx %", "Rx pps", "Tx Mbps", "Tx %", "Tx pps" ])
	pt.align["Port"] = "l" # Left align city names
	pt.padding_width = 1 # One space between column edges and contents (default)
	resp = requests.post( util.get_nxapi_endpoint( hostip), data=json.dumps( util.get_payload_ascii( "python bootflash:whchoi/interface_rate.py")), headers=util.myheaders,auth=(userid,passwd)).json()
	outputs = resp['ins_api']['outputs']
	if not 'Success' in outputs['output']['msg']:
		return
	body = outputs['output']['body']
	items = body.split("\n")
	for item in items:
		vals = item.split(' ')
		#print len(vals)
		if len(vals) > 46: 
			pt.add_row( util.remove_empty_element_from_list( vals))
	print pt

def show_interface_stat(hostip,userid,passwd):
	pt = PrettyTable(["interface", 'eth_ip_addr', "eth_inucast","eth_inpkts", "eth_inbytes", "eth_outucast", "eth_outpkts", "eth_outbytes"])
	pt.align["interface"] = "l" # Left align city names
	pt.padding_width = 1 # One space between column edges and contents (default)
	intfs = ['eth1/1', 'eth1/2', 'eth1/3', 'eth1/4']
	for intf in intfs:
		resp = requests.post( util.get_nxapi_endpoint( hostip), data=json.dumps( util.get_payload( "show interface %s" %intf)), headers=util.myheaders,auth=(userid,passwd)).json()
		outputs = resp['ins_api']['outputs']
		if not 'Success' in outputs['output']['msg']:
			return
		row = outputs['output']['body']['TABLE_interface']['ROW_interface']
		pt.add_row([ row['interface'], row['eth_ip_addr'], row['eth_inucast'], row['eth_inpkts'], row['eth_inbytes'], row['eth_outucast'], row['eth_outpkts'] , row['eth_outbytes'] ])
	print pt

def clear_interafce_all(hostip,userid,passwd):
	resp = requests.post( util.get_nxapi_endpoint( hostip), data=json.dumps( util.get_conf_payload( "clear counters interface all")), headers=util.myheaders,auth=(userid,passwd)).json()
	print resp['ins_api']['outputs']['output']['msg']

func_table = {
	'nve_peer': show_nve_peers,
	'nve_vni': show_nve_vni,
	'mac_all': show_mac_all,
	'mac_ip_all': show_mac_ip_all,
	'ip_arp': show_ip_arp_suppression,
	'vxlan': show_vxlan_interface,
	'vmtracker': show_vmtracker,
	'intrate' : show_interface_rate,
	'intstat' : show_interface_stat,
	'clear_int' : clear_interafce_all,
}

if __name__ == '__main__':
	hosts = []
	if len(sys.argv) != 3:
		print '#python mon_vxlan.py {nve_peer|nve_vni|mac_all|mac_ip_all|ip_arp|vxlan|vmtracker|intrate|intstat|clear_int} switch-model.yaml'
		sys.exit(0)

	cmd = sys.argv[1]
	model = util.load_model_config( sys.argv[2]) #switch-model.yaml 
	for h in model.keys():
		if model[h].has_key('role') :
			if model[h]['role'] == 'leaf':
				hosts.append( h)
	
	func = get_func(cmd)
	if func != None:
		for host in hosts:
			print 'Host = %s' %host
			func(host, os.environ['NEXUS_USER'], os.environ['NEXUS_PASSWD'])


