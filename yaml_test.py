#!/usr/bin/env python
# -*- coding: utf-8 -*-


import yaml
import sys
import json

def convert_to_json( yaml_file):
	with open( yaml_file, 'r') as file:
		model = yaml.load( file.read())
		print json.dumps( model)


if __name__ == "__main__":
	convert_to_json( sys.argv[1])
