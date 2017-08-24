#! /usr/bin/env python
#################################################################
###  This program is part of PyINT  v1.0                      ### 
###  Copy Right (c): 2017, Yunmeng Cao                        ###  
###  Author: Yunmeng Cao                                      ###                                                          
###  Email : ymcmrs@gmail.com                                 ###
###  Univ. : Central South University & University of Miami   ###   
#################################################################


import numpy as np
import os
import sys
import getopt
import array
import argparse
from skimage import io

def get_sufix(STR):
    n = len(STR.split('.'))
    SUFIX = STR.split('.')[n-1]
   
    return SUFIX 

def read_region(STR):
    WEST = STR.split('/')[0]
    EAST = STR.split('/')[1].split('/')[0]
    
    SOUTH = STR.split(EAST+'/')[1].split('/')[0]
    NORTH = STR.split(EAST+'/')[1].split('/')[1]
    
    WEST =float(WEST)
    SOUTH=float(SOUTH)
    EAST=float(EAST)
    NORTH=float(NORTH)
    return WEST,SOUTH,EAST,NORTH


def write_demrsc_file(FILE,Corner_LON,Corner_LAT,X_STEP,Y_STEP,WIDTH,LENGTH):
    f = open(FILE,'w')
    f.write('DATE12         111111-222222\n')
    f.write('FILE_LENGTH    ' + str(int(LENGTH)) + '\n')
    f.write('FILE_TYPE      .dem\n')
    f.write('PROCESSOR      roipac\n') 
    f.write('PROJECTION     LATLON\n') 
    f.write('RLOOKS         1\n') 
    f.write('WIDTH          ' + str(int(WIDTH)) + '\n') 
    f.write('XMAX           ' + str(int(int(WIDTH)-1)) + '\n') 
    f.write('XMIN           0\n')
    f.write('X_FIRST        ' + str(float(Corner_LON)) + '\n')
    f.write('X_STEP         ' + str(float(X_STEP)) + '\n')
    f.write('X_UNIT         degrees\n')
    f.write('YMAX           ' + str(int(int(LENGTH)-1)) + '\n') 
    f.write('YMIN           0\n')
    f.write('Y_FIRST        ' + str(float(Corner_LAT)) + '\n')
    f.write('Y_STEP         ' + str(float(Y_STEP)) + '\n')
    f.write('Y_UNIT         degrees\n')
    f.write('Z_OFFSET       0\n')
    f.write('Z_SCALE        1\n') 
    f.close
    
    
def write_dempar_file(FILE,Corner_LON,Corner_LAT,X_STEP,Y_STEP,WIDTH,LENGTH,DATA_FORMAT):
    DEM_TYPE = 'SRTM1'
    Proj = 'EQA'
    f=open(FILE,'w')
    f.write("Gamma DIFF&GEO DEM/MAP parameter file\n")
    f.write("title:\tIMPORTED DEM FROM %s\n" % DEM_TYPE)  # SRTM1 (30m) or SRTM3 (90m)
    f.write("DEM_projection:     %s\n" % Proj)        # Projection should be checked.
    f.write("data_format:        %s\n" % DATA_FORMAT)  # INTEGER*2 OR REAL*4 should be modified    
    f.write("DEM_hgt_offset:          0.00000\n")
    f.write("DEM_scale:               1.00000\n")
    f.write("width:                %s\n" % WIDTH)
    f.write("nlines:               %s\n" % LENGTH)
    f.write("corner_lat:   %s  decimal degrees\n" % Corner_LAT)
    f.write("corner_lon:   %s  decimal degrees\n" % Corner_LON)
    f.write("post_lat:   %s  decimal degrees\n" % Y_STEP)
    f.write("post_lon:   %s  decimal degrees\n" % X_STEP)
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

#########################################################################

INTRODUCTION = '''
#############################################################################
   Copy Right(c): 2017, Yunmeng Cao   [ymcmrs@gmail.com]
   
   Generating DEM used in interferometry both for GAMMA and ROI_PAC processor.  
   
   1) Available raw DEM files can be used, e.g., dem.tif, dem.grd;
   2) If no raw DEM is provided, SRTM-1 (30m) can be downloaded automatically.
   
   Requirement:      
       Python 2.7 or higher version. GDAL should be installed in your PC. 
'''

EXAMPLE = '''
    Usage:
            makedem.py -r west/east/south/north -d raw_demfile -p processor -o output
            makedem.py -r west/east/south/north -p processor <gamma or roi_pac> 
            makedem.py -d raw_demfile --byteorder <little or big>
            
    Examples:
            makedem.py -r " -118/-116/33/34 " -p gamma -o SouthCalifornia 
            makedem.py -r " -118/-116/33/34 " --byteorder little
            makedem.py -d dem.tif -p roi_pac --byteorder big
            makedem.py -s 20101108.slc.par -p roi_pac 
##############################################################################
'''


def cmdLineParse():
    parser = argparse.ArgumentParser(description='Generate DEM for interferometry processing.',\
                                     formatter_class=argparse.RawTextHelpFormatter,\
                                     epilog=INTRODUCTION+'\n'+EXAMPLE)

    parser.add_argument('-r',dest = 'region',help='Research region, west/east/south/north.')
    parser.add_argument('-d', dest='dem', help='Raw dem file that used for further processing.')
    parser.add_argument('-s', dest='par', help='SLC parameter file of SAR image used for determining research region.')
    parser.add_argument('-p', dest='processor', help='Interferometry processor. [ gamma or roi_pac ] [default: gamma]')
    parser.add_argument('-o', dest='out', help='Output name of the generated DEM.')
    parser.add_argument('--byteorder', dest='byteorder', help='Byteorder of the generated DEM: big or little. [default: big for gamma and little for roi_pac]')
    parser.add_argument('--dir', dest='PATH', help='Processing directory for generating DEM. [default: Current directory]')
    
    inps = parser.parse_args()
    
    if not inps.region and not inps.dem and not inps.par:
        parser.print_usage()
        sys.exit(os.path.basename(sys.argv[0])+': error: research region, raw_demfile and SLC parameter file, at least one is needed.')

    return inps

################################################################################

def main(argv):
    
    inps = cmdLineParse() 
    
    if inps.par: 
        PAR = inps.par
        CentLat = UseGamma(PAR,'read','center_latitude')
        CentLat = float(CentLat.split('degrees')[0])
        
        CentLon = UseGamma(PAR,'read','center_longitude')
        CentLon = float(CentLon.split('degrees')[0])
        
        west = CentLon - 2    #   dem with radius of 2 degrees according to center coordinates will be generated.  
        east = CentLon + 2
        
        south = CentLat - 2
        north = CentLat + 2
        
    
    if inps.region: 
        region = inps.region
        west,south,east,north = read_region(region)
        
        #print 'Research region: %s/%s/%s/%s' % west,south,east,north
    
    if inps.dem:
        dem = inps.dem
        print 'Raw dem file is provided: %s .' % dem
        
    if inps.out: Name = inps.out
    else: Name = "out"
        
    if inps.processor: processor = inps.processor
    else: processor ='gamma'
    
    if inps.byteorder: Byteorder = inps.byteorder
    else: 
        if processor == 'gamma': Byteorder = 'big'
        else: Byteorder ='little'
       
    if inps.PATH: workdir = inps.PATH
    else: workdir = os.getcwd()        
    os.chdir(workdir)
    
    if not inps.dem:
        print 'Research region: %s(west)  %s(south)  %s(east)  %s(north)' % (west,south,east,north)
        print '>>> Ready to download SRTM1 dem over research region.'
        call_str='wget -q -O dem.tif "http://ot-data1.sdsc.edu:9090/otr/getdem?north=%f&south=%f&east=%f&west=%f&demtype=SRTMGL1"' % (north,south,east,west)
        os.system(call_str)
        print '>>> DEM download finished.'
        
        DEM_TYPE='SRTM1'
        Proj = 'EQA'
        
        DEM = 'dem.tif'
    else:
        DEM = inps.dem
        
    SUFIX = get_sufix(DEM)
    SS ='.' + SUFIX
    DTIF = DEM.replace(SS,'.tif')

    if not SUFIX == 'tif':
        call_str = 'gdal_translate ' + DEM + ' -of GTiff ' + DTIF
        os.system(call_str)


    DEM = DTIF
    call_str = 'gdalinfo ' + DEM + ' >ttt'     
    os.system(call_str)
    
    f = open('ttt')    
    for line in f:
        if 'Origin =' in line:
            STR1 = line
            AA = STR1.split('Origin =')[1]
            Corner_LON = AA.split('(')[1].split(',')[0]
            Corner_LAT = AA.split('(')[1].split(',')[1].split(')')[0]
        elif 'Pixel Size ' in line:
            STR2 = line
            AA = STR2.split('Pixel Size =')[1]
            Post_LON = AA.split('(')[1].split(',')[0]
            Post_LAT = AA.split('(')[1].split(',')[1].split(')')[0]
        
        elif 'Size is' in line:
            STR3 = line
            AA =STR3.split('Size is')[1]
            WIDTH = AA.split(',')[0]
            FILE_LENGTH = AA.split(',')[1]
    f.close()
    
    dem_data = io.imread(DEM)
    if dem_data.dtype=='float32':
        DATA_FORMAT='REAL*4'
    else: 
        DATA_FORMAT='INTEGER*2'
        
        
    if not sys.byteorder == Byteorder:
        dem_data.byteswap(True)
    
    if processor =='gamma':
        DEMDATA = Name + '.dem'
        DEMPAR = Name + '.dem.par'
    elif processor =='roi_pac':
        DEMDATA = Name + '.dem'
        DEMPAR = Name + '.dem.rsc'
        
    dem_data.tofile(DEMDATA)    
    
    if processor =='gamma':
        write_dempar_file(DEMPAR,Corner_LON,Corner_LAT,Post_LON,Post_LAT,WIDTH,FILE_LENGTH,DATA_FORMAT)
    elif processor =='roi_pac':
        write_demrsc_file(DEMPAR,Corner_LON,Corner_LAT,Post_LON,Post_LAT,WIDTH,FILE_LENGTH)
    
    BB =Byteorder + ' endian'
    print ''
    print '%s %s and %s are generated.' % (BB,DEMDATA,DEMPAR)
    print 'Congratulations! Done!'
    #print "Generating %s processor %s and %s is done!" % (processor,DEMDATA,DEMPAR)
    sys.exit(1)
       

if __name__ == '__main__':
    main(sys.argv[1:])
