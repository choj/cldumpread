import os.path
import decimal


from optparse import OptionParser
from header import header
import struct
import csv

class Windaqreader(object):

	winvalue_struct = struct.Struct("<h") # little endian short int, single 16-bit word (up to 2^15, one bit unused)
	slope_struct = struct.Struct("<d") # little endian double float, 32-bit
	
	def __init__(self,file):
		self.file = open(file, "rb")
		self.chan_count = header(self.file).get_chan_count()

	def print_header(self):
		h = header(self.file)
		self.header_extent = h.get_extent()
		self.adc_extent = h.get_adc_extent()
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
		self.tag = self.file.read(4).decode('ascii')
		
		print(self.slope, self.intercept, self.tag)
		
	def get_slopes(self):
		# get all slopes per channel count
		self.slopes = []
		self.intercepts = []
		self.tags = []
		for i in range(self.chan_count):
			self.file.seek(118 + i*36)
			self.slopes.append(Windaqreader.slope_struct.unpack(self.file.read(8))[0])
			self.intercepts.append(Windaqreader.slope_struct.unpack(self.file.read(8))[0])
			self.tags.append(self.file.read(4).decode('ascii'))
			
		print("\nch\tslope\t\tintercept\tunit")
		for i in range(self.chan_count):
			print('{}\t{:.6f}\t{:12.4f}\t{}'.format(i+1, self.slopes[i], self.intercepts[i], self.tags[i]))
		print("\n")
		
	def print_data_file(self):
	
		# seek to end of header
		self.file.seek(self.header_extent)
		self.values = []
		
		# step thru data section, 2 bytes at a time
		try:
			while self.file.tell() < self.header_extent + self.adc_extent:
				for i in range(len(self.slopes)):
					data = self.file.read(2)
					if(data == "" ):
						break
					# shift bits right 2 places per doc. i believe this knocks out the first two bits, which are state vars
					val1 = Windaqreader.winvalue_struct.unpack(data)[0] >> 2
					self.values.append(round(val1*self.slopes[i] + self.intercepts[i], 6))
               
		except Exception as e:
			#print "Caught Exception while printing list:%d values read : Error %s" % (i,e.message)
			pass
			
		# write tab separated values
		self.outfile = open(os.path.splitext(self.file.name)[0] + "_outfile.csv" , "w")
		csvwriter = csv.writer(self.outfile, dialect='excel', lineterminator='\n', delimiter = '\t')
		val_list = self.chan_count * ['']
		i = 0
		
		for val in self.values:
			val_list[i] = '{:.6f}'.format(val)
			i += 1
			if i == self.chan_count:
				i = 0
				csvwriter.writerow(val_list)
		 
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
	wq.get_slopes()
	wq.print_data_file()


if __name__ == "__main__":
	main()
