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
import subprocess
import getopt
import time
import glob
import argparse

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
        print("Keyword " + keyword + " doesn't exist in " + inFile)
        f.close()

def StrNum(S):
    S = str(S)
    if len(S)==1:
        S='0' +S
    return S


#########################################################################

INTRODUCTION = '''
##############################################################################################
   Copy Right(c): 2017, Yunmeng Cao   @PyINT v1.0   
   
   Download and update the orbit data of Sentinel-1A/B slc par files based on the AUX_POEORB data.
   See also:  Sen_PreOrbit.py, Update_Orbit_Sen.py
   
'''

EXAMPLE = '''
    Usage:
            Sen_Orbit_Cor.py projectName Date
 
    Examples:
            Sen_Orbit_Cor.py projectName Date

###################################################################################################
'''


def cmdLineParse():
    parser = argparse.ArgumentParser(description='Download and update orbit date for Sentinel-1 data.',\
                                     formatter_class=argparse.RawTextHelpFormatter,\
                                     epilog=INTRODUCTION+'\n'+EXAMPLE)

    parser.add_argument('projectName',help='Name of the projection.')
    parser.add_argument('date',help='SAR acquisition date.')
    
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

    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    