#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json

nexus72 = False
try:
	import cli
except:
	import cisco as cli
	nexus72 = True


def get_user_desc( intf):
	txt = cli.clid('show interface %s desc' %intf)
	try:
		if type(txt) == str:
			d = json.loads(txt)
			desc = d['TABLE_interface']['ROW_interface']['desc']
		else:
			desc = txt['TABLE_interface']['ROW_interface']['desc']
		if desc != None and len(desc) > 1:
			msg = desc.split(':')                                 
			return msg[0].strip() if len(msg) > 1 else ''  
	except:
		pass
	return ''
		

def update_desc_with_cdp_neighbors( neighbors):
	devices = neighbors['TABLE_cdp_neighbor_brief_info']['ROW_cdp_neighbor_brief_info']
	for device in devices:
		desc = get_user_desc(device['intf_id']) + " : to %(port_id)s of %(device_id)s" %device
		r = cli.cli('conf t ; interface %s ; desc %s' %(device['intf_id'], desc))
		print r

def update_desc_with_cdp_neighbors_nexus72( neighbors):
	mydevices = {}
	for item in neighbors.keys():
		keys = item.split('/')
		if keys[1] in ['intf_id', 'port_id', 'device_id'] :
			if not mydevices.has_key( keys[2]):
				dev = {}
			dev[ keys[1]] = neighbors[item]
			mydevices[ keys[2]] = dev

	for idx in mydevices.keys():
		desc = "to %(port_id)s of %(device_id)s" %mydevices[idx]
		r = cli.cli('conf t ; interface %s ; desc %s' %(mydevices[idx]['intf_id'], desc))
		print r

if __name__ == '__main__':
	txt = cli.clid('show cdp nei')
	if type(txt) == str:
		update_desc_with_cdp_neighbors(json.loads(txt))
	else:
		update_desc_with_cdp_neighbors_nexus72 (txt)

