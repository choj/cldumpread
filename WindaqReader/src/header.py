import struct

class header(object):
	# set new Struct objects with format strings. each object reads/writes binary data per format str
	
	# little endian short int, single 16-bit word (up to 2^15, one bit unused)
	header_extent = struct.Struct("<h") 
	value_8001H = struct.Struct("<h")
	
	# little endian unsigned long int
	adc_extent = struct.Struct("<L") 
	
	# element 27 refers to codas doc, where el 27 bit 14 specifies packedness
	# little endian unsigned short int, single value
	element27 = struct.Struct("<H") 
	
	# element 13 is used to calculate sample rate
	element13 = struct.Struct("<d")

	def __init__(self, wholefile):
		# set self.file = object for this instance of header
		self.file = wholefile
		self.get_chan_count()
		self.get_extent()

	# get number of channels
	def get_chan_count(self):
		self.file.seek(1)
		
		#if self.get_extent() == 1156:
		if ord(self.file.read(1)) == 0:
			#read chan count for STANDARD windaq file
			self.file.seek(0)
			
			# return value with 5th bit cleared: https://wiki.python.org/moin/BitManipulation
			# per CODAS doc, 5th bit is set for STANDARD windaq files
			# this works by doing a bitwise AND with the complement of 1 shifted left 5
			# 0001 0000, complement: 1110 1111
			self.chan_count = ord(self.file.read(1)) & ~(1 << 5)
		else:
			#read chan count for MULTIPLEXER windaq file
			self.file.seek(0)
			self.chan_count = ord(self.file.read(1))
	
	def get_sample_rate(self):
		self.file.seek(28)
		self.el13 = header.element13.unpack(self.file.read(8))[0]
		
		# note: codas documentation says sr = number of channels/element 13, which appears incorrect.
		# 1/element 13 seems to produce correct values
		self.sr = 1/self.el13
		return self.sr
	
	def get_extent(self): # get number of bytes in header (element 5)
		self.file.seek(6) # go to byte 6
		self.extent = header.header_extent.unpack(self.file.read(2))[0]
		return self.extent
		
	def get_adc_extent(self): # get number of bytes in adc (excluding header)
		self.file.seek(8) # byte 8
		self.adc_extent = header.adc_extent.unpack(self.file.read(4))[0] # read 4 bytes because a long is 32 bits
		return self.adc_extent

	def get_value_8001H(self):
		self.file.seek(self.extent - 2)
		self.values_8001H = header.value_8001H.unpack(self.file.read(2))[0]
		return self.values_8001H

	# read event markers from trailer
		
	def get_is_packed(self):
		# go to 100th byte
		self.file.seek(100)
		
		# read in 2 bytes (bytes 100, 101) for element 27's entirety
		(whole_27,) = header.element27.unpack(self.file.read(2))
		
		self.is_packed = whole_27 & 0x0002 # & does a bitwise "and", refer to https://wiki.python.org/moin/BitwiseOperators. 
		# 0x0002 is two bytes in hex. binary = 0000 0000  0000 00010 (14th bit is 1, counting starts at 0)
		# this is bitmasking https://en.wikipedia.org/wiki/Bitwise_operation#AND
		
		return self.is_packed
		
	# calc event markers
		# get trailer 1 start and end
		#	 header_extent + adc_extent, header_extent + adc_extent + element 7 (byte 12)
		# seek to trailer start
		# there are four possible sequences of signed longs for each event marker 
		#
		# 1: [event marker 1][event marker 2] ...
		# 2: [event marker 1][time/date stamp][event marker 2] ...
		# 3: [event marker 1][time/date stamp][comment][event marker 2] ...
		# 4: [event marker 1][comment][event marker 2] ...
		#
		# read first long
		# check if second long is time/date stamp
		# if YES, check if third long is a comment
		#	YES comment, skip to fourth long which is an event marker [3]
		#	NO, third long is event marker [2]
		# if NO, check if second long is a comment or event marker
		#	YES comment, skip to third long which is an event marker [4]
		#	NO, second long is event marker [1]
		#
		#
		#read first long
		# check if second long is time/date stamp
		# if YES, check if third long is a comment
		#	YES comment, skip to fourth long which is an event marker [3]
		#	NO, third long is event marker [2]
		# if NO, check if second long is a comment or event marker
		#	YES comment, skip to third long which is an event marker [4]
		#	NO, second long is event marker [1]
		
		
		
