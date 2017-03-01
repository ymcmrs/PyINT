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

def main(argv):
    try:
        SLCpar = argv[1]
    except:
        
        print "  ******************************************************************************************************"
        print "  ******************************************************************************************************"
        print "  ******************************************************************************************************"
        print " "
        print "  Make DEM in gamma format                           "
        print "  Do not need SRMDDIR anymore, 1 for 1 arc second dem (30m resolution) can be download automatically  
        print "  wget will be called in this script, so your CP should have access to internet     
        print "  "
        print " "
        print "  Usage:"
        print "           makedem_gamma.py SLCpar       
        print "       or        
        print "           makedem_gamma.py SLCpar workdir  
        print "        
        print "  Example: "
        print "          makedem_gamma.py $SCRATCH/LosAngelesT64F109S1A/SLC/170101.slc.par
        print "          makedem_gamma.py $SCRATCH/LosAngelesT64F109S1A/SLC/170101.slc.par workdir
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
        LatLine = File.readlines(9)
        LonLine = File.readlines(10)
        
        print LatLine
        print Lonline
        
        
        
        
        
        
