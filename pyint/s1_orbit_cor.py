#! /usr/bin/env python
#################################################################
###  This program is part of PyINT  v2.1                      ### 
###  Copy Right (c): 2017-2019, Yunmeng Cao                   ###  
###  Author: Yunmeng Cao                                      ###                                                          
###  Contact : ymcmrs@gmail.com                               ###  
#################################################################

import numpy as np
import os
import sys  
import subprocess
import getopt
import time
import glob
import argparse

from pyint import _utils at ut
#########################################################################

INTRODUCTION = '''
-------------------------------------------------------------------  
   
       Download and update the orbit data for S1-A/B based on the AUX_POEORB data.
   
'''

EXAMPLE = '''
    Usage:
            s1_orbit_cor.py projectName Date
 
-------------------------------------------------------------------  
'''


def cmdLineParse():
    parser = argparse.ArgumentParser(description='Download and update orbit date for Sentinel-1 data.',\
                                     formatter_class=argparse.RawTextHelpFormatter,\
                                     epilog=INTRODUCTION+'\n'+EXAMPLE)

    parser.add_argument('s1_par',help='SLC par file of Sentinel-1.')

    inps = parser.parse_args()
    return inps

################################################################################    


def main(argv):
    
    inps = cmdLineParse()
    
    
    projectName = inps.projectName
    DATE = inps.date
    scratchDir = os.getenv('SCRATCHDIR')
    slcDir     = scratchDir + '/' + projectName + "/SLC"
    
    if len(DATE)==8:
        DATE = DATE[2:9]
    
    SLCPATH = slcDir + '/' + DATE
    
    KK=os.listdir(SLCPATH)
    SLC_PAR  = []
    for ll in KK:
        if 'slc.par' in ll:
            SLC_PAR.append(ll)
    os.chdir(SLCPATH)
    FF = SLC_PAR[0]
    
    SENSOR = UseGamma(FF, 'read', 'sensor:')
    
    if 'S1A' in SENSOR:
        SAT = 'A'
    else:
        SAT = 'B'
     
    print('SAR image is acquired by Sentinel-1%s.' % SAT)
    
    call_str = 'Sen_PreOrbit.py ' + DATE + ' ' + SAT
    os.system(call_str)
    
    call_str = 'Update_Orbit_Sen.py ' + SLCPATH
    os.system(call_str)
    
    
    print('Download and update the precise orbit date for Sentinel-1%s data %s is finished.' % (SAT,DATE))
    
    sys.exit(1)
    
if __name__ == '__main__':
    main(sys.argv[:])

    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    