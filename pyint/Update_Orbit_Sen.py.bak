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

def StrNum(S):
    S = str(S)
    if len(S)==1:
        S='0' +S
    return S


#########################################################################

INTRODUCTION = '''
##############################################################################################
   Copy Right(c): 2017, Yunmeng Cao   @PyINT v1.0   
   
   Update the orbit data of Sentinel-1A/B slc par files based on the AUX_POEORB data.
   See also:  Sen_PreOrbit.py
   
'''

EXAMPLE = '''
    Usage:
            Update_Orbit_Sen.py SLCPATH/Date 
 
    Examples:
            Update_Orbit_Sen.py /scratch/projects/insarlab/yxc773/ShanghaiT171F96S1A/SLC/170122 

###################################################################################################
'''


def cmdLineParse():
    parser = argparse.ArgumentParser(description='Update the orbit data for the slc par files.',\
                                     formatter_class=argparse.RawTextHelpFormatter,\
                                     epilog=INTRODUCTION+'\n'+EXAMPLE)

    parser.add_argument('slc_path',help='Path of SLC directory.')
    
    inps = parser.parse_args()
    return inps

################################################################################    


def main(argv):
    
    inps = cmdLineParse()
    PATH  = inps.slc_path
    os.chdir(PATH)
    
    path = os.getcwd()
    KK=os.listdir(path)
    
    Date = os.path.basename(path)
    if len(Date)==6:
        Date = '20'+Date
    Date0 = int(Date)-1
    FF0 = 'V'+str(Date0)    
    
    
    
    SLC_PAR  = []
    ORBIT = 'test'
    for ll in KK:
        if 'slc.par' in ll:
            SLC_PAR.append(ll)
        if 'S1A_OPER_AUX_POEORB_OPOD_' and FF0 in ll:
            print ll
            ORBIT = ll
    
    if not os.path.isfile(ORBIT):

        print 'Precise orbit file is not found! Please use Sen_PreOrb.py to download the orbit data.'
        sys.exit(1)
    
    print SLC_PAR
    N = len(SLC_PAR)
           
    for ff in SLC_PAR:
        call_str = 'S1_OPOD_vec ' + ff + ' ' + ORBIT
        os.system(call_str)
        
    print 'Update the orbit parameters of the slc par files for date %s is finished.' % Date
    sys.exit(1)
    
if __name__ == '__main__':
    main(sys.argv[:])
        
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    