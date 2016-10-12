#!/usr/bin/python
import argparse


def optParser():
	parser = argparse.ArgumentParser(description='\tConvert bin file to NVM text')
	parser.add_argument('input_file', help='The bin/dfu file to be converted back to nvm')
	#parser.print_help()
	return parser.parse_args()

def bin2nvm():
	args = optParser()
	print args.input_file

bin2nvm()
