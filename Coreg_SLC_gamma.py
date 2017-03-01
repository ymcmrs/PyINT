#! /usr/bin/env python

#'''
########################################################
# Author:  Yun-Meng Cao                                #
# Feb., 2017                                           #
# gamma based coregistration script                    # 
# ######################################################
#'''

import numpy as np
import os
import pysar._readfile as readfile
import sys  
import subprocess
import time
import messageRsmas
import glob
import re

def main(argv):
    try:
        Mslc = argv[1]
        Mslc_par = argv[2]
        Sslc = argv[3]
        Sslc_par=argv[4]
    except:
        print "*******************************"
        print "  not enough input parameters  "
        print "*******************************"
        sys.exit(1)
    
    GAMMA_BIN_2015="/nethome/yxc773/test/test1/rsmas_insar/3rdparty/gamma/GAMMA_SOFTWARE-20150702/BIN"
    templateFile=sys.argv[1]
    templateContents=readfile.read_template(templateFile)

    path_SLC=templateContents['path_SLC']
    Mdate=templateContents['Mdate']
    Sdate =templateContents['Sdate']
    Pair = Mdate + "_" + Sdate


    Mslc = path_SLC+"/"+Mdate+"/"+Mdate+".slc"
    MslcPar = path_SLC+"/"+Mdate+"/"+Mdate+".slc.par"

    Sslc = path_SLC+"/"+Sdate+"/"+Sdate+".slc"
    SslcPar = path_SLC+"/"+Sdate+"/"+Sdate+".slc.par"

    dem = temlateContents['DEM']
    demPar = dem+".par"
     
    workdir = templateContents['path_process']

    Pair = Mdate + "_" + Sdate
    off = workdir+"/"+Pair+".off"
    snr = workdir+"/"+Pair+".snr"    # which in 2016 version GAMMA has changed to ccp, and the threshold value should also change.  
    offs = workdir+"/"+Pair + ".offs"
    coffs = workdir+"/"+Pair + ".coffs"
    coffsets = workdir+"/"+Pair + ".coffsets"
    
    if os.path.isfile(off):
        os.remove(off)
    

#####definition of parameter variables which may be included in the Template file

    rlks4cor = "4"
    azlks4cor = "4"
    rpos4cor = "-"
    azpos4cor = "-"
    patch4cor = "512"
    thresh4cor = "0.3"
    rwin4cor = "256"
    azwin4cor = "256"
    rfwin4cor = "128"
    azfwin4cor = "128"
    
    
    
    os.chdir(workdir)
    

    call_str= GAMMA_BIN_2015+"/create_offset " + Mslc_par + " " + Slc_par + " " + off + " 1 - - 0"
    os.system(call_str)

    call_str = GAMMA_BIN_2015+"/init_offset_orbit "+ MslcPar + " " + SslcPar + " " + off
    os.system(call_str)
    
    call_str = GAMMA_BIN_2015+"/init_offset "+ Mslc + " " + Sslc + " " + MslcPar + " " + SslcPar + " " + off + " " + rlks4cor + " " + azlks4cor + " " + rpos4cor + " " + azpos4cor
    os.system(call_str)
    
    call_str = GAMMA_BIN_2015 + "/offset_pwr " + Mslc + " " + Sslc + " " + MslcPar + " " + SslcPar + " " + off + " " + offs + " " + snr + " " + rwin4cor + " " + azwin4cor + " " + offsets + " 2 16 32"
    os.system(call_str)
    
    call_str = GAMMA_BIN_2015 +"/offset_fit " + offs + " " + snr + " " + off + " " + coffs + " " + coffsets + " 0.7 3" 
    os.system(call_str)
    
    print "Coregistration without DEM is done"

    sys.exit(1)

if __name__=='__main__':
    main(sys.argv[:])















