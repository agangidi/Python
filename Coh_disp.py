Python
======

Python Code to De-disperse Pulsar Data


 
"""
 Code Function: Observation of Coherent De-dispersion
                on pulsar data acquired from 2-channels
                representing two polarizations.

 Author: Adithya Reddy

@@-----------------------------------------------------------------
    For execution of code and to view one pulsar peak

   1) go to the Directory containing the pulsar raw data
      (after markers are fixed with C code) and Config
      file  "config_Nov_23_2002.das"

   2) NOW IN THE PYTHON INTERPRETER

    >>from coh_dedisp import *
    >>data=read_data(filename, header())

   3) Followed by giving inputs below to the dialogue u can store
      the dedispersed data in a array variable

      # Comments: for ready observation of de-disperse pulsar peak 

     input_a) percent=2  (percent of total datafile you want to de-disperse)
     input_b) chan=1     (channel you wish to analyse details of)
     input_c) prefix_percent=22 (prefix pecent of data where correction needs to be started)
     input_d) factor=16  (factor by which time resolution should be decrease)   

   4) now to plot this data

    >>plot(data)
    >>show()
@@-----------------------------------------------------------------


Created on April 30 th 2009


4th modification: 23-27 May, 2009
Code Ver:1.2

Changes:
       1) Separated 4 functions from read_data apart from header 
           that was separated in 4 th modification

         res_dec()-- Decrease of the exisiting time resolution by a factor
         split_code()-- Creates the split code's as a look up table 
         phase_array()--Creates a phase correction array to correct the phase
         correct_data()--Corrects the data by converting it to frequency spectrum

         read_data()--Some function similar to main function which calls the 
                      above functions and thus completes the process of reading
                      the data and correcting it

         More functions to be split from the read_data and it will be done in 5 th modification

3 rd modification on May 17th
Code Ver: 1.1

Changes:
      1) Separated function for reading header information
          It returns list=[bw,f_0,dm,header_exist]
          bw stands for bandwidth
          f_0 stands for Center frequency at which radiation was obtained  
          dm= Dispersion Measure
          header_exist = Indicative if valid header exists or not 

          The above list is passed as an argument to Function read_data(list)
            which reads the wanted data and corrects it


2nd modification on: May 3rd used 32k FFT
Ver:1.0

1st modification on May 1st 2009
change: Numpy Array's deleted after use;   @ Line 89,175
by: Adithya

"""


import pylab
from pylab import *
from numpy import *
import numpy
import scipy as scipy
import os
from scipy import fft
import math


def header(filename):
	import numpy
	import os	
	
#       filename = '0809_mod_fixed'  #name of file after "REMOVING MARKERS"

	nfft=2084.0*16
	
	if not os.path.exists(filename):
		print 'No data file'
		raw_input('Press enter to exit')
		raise SystemExit
	
	fp=open(filename) #if NULL file does not exist
	
	g=fp.read(2048) # Read 2048 byte long header information
	
	#Unpacking Header
	
	dh0= numpy.frombuffer(g[0:8], dtype=numpy.double) 
                #Reading double value from header  ("dh" double value in header)
	
	fh2=numpy.frombuffer(g[8:12], dtype=numpy.float32) #Reading float values
	fh3=numpy.frombuffer(g[12:16], dtype=numpy.float32) 
	
	ih4=numpy.frombuffer(g[16:20], dtype=numpy.int) 
                # Reading series of integers from header information
	ih5=numpy.frombuffer(g[20:24], dtype=numpy.int)
	ih6=numpy.frombuffer(g[24:28], dtype=numpy.int)
	ih7=numpy.frombuffer(g[28:32], dtype=numpy.int)
	ih8=numpy.frombuffer(g[32:36], dtype=numpy.int)
	ih9=numpy.frombuffer(g[36:40], dtype=numpy.int)
	ih10=numpy.frombuffer(g[40:44], dtype=numpy.int)
	
	mark_gap=ih4 #ih4 corresponds to mark_gap value
	
	header_exist=1
	if mark_gap != 4096:
	    print " The header has wrong entry for marker_interval. May be header is absent\n"
            print " Continuing... IRRELAVENT INFO ABOUT HEADER.. ASSUME HEADER DOESN'T EXIST"
            header_exist=0
	
	bw = dh0
	invert = 1
	if bw < 0.0:
            bw = -bw;
            invert = -1;
	
	f_0 = fh2  
	
	dm = fh3	#Disp measure
	dd = ih5	#Data and time of observation
	mm = ih6
	yy = ih7
	
	hr = ih8
	mt = ih9
	sec = ih10
	
	del ih4,ih5,ih6,ih7,ih8,ih9,ih10,dh0,fh2,fh3
	
	#memcpy(psrname, ph+44, 32);
	psrname=g[44:76]
	print "PSR name: ", psrname
	
	data_file=g[76:108]
	print "Data file: ",data_file
	
	site_name=g[108:140];
	print "Site Name: ",site_name
	
	
	
	print " ===================================\n"
	
	
	#Opening "CONFIG" file for forcing the values which might be wrong in the header
	print "Forcing the suspected and important information with Config file"
	
	hand_cfg = open('config_Nov_23_2002.das',"r")
	
	
	
	f_0=float(hand_cfg.readline())
	invert=int(hand_cfg.readline())
	f_clk=float(hand_cfg.readline())
	div_panel=int(hand_cfg.readline())
	site_name=str(hand_cfg.readline())
	mark_gap=int(hand_cfg.readline())
	dm=float(hand_cfg.readline())
	
	hand_cfg.close()
	
	
	bw = (1000.0*f_clk)/(2*div_panel+2)
	
	
	print "bandwidth of obs.n :",bw," kHz"
	print "Centred at :",f_0," MHz"
	print "header DM :",dm," pc/cc"
	print "marker interval :",mark_gap," words"
	print "date :",dd,mm,yy
	print "Field name :",psrname
	print "Original data file name :",data_file
	print "Telescope site_code :",site_name
	
	print " ===================================\n"
	
	
	print "Reading Header extension"
	
	
	
	ih35=numpy.frombuffer(g[140:144], dtype=numpy.int)
	
	
	n_rfch = ih35;
	
	if (n_rfch > 0) & (n_rfch < 3):
	
		nbits=numpy.frombuffer(g[144:148], dtype=numpy.int)
		f_1 = numpy.frombuffer(g[148:152], dtype=float32)
		bw1 = numpy.frombuffer(g[152:160], dtype=double)
		#memcpy(observer, ph+160, 32);   /* ih[40] */
		observer=g[160:192]
		#printf(" Observer %s \n",observer);
		#printf(" ===================================\n");
		hund_sec =  numpy.frombuffer(g[192:196], dtype=int) # ih48;
		# /* next usable: ih[49] or fh[49] or dh[25-] or ph+196  */
		print "2nd channel details"
		print "no of RF_channels : No of bits : 2nd banddwidth : observer"
		print n_rfch, "  ",nbits," ", bw, " KHz ","  ",observer  
	else:
	  
		nbits = 2
		n_rfch = 1
		bw1 = bw
		f_1 = f_0
		hund_sec = 0
		print "Observer Unknown (due to old header)\n"
	
	 
	
	######################################
	
	del g,ih35
	return [bw,f_0,dm,header_exist]
#--------------------------------------------------- end header()

#time resolution decrease

def res_dec(n,b,rblock,factor):							
		for count in range(0,(int(rblock)*2)/factor):
			b=append(b,(sum(pow(n[count*factor:factor*(count+1)],2))))
		return b


def split_code(nbits):
	byte_split=zeros([256,4])

	offset = 0	
	j=0
	while j < 256:
	
		if nbits > 1:
			n = 1
			o = 0 
			while o <= 3:    #//  deal with only one byte
				
				k = j;
				temp  = ((k/n) & (0x03))
				byte_split[j][o] = (2*temp - 3)
				n = n * 4;
				o=o+1
		j=j+1
	return byte_split	        
		#print byte_split[0:255] #for debugging

def phase_array(rblock,bw,f_0,dm): 
	bw= bw/1000.0   # To write the value in MHz
	nu1= f_0-(bw/2) # Frequency at lower edge of RF band in MHz, -bw/2 for lower edge
	disp_delay=(4150*dm*pow(nu1,-2))  #Dispersion delay at lower edge of RF band nu1 
	
	
	phase=zeros(2*rblock+1)
	base_b=zeros(2*rblock+1)
	complex_phase= append(numpy.zeros((rblock*2,1), dtype=complex),0)
	
	
	channel_n=1
	while channel_n<(2*rblock+1):
		base_b[channel_n]=(((bw/(rblock*2*2))*channel_n)) #BB frequency
		phase[channel_n]=((base_b[channel_n])/(nu1+(base_b[channel_n])))*\
                                 2*pi*disp_delay*base_b[channel_n]*1000000
                              #Creating Phase correction various for channel freq

		#ti=pow((1+pow((vb/(0.47*bw)),80)),-1/2) 
                #Window function for Overlap add used in Reference [1] #not relavent

		complex_phase[channel_n]=complex(cos(phase[channel_n]),sin(phase[channel_n]))
                      # exp(-i*(phi-d)) used for correction of Phase

		channel_n=channel_n+1

        #---- end while channel_n

	return complex_phase
#------------------------------------------------- end phase_array
def correct_data(current_channel_data,complex_phase,rblock):

	outputa= append(numpy.zeros((rblock*4,1), dtype=complex),0)
       	         #contains de-dispersed time output when updated
        modspect=append(numpy.zeros((rblock*4,1), dtype=complex),0)
                 #contains modified spectrum information when updated
	out1=append(numpy.zeros((rblock*4,1), dtype=complex),0)
	f1=append(numpy.zeros((rblock*4,1), dtype=complex),0)
	modspect[0]=complex(0)
	out1[0]=complex(0)

	# Creating FFT plan to use FFTW3 library and call FFT, IFFT functions



#       fft1 = fftw3.Plan(f1,out1, direction='forward', flags=['measure'])
                 # Refer to report for usage of FFTW
#       ifft1 = fftw3.Plan(modspect,outputa,direction='backward', flags=['measure'])
#	fft(f1)  #executing the planned FFT above

	f1=current_channel_data
        out1 = fft(f1)	

	modspect[0]=out1[0]
	
	i=1
	while i<(2*rblock+1):
            modspect[i]= out1[i]*complex_phase[i]
		   #Phase correcting the spectrum for coherent de-dispersion
	    modspect[4*rblock+1-i]=conj(modspect[i])
      	    i=i+1
	
	outputa = ifft1(modspect)
	return outputa		



def read_data(filename, list_parameter):
	bw=list_parameter[0]	
	f_0=list_parameter[1]
	dm=list_parameter[2]
	header_exist=int(list_parameter[3])	

#	filename = '0809_mod_fixed'  #name of file after "REMOVING MARKERS"
	if not os.path.exists(filename):
		print 'No data file'
		raw_input('Press enter to exit')
		raise SystemExit
	
	fp=open(filename)	
	
	nfft=2084.0*16  ##########
	nbits=2		##########
	rblock=int(nfft) #number of bytes read per channel per block 
	#Initialising Variables for carrying out FFT
	
	
	
	current_channel_data = numpy.zeros((rblock*4,1), dtype=complex)
                   #For Odd/even channel information
		
	
	
	#byte_split method borrowed from Asgekar Sir's code 2_compute_spectra.c (das_spectro.c)
	#This is used to create look up table for unpacking Short Int 
        #  values as 8 samples of 2 bits each
	
	
	
	print "Creating split codes \n" 
	
	byte_split=split_code(nbits)
	
	
		
	print "Unpacking data with split codes \n"
	
	
	
	
	
	print "How much % of data do u wish to fold the spectrum for ? \n"
	while True:
		percent=raw_input()
		try:percent = float(percent)
		except ValueError:print 'Improper input';continue
		if not ( 0 <= percent <= 100 ):print 'Improper input';continue
		else:break
	
	print "Press 1 to correct the 1st channel and any other key \
                   for the 2nd chanel correction  \n"
	chan=raw_input()
	
	print "enter prefixed value in % with which pulsar observation starts   \n"
	
	while True:
		percent_prefix=raw_input()
		try:percent_prefix = float(percent_prefix)
		except ValueError:print 'Improper input';continue
		if not ( 0 <= percent_prefix <= 100 ):print 'Improper input';continue
		else:break	
	
	print "enter a factor by which output time resolution should be\
                  decreased [SHOULD be power of 2 : and <= 512]  \n"
	
	while True:
		factor=raw_input()				#inspired from Nishant's code
		if not factor.isdigit():print 'Improper input';continue
		factor = int(factor)
		power = math.log(factor,2)
		if not ( power%1==0 and 0 < power < 10 ) :print 'Improper input';continue
		else:break
	
	nblocks=int(percent*int(os.stat(filename).st_size)/(100*float(rblock)))
	
	prefix=int(percent_prefix*int(os.stat(filename).st_size)/(100*float(rblock)))
		
		    #Number of samples per channel I wish to have when I read a block  of data

	rblock=nfft 
                    #The number of bytes I deal with per channel 
                    #when I read one block -assuming 2 bit quantisation 
		
	
	current_block= numpy.zeros((rblock*8,1), dtype=complex)
	
	complex_phase=phase_array(nfft,bw,f_0,dm)	
	
	
	
	#Function to plot o/p after decreasing resolution by a specified "factor" 
	
	final_dedisp=0
		
	
	
	
	
	limit =int(rblock) # No of short Ints need to be decoded 
			   # For reading two channels of data each 2048 bytes 
                           #    we need 1024*2=rblock short-ints 
	
	
	
	block_count=prefix		
               #prefix is input value which tells you how many blocks of 2048 bytes
               #after which you wish to start reading data and analyze
	
	while block_count<(nblocks+prefix):
	
		
            fp.seek((block_count*int(rblock))+(header_exist*2048))
                #due to the overlap and 2048 is length of header
	    current_data=fp.read(int(rblock)*2)	
                #due to the 50% overlap on either sides 2*rblock bytes are read
	    a=[0,0,0,0]
	    b=[0,0,0,0]
	    d=[]
		
		
	    current_block[:] = numpy.zeros((int(rblock)*2*4,1), dtype=complex)[:] 
                #Values of decoded samples (fixed to 4 samples per byte in this version)
				
	    z=numpy.frombuffer(current_data, dtype=numpy.uint16) 
                #packing currently read data as Short int(2 bytes together) 
		
		
	    offset=0	
	    m = 0   #    // Initialize the Dest. index for d array
	    l = offset
		
	    while  l < limit:  #// assumed 2k words
	 
	        temp = z[l]/256;
		n = z[l] - temp*256;
		#//              n = 0;      // only to test
		current_block[m] = byte_split[n][0]; # // hopefully not reversed 
		m=m+1
		current_block[m] = byte_split[n][1];
		m=m+1
		current_block[m] = byte_split[n][2];
		m=m+1
		current_block[m] = byte_split[n][3];
		m=m+1
				
		n = temp;
		#//              n = 255;   // only to test
		current_block[m] = byte_split[n][0];
		m=m+1
		current_block[m] = byte_split[n][1];
		m=m+1
		current_block[m] = byte_split[n][2];
		m=m+1
		current_block[m] = byte_split[n][3];
		m=m+1
		#print m
		#print limit
		l=l+1
	
		
		#print e[1:100]
		#print d[1:100]
		
		if chan=='1':
		    index=0
		    while index<(rblock*2):
			current_channel_data[index]=current_block[index*2]    
                            #current_block has two channel information:Picking 1st/even channel
			index=index+1
			
		else:
		    index=0
		    while index<(rblock*2):
			current_channel_data[index]=current_block[index*2+1] 
                            #current_block has two channel information:Picking 2nd/odd channel
			index=index+1
		
		
		outputa=correct_data(current_channel_data,complex_phase,rblock)
			
		final_dedisp=res_dec(outputa[int(rblock):(int(rblock)*3)]/\
                                     (rblock*4),final_dedisp,rblock,factor)
                               # rblock*4 is number of points taken for FFT 	

		block_count=block_count+1
                               #resdec function used to decrese the time resolution
	
	
	
	print "Dedispersed data plotted after decreasing time resolution by factor", factor
	
	return final_dedisp


