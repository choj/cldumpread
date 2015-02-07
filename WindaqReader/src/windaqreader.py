import os.path
import decimal
# To change this template, choose Tools | Templates
# and open the template in the editor.

__author__="hari"
__date__ ="$May 20, 2009 11:13:44 AM$"
from optparse import OptionParser
from header import header
import struct
import csv

class Windaqreader(object):

	winvalue_struct = struct.Struct("<h") # little endian short int, single 16-bit word (up to 2^15, one bit unused)
	slope_struct = struct.Struct("<d") # little endian double float, 32-bit
	unit_struct = struct.Struct("<B") # little endian unsigned char
	
	def __init__(self,file):
		self.file = open(file, "rb")

	def print_header(self):
		h = header(self.file)
		self.header_extent = h.get_extent()
		self.adc_extent = h.get_adc_extent()
		self.chan_count = h.get_chan_count()
		my8001h = h.get_value_8001H()
		print("Channel Count: %d" % self.chan_count)
		print("Header Bytes: %d" % self.header_extent)
		print("ADC Data Bytes: %d" % self.adc_extent)
		print("Value  8001H: %d" % my8001h)
		print("Is   Packed: %d" % h.get_is_packed())
		
	def get_slope(self):
	
		# below three values hardcoded for single channel
		self.file.seek(110)
		
		# seek to byte 118, which is item 3 in element 34 per CODAS spec, storing slope (m)
		self.file.seek(118)

		self.slope = Windaqreader.slope_struct.unpack(self.file.read(8))[0]
		self.intercept = Windaqreader.slope_struct.unpack(self.file.read(8))[0]
		self.tag = self.file.read(6)
		print(self.slope, self.intercept, self.tag)
		
	def print_data_file(self):
	
		# seek to end of header
		self.file.seek(self.header_extent)
		self.values = []

		try:
			#while True:
			while self.file.tell() < self.header_extent + self.adc_extent:
				data = self.file.read(2)
				if(data == "" ):
					break
				# shift bits right 2 places per doc. i believe this knocks out the first two bits, which are state vars
				val1 = Windaqreader.winvalue_struct.unpack(data)[0] >> 2
				true = round(val1*self.slope + self.intercept, 6)
				#print(true)
				#print(self.file.tell())
				composite = []
				#composite.append(true * -1)
				composite.append(true)
				self.values.append(composite)
		   
		except Exception as e:
			#print "Caught Exception while printing list:%d values read : Error %s" % (i,e.message)
			pass

		import os
		self.outfile = open(os.path.splitext(self.file.name)[0] + "_outfile.csv" , "w")
		csvwriter = csv.writer(self.outfile, dialect='excel', lineterminator='\n')
		for val in self.values:
			csvwriter.writerow(val)
		 
		self.outfile.write("\n")
		self.outfile.flush()
		self.outfile.close()


def main():
	parser = OptionParser()
	parser.add_option("-i", dest="file", help="input windaq file", metavar="*.daq")
	(options,spillover) = parser.parse_args()
	wq = Windaqreader(options.file)
	wq.print_header()
	wq.get_slope()
	wq.print_data_file()


if __name__ == "__main__":
	main()
