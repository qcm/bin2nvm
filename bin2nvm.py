#!/usr/bin/python
import argparse
import binascii

NVM_TLV_DATA_START = 4
NVM_TLV_TAG = 2
NVM_TLV_LEN = 2
NVM_TLV_ZERO_PADDING = 8
NVM_BODY_LEN = 0

bin_data = []

def optParser():
	parser = argparse.ArgumentParser(description='\tConvert bin file to NVM text')
	parser.add_argument('input_file', help='The bin/dfu file to be converted back to nvm')
	#parser.print_help()
	return parser.parse_args()

def fileChecker(inputf, data):
	if data[0] != b'\x02':
		print '* ' + inputf + ' is not a valid NVM bin source'
	else:
		print '\tStart to converting ' + inputf

def getDataLength(m):
	print binascii.b2a_hex(m)

# main function
def bin2nvm():
	args = optParser()
	#print args.input_file
	try:
		with open(args.input_file, 'rb+') as fobj:
			bin_data = fobj.read()
			fileChecker(args.input_file, bin_data)
			fobj.close()
	except IOError:
		print args.input_file + ' is not a valid file name'
	
	NVM_BODY_LEN = bin_data[1:NVM_TLV_DATA_START]
	print NVM_BODY_LEN
	print binascii.b2a_hex(NVM_BODY_LEN)
	getDataLength(NVM_BODY_LEN)

bin2nvm()
