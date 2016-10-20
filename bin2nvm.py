#!/usr/bin/python
import argparse
import binascii
from datetime import datetime

NVM_TLV_DATA_START = 4
NVM_TLV_TAG = 2
NVM_TLV_LEN = 2
NVM_TLV_ZERO_PADDING = 8
NVM_BODY_LEN = 0
TAG_NUM = 0

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
	fobj.write('#\n#\n')
	fobj.write('#	Tag Listfile\n')
	fobj.write('#\n#\n')
	fobj.write('\n')
	fobj.write('[General]\n')
	fobj.write('Signature = windows\n')
	fobj.write('FormatVersion = 1.0\n')

	s = ' '
	dt = datetime.now()
	s += dt.strftime('%A %B %d, %Y   %I:%M:%S %p')	
	
	fobj.write('TimeStamp =' + s)
	fobj.write('\n\n')
	fobj.write('[Tag]\n')
	s = 'Num = ' + str(TAG_NUM) + '\n\n'
	fobj.write(s)
	

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

	def inputval(self, fobj = None, b_data = None, b_index = None):
		iLSB = int(binascii.b2a_hex(self.TagLengthLSB), 16)
		iMSB = int(binascii.b2a_hex(self.TagLengthMSB), 16)
		self.length = iLSB + iMSB*16
		nLSB = int(binascii.b2a_hex(self.TagNumLSB), 16)
		nMSB = int(binascii.b2a_hex(self.TagNumMSB), 16)
		self.num = nLSB + nMSB*16
		#print self.num
		if b_data is None:
			#print 'fobj'
			for i in range(self.length):
				x = fobj.read(1)
				self.TagValue.append(x)
				i += 1
		elif fobj is None and type(b_index) is int:
			#print 'b_data'
			print '\t...'
			#print binascii.b2a_hex(b_data[b_index])
			b_index += NVM_TLV_TAG + NVM_TLV_LEN + NVM_TLV_ZERO_PADDING
			for i in range(b_index, b_index + self.length):
				self.TagValue.append(b_data[i])
		else:
			print 'inputval error'
	
	def writeToFile(self, fobj):
		sTagHeader = '[Tag' + str(self.TagIndex) + ']\n'
		sTagNum = 'TagNum = ' + str(self.num) + '\n'
		sTagLength = 'TagLength = ' + str(self.length) + '\n'
		sTagValue = 'TagValue =' 
		for b in self.TagValue:
			s = binascii.b2a_hex(b)
			sTagValue += ' ' + s
		sTagValue += '\n\n'
		fobj.write(sTagHeader + sTagNum + sTagLength + sTagValue)
	
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
	#print binascii.b2a_hex(NVM_BODY_LEN)
	#print getDataLength(NVM_BODY_LEN)

	total_length = getDataLength(NVM_BODY_LEN)
	index = NVM_TLV_DATA_START
	global TAG_NUM
	while index < total_length:
		nvm_list.append(
			NVMTag(TAG_NUM, bin_data[index], bin_data[index+1], 
				bin_data[index+2], bin_data[index+3])
		)
		nvm_list[TAG_NUM].inputval(None, bin_data, index)
		#nvm_list[TAG_NUM].printall()
		index += nvm_list[TAG_NUM].length + NVM_TLV_TAG + NVM_TLV_LEN + NVM_TLV_ZERO_PADDING
		TAG_NUM += 1
		

	with open(OUTPUT_FILENAME, 'w+') as fobj:
		writeHeaderToFile(fobj)
		for nvm in nvm_list:
			nvm.writeToFile(fobj)
		fobj.close()
	print '\tConversion done.'

bin2nvm()
