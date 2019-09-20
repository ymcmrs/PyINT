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

from pyint import _utils as ut


def get_s1_date(raw_file):
    file0 = os.path.basename(raw_file)
    date = file0[17:25]
    return date
    
def cmdLineParse():
    parser = argparse.ArgumentParser(description='Generate SLC from S1 raw file using GAMMA.',\
                                     formatter_class=argparse.RawTextHelpFormatter,\
                                     epilog=INTRODUCTION+'\n'+EXAMPLE)

    parser.add_argument('s1_raw', help='raw Sentinel-1 file. e.g., S1A*.zip')
    parser.add_argument('root_path',help='root path for saving the SLC files')
       
    inps = parser.parse_args()

    return inps


INTRODUCTION = '''
-------------------------------------------------------------------  

   Generate SLC from Sentinel-1 raw data using GAMMA.
   
'''

EXAMPLE = """Usage:
  
  down2slc_sen.py S1A_IW_SLC_XXXX.zip /Yunmeng/S1_test
  
------------------------------------------------------------------- 
"""

def main(argv):
    
    inps = cmdLineParse() 
    raw_file = inps.s1_raw
    root_dir = inps.root_path
    
    date = get_s1_date(raw_file)
    if not os.path.isdir(root_dir):
        os.mkdir(root_dir)
    
    slc_dir = root_dir + '/' + date
    if not os.path.isdir(slc_dir):
        os.mkdir(slc_dir)
    
    if len(os.path.dirname(raw_file))==0:
        raw_file_dir = os.getcwd()
    else:
        raw_file_dir = os.path.dirname(raw_file)
    
    raw_dir = raw_file.replace('.zip','.SAFE')
    
    if not os.path.isdir(raw_dir): 
        call_str = 'unzip ' + raw_file + ' -d ' + raw_file_dir
        os.system(call_str)
      
    measureDir = raw_dir + '/measurement'
    annotatDir = raw_dir + '/annotation'
    calibraDir = raw_dir + '/annotation/calibration'
    
    MM = glob.glob(measureDir + '/*vv*tiff')
#     MEASURE = glob.glob(measureDir + '/*vv*tiff')
#    ANNOTAT = glob.glob(annotatDir + '/*vv*xml' )
#    CALIBRA = glob.glob(calibraDir+'/calibration*vv*') 
#    NOISE = glob.glob(calibraDir+'/noise*vv*')
    
    SLC_Tab = slc_dir + '/' + date+'_SLC_Tab'   
    TEST = slc_dir + '/' + date + '.IW1.slc'
    
    if not os.path.isfile(TEST):
        if os.path.isfile(SLC_Tab):
            os.remove(SLC_Tab)
        for kk in range(len(MM)):
            SLC    = slc_dir + '/' + date + '.IW' + str(kk+1)+'.slc'
            SLCPar = slc_dir + '/' + date + '.IW' + str(kk+1)+'.slc.par'
            TOPPar = slc_dir + '/' + date + '.IW' + str(kk+1)+'.slc.TOPS_par'
            BURST = slc_dir + '/' + date + '.IW' + str(kk+1)+'.burst.par'
        
            if os.path.isfile(BURST):
                os.remove(BURST)
            call_str = 'echo ' + SLC + ' ' + SLCPar + ' ' + TOPPar + ' >> ' + SLC_Tab
            os.system(call_str)
        
            MEASURE = glob.glob(measureDir + '/*iw' + str(kk+1) + '*vv*tiff')
            ANNOTAT = glob.glob(annotatDir + '/*iw' + str(kk+1) + '*vv*xml' )
            CALIBRA = glob.glob(calibraDir+'/calibration*'+ 'iw' + str(kk+1) + '*vv*') 
            NOISE = glob.glob(calibraDir+'/noise*' + 'iw' + str(kk+1) + '*vv*')
        
            #call_str = 'S1_burstloc ' + ANNOTAT[0] + '> ' +BURST
            #os.system(call_str)
            
            if int(date) > 180311:
                call_str = 'par_S1_SLC ' + MEASURE[0] + ' ' + ANNOTAT[0] + ' ' + CALIBRA[0] + ' - ' + SLCPar + ' ' + SLC + ' ' + TOPPar
            else:
                call_str = 'par_S1_SLC ' + MEASURE[0] + ' ' + ANNOTAT[0] + ' ' + CALIBRA[0] + ' ' + NOISE[0] + ' ' + SLCPar + ' ' + SLC + ' ' + TOPPar
            
            os.system(call_str)
            
            call_str = 'SLC_burst_corners ' + SLCPar + ' ' +  TOPPar + ' > ' +BURST
            os.system(call_str)
        
    TSLC = slc_dir + '/' + date + '.slc'
    TSLCPar = slc_dir + '/' + date + '.slc.par'
    
    TMLI =  slc_dir + '/' + date + '_20rlks.amp'
    TMLIPar = slc_dir + '/' + date + '_20rlks.amp.par'
    
    call_str = 'SLC_mosaic_S1_TOPS ' +  SLC_Tab + ' ' + TSLC + ' ' + TSLCPar + ' 10 2'
    os.system(call_str)
   
    call_str = 'multi_look ' + TSLC + ' ' + TSLCPar + ' ' + TMLI + ' ' + TMLIPar + ' 20 4' 
    os.system(call_str)
    
    nWidth = ut.read_gamma_par(TMLIPar, 'read','range_samples:')
    call_str = 'raspwr ' + TMLI + ' ' + nWidth + ' - - - - - - - '
    os.system(call_str)

    call_str = 'rm -rf ' + raw_dir
    os.system(call_str)    

    print("Down to SLC for %s is done! " % date)
    sys.exit(1)
    
if __name__ == '__main__':
    main(sys.argv[:])    
    
    
    
    
    
    
