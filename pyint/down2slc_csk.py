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
   Copy Right(c): 2017-2020, Yunmeng Cao   @PyINT v2.0   
   
   Generate SLC for CSK raw data (with **.tar.gz format).
     
'''

EXAMPLE = '''
    Usage:
            down2slc_csk.py projectName date
 
    Examples:
            down2slc_csk.py KilaueaT10CskA 20180419

##############################################################################
'''


def cmdLineParse():
    parser = argparse.ArgumentParser(description='Generate SLC for ERS raw data with ENVISAT format.',\
                                     formatter_class=argparse.RawTextHelpFormatter,\
                                     epilog=INTRODUCTION+'\n'+EXAMPLE)

    parser.add_argument('projectName',help='project name.')
    parser.add_argument('date',help='to be processed date.')
    
    inps = parser.parse_args()
    return inps

################################################################################    


def main(argv):
      
    inps = cmdLineParse()
    projectName = inps.projectName
    date = inps.date

    scratchDir = os.getenv('SCRATCHDIR')
    templateDir = os.getenv('TEMPLATEDIR')
    templateFile = templateDir + "/" + projectName + ".template"
    
    downDir    = scratchDir + '/' + projectName + "/DOWNLOAD"    
    slcDir     = scratchDir + '/' + projectName + "/SLC"
    rslcDir     = scratchDir + '/' + projectName + "/RSLC"   
    
    if not os.path.isdir(slcDir):
        call_str = 'mkdir ' + slcDir
        os.system(call_str)    
    
    slcDir1 = slcDir + '/' + date
    if not os.path.isdir(slcDir1):
        call_str = 'mkdir ' + slcDir1
        os.system(call_str)     

    tar0 = glob.glob(downDir + '/*' + date + '*.tar.gz')[0]
    rawDir = downDir + '/raw_' + date    
    
    if not os.path.isdir(rawDir):
        call_str = 'mkdir ' + downDir + '/raw_' + date
        os.system(call_str)      
    
    call_str = 'tar -xzf ' + tar0 + ' -C ' + rawDir
    os.system(call_str)    

    par = rawDir + '/' + date + '.sar_par'
    raw = rawDir + '/' + date + '.raw'
    azsp = rawDir + '/' + date + '.azsp'
    dop = rawDir + '/' + date + '.dop'
    rspec = rawDir + '/' + date + '.rspec'
    rc = rawDir + '/' + date + '.rc'
    autof = rawDir + '/' + date + '.autof'
    dop_ambig = rawDir + '/' + date  + '.dop_ambig'
    
    h5file = glob.glob(rawDir + '/*.h5')[0]    
    
    pslc_par = rawDir + '/' + 'p' + date + '.slc.par'
    slc_par = slcDir1 + '/' + date + '.slc.par'
    slc  = slcDir1 + '/' +date + '.slc'
    mli_par = slcDir1 + '/' +date + '.mli.par'
    mli = slcDir1 + '/' + date + '.mli'
    
    call_str = 'CS_proc ' + h5file + ' ' + par + ' ' + pslc_par + ' '  + raw + ' - - '
    os.system(call_str)
    
    cal_str = 'dop_ambig ' + par + ' ' + pslc_par + ' ' + raw + ' 2 - ' + dop_ambig 
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
    
    call_str = 'az_proc ' + par + ' ' + pslc_par + ' ' + rc + ' ' + slc + ' - 1 ' + ' - 0 2.120 '
    os.system(call_str)

    call_str = 'par_MSP ' + par + ' ' + pslc_par + ' ' + slc_par + ' 1'
    os.system(call_str)

    call_str = 'multi_look ' + slc + ' ' + slc_par + ' ' + mli + ' ' +  mli_par  + ' 20 16'
    os.system(call_str)
    
    
    Width = UseGamma(mli_par, 'read', 'range_samples: ')
    call_str = 'raspwr ' + mli + ' ' + Width
    os.system(call_str)
    
    
    print("Generate SLC for %s is done." % date)
    sys.exit(1)
    
if __name__ == '__main__':
    main(sys.argv[:])
    
    
    
    
    
    
    
    
    
    

