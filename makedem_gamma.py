#! /usr/bin/env python

#'''
######################################################################
###         Author:    Yun-Meng Cao                                ### 
###         Date  :   February, 2017                               ###  
###         Email :   ymcmrs@gmail.com                             ###   
### This script is used to generate GAMMA format dem and dem_par   ###    
######################################################################
#'''

import gdal
import numpy as np
import os
import sys
import getopt
import array

#########################################################################

def usage():
    print 
    '''
******************************************************************************************************
 
   Make DEM in gamma format.    Python's GDAL module is required.
   You have different choices: With or without DEM, Big-endien or little-endien.
   If without available DEM, 1 for 1 arc second dem (30m resolution) can be download automatically.
   Big-endien or little-endien should be corresponding to the GAMMA version.
                         

   usage:
   
            makedem_gamma.py -p SLCpar -N Name -d workdir -b little -D DEM
      e.g.  makedem_gamma.py -p /Users/Yunmeng/Documents/SCRATCH/20100101.slc.par
      e.g.  makedem_gamma.py -D /Users/Yunmeng/Documents/SCRATCH/dem.tif
          
            -p  : gamma-based par file of SLC    e.g: 20100101.slc.par
            -N  : output name of DEM, e.g., PacayaT170F120S1A  [ default: UTM ]
            -d  : work dir used to save the generated dem and dem.par file  [ default: current directory ]
            -b  : "little",little-endien byteorder; "big", big-endien byteorder  [ default: big-endien ]
            -D  : External DEM is available.    e.g.,   /path/dem.tif
            -T  : DEM TYPE of the available DEM     [ default: SRTM1 ]
            -P  : projection type of the available DEM    [ default: EQA ]
            
*******************************************************************************************************
'''   

def main(argv):
    
    Byteorder='big'
    workdir=os.getcwd()
    DEM_TYPE='SRTM1'
    Proj = 'EQA'
    Name = 'UTM'
    Par=''
    DEM=''
    
    if len(sys.argv)> 2:
        try:opts,args=getopt.getopt(argv,'h:p:N:b:d:D:T:P')
        except getopt.GetoptError: print 'Error while getting args'; usage();sys.exit(1)
        
        for opt,arg in opts:
            if   opt in ['h','--help']: usage();sys.exit(1)
            elif opt in '-p': Par       = arg
            elif opt in '-N': Name      = arg
            elif opt in '-b': Byteorder = arg    
            elif opt in '-d': workdir   = arg
            elif opt in '-D': DEM       = arg  
            elif opt in '-T': DEM_TYPE  = arg   # option:  default SRTM1
            elif opt in '-P': Proj      = arg   # option: default EQA
                    
    elif len(sys.argv)==2:
        if argv[0] in ['-h','--help']: usage(); sys.exit(1)
        elif argv[0] in ['-p']: Par=argv[0]
        elif argv[0] in ['-D']: DEM=argv[0]
    
    else:
        usage();sys.exit(1)
    
    
    
    if os.path.isfile(Par):
        print "*** A Gamma-format DEM will be generated based on SLC-Par:  %s" % Par
    
    print "*** DEM name:    %s" % Name        
    print "*** Byteorder of the generated DEM:     %s-endien " % Byteorder      
    print "*** DEM directory:     %s" % workdir  
        
#    print "*** DEM type: %s" % DEM_TYPE
    
#    print "*** Projection of the generated DEM : %s" % Proj
    
    
    DEM_GAMMA=workdir+'/'+Name+'.dem'
    DEM_GAMMA_PAR=workdir+'/'+Name+'.dem.par'
    os.chdir(workdir)
  
    if not ( os.path.isfile(Par) or os.path.isfile(DEM)):
        usage(); sys.exit(1)
        
    if os.path.isfile(Par):
        print "SLC_par file is provided:    %s" % Par
        print "SRTM1 over research region will be downloaded automatically based on %s" % Par
        call_str = "SLC_corners "+ Par + " > corners.txt"
        os.system(call_str)
        
        File = open("corners.txt","r")
        InfoLine = File.readlines()[8:10]      
        File.close()
           
        MinLat = float(InfoLine[0].split(':')[1].split('  max. ')[0])
        MaxLat = float(InfoLine[0].split(':')[2])
        MinLon = float(InfoLine[1].split(':')[1].split('  max. ')[0])
        MaxLon = float(InfoLine[1].split(':')[2])
        
        north = MaxLat + 0.15
        south = MinLat - 0.15
        east = MaxLon + 0.15
        west = MinLon - 0.15

        print 'The coverage area of DEM:   '    
        print '*** maxlat: '+str(north)
        print '*** minlat: '+str(south)
        print '*** maxlon: '+str(east)
        print '*** minlon: '+str(west)
    
        print 'Ready to download dem ......'

        call_str='wget -O dem.tif "http://ot-data1.sdsc.edu:9090/otr/getdem?north=%f&south=%f&east=%f&west=%f&demtype=SRTMGL1"' % (north,south,east,west)
        os.system(call_str)
        DEM_TYPE='SRTM1'
        Proj = 'EQA'
        DEMTIF=gdal.Open('dem.tif')
        
        print "Download job done!"
    
    if os.path.isfile(DEM):
        print "External DEM is provided to generate GAMMA format DEM:  %s" % DEM
        DEMTIF=gdal.Open(DEM)
    
    
    dem=DEMTIF.ReadAsArray()
    if dem.dtype=='float32':
        DATA_FORMAT='REAL*4'
    else: 
        DATA_FORMAT='INTEGER*2'
    
    print "DEM data format:    %s" % DATA_FORMAT
    
    if not sys.byteorder == Byteorder:
        dem.byteswap(True)
        
   
    nWidth  = dem.shape[1]    # longitude
    nLength = dem.shape[0]    # latitude
    
    print "width :  %d     Line :  %d" % ( nWidth, nLength)
    
    
    print "Start to generate %s.dem and %s.dem.par for GAMMA processing! " % ( Name, Name )
    
    dem.tofile(DEM_GAMMA)
    GEOTRANS=DEMTIF.GetGeoTransform()

   
    
    left_corner_lon = GEOTRANS[0]
    post_lat = GEOTRANS[1]
    
    left_corner_lat = GEOTRANS[3]
    post_lon = GEOTRANS[5]
    
    
    f=open(DEM_GAMMA_PAR,'w')
    f.write("Gamma DIFF&GEO DEM/MAP parameter file\n")
    f.write("title:\tIMPORTED DEM FROM %s\n" % DEM_TYPE)  # SRTM1 (30m) or SRTM3 (90m)
    f.write("DEM_projection:     %s\n" % Proj)        # Projection should be checked.
    f.write("data_format:        %s\n" % DATA_FORMAT)  # INTEGER*2 OR REAL*4 should be modified    
    f.write("DEM_hgt_offset:          0.00000\n")
    f.write("DEM_scale:               1.00000\n")
    f.write("width:                %d\n" % nWidth)
    f.write("nlines:               %d\n" % nLength)
    f.write("corner_lat:   %f  decimal degrees\n" % left_corner_lat)
    f.write("corner_lon:   %f  decimal degrees\n" % left_corner_lon)
    f.write("post_lat:   %f  decimal degrees\n" % post_lat)
    f.write("post_lon:   %f  decimal degrees\n" % post_lon)
    f.write("\n")
    f.write("ellipsoid_name: WGS 84\n")
    f.write("ellipsoid_ra:        6378137.000   m\n")
    f.write("ellipsoid_reciprocal_flattening:  298.2572236\n")
    f.write("\n")
    f.write("datum_name: WGS 1984\n")
    f.write("datum_shift_dx:              0.000   m\n")
    f.write("datum_shift_dy:              0.000   m\n")
    f.write("datum_shift_dz:              0.000   m\n")
    f.write("datum_scale_m:         0.00000e+00\n")
    f.write("datum_rotation_alpha:  0.00000e+00   arc-sec\n")
    f.write("datum_rotation_beta:   0.00000e+00   arc-sec\n")
    f.write("datum_rotation_gamma:  0.00000e+00   arc-sec\n")
    f.write("datum_country_list Global Definition, WGS84, World\n")
    f.write("\n")
    
    f.close()

                        
    print "GAMMA format DEM and DEM_par are generated! Done!"

    sys.exit(1)

if __name__ == '__main__':
    main(sys.argv[1:])
