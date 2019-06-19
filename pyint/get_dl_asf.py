#! /usr/bin/env python
############################################################
# Program is part of PyINT v1.0                            #
# Copyright(c) 2018, Yunmeng Cao                           #
# Author:  Yunmeng Cao                                     #
############################################################

import numpy as np
import gdal
import getopt
import sys
import os
import h5py
import argparse
import matplotlib.pyplot as plt
from matplotlib.ticker import MultipleLocator, FormatStrFormatter


#def read_region(STR):
#    WEST = STR.split('/')[0]
#    SOUTH = STR.split('/')[1].split('/')[0]
    
#    EAST = STR.split(SOUTH+'/')[1].split('/')[0]
#    NORTH = STR.split(SOUTH+'/')[1].split('/')[1]
    
#    WEST =float(WEST)
#    SOUTH=float(SOUTH)
#    EAST=float(EAST)
#    NORTH=float(NORTH)
#    return WEST,SOUTH,EAST,NORTH

def read_region(STR):
    WEST = STR.split('/')[0]
    EAST = STR.split('/')[1].split('/')[0]
    
    SOUTH = STR.split(EAST+'/')[1].split('/')[0]
    NORTH = STR.split(EAST+'/')[1].split('/')[1]
    
    WEST =float(WEST)
    SOUTH=float(SOUTH)
    EAST=float(EAST)
    NORTH=float(NORTH)
    return WEST,SOUTH,EAST,NORTH
    
        
#######################################################################################

INTRODUCTION = '''
    
    Get downloadUrl from ASF download file.
    
'''


EXAMPLE = '''EXAMPLES:
    get_dl_asf.py download-all-2018-07-25_17-24-59.py
    get_dl_asf.py download-all-2018-07-25_17-24-59.py -o Shanghai_Url.txt

    
'''


def cmdLineParse():
    parser = argparse.ArgumentParser(description='Download SRTM 30m data.',\
                                     formatter_class=argparse.RawTextHelpFormatter,\
                                     epilog=INTRODUCTION+'\n'+EXAMPLE)

    parser.add_argument('asf_file',help='ASF python file for downloading the SLC data.')
    parser.add_argument('-o', dest= 'out',help='Output file name.')
    inps = parser.parse_args()

    if not inps.asf_file:
        parser.print_usage()
        sys.exit(os.path.basename(sys.argv[0])+': error: ASF downloading file should be provided.')

    return inps  


################################################################################################


def main(argv):
    
    inps = cmdLineParse()
    ASF = inps.asf_file

    if inps.out: OUT = inps.out
    else: OUT = 'ASF_SAR_Url'
    
    OUT0 = 'OUT0'
    call_str = "grep 'https://datapool.asf.alaska.edu/SLC/SA/S1A_IW_SLC__' -C 0 " + ASF + ' > '  + OUT0
    os.system(call_str)

    call_str = "awk -F'" + '"' + "' " + "'{print $2}' " +  OUT0
    os.system(call_str)
    
    call_str = "awk -F'" + '"' + "' " + "'{print $2}' " +  OUT0 + ' > ' +OUT
    os.system(call_str)
    
if __name__ == '__main__':
    main(sys.argv[1:])

