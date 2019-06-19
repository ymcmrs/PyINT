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


#########################################################################

INTRODUCTION = '''
#############################################################################
   Copy Right(c): 2017, Yunmeng Cao   @PyINT v1.0   
   
   Download precise sentinel orbit data (AUX_POEORB)automatically.
   refered website:  https://qc.sentinel1.eo.esa.int/aux_poeorb/
   
'''

EXAMPLE = '''
    Usage:
            Sen_PreOrbit.py Date Satellite (A or B)
 
    Examples:
            Sen_PreOrbit.py 20160101 A

##############################################################################
'''


def cmdLineParse():
    parser = argparse.ArgumentParser(description='Download precise S1 orbit data.',\
                                     formatter_class=argparse.RawTextHelpFormatter,\
                                     epilog=INTRODUCTION+'\n'+EXAMPLE)

    parser.add_argument('date',help='SAR date that need precise orbital data.')
    parser.add_argument('satellite',help='satellite type: A (Sentinel-1A) or B(Sentinel-1B).')
    
    inps = parser.parse_args()
    return inps

################################################################################    


def main(argv):
      
    total = time.time()
    inps = cmdLineParse()
    
    DATE = inps.date
    
    if len(DATE)==6:
        DATE = '20' + DATE
    ST = inps.satellite
    YEAR = int(DATE[0:4])
    MON = int(DATE[4:6])
    DAY = int(DATE[6:8])
   
    MON_DAY = [31,28,31,30,31,30,31,31,30,31,30,31]
    
    if YEAR%4==0:
        MON_DAY[1]=29
      
    if MON ==1 and DAY ==1:
        DAY0 = 31
        MON0 = 12
        YEAR0 =YEAR -1
    elif MON!=1 and DAY ==1:
        DAY0 = MON_DAY[MON-2]
        MON0 = MON-1
        YEAR0 = YEAR
    else:
        DAY0 = DAY -1
        MON0 = MON
        YEAR0 = YEAR
    
    MONDAY0 = MON_DAY[MON0-1]
    
    TT = [1,4,7,10,13,16,19,22,25,28,MONDAY0] 

    T0 = []
    for k in range(len(TT)):
        T0.append(TT[k])
        TT[k] = TT[k]-DAY0

    for k in range(len(TT)):
        if k == len(TT)-1:
            if TT[k]==0: 
                ff = k-1
        else:
            if TT[k]<=0 and TT[k+1]>0:
                ff = k
            
  
    DAY1 = T0[ff]
    DAY2 = T0[ff+1]
    
    S1 = StrNum(YEAR0) + '-' + StrNum(MON0)
    S2 = StrNum(YEAR0) + '-' + StrNum(MON0) + '-' + StrNum(DAY1)
    S3 = StrNum(YEAR0) + '-' + StrNum(MON0) + '-' + StrNum(DAY2)
    S4 = StrNum(YEAR0) + '-' + StrNum(MON0) + '-' + StrNum(DAY0)
    
    #SS = 'https://qc.sentinel1.eo.esa.int/aux_poeorb/?mission=S1' + ST + '&validity_start_time=' + StrNum(YEAR0) + '&validity_start_time=' + S1 + '&validity_start_time=' + S2 + '..' + S3 + '&validity_start_time=' + S4
    SS = 'https://qc.sentinel1.eo.esa.int/aux_poeorb/?validity_start=' + StrNum(YEAR0) + '&validity_start=' + S1 + '&validity_start=' + S2 + '..' + S3 + '&validity_start=' +S4 + '&sentinel1__mission=S1'+ST+ '&sentinel1_mission=S1'+ST+ '&sentinel1_mission=S1'+ST+ '&sentinel1_mission=S1'+ST

    
    SS = "'" + SS + "'"
    print(SS)
    call_str = 'curl ' + SS + ' >tt'
    os.system(call_str)
    
    call_str = "grep 'EOF' -C 0 tt >t0"
    os.system(call_str)
    
    
    call_str="awk -F'href=' '{print $2}' t0 >t00"
    os.system(call_str)
    
    call_str= "awk -F'>' '{print $1}' t00 > t0"
    os.system(call_str)
    
    SS=linecache.getline('t0', 1)
    print(SS)
    
    call_str = 'wget -q --no-check-certificate ' + SS
    os.system(call_str)
    
    
    print("Download precise orbital data for %s is done." % DATE)
    sys.exit(1)
    
if __name__ == '__main__':
    main(sys.argv[:])
    
    
    
    
    
    
    
    
    
    
    
