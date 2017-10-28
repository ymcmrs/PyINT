#! /usr/bin/env python
#'''
###################################################################################
#                                                                                 #
#            Author:   Yun-Meng Cao                                               #
#            Email :   ymcmrs@gmail.com                                           #
#            Date  :   March, 2017                                                #
#                                                                                 #
#         Transform lat and lon to SAR coordinates based on SLCPar and DEM        #
#                                                                                 #
###################################################################################
#'''

import numpy as np
import os
import sys  
import subprocess
import getopt
import time
import glob

def UseGamma(inFile, task, keyword):
    if task == "read":
        f = open(inFile, "r")
        while 1:
            line = f.readline()
            if not line: break
            if line.count(keyword) == 1:
                strtemp = line.split(":")
                value = strtemp[1].strip()
                return value
        print "Keyword " + keyword + " doesn't exist in " + inFile
        f.close()
        

def usage():
    print '''
******************************************************************************************************
 
              Transform lat and lon to SAR coordinates based on SLCPar and DEM

   usage:
   
            UTM2SARPIX.py latitude longitude SLCPar DEM 
      
      e.g.  UTM2SARPIX.py 31.1 -108.2 /Yunmeng/2010.slc.par /Yunmeng/2010.dem

*******************************************************************************************************
    '''   
    
    
def main(argv):
    
    if len(sys.argv)==5:
        LAT = sys.argv[1]
        LON = sys.argv[2]
        PAR = sys.argv[3]
        DEM = sys.argv[4]
    else:
        usage();sys.exit(1)
         
    DEMpar = DEM + '.par'  
    
    DateFormat = UseGamma(DEMpar, 'read', 'data_format:')

    nWidth = UseGamma(DEMpar, 'read', 'width:')
    nLength = UseGamma(DEMpar, 'read', 'nlines:')

    Corner_LAT = UseGamma(DEMpar, 'read', 'corner_lat:') 
    Corner_LON = UseGamma(DEMpar, 'read', 'corner_lon:')

    Corner_LAT =Corner_LAT.split(' ')[0]
    Corner_LON =Corner_LON.split(' ')[0]

    post_Lat = UseGamma(DEMpar, 'read', 'post_lat:')
    post_Lon = UseGamma(DEMpar, 'read', 'post_lon:')

    post_Lat =post_Lat.split(' ')[0]
    post_Lon =post_Lon.split(' ')[0]

    if DateFormat =='INTEGER*2':
        STR = '>i2'
    else:
        STR = '>f4'

    TXT = 'SARCOORD'
    
    DEMdate = np.fromfile(DEM,STR,int(nLength)*int(nWidth)).reshape(int(nLength),int(nWidth))  

    LAT = float(LAT); LON =float(LON)
    nWidth=int(nWidth);nLength=int(nLength)
    Corner_LAT = float(Corner_LAT); Corner_LON=float(Corner_LON)
    post_Lat = float(post_Lat); post_Lon=float(post_Lon)

    XX = int (( LAT - Corner_LAT ) / post_Lat)  # latitude   width   range
    YY = int (( LON - Corner_LON ) / post_Lon)  # longitude   nline  azimuth


    ELEV = DEMdate[XX][YY]

    call_str = 'coord_to_sarpix ' + PAR + ' - - ' + str(LAT) + ' ' + str(LON) + ' ' + str(ELEV) + ' >' +TXT
    os.system(call_str)

    call_str = 'cat ' + TXT
    os.system(call_str)
    
    
if __name__ == '__main__':
    main(sys.argv[:])

    
    
    
    
    
    
    
    
    
    
    
    
    
  
    
    
    
    
