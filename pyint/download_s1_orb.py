#! /usr/bin/env python
#################################################################
###  This program is part of PyINT  v2.1                      ### 
###  Copy Right (c): 2017-2019, Yunmeng Cao                   ###  
###  Author: Yunmeng Cao                                      ###                                                          
###  Contact: ymcmrs@gmail.com                                ###  
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
-------------------------------------------------------------------  

   Download precise Sentinel-1 orbit file from https://qc.sentinel1.eo.esa.int/
   
'''

EXAMPLE = """Usage:
  
  download_s1_orb.py date Satellite
 
Example: 

  download_s1_orb.py 20180101 A
  download_s1_orb.py 20180101 A --dir /Yunmeng/test
  
  
------------------------------------------------------------------- 
"""


def cmdLineParse():
    parser = argparse.ArgumentParser(description='Download precise S1 orbit data.',\
                                     formatter_class=argparse.RawTextHelpFormatter,\
                                     epilog=INTRODUCTION+'\n'+EXAMPLE)

    parser.add_argument('date',help='SAR date that need precise orbital data.')
    parser.add_argument('satellite',help='satellite type: A (Sentinel-1A) or B(Sentinel-1B).')
    parser.add_argument('--dir', dest='save_dir',help='Directory for saving the orbit file. [Default: current dir]')
    
    inps = parser.parse_args()
    return inps

################################################################################    


def main(argv):
      
    total = time.time()
    inps = cmdLineParse()
    if inps.save_dir: root_path = inps.save_dir
    else: root_path = os.getcwd()
    
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

    date = DATE
    SS = "'" + SS + "'"
    print(SS)
    tt ='tt_orb_' + date
    tt0 ='tt0_orb_' + date
    tt00 ='tt00_orb_' + date
    tt000 ='tt000_orb_' + date

    call_str = "curl -s -l " + SS + " > " + tt
    os.system(call_str)
    
    call_str = "grep 'EOF' -C 0 " + tt + " > " + tt0
    os.system(call_str)
    
    call_str="awk -F'href=' '{print $2}' " + tt0 +" > " + tt00
    os.system(call_str)
    
    call_str= "awk -F'>' '{print $1}' " + tt00 + '> ' + tt000
    os.system(call_str)
    
    SS=linecache.getline(tt000, 1)
    SS = SS.split('"')[1]
    filename = os.path.basename(SS)
    print(filename)
    call_str = "wget -q --no-check-certificate " + SS + " -O " + root_path + "/" + filename
    os.system(call_str)
    
    
    os.remove(tt)
    os.remove(tt0)
    os.remove(tt00)
    os.remove(tt000)
    
    
    print("Download precise orbital data for %s is done." % DATE)
    sys.exit(1)
    
if __name__ == '__main__':
    main(sys.argv[:])
    
    
    
    
    
    
    
    
    
    
    
