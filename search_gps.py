#! /usr/bin/env python
############################################################
# Program is part of PySAR v1.2                            #
# Copyright(c) 2017, Yunmeng Cao                           #
# Author:  Yunmeng Cao                                     #
############################################################


import numpy as np
import getopt
import sys
import os
import h5py
import matplotlib.pyplot as plt
from matplotlib.ticker import MultipleLocator, FormatStrFormatter

def float_yyyymmdd(DATESTR):
    year = float(DATESTR.split('-')[0])
    month = float(DATESTR.split('-')[1])
    day = float(DATESTR.split('-')[2])
    
    date = year + month/12 + day/365 
    return date

def rm(FILE):
    call_str = 'rm ' + FILE
    os.system(call_str)
    
def usage():
    print '''
    ***********************************************************************************

    Searching available GPS stations over the research region.
    
    Global GPS stations are referred the GPSNetMap of Nevada Geodetic Laboratory
    Details can be found from http://geodesy.unr.edu/NGLStationPages/gpsnetmap/GPSNetMap.html
 
    Usage:
   
        search_gps.py SLC_par
        search_gps.py timeseries.h5
        search_gps.py velocity.h5
        search_gps.py -f SLC_par -s Date1 -e Date2 

    e.g.:
        
         search_gps.py /Yunmeng/SCRATCH/PichinchaSMT51TsxD/SLC/20100101.slc.par
         search_gps.py /Yunmeng/SCRATCH/PichinchaSMT51TsxD/PROCESS/TSH5/timeseries.h5
         search_gps.py /Yunmeng/SCRATCH/PichinchaSMT51TsxD/PROCESS/TSH5/velocity.h5
         search_gps.py -f 20100101.slc.par -s 2010-01-01 -e 2015-01-10     
    ***********************************************************************************

    '''
def main(argv):
    
    FILE = ''
    Dbeg = ''
    Dend = ''
      
    if len(sys.argv)>2:
        try:   opts, args = getopt.getopt(argv,"h:f:s:e:")
        except getopt.GetoptError:
            usage() ; sys.exit(1)
  
        for opt,arg in opts:
            if opt in ("-h","--help"):  usage();   sys.exit()
            elif opt == '-f':           FILE  = arg
            elif opt == '-s':           Dbeg  = arg
            elif opt == '-e':           Dend  = arg
  
    elif len(sys.argv)==2:
        if os.path.isfile(argv[0]):     FILE = argv[0]
        else:  usage(); sys.exit(1)
    else:  usage(); sys.exit(1)
        
    if not os.path.isfile(FILE):
        usage(); sys.exit(1)
    
    ########################## Get GPS station infomation ##################################
    
    call_str = 'wget -q http://geodesy.unr.edu/NGLStationPages/DataHoldings.txt'
    os.system(call_str)

    call_str = 'tail -n +2 DataHoldings.txt > tt'
    os.system(call_str)
    
    call_str = "awk '{print $1}' tt >t_Name"
    os.system(call_str)
    
    call_str = "awk '{print $2}' tt >t_Lat"
    os.system(call_str)
    
    call_str = "awk '{print $3}' tt >t_Lon"
    os.system(call_str)

    call_str = "awk '{print $8}' tt >t_Dbeg"
    os.system(call_str)
    
    call_str = "awk '{print $9}' tt >t_Dend"
    os.system(call_str)
    
    P_Name = np.loadtxt('t_Name',dtype = np.str)
    
    P_Lat = np.loadtxt('t_Lat')
    P_Lat = np.asarray(P_Lat)
    
    P_Lon = np.loadtxt('t_Lon')
    P_Lon = np.asarray(P_Lon)
    
    P_Dbeg = np.loadtxt('t_Dbeg',dtype = np.str)
    P_Dend = np.loadtxt('t_Dend',dtype = np.str)
    
    rm('t_Lat'),rm('t_Lon'),rm('t_Dbeg'),rm('t_Name'),rm('DataHoldings.txt'),rm('t_Dend'),rm('tt')
    
    ########################### Get SAR coverage information #####################################
    
    BName = os.path.basename(FILE)
    Sufix = BName.split('.')[len(BName.split('.'))-1]
    if Sufix == 'par':
        print ' '
        call_str = "SLC_corners "+ FILE + " > corners.txt"
        os.system(call_str)
        
        File = open("corners.txt","r")
        InfoLine = File.readlines()[8:10]      
        File.close()
           
        MinLat = float(InfoLine[0].split(':')[1].split('  max. ')[0])
        MaxLat = float(InfoLine[0].split(':')[2])
        MinLon = float(InfoLine[1].split(':')[1].split('  max. ')[0])
        MaxLon = float(InfoLine[1].split(':')[2])
        
        if ((MinLon < 0) and (MaxLon < 0 ) ):
            MinLon = MinLon + 360
            MaxLon = MaxLon + 360
        elif ((MinLon < 0) and (MaxLon > 0 )):
            MinLon = MinLon + 360
            MaxLon = MaxLon + 360
            IDX = np.where(P_Lon > 0)
            P_Lon[IDX] = P_Lon[IDX] + 360
            
            
        north = MaxLat
        south = MinLat
        east = MaxLon
        west = MinLon

        print 'The coverage area of SAR image is :   '    
        print '*** maxlat: '+str(north)
        print '*** minlat: '+str(south)
        print '*** maxlon: '+str(east)
        print '*** minlon: '+str(west)
    
    rm('corners.txt')
    ######################## Search GPS stations #########################################
    
    print ''
    print 'Start to search available GPS stations in SAR coverage >>> '
    
    IDX = np.where( (MinLat< P_Lat) & (P_Lat < MaxLat) & ( MinLon< P_Lon) & (P_Lon < MaxLon))
    kk = []
    
    for i in IDX:
        kk.append(i)
        
    kk = np.array(kk)
    kk = kk.flatten()
    print '...'
    
    date1 = 0
    date2 = 99999999
    
    if len(Dbeg) > 0:
        date1 = float_yyyymmdd(Dbeg)
    if len(Dend) > 0:
        date2 = float_yyyymmdd(Dend)
        
    x = len(kk)
    kk_mod = []
    
    for i in range(x):
        dt1 = float_yyyymmdd(P_Dbeg[kk[i]])
        dt2 = float_yyyymmdd(P_Dend[kk[i]])
        if (dt1 > date1 and dt1 < date2) or (dt2 > date1 and dt2 < date2):
            kk_mod.append(kk[i])
    
    kk = kk_mod
    x = len(kk)
    if x ==0:
        print 'No GPS station is found in the SAR coverage!'
    else:
        print 'Number of available GPS station:  %s' % str(x)
        print ''
        print '  Station Name      Lat(deg)      Long(deg)       Date_beg      Date_end  '
    
    for i in range(x):
        Nm = P_Name[kk[i]]
        LAT = P_Lat[kk[i]]
        LON = P_Lon[kk[i]]
        DB = P_Dbeg[kk[i]] 
        DE = P_Dend[kk[i]]
        
        print '     ' + str(Nm) + '           ' + str(LAT) + '       ' + str(LON) + '       ' + str(DB) + '     ' + str(DE) 
        
               

if __name__ == '__main__':
    main(sys.argv[1:])

