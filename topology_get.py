#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
 NX-API-BOT 
"""
import requests
import json
import sys
import util
import os


def get_neighbors( hostip, userid, passwd):
	myentries = []
	resp = requests.post( util.get_nxapi_endpoint( hostip), data=json.dumps( util.get_payload('show cdp neighbors')), headers=util.myheaders,auth=(userid,passwd)).json()
	#print resp
	success = resp['ins_api']['outputs']['output']['msg']
	if success == 'Success' :
		entries = resp['ins_api']['outputs']['output']['body']['TABLE_cdp_neighbor_brief_info']['ROW_cdp_neighbor_brief_info']
		if type(entries) == list:
			for entry in entries:
				e = {}
				e['device_id'] = entry['device_id']
				e['intf_id'] = entry['intf_id']
				e['port_id'] = entry['port_id']
				myentries.append( e)
			return myentries
		elif type(entries) == dict:
			e = {}
			e['device_id'] = entries['device_id']
			e['intf_id'] = entries['intf_id']
			e['port_id'] = entries['port_id']
			myentries.append( e)
		return myentries


def find_index_from_nodes( name, nodes):
	for idx,val in enumerate(nodes):
		if name.lower() == val['name'].lower():
			return idx
	return -1
def get_hostname_from_address( hostip, nodes):
	for idx,val in enumerate(nodes):
		if hostip == val['address']:
			return val['name']
	return ""

def build_nodes( node, hostip=None):
	item = {}
	item['name'] = node
	item['size'] = 20
	if 'leaf' in node.lower():
		item['type'] = 'leaf'
	else:
		item['type'] = 'spine'
	if hostip:
		item['address'] = hostip
	return item

def get_host_from_device_id( devid):
	return devid.split('(')[0]

if __name__ == '__main__':
	hosts = util.load_config( sys.argv[1])
	graph = {}
	graph['nodes'] = []
	graph['links'] = []
	for hostip in hosts:
		graph['nodes'].append( util.build_nodes( util.get_host(hostip,os.environ['NEXUS_USER'], os.environ['NEXUS_PASSWD']), hostip))

	for hostip in hosts:
		entries = get_neighbors( hostip, os.environ['NEXUS_USER'], os.environ['NEXUS_PASSWD'])
		source = find_index_from_nodes( get_hostname_from_address(hostip, graph['nodes']), graph['nodes'])
		for entry in entries:
			target = find_index_from_nodes( get_host_from_device_id(entry['device_id']), graph['nodes'])
			link = {'bond':1}
			link['source'] = source
			link['target'] = target
			if source >= 0 and target >= 0:
				graph['links'].append( link)

	print json.dumps(graph)
	