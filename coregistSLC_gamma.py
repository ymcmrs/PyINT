#! /usr/bin/env python
#'''
##################################################################################
#                                                                                #
#            Author:   Yun-Meng Cao                                              #
#            Email :   ymcmrs@gmail.com                                          #
#            Date  :   February, 2017                                            #
#                                                                                #
#   Coregistration of SAR images based on cross-correlation by using gamma       #
#                                                                                #
##################################################################################
#'''
import numpy as np
import os
import pysar._readfile as readfile
import sys  
import subprocess
import getopt
import time
import glob

def ras2jpg(input, strTitle):
    call_str = "convert " + input + ".ras " + input + ".jpg"
    os.system(call_str)
    call_str = "convert " + input + ".jpg -resize 250 " + input + ".thumb.jpg"
    os.system(call_str)
    call_str = "convert " + input + ".jpg -resize 500 " + input + ".bthumb.jpg"
    os.system(call_str)
    call_str = "$INT_SCR/addtitle2jpg.pl " + input + ".thumb.jpg 14 " + strTitle
    os.system(call_str)
    call_str = "$INT_SCR/addtitle2jpg.pl " + input + ".bthumb.jpg 24 " + strTitle
    os.system(call_str)

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
        print "Keyword " + keyword + " doesn't exist in " + inFile
        f.close()

def usage():
    print '''
******************************************************************************************************
 
       Coregistration of SAR images based on cross-correlation by using GAMMA.
       With or without DEM assisstance can be chosen.

   usage:
   
            coregistSLC_init_gamma.py igramDir
      
      e.g.  coregistSLC_init_gamma.py IFGRAM_PacayaT163TsxHhA_131021-131101_0011_-0007
          
            
*******************************************************************************************************
    '''   
    
def main(argv):
    
    if len(sys.argv)==2:
        if argv[0] in ['-h','--help']: usage(); sys.exit(1)
        else: igramDir=sys.argv[1]        
    else:
        usage();sys.exit(1)
       
    projectName = igramDir.split('_')[1]
    IFGPair = igramDir.split(projectName+'_')[1].split('_')[0]
    MDate = IFGPair.split('-')[0]
    SDate = IFGPair.split('-')[1]
    
    
    scratchDir = os.getenv('SCRATCHDIR')
    templateDir = os.getenv('TEMPLATEDIR')
    templateFile = templateDir + "/" + projectName + ".template"
    
    processtDir = scratchDir + '/' + projectName + "/PROCESS"
    slcDir     = scratchDir + '/' + projectName + "/SLC"
    workDir    = processDir + '/' + igramDir   
    
    templateContents=readfile.read_template(templateFile)
    coregCoarse = templateContents['Coreg_Coarse']
    coregThreshold = templateContents['Coreg_Threshold']
    
    rlks = templateContents['Range_Looks']
    azlks = templateContents['Azimuth_Looks']
    
# input slcs

    SslcDir = slcDir + "/" + Sdate
    MslcDir = slcDir + "/" + Mdate

    MslcImg = MslcDir + "/" + Mdate + ".slc"
    MslcPar = MslcDir + "/" + Mdate + ".slc.par"
    SslcImg = SslcDir + "/" + Sdate + ".slc"
    SslcPar = SslcDir + "/" + Sdate + ".slc.par"

# output slcs

    MrslcImg = workDir + "/" + Mdate + ".rslc"
    MrslcPar = workDir + "/" + Mdate + ".rslc.par"
    SrslcImg = workDir + "/" + Sdate + ".rslc"
    SrslcPar = workDir + "/" + Sdate + ".rslc.par"

# output multi-looked amplitude

    MampImg = workDir + "/" + Mdate + ".amp"	
    MampPar = workDir + "/" + Mdate + ".amp.par"
    SampImg = workDir + "/" + Sdate + ".amp"
    SampPar = workDir + "/" + Sdate + ".amp.par"


##  MSLCImg = MslcDir + "/" + Mdate + ".SLC"
##  MSLCPar = MslcDir + "/" + Mdate + ".SLC.par"
##  SSLCImg = SslcDir + "/" + Sdate + ".SLC"
##  SSLCPar = SslcDir + "/" + Sdate + ".SLC.par"

    off = workDir + "/" + IFGPair + "/off"
    offs = workDir + "/" + IFGPair +"/offs"
    snr = workDir + "/" + IFGPair +"/snr"
    offsets = workDir + "/" + IFGPair + "/offsets"
    coffs = workDir + "/" + IFGPair + "/coffs"
    coffsets = workDir + "/" + IFGPair + "/coffsets"
    off_std = workDir + "/" + IFGPair + "/off_std"
# definition of parameter variables which may be included in the Template file

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


    if os.path.isfile(off):
        os.remove(off)

# real processing

    call_str = "$GAMMA_BIN/create_offset " + MslcPar + " " + SslcPar + " " + off + " 1 - - 0"
    os.system(call_str)

    if coregCoarse == 'both':
        print 'init offset estimation by both orbit and ampcor'
        call_str = '$GAMMA_BIN/init_offset_orbit '+ MslcPar + ' ' + SslcPar + ' ' + off
        os.system(call_str)

        call_str = '$GAMMA_BIN/init_offset '+ MslcImg + ' ' + SslcImg + ' ' + MslcPar + ' ' + SslcPar + ' ' + off + ' ' + rlks4cor + ' ' + azlks4cor + ' ' + rpos4cor + ' ' + azpos4cor
        call_str = '$GAMMA_BIN/init_offset '+ MslcImg + ' ' + SslcImg + ' ' + MslcPar + ' ' + SslcPar + ' ' + off + ' ' + rlks4cor + ' ' + azlks4cor + ' ' + 1 + ' ' + 1
        os.system(call_str)

    elif coregCoarse == 'orbit':
        print 'init offset estimation by orbit only'
        call_str = '$GAMMA_BIN/init_offset_orbit '+ MslcPar + ' ' + SslcPar + ' ' + off
        os.system(call_str)
    elif coregCoarse == 'ampcor':
        print 'init offset estimation by ampcor only'
        call_str = '$GAMMA_BIN/init_offset '+ MslcImg + ' ' + SslcImg + ' ' + MslcPar + ' ' + SslcPar + ' ' + off + ' ' + rlks4cor + ' ' + azlks4cor + ' ' + rpos4cor + ' ' + azpos4cor
        call_str = '$GAMMA_BIN/init_offset '+ MslcImg + ' ' + SslcImg + ' ' + MslcPar + ' ' + SslcPar + ' ' + off + ' ' + rlks4cor + ' ' + azlks4cor + ' ' + 1 + ' ' + 1
        os.system(call_str)
        
######################## 1st time  ############################

    call_str = "$GAMMA_BIN/offset_pwr " + MslcImg + " " + SslcImg + " " + MslcPar + " " + SslcPar + " " + off + " " + offs + " " + snr + " " + rwin4cor + " " + azwin4cor + " " + offsets + " 2 16 32"
    os.system(call_str)

    call_str = "$GAMMA_BIN/offset_fit " " " + offs + " " + snr + " " + off + " " + coffs + " " + coffsets + " " + CoregThreshold +" 3" 
    os.system(call_str)
    
########################  2nd time  #############################

#    call_str = "$GAMMA_BIN/offset_pwr " + MslcImg + " " + SslcImg + " " + MslcPar + " " + SslcPar + " " + off + " " + offs + " " + snr + " " + rfwin4cor + " " + azfwin4cor + " " + offsets + " 2 32 64"
    call_str = "$GAMMA_BIN/offset_pwr " + MslcImg + " " + SslcImg + " " + MslcPar + " " + SslcPar + " " + off + " " + offs + " " + snr + " 128 128 " + offsets + " 2 32 64" 
    
    os.system(call_str)
    call_str = "$GAMMA_BIN/offset_fit " " " + offs + " " + snr + " " + off + " " + coffs + " " + coffsets + " " + CoregThreshold +" 3 >" + off_std 
    os.system(call_str)
    
######################## Resampling Slave Image ####################

    call_str = "$GAMMA_BIN/SLC_interp " + SslcImg + " " + MslcPar + " " + SslcPar + " " + off + " " + SrslcImg + " " + SrslcPar
    os.system(call_str)

    call_str = "cp " + MslcImg + " " + MrslcImg
    os.system(call_str)

    call_str = "cp " + MslcPar + " " + MrslcPar
    os.system(call_str)


####################  multi-looking for RSLC #########################################

    call_str = '$GAMMA_BIN/multi_look ' + MrslcImg + ' ' + MrslcPar + ' ' + MampImg + ' ' + MampPar + ' ' + rlks + ' ' + azlks
    os.system(call_str)

    call_str = '$GAMMA_BIN/multi_look ' + SrslcImg + ' ' + SrslcPar + ' ' + SampImg + ' ' + SampPar + ' ' + rlks + ' ' + azlks
    os.system(call_str)

    nWidth = UseGamma(MampPar, 'read', 'range_samples')

    call_str = '$GAMMA_BIN/raspwr ' + MampImg + ' ' + nWidth 
    os.system(call_str)
  
    ras2jpg(MampImg, Mdate) 
    call_str = '$GAMMA_BIN/raspwr ' + SampImg + ' ' + nWidth 
    os.system(call_str)

    ras2jpg(SampImg, Sdate)

    
#    os.remove(off)
    os.remove(offs)
    os.remove(snr)
    os.remove(offsets)
    os.remove(coffs)
    os.remove(coffsets)


    print "Coregistration without DEM is done!"
 
    sys.exit(1)

if __name__ == '__main__':
    main(sys.argv[:])
