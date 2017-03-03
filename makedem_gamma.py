#! /usr/bin/env python

#'''
###########################################################
# Author:   Yun-Meng Cao                                  #
# Date  :   Feb., 2017                                    #
# Email :   ymcmrs@gmail.com                              #  
# This script is used to generate GAMMA format dem        # 
# #########################################################
#'''

import numpy as np
import os
import sys

def main(argv):
    try:
        SLCpar = argv[1]
    except:
        
        print "  ******************************************************************************************************"
        print "  ******************************************************************************************************"
        print "  ******************************************************************************************************"
        print " "
        print "  Make DEM in gamma format                           "
        print "  Do not need SRMDDIR anymore, 1 for 1 arc second dem (30m resolution) can be download automatically    "
        print "  wget will be called in this script, so your CP should have access to internet                         "
        print "  "
        print " "
        print "  Usage:"
        print "           makedem_gamma.py SLCpar                   "         
        print "       or                                            "
        print "           makedem_gamma.py SLCpar workdir            "
        print "  "      
        print "  Example: "
        print "          makedem_gamma.py $SCRATCH/LosAngelesT64F109S1A/SLC/170101.slc.par   "
        print "          makedem_gamma.py $SCRATCH/LosAngelesT64F109S1A/SLC/170101.slc.par workdir "
        print "  ******************************************************************************************************"
        print "  ******************************************************************************************************"
        print "  ******************************************************************************************************"
        sys.exit(1)
        
    SLCpar=sys.argv[1]
        
    if len(sys.argv)==3:
        workdir=sys.argv[2]
        os.chdir(workdir)
        
    call_str = "SLC_corners "+ SLCpar + " > corners.txt"
    os.system(call_str)
        
    File = open("corners.txt","r")
    InfoLine = File.readlines()[8:10]      
    File.close()
        
    print InfoLine[0]
    print InfoLine[1]
    
    MinLat = float(InfoLine[0].split(':')[1].split('  max. ')[0])
    MaxLat = float(InfoLine[0].split(':')[2])
    MinLon = float(InfoLine[1].split(':')[1].split('  max. ')[0])
    MaxLon = float(InfoLine[1].split(':')[2])


  
    print 'minlat: '+str(MinLat)
    print 'maxlat: '+str(MaxLat)
    print 'minlon: '+str(MinLon)
    print 'maxlon: '+str(MaxLon)

    north = MaxLat + 0.15
    south = MinLat - 0.15
    east = MaxLon + 0.15
    west = MinLon - 0.15
    call_str='wget -O dem.tif "http://ot-data1.sdsc.edu:9090/otr/getdem?north=%f&south=%f&east=%f&west=%f&demtype=SRTMGL1"' % (north,south,east,west)
    os.system(call_str)
                        


    sys.exit(1)

if __name__ == '__main__':
    main(sys.argv[:])
