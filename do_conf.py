#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import requests
import json
import util
import os

FEATURES = ['telnet', 'nxapi', 'bash-shell', 'scp-server', 'ospf', 'bgp', 'lldp', 'vn-segment-vlan-based', 'interface-vlan', 'nv overlay']


def conf_basic( hostip, userid, passwd, role):
	retval = True
	target_cmd = "conf t ; vlan 1 ; ip domain-lookup ; line console ; line vty ; "
	if role == 'leaf':
		target_cmd += 'hardware access-list tcam region vacl 0 ; hardware access-list tcam region arp-ether 256 ; hardware qos ns-buffer-profile burst '		
	target_cmd = util.remove_last_semicolon(target_cmd)
	print target_cmd
	resp = requests.post( util.get_nxapi_endpoint( hostip), data=json.dumps( util.get_conf_payload( target_cmd)), headers=util.myheaders,auth=(userid,passwd)).json()
	outputs = resp['ins_api']['outputs']['output']
	#print outputs
	for out in outputs:
		if not 'Success' in out['msg']:
			retval = False
	print 'do conf nve1 on %s is %s' %(hostip, retval)
	return retval

def conf_nve1( hostip, userid, passwd ):
	retval = True
	target_cmd = "conf t ; interface nve1 ; no shutdown ; source-interface loopback0 ; host-reachability protocol bgp"

	target_cmd = util.remove_last_semicolon(target_cmd)
	print target_cmd
	resp = requests.post( util.get_nxapi_endpoint( hostip), data=json.dumps( util.get_conf_payload( target_cmd)), headers=util.myheaders,auth=(userid,passwd)).json()
	outputs = resp['ins_api']['outputs']['output']
	#print outputs
	for out in outputs:
		if not 'Success' in out['msg']:
			retval = False
	print 'do conf nve1 on %s is %s' %(hostip, retval)
	return retval


def conf_vxlan_mcast( hostip, userid, passwd, anycast, mgrp_list, list_lo1, role='spine'):
	retval = True
	target_cmd = "conf t ; ip pim rp-address %s  group-list %s/8 ; ip pim ssm range 232.0.0.0/8 ; " %(anycast, mgrp_list)
	if role == 'leaf':
		target_cmd += "fabric forwarding anycast-gateway-mac 0000.2222.3333 ; "
	if role == 'spine':
		target_cmd += "ip pim rp-candidate loopback1 group-list %s/8 ; " %(mgrp_list)
		for lo1 in list_lo1:
			target_cmd += "ip pim anycast-rp %s %s ; " %(anycast, util.get_ip_from_cidr(lo1))
	
	target_cmd = util.remove_last_semicolon(target_cmd)
	print target_cmd
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
	target_cmd = "conf t ; vrf context %s ; vni %d ; rd auto ; address-family ipv6 unicast ; route-target both auto ; route-target both auto evpn ; " %(vrf_name, vnid)
	target_cmd += "interface nve1 ; member vni %d associate-vrf" %(vnid)
	target_cmd = util.remove_last_semicolon(target_cmd)
	print target_cmd
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
	retval = True
	#create vlan and map vxlan 
	target_cmd = "conf t ; vlan %d ; vn-segment %d ;" %(vlan, vxlan)
	#config vlan svi 
	target_cmd += " interface vlan %d ; no shut ;  vrf member %s ; ip address %s/24 ; ipv6 address %s/64 ; fabric forwarding mode anycast-gateway ; " %(vlan, vrf, vlan_svi, util.to_simple_ipv6(vlan_svi))
	#add nve1 
	target_cmd += " interface nve1 ; member vni %d ; suppress-arp ; mcast-group %s ;" %(vxlan, mcast)
	#add evpn
	target_cmd += " evpn ; vni %d l2 ; route-target import auto ; route-target export auto" %(vxlan)
	target_cmd = util.remove_last_semicolon(target_cmd)
	#print target_cmd
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
	target_cmd  = "conf t ; no interface vlan %d ; no vlan %d ; interface nve1 ; no member vni %d ; evpn ; no vni %d l2" %(vlan, vlan, vxlan, vxlan)
	target_cmd = util.remove_last_semicolon(target_cmd)
	resp = requests.post( util.get_nxapi_endpoint( hostip), data=json.dumps( util.get_conf_payload( target_cmd)), headers=util.myheaders,auth=(userid,passwd)).json()
	outputs = resp['ins_api']['outputs']['output']
	#print outputs
	for out in outputs:
		if not 'Success' in out['msg']:
			retval = False
	print 'delete vlan on %s is %s' %(hostip, retval)
	return retval

def conf_interface( hostip, userid, passwd, switch_model, ospf_as):
	retval = True
	target_cmd = 'conf t ; interface lo0 ; ip address %s ; ip router ospf %s area 0.0.0.0 ; ip pim sparse-mode ; ' %( switch_model['lo0'], ospf_as)
	if switch_model.has_key('lo1') and switch_model['role'] == 'spine' :
		target_cmd += 'interface lo1 ; ip address %s ; ip router ospf %s area 0.0.0.0 ; ip pim sparse-mode ; ' %( switch_model['lo1'], ospf_as)
	for intf in switch_model['fabric'].keys():
		target_cmd += 'interface %s ; ip address %s ; ip router ospf %s area 0.0.0.0 ; ip pim sparse-mode ; no shut ; ' %(intf, switch_model['fabric'][intf], ospf_as)
	target_cmd = util.remove_last_semicolon(target_cmd)
	print target_cmd
	resp = requests.post( util.get_nxapi_endpoint( hostip), data=json.dumps( util.get_conf_payload( target_cmd)), headers=util.myheaders,auth=(userid,passwd)).json()
	outputs = resp['ins_api']['outputs']['output']
	#print outputs
	for out in outputs:
		if not 'Success' in out['msg']:
			retval = False
	print 'conf interface on %s is %s' %(hostip, retval)
	return retval	

def conf_features( hostip, userid, passwd, features):
	retval = True
	target_cmd = ""
	cmd = " feature %s ;"
	for f in features:
		target_cmd +=  cmd % f
	target_cmd = util.remove_last_semicolon(target_cmd)
	print target_cmd
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
	target_cmd = 'conf t ; router ospf %d'
	for intf in intfs:
		target_cmd += 'interface %s ; ip router ospf %s area 0.0.0.0 ; ' %(intf, ospf_as)
	target_cmd = util.remove_last_semicolon(target_cmd)
	print target_cmd
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
		target_cmd += ' neighbor %s remote-as %s ; update-source loopback0 ; address-family l2vpn evpn ; send-community both ; ' % (peer, bgp_as)
		if role == 'spine':
			target_cmd += ' route-reflector-client ; '
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


if __name__ == '__main__':
	host_role = {'spine':[], 'leaf':[]}
	conf_model = util.load_model_config( sys.argv[1]) #switch-model.yaml 
	for h in conf_model.keys():
		if conf_model[h].has_key('role') :
			if conf_model[h]['role'] == 'spine':
				host_role['spine'].append( h)
			else:
				host_role['leaf'].append( h)
	print host_role

	
	for host in host_role['spine']:
		conf_basic(host, os.environ['NEXUS_USER'], os.environ['NEXUS_PASSWD'], 'spine')
		conf_features( host, os.environ['NEXUS_USER'], os.environ['NEXUS_PASSWD'], FEATURES)
		conf_interface( host, os.environ['NEXUS_USER'], os.environ['NEXUS_PASSWD'], conf_model[host], conf_model['common']['ospf_as'])
		conf_vxlan_mcast( host, os.environ['NEXUS_USER'], os.environ['NEXUS_PASSWD'], 
			util.get_ip_from_cidr(conf_model[host]['lo1']), '225.0.0.0', util.get_spine_lo0_list( conf_model),
			'spine')
		conf_bgp(host, os.environ['NEXUS_USER'], os.environ['NEXUS_PASSWD'], 
			conf_model['common']['bgp_as'], util.get_ip_from_cidr(conf_model[host]['lo0']), 
			util.get_bgp_peers( host, conf_model), 'spine')

	for host in host_role['leaf']:
		conf_basic(host, os.environ['NEXUS_USER'], os.environ['NEXUS_PASSWD'], 'leaf')
		conf_features( host, os.environ['NEXUS_USER'], os.environ['NEXUS_PASSWD'], FEATURES)
		conf_interface( host, os.environ['NEXUS_USER'], os.environ['NEXUS_PASSWD'], conf_model[host], conf_model['common']['ospf_as'])
		conf_vxlan_mcast( host, os.environ['NEXUS_USER'], os.environ['NEXUS_PASSWD'], 
			util.get_spine_lo1(conf_model), '225.0.0.0', util.get_spine_lo0_list( conf_model),
			'leaf')
		conf_nve1(host, os.environ['NEXUS_USER'], os.environ['NEXUS_PASSWD'])
		conf_bgp(host, os.environ['NEXUS_USER'], os.environ['NEXUS_PASSWD'], 
			conf_model['common']['bgp_as'], util.get_ip_from_cidr(conf_model[host]['lo0']), 
			util.get_bgp_peers( host, conf_model), 'leaf')
		create_vrf(host, os.environ['NEXUS_USER'], os.environ['NEXUS_PASSWD'], "vxlan-90001", 90001)

	
	#retval = create_vlan( '10.72.86.56', os.environ['NEXUS_USER'], os.environ['NEXUS_PASSWD'], 1003, '192.168.103.1', 'vxlan-900001', 2001003, '225.4.0.1')
	#for host in host_role['leaf']:
		#retval = create_vlan( host, os.environ['NEXUS_USER'], os.environ['NEXUS_PASSWD'], 1003, '192.168.103.1', 'vxlan-900001', 2001003, '225.4.0.1')
		#retval = delete_vlan( host, os.environ['NEXUS_USER'], os.environ['NEXUS_PASSWD'], 1003, '192.168.103.1', 'vxlan-900001', 2001003, '225.4.0.1')


