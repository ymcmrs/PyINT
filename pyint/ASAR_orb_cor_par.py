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
import datetime

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
   
   Precise ENVISAT orbit data from Delft (http://www.deos.tudelft.nl/).
   Correct the orbit parameters using DORIS_vec
     
'''

EXAMPLE = '''
    Usage:
            ASAR_orb_cor_par.py slc_par
 
    Examples:
            ASAR_orb_cor_par.py 960101.slc.par

##############################################################################
'''


def cmdLineParse():
    parser = argparse.ArgumentParser(description='Download (and correct) precise ERS orbit data.',\
                                     formatter_class=argparse.RawTextHelpFormatter,\
                                     epilog=INTRODUCTION+'\n'+EXAMPLE)

    parser.add_argument('slc_par',help='slc_par file.')
    
    inps = parser.parse_args()
    return inps

################################################################################    


def main(argv):
      
    total = time.time()
    inps = cmdLineParse()
    
    slcpar = inps.slc_par
    ASAROrbDir = os.getenv('ASARORBDIR')
    PATH =os.getcwd()
    
    DATE = UseGamma(slcpar,'read','date:')
    Year = str(int(DATE[0:4]))
    Month = str(int(DATE[4:8]))
    Day = str(int(DATE[8:12]))
    
    DATE1 = (datetime.date(int(Year),int(Month),int(Day)) + datetime.timedelta(days=-1)).strftime("%Y%m%d")
    DATE2 = (datetime.date(int(Year),int(Month),int(Day)) + datetime.timedelta(days=1)).strftime("%Y%m%d")
    
    os.chdir(ASAROrbDir)
    call_str = 'ls > t0'
    os.system(call_str)
    
    call_str="grep " + DATE1 + " t0 | grep " + DATE2 + " > t01"
    os.system(call_str)
    
    AA= np.loadtxt('t01',dtype=np.str)
    AA_file = ASAROrbDir + '/' + str(AA)
    
    os.chdir(PATH)
    call_str = 'DORIS_vec ' + slcpar + ' ' + AA_file + ' 20'
    os.system(call_str)
    
    
    print("Using DORIS orbital data for %s is done." % slcpar)
    sys.exit(1)
    
if __name__ == '__main__':
    main(sys.argv[:])
    
    
    
    
    
    
    
    
    
    
    
