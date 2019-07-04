#! /usr/bin/env python
#################################################################
###  This program is part of PyINT  v2.0                      ### 
###  Copy Right (c): 2017-2019, Yunmeng Cao                   ###  
###  Author: Yunmeng Cao                                      ###                                                          
###  Email : ymcmrs@gmail.com                                 ###
###  Univ. : Now at KAUST                                     ###   
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

        
def check_ERS_par(SAR_IM_0P):
    Name = os.path.basename(SAR_IM_0P)
    ff = Name.split('.')[1]
    date = (Name.split('SAR_IM__0PWDSI')[1]).split('_')[0]

    if  ff == 'E1':
        par = 'ERS1_ESA.par'
        antenna = 'ERS1_antenna.gain'
        orbdir = os.getenv('ERS1ORBDIR')
    elif ff == 'E2':
        par = 'ERS2_ESA.par'
        antenna = 'ERS2_antenna.gain'
        orbdir = os.getenv('ERS2ORBDIR')
    else:
        print('Invalid input SAR_IM_0P file.')
        sys.exit(1)
        
    return par, antenna, orbdir, date   
        
#########################################################################

INTRODUCTION = '''
#############################################################################
   Copy Right(c): 2017-2019, Yunmeng Cao   @PyINT v1.0   
   
   Generate SLC for ERS raw data with ENVISAT format
     
'''

EXAMPLE = '''
    Usage:
            raw2slc_ers_envisat.py SAR_IM_OP -o output_prefix
 
    Examples:
            raw2slc_ers_envisat.py SAR_IM_OP -o 19950102

##############################################################################
'''


def cmdLineParse():
    parser = argparse.ArgumentParser(description='Generate SLC for ERS raw data with ENVISAT format.',\
                                     formatter_class=argparse.RawTextHelpFormatter,\
                                     epilog=INTRODUCTION+'\n'+EXAMPLE)

    parser.add_argument('ers_envisat_raw',help='ERS raw data with ENVISAT format, e.g., SAR_IM_0PXXXX.E1')
    parser.add_argument('-o',dest='out_put',help='prefix of the output file, e.g., output.slc, output.slc.par')
    
    inps = parser.parse_args()
    return inps

################################################################################    


def main(argv):
      
    inps = cmdLineParse()
    SAR_IM_0P = inps.ers_envisat_raw
    par,antenna,orbdir,date = check_ERS_par(SAR_IM_0P)
    
    raw = date + '.raw'
    azsp = date + '.azsp'
    dop = date + '.dop'
    rspec = date + '.rspec'
    rc = date + '.rc'
    autof = date + '.autof'
    
    
    if not os.path.isfile(par):
        call_str = 'cp $GAMMA_HOME/MSP/sensors/' + par + ' .'
        os.system(call_str)
    if not os.path.isfile(antenna):
        call_str = 'cp $GAMMA_HOME/MSP/sensors/' + antenna + ' .'
        os.system(call_str) 
    
    if inps.out_put:
        pslc_par = 'p' + inps.out_put + '.slc.par'
        slc_par = inps.out_put + '.slc.par'
        slc  = inps.out_put + '.slc'
        mli_par = inps.out_put + '.mli.par'
        mli = inps.out_put + '.mli'
    else:
        pslc_par = 'p' + date + '.slc.par'
        slc_par = date + '.slc.par'
        slc  = date + '.slc'
        mli_par = date + '.mli.par'
        mli = date + '.mli'
        
    call_str = 'ERS_ENVISAT_proc ' + SAR_IM_0P + ' ' + par + ' ' + pslc_par + ' ' + raw
    os.system(call_str)
    
    call_str = 'DELFT_proc2 ' + pslc_par + ' ' + orbdir
    os.system(call_str)
    
    call_str = 'azsp_IQ ' + par + ' ' + pslc_par + ' ' + raw + ' ' + azsp
    os.system(call_str)
    
    call_str = 'doppler ' + par + ' ' + pslc_par + ' ' + raw + ' ' + dop
    os.system(call_str)
    
    call_str = 'rspec_IQ ' + par + ' ' + pslc_par + ' ' + raw + ' ' + rspec
    os.system(call_str)
    
    call_str = 'pre_rc ' + par + ' ' + pslc_par + ' ' + raw + ' ' + rc
    os.system(call_str)
    
    call_str = 'autof ' + par + ' ' + pslc_par + ' ' + rc + ' ' + autof + ' 2.0 ' 
    os.system(call_str)
    
    call_str = 'autof ' + par + ' ' + pslc_par + ' ' + rc + ' ' + autof + ' 2.0 ' 
    os.system(call_str)
    
    call_str = 'az_proc ' + par + ' ' + pslc_par + ' ' + rc + ' ' + slc + ' 4096 1 57.2 0 2.120 '
    os.system(call_str)

    call_str = 'par_MSP ' + par + ' ' + pslc_par + ' ' + slc_par + ' 1'
    os.system(call_str)

    call_str = 'multi_look ' + slc + ' ' + slc_par + ' ' + mli + ' ' +  mli_par  + ' 2 10'
    os.system(call_str)
    
    
    Width = UseGamma(mli_par, 'read', 'range_samples: ')
    call_str = 'raspwr ' + mli + ' ' + Width
    os.system(call_str)
    
    
    print("Generate SLC from %s is done." % SAR_IM_0P)
    sys.exit(1)
    
if __name__ == '__main__':
    main(sys.argv[:])
    
    
    
    
    
    
    
    
    
    
    
