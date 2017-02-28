#! /usr/bin/env python

#'''
########################################################
# Author:  Yun-Meng Cao                                #
# Feb., 2017                                           #
# gamma based coregistration script                    # 
# ######################################################
#'''

import numpy as np
import os
import pysar._readfile as readfile
import sys  
import subprocess
import time
import messageRsmas
import glob
import re

def main(argv):
    try:
        Mslc = argv[1]
        Mslc_par = argv[2]
        Sslc = argv[3]
        Sslc_par=argv[4]
    except:
        print "*******************************"
        print "  not enough input parameters  "
        print "*******************************"
        sys.exit(1)
        
Mdate=os.path.basename(Mslc).split('.')[0]
Sdate=os.path.basename(Sslc).split('.')[0]

Pair=Mdate + "_" + Sdate

call_str="$GAMMA_BIN/create_offset" + Mslc_par + " " + Slc_par + " " + off + " 1 - - 0"
os.system(call_str)

print "Coregistration without DEM is done"

sys.exit(1)

if __name__=='__main__':
    main(sys.argv[:])















