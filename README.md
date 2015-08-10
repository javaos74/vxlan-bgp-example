# vxlan-bgp-example

#환경 설정 
export NEUXS_USER=xxxx 
export NEXUS_PASSWD=yyyy 

#ip interface 보기 
python list_ip_intf.py hosts.yaml 

#vrf interface 보기 
python list_vrf_intf.py hosts.yaml 

#switch-model.yaml 에 설정된 값으로 leaf/spine 설정하기 
python do_conf.py switch-model.yaml 

#monitoring 
python {nve_peer|nve_vni|mac_all|mac_ip_all} mon_vxlan.py switch-model.yaml 

