#!/usr/bin/env python
# -*- coding: utf-8 -*-

import yaml
import requests
import json

URL='http://%s/ins'

myheaders={'content-type':'application/json'}
payload={
  "ins_api": {
    "version": "1.0",
    "type": "cli_show",
    "chunk": "0",
    "sid": "1",
    "input": "",
    "output_format": "json"
  }
}


def get_nxapi_endpoint( hostip):
  url = URL %hostip
  return url

def get_payload( cmd):
	mypay = payload
	mypay['ins_api']['input'] = cmd
	return mypay

def get_conf_payload( cmd):
  mypay = payload
  mypay['ins_api']['type'] = 'cli_conf'
  mypay['ins_api']['input'] = cmd
  return mypay

def load_config( file):
  with open(file, 'r') as f:
    hosts = yaml.load(f)
  return hosts

def load_model_config( file):
  with open(file, "r") as f:
    model_conf = yaml.load( f)
  return model_conf

def remove_last_semicolon(cmd):
  x = cmd.strip()
  if x[-1] == ';':
    return x[:-1]
  else:
    return x

def get_ip_from_cidr( ipaddr):
  return ipaddr.split('/')[0]

def get_bgp_peers( myhost, model):
  peers = []
  myrole = model[myhost]['role']
  for k in model.keys():
    if not k == 'common':
      if not model[k]['role'] == myrole :
        lo0 = model[k]['lo0']
        if not lo0 == None:
          peers.append ( get_ip_from_cidr( model[k]['lo0']))
  return peers

def to_simple_ipv6(ipv4):
  digits = ipv4.split(".")
  return ":".join(digits) + "::1"
  

def get_host( hostip, userid, passwd):
  resp = requests.post( get_nxapi_endpoint( hostip), data=json.dumps( get_payload('show hostname')), headers=myheaders,auth=(userid,passwd)).json()
  success = resp['ins_api']['outputs']['output']['msg']
  if success == 'Success' :
    return resp['ins_api']['outputs']['output']['body']['hostname']
  else:
    return 'unknown'  