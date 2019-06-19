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
   
   Download precise ERS orbit data from Delft (http://www.deos.tudelft.nl/).
   Correct the orbit parameters using DELFT_vec2
   
   ftp://dutlru2.lr.tudelft.nl/pub/orbits/ODR.ERS-2/dgm-e04/arclist
   
   
'''

EXAMPLE = '''
    Usage:
            ERS_DEOS.py projectName Date
 
    Examples:
            ERS_DEOS.py AqabaERSA 960101

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
    slcDir = scratchDir + '/' + projectName + '/SLC'
    projDir = scratchDir + '/' + projectName
    
    ERS1_Orb_Dir = scratchDir + '/' + projectName + '/ERS1_Orb'
    ERS2_Orb_Dir = scratchDir + '/' + projectName + '/ERS2_Orb'
    
    if not os.path.isdir(ERS1_Orb_Dir):
        call_str = 'mkdir ' + ERS1_Orb_Dir
        os.system(call_str)
        
    if not os.path.isdir(ERS2_Orb_Dir):
        call_str = 'mkdir ' + ERS2_Orb_Dir
        os.system(call_str)
    
    ERS1_Orb_list = ERS1_Orb_Dir + '/ERS1_Orb_list'
    ERS2_Orb_list = ERS2_Orb_Dir + '/ERS2_Orb_list'

    os.chdir(ERS1_Orb_Dir)
    if not os.path.isfile(ERS1_Orb_list):
        Url = 'ftp://dutlru2.lr.tudelft.nl/pub/orbits/ODR.ERS-1/dgm-e04/arclist'
        call_str = 'wget ' + Url + ' -O ERS1_Orb_list'
        os.system(call_str)
        
        call_str = 'cp ERS1_Orb_list arclist'
        os.system(call_str)
    
    os.chdir(ERS2_Orb_Dir)
    if not os.path.isfile(ERS2_Orb_list):
        Url = 'ftp://dutlru2.lr.tudelft.nl/pub/orbits/ODR.ERS-2/dgm-e04/arclist'
        call_str = 'wget ' + Url + ' -O ERS2_Orb_list'
        os.system(call_str)
        
        call_str = 'cp ERS2_Orb_list arclist'
        os.system(call_str)
        
    if len(DATE)==8:
        DATE6 = DATE[2:8]
    else:
        DATE6 = DATE
    
    slcDir1 = slcDir + '/' + DATE6
    slcpar = slcDir1 + '/' + DATE6 + '.slc.par'
    Title = UseGamma(slcpar, 'read', 'title:')
    if 'E1' in Title:
        Flag = 'ERS1'
        Url = 'ftp://dutlru2.lr.tudelft.nl/pub/orbits/ODR.ERS-1/dgm-e04/'
        List = ERS1_Orb_list 
        Dir = ERS1_Orb_Dir
    elif 'E2' in Title:
        Flag = 'ERS2'
        Url = 'ftp://dutlru2.lr.tudelft.nl/pub/orbits/ODR.ERS-2/dgm-e04/'
        List = ERS2_Orb_list
        Dir = ERS2_Orb_Dir
    else:
        print('The SAR data is invalid.')
        sys.exit(1) 
    
    if len(DATE)==6:
        A0 = int(DATE[0:2])
        if A0 < 50:
            DATE = '20' + DATE
        else:
            DATA = '19' + DATE
    
    YYMM = DATE6[0:2] + DATE6[2:4]
    
    call_str = 'grep ' + YYMM + ' ' + List + ' > list0'
    os.system(call_str)
    
    call_str = "awk '{print $12}' list0 > start_end"
    os.system(call_str)
    
    call_str = "awk '{print $1}' list0 > vec_num"
    os.system(call_str)
    
    AA= np.loadtxt('start_end',dtype=np.str)
    Na = AA.size
    
    print(AA)
    
    A_num= np.loadtxt('vec_num',dtype=np.str)
    Na_num = A_num.size
    
    for i in range(Na-1):
        A0 = AA[i]
        A1 = AA[i+1]
        print(DATE6)
        print(A0)
        print(A1)
        if int(DATE6)==int(A0):
            m = i
        elif int(DATE6)==int(A1):
            m = i+1
        elif int(A0) < int(DATE6) < int(A1):
            m = i
            
    FF = A_num[int(m)]
    SS = Url + 'ODR.' + FF
    print(SS)

    call_str = 'wget -q --no-check-certificate ' + SS + ' -P ' + Dir
    os.system(call_str)
    
    
    print("Download precise DEFT orbital data for %s is done." % DATE)
    sys.exit(1)
    
if __name__ == '__main__':
    main(sys.argv[:])
    
    
    
    
    
    
    
    
    
    
    
