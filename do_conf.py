#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import requests
import json
import util
import os

FEATURES = ['telnet', 'nxapi', 'bash-shell', 'scp-server', 'ospf', 'bgp', 'lldp', 'vn-segment-vlan-based', 'interface-vlan', 'nv overlay']


def conf_nve1( hostip, userid, passwd ):
	retval = True
	target_cmd = "conf t ; interface nve1 ; no shutdown ; source-interface loopback0 ; host-reachability protocol bgp"

	target_cmd = util.remove_last_semicolon(target_cmd)
	resp = requests.post( util.get_nxapi_endpoint( hostip), data=json.dumps( util.get_conf_payload( target_cmd)), headers=util.myheaders,auth=(userid,passwd)).json()
	outputs = resp['ins_api']['outputs']['output']
	#print outputs
	for out in outputs:
		if not 'Success' in out['msg']:
			retval = False
	print 'do conf nve1 on %s is %s' %(hostip, retval)
	return retval


def conf_vxlan( hostip, userid, passwd, anycast, mgrp_list, list_lo1, role='spine'):
	retval = True
	target_cmd = "conf t ; ip pim rp-address %s  group-list %s/8 ; ip pim ssm range 232.0.0.0/8 ; " %(anycast, mgrp_list)
	if role == 'leaf':
		target_cmd += "fabric forwarding anycast-gateway-mac 0000.2222.3333 ; "
	if role == 'spine':
		target_cmd += "ip pim rp-candidate loopback1 group-list %s/8 ; " %(mgrp_list)
		for lo1 in list_lo1:
			target_cmd += "ip pim anycast-rp %s %s ; " %(anycast, lo1)
	
	target_cmd = util.remove_last_semicolon(target_cmd)
	resp = requests.post( util.get_nxapi_endpoint( hostip), data=json.dumps( util.get_conf_payload( target_cmd)), headers=util.myheaders,auth=(userid,passwd)).json()
	outputs = resp['ins_api']['outputs']['output']
	#print outputs
	for out in outputs:
		if not 'Success' in out['msg']:
			retval = False
	print 'do conf vxlan/nve1 on %s is %s' %(hostip, retval)
	return retval


def create_vrf(hostip, userid, passwd, vrf_name, vnid ):
	retval = True
	target_cmd = "conf t ; vrf context %s ; vni %d ; rd auto ; address-family ipv6 unicast ; route-target both auto ; route-target both auto evpn " %(vrf_name, vnid)
	target_cmd += "interface nve1 ; member vni %d associate-vrf" %(vnid)
	target_cmd = util.remove_last_semicolon(target_cmd)
	resp = requests.post( util.get_nxapi_endpoint( hostip), data=json.dumps( util.get_conf_payload( target_cmd)), headers=util.myheaders,auth=(userid,passwd)).json()
	outputs = resp['ins_api']['outputs']['output']
	#print outputs
	for out in outputs:
		if not 'Success' in out['msg']:
			retval = False
	print 'do conf vrf/tenant on %s is %s' %(hostip, retval)
	return retval

def delete_vrf( hostip, userid, passwd, vrf_name, vnid):
	retval = True
	target_cmd = "conf t ; no vrf context %s ; interface nve1 ; no member vni %d associate-vrf " %(vrf_name, vnid)
	target_cmd = util.remove_last_semicolon(target_cmd)
	resp = requests.post( util.get_nxapi_endpoint( hostip), data=json.dumps( util.get_conf_payload( target_cmd)), headers=util.myheaders,auth=(userid,passwd)).json()
	outputs = resp['ins_api']['outputs']['output']
	#print outputs
	for out in outputs:
		if not 'Success' in out['msg']:
			retval = False
	print 'do delete vrf/tenant on %s is %s' %(hostip, retval)
	return retval

def create_vlan( hostip, userid, passwd, vlan, vlan_svi, vrf, vxlan, mcast):
	#create vlan and map vxlan 
	target_cmd = "conf t ; vlan %d ; vn-segment %d ;"
	#config vlan svi 
	target_cmd += " interface vlan %d ; no shut ;  vrf member %s ; ip address %s/24 ; ipv6 address %s/64 fabric forwarding mode anycast-gateway " %(vlan, vrf, vlan_svi, util.to_simple_ipv6(vlan_svi))
	#add nve1 
	target_cmd += " interface nve1 ; member vni %d ; suppress-arp ; mcast-group %s " %(vxlan, mcast)

	target_cmd = util.remove_last_semicolon(target_cmd)
	resp = requests.post( util.get_nxapi_endpoint( hostip), data=json.dumps( util.get_conf_payload( target_cmd)), headers=util.myheaders,auth=(userid,passwd)).json()
	outputs = resp['ins_api']['outputs']['output']
	#print outputs
	for out in outputs:
		if not 'Success' in out['msg']:
			retval = False
	print 'create vlan on %s is %s' %(hostip, retval)
	return retval

def delete_vlan(hostip, userid, passwd, vlan, vlan_svi, vrf, vxlan, mcast):
	retval = True
	target_cmd  = "conf t ; no interface vlan %d ; no vlan %d "
	target_cmd = util.remove_last_semicolon(target_cmd)
	resp = requests.post( util.get_nxapi_endpoint( hostip), data=json.dumps( util.get_conf_payload( target_cmd)), headers=util.myheaders,auth=(userid,passwd)).json()
	outputs = resp['ins_api']['outputs']['output']
	#print outputs
	for out in outputs:
		if not 'Success' in out['msg']:
			retval = False
	print 'delete vlan on %s is %s' %(hostip, retval)
	return retval

def conf_features( hostip, userid, passwd, features):
	retval = True
	target_cmd = ""
	cmd = " feature %s ;"
	for f in features:
		target_cmd +=  cmd % f
	target_cmd = util.remove_last_semicolon(target_cmd)
	resp = requests.post( util.get_nxapi_endpoint( hostip), data=json.dumps( util.get_conf_payload( target_cmd)), headers=util.myheaders,auth=(userid,passwd)).json()
	outputs = resp['ins_api']['outputs']['output']
	#print outputs
	for out in outputs:
		if not 'Success' in out['msg']:
			retval = False
	print 'do conf feature on %s is %s' %(hostip, retval)
	return retval


def conf_ospf( hostip, userid, passwd, ospf_as, intfs):
	retval = True
	target_cmd = 'conf t ; '
	for intf in intfs:
		target_cmd += 'interface %s ; ip router ospf %s area 0.0.0.0 ; ' %(intf, ospf_as)
	target_cmd = util.remove_last_semicolon(target_cmd)
	#print target_cmd
	resp = requests.post( util.get_nxapi_endpoint( hostip), data=json.dumps( util.get_conf_payload( target_cmd)), headers=util.myheaders,auth=(userid,passwd)).json()
	outputs = resp['ins_api']['outputs']['output']
	for output in outputs:
		if not 'Success' == output['msg']:
			retval = False
	print 'do ospf conf on %s is %s' %(hostip, retval)
	return retval

def conf_bgp( hostip, userid, passwd, bgp_as, lo0, peers, role = 'spine'):
	retval = True
	target_cmd = 'conf t ; router bgp %s ; router-id %s ;' %(bgp_as, lo0)
	for peer in peers:
		target_cmd += ' neighbor %s remote-as %s ; update-source loopback0 ; address-family l2vpn evpn ; send-community both ' % (peer, bgp_as)
		if role == 'spine':
			target_cmd += ' ; route-reflector-client ;'
	target_cmd = util.remove_last_semicolon(target_cmd)
	print target_cmd
	
	resp = requests.post( util.get_nxapi_endpoint( hostip), data=json.dumps( util.get_conf_payload( target_cmd)), headers=util.myheaders,auth=(userid,passwd)).json()
	outputs = resp['ins_api']['outputs']['output']
	#print outputs
	for output in outputs:
		if not 'Success' == output['msg']:
			retval = False
	print 'do bgp conf on %s is %s' %(hostip, retval)	
	return retval

def get_vrf_list(hostip,userid,passwd):
	retval = True
	target_cmd = "show vrf interface "

if __name__ == '__main__':
	host_role = util.load_config( sys.argv[1]) #hosts.yaml
	hosts = host_role['spine'];
	hosts.extend( host_role['leaf'])
	conf_model = util.load_model_config( sys.argv[2]) #switch-model.yaml 
	'''
	retval = conf_features(hosts[0],os.environ['NEXUS_USER'], os.environ['NEXUS_PASSWD'], FEATURES )
	retval = conf_bgp( hosts[0], os.environ['NEXUS_USER'], os.environ['NEXUS_PASSWD'], 
			conf_model['common']['bgp_as'], 
			conf_model[ hosts[0]]['lo0'].split('/')[0],
			util.get_bgp_peers( hosts[0], conf_model), 
			conf_model[hosts[0]]['role'])
	'''
	for host in host_role['leaf']:
		retval = create_vlan( host, os.environ['NEXUS_USER'], os.environ['NEXUS_PASSWD'], 1003, '192.168.103.1', 'vxlan-900001', '2001003', '255.4.0.1')


