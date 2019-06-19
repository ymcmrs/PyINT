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
import linecache

def StrNum(S):
    S = str(S)
    if len(S)==1:
        S='0' +S
    return S

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

#########################################################################

INTRODUCTION = '''
#############################################################################
   Copy Right(c): 2017-2019, Yunmeng Cao   @PyINT v1.0   
   
   Precise ERS orbit data from Delft (http://www.deos.tudelft.nl/).
   Correct the orbit parameters using DELFT_vec2
     
'''

EXAMPLE = '''
    Usage:
            ERS_orb_cor_par.py SLC_par
 
    Examples:
            ERS_orb_cor_par.py 960101.slc.par
            
##############################################################################
'''


def cmdLineParse():
    parser = argparse.ArgumentParser(description='Download (and correct) precise ERS orbit data.',\
                                     formatter_class=argparse.RawTextHelpFormatter,\
                                     epilog=INTRODUCTION+'\n'+EXAMPLE)

    parser.add_argument('slc_par',help='slc par file')
   
    inps = parser.parse_args()
    return inps

################################################################################    


def main(argv):
      
    total = time.time()
    inps = cmdLineParse()
    
    slcpar = inps.slc_par

    Ers1OrbDir = os.getenv('ERS1ORBDIR')
    Ers2OrbDir = os.getenv('ERS2ORBDIR')
    
    Title = UseGamma(slcpar, 'read', 'title:')
    if 'E1' in Title:
        Flag = 'ERS1'
        #Url = 'ftp://dutlru2.lr.tudelft.nl/pub/orbits/ODR.ERS-1/dgm-e04/'
        #List = ERS1_Orb_list 
        Dir = Ers1OrbDir
    elif 'E2' in Title:
        Flag = 'ERS2'
        #Url = 'ftp://dutlru2.lr.tudelft.nl/pub/orbits/ODR.ERS-2/dgm-e04/'
        #List = ERS2_Orb_list
        Dir = Ers2OrbDir
    else:
        print('The SAR data is invalid.')
        sys.exit(1) 
    
    call_str = 'DELFT_vec2 ' + slcpar + ' ' + Dir
    os.system(call_str)
    
    
    print("Using DEFT orbital data for %s is done." % slcpar)
    sys.exit(1)
    
if __name__ == '__main__':
    main(sys.argv[:])
    
    
    
    
    
    
    
    
    
    
    
