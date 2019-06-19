#! /usr/bin/env python
#################################################################
###  This program is part of PyINT  v1.0                      ### 
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

def StrNum(S):
    S = str(S)
    if len(S)==1:
        S='0' +S
    return S

def StrNum1(S):
    S=str(S)
    if len(S)==1:
        S='00' +S
    elif len(S)==2:
        S = '0' +S
    else:
        S = S
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

def print_progress(iteration, total, prefix='calculating:', suffix='complete', decimals=1, barLength=50, elapsed_time=None):
    """Print iterations progress - Greenstick from Stack Overflow
    Call in a loop to create terminal progress bar
    @params:
        iteration   - Required  : current iteration (Int)
        total       - Required  : total iterations (Int)
        prefix      - Optional  : prefix string (Str)
        suffix      - Optional  : suffix string (Str)
        decimals    - Optional  : number of decimals in percent complete (Int) 
        barLength   - Optional  : character length of bar (Int) 
        elapsed_time- Optional  : elapsed time in seconds (Int/Float)
    
    Reference: http://stackoverflow.com/questions/3173320/text-progress-bar-in-the-console
    """
    filledLength    = int(round(barLength * iteration / float(total)))
    percents        = round(100.00 * (iteration / float(total)), decimals)
    bar             = '#' * filledLength + '-' * (barLength - filledLength)
    if elapsed_time:
        sys.stdout.write('%s [%s] %s%s    %s    %s secs\r' % (prefix, bar, percents, '%', suffix, int(elapsed_time)))
    else:
        sys.stdout.write('%s [%s] %s%s    %s\r' % (prefix, bar, percents, '%', suffix))
    sys.stdout.flush()
    if iteration == total:
        print("\n")

    '''
    Sample Useage:
    for i in range(len(dateList)):
        print_progress(i+1,len(dateList))
    '''
    return       
        
        
#########################################################################

INTRODUCTION = '''
#############################################################################
   Copy Right(c): 2017-2019, Yunmeng Cao   @PyINT v1.0   
  
   Download precise ERS orbit data from Delft Institute for Earth-Oriented Space Research (http://www.deos.tudelft.nl/).
  
'''

EXAMPLE = '''
    Usage:
            download_ers_deos.py ERS1
            download_ers_deos.py ERS2
            
##############################################################################
'''


def cmdLineParse():
    parser = argparse.ArgumentParser(description='Download (and correct) precise ERS orbit data.',\
                                     formatter_class=argparse.RawTextHelpFormatter,\
                                     epilog=INTRODUCTION+'\n'+EXAMPLE)

    parser.add_argument('sar',help='project name')
    
    inps = parser.parse_args()
    return inps

################################################################################    


def main(argv):
      
    total = time.time()
    inps = cmdLineParse()
    sar = inps.sar
    PATH = os.getcwd()
    listfile = 'arclist'     
        
    if sar == 'ERS1':
        Url = 'ftp://dutlru2.lr.tudelft.nl/pub/orbits/ODR.ERS-1/dgm-e04/'
        Url_list = 'ftp://dutlru2.lr.tudelft.nl/pub/orbits/ODR.ERS-1/dgm-e04/arclist'
        num_min = 6
        num_max = 511
        N_num = 506
        if not os.path.isfile(listfile):
            call_str = 'wget -q ' + Url_list
            os.system(call_str)
        
    elif sar =='ERS2':
        Url = 'ftp://dutlru2.lr.tudelft.nl/pub/orbits/ODR.ERS-2/dgm-e04/'
        Url_list = 'ftp://dutlru2.lr.tudelft.nl/pub/orbits/ODR.ERS-2/dgm-e04/arclist'
        num_min = 3
        num_max = 867
        N_num = 865
        if not os.path.isfile(listfile):
            call_str = 'wget -q ' + Url_list
            os.system(call_str)
        
    else:
        print('SAR name is invalid!')
        sys.exit(1)
    
    for i in range(N_num):
        kk = num_min + i
        kk=int(kk)
        SS = Url + 'ODR.' + StrNum1(kk)
        print_progress(i+1, N_num, prefix='DEFT_vec: ', suffix=StrNum1(kk))
    
        call_str = 'wget -q --no-check-certificate ' + SS + ' -P ' + PATH
        os.system(call_str)
   
    
    print("Download precise DEFT orbital data for %s is done." % sar)
    sys.exit(1)
    
if __name__ == '__main__':
    main(sys.argv[:])
    
    
    
    
    
    
    
    
    
    
    
