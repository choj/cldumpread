import struct

class header(object):
	# set new Struct objects with format strings. each object reads/writes binary data per format str
    header_extent = struct.Struct("<h") # little endian short int, single 16-bit word (up to 2^15, one bit unused)
    adc_extent = struct.Struct("<L") # little endian unsigned long int
    value_8001H = struct.Struct("<h") # "
	
	# element 27 refers to codas doc, where el 27 bit 14 specifies packedness
    element27 = struct.Struct("<H") # little endian unsigned short int, single value

    def __init__(self,wholefile):
		# set self.file = object for this instance of header
        self.file = wholefile
        self.get_extent()

		
    def get_extent(self): # get number of bytes in header
        self.file.seek(6) # go to 7th byte in file (first byte = 0)
        self.extent = header.header_extent.unpack(self.file.read(2))[0]
        return self.extent
		
    def get_adc_extent(self): # get number of bytes in header
        self.file.seek(8) # go to 9th byte in file (first byte = 0)
        self.adc_extent = header.adc_extent.unpack(self.file.read(4))[0] # read 4 bytes because a long is 32 bits
        return self.adc_extent

		#element 6, byte 8-11, type UL, Unpacked Files: Number of ADC data bytes in file excluding header. Can be used to determine trailer start

    def get_value_8001H(self):
        self.file.seek(self.extent-2)
        self.values_8001H = header.value_8001H.unpack(self.file.read(2))
        return self.values_8001H[0]

    def get_is_packed(self):
		# go to 100th byte
        self.file.seek(100)
		
		# read in 2 bytes (bytes 100, 101) for element 27's entirety
        (whole_27,) = header.element27.unpack(self.file.read(2))
		
        self.is_packed = whole_27 & 0x0002 # & does a bitwise "and", refer to https://wiki.python.org/moin/BitwiseOperators. 
		# 0x0002 is two bytes in hex. binary = 0000 0000  0000 00010 (14th bit is 1, counting starts at 0)
		# this is bitmasking https://en.wikipedia.org/wiki/Bitwise_operation#AND
		
        return self.is_packed
