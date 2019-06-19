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
   
   Precise ERS orbit data from Delft (http://www.deos.tudelft.nl/).
   Correct the orbit parameters using DELFT_vec2
     
'''

EXAMPLE = '''
    Usage:
            ERS_orb_cor.py projectName Date
 
    Examples:
            ERS_orb_cor.py AqabaERSA 960101

##############################################################################
'''


def cmdLineParse():
    parser = argparse.ArgumentParser(description='Download (and correct) precise ERS orbit data.',\
                                     formatter_class=argparse.RawTextHelpFormatter,\
                                     epilog=INTRODUCTION+'\n'+EXAMPLE)

    parser.add_argument('projectName',help='project name')
    parser.add_argument('date',help='date of the ERS data')
    
    inps = parser.parse_args()
    return inps

################################################################################    


def main(argv):
      
    total = time.time()
    inps = cmdLineParse()
    
    projectName = inps.projectName
    DATE = inps.date
    scratchDir = os.getenv('SCRATCHDIR')
    templateDir = os.getenv('TEMPLATEDIR')
    ASAROrbDir = os.getenv('ASARORBDIR')

    
    slcDir = scratchDir + '/' + projectName + '/SLC'
    projDir = scratchDir + '/' + projectName
    
        
    if len(DATE)==8:
        DATE8 = DATE
        DATE6 = DATE[2:8]
    else:
        DATE8 = '20' + DATE
        DATE6 = DATE
        
    
    slcDir1 = slcDir + '/' + DATE6
    slcpar = slcDir1 + '/' + DATE6 + '.slc.par'

    
    Year = DATE8[0:4]
    Month = DATE8[4:6]
    Day = DATE8[6:8]
    
    DATE1 = (datetime.date(int(Year),int(Month),int(Day)) + datetime.timedelta(days=-1)).strftime("%Y%m%d")
    DATE2 = (datetime.date(int(Year),int(Month),int(Day)) + datetime.timedelta(days=1)).strftime("%Y%m%d")
    
    os.chdir(ASAROrbDir)
    call_str = 'ls > t0'
    os.system(call_str)
    
    call_str="grep " + DATE1 + " t0 | grep " + DATE2 + " >t01"
    os.system(call_str)
    
    AA= np.loadtxt('t01',dtype=np.str)
    AA_file = ASAROrbDir + '/' + str(AA)
    
    call_str = 'DORIS_vec ' + slcpar + ' ' + AA_file
    os.system(call_str)
    
    
    print("Using DORIS orbital data for %s is done." % DATE)
    sys.exit(1)
    
if __name__ == '__main__':
    main(sys.argv[:])
    
    
    
    
    
    
    
    
    
    
    
