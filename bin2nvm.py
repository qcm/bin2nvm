#!/usr/bin/python
import argparse
import binascii

NVM_TLV_DATA_START = 4
NVM_TLV_TAG = 2
NVM_TLV_LEN = 2
NVM_TLV_ZERO_PADDING = 8
NVM_BODY_LEN = 0

bin_data = []
nvm_list = []
OUTPUT_FILENAME = 'reverted_tlv.nvm'

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

def getDataLength(l):
	# get LSB
	l1 = int(binascii.b2a_hex(l[0]), 16)
	# get 2nd byte
	l2 = int(binascii.b2a_hex(l[1]), 16)
	# get MSB
	l3 = int(binascii.b2a_hex(l[2]), 16)
	return (l1%16)+(l1/16)*16 + ((l2%16)+(l2/16)*16)*256 + ((l3%16)+(l3/16))*65536

def writeHeaderToFile(fobj):
	fobj.write('#\n')
	fobj.write('#\n')
	fobj.write('#	Tag Listfile\n')
	fobj.write('#\n')
	fobj.write('#\n')
	fobj.write('\n')

class NVMTag:
	def __init__(self, TIDX, TNL, TNB, TLL, TLM):
		self.TagIndex = TIDX
		self.TagNumLSB = TNL  
		self.TagNumMSB = TNB
		self.TagLengthLSB = TLL
		self.TagLengthMSB = TLM
		self.length = 0
		self.TagValue = []
		self.num = 0

	def inputval(self, fobj):
		iLSB = int(binascii.b2a_hex(self.TagLengthLSB), 16)
		iMSB = int(binascii.b2a_hex(self.TagLengthMSB), 16)
		self.length = iLSB + iMSB*16
		nLSB = int(binascii.b2a_hex(self.TagNumLSB), 16)
		nMSB = int(binascii.b2a_hex(self.TagNumMSB), 16)
		self.num = nLSB + nMSB*16
		#print self.num
		for i in range(self.length):
			x = fobj.read(1)
			self.TagValue.append(x)
			i += 1
	
	def printall(self):
		print binascii.b2a_hex(self.TagNumLSB)
		print binascii.b2a_hex(self.TagNumMSB)
		print binascii.b2a_hex(self.TagLengthLSB)
		print binascii.b2a_hex(self.TagLengthMSB)
		for i in range(self.length):
			print binascii.b2a_hex(self.TagValue[i])
			i += 1

	
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
		exit()
	
	NVM_BODY_LEN = bin_data[1:NVM_TLV_DATA_START]
	#print NVM_BODY_LEN
	print binascii.b2a_hex(NVM_BODY_LEN)
	print getDataLength(NVM_BODY_LEN)

	length = getDataLength(NVM_BODY_LEN)
	
	for i in range(NVM_TLV_DATA_START, NVM_TLV_DATA_START+3):
		nvm_list.append(
		NVMTag(i-NVM_TLV_DATA_START, bin_data[i], bin_data[i+1], bin_data[i+2], bin_data[i+3])
		)
		nvm_list[i-NVM_TLV_DATA_START].printall()

	with open(OUTPUT_FILENAME, 'w+') as fobj:
		writeHeaderToFile(fobj)
		fobj.close()

bin2nvm()
