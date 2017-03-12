#! /usr/bin/env python
#'''
###################################################################################
#                                                                                 #
#            Author:   Yun-Meng Cao                                               #
#            Email :   ymcmrs@gmail.com                                           #
#            Date  :   February, 2017                                             #
#                                                                                 #
#   Coregistration of SAR images based on cross-correlation with DEM assisstance  #
#                                                                                 #
###################################################################################
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
   
            coregistSLC_DEM_gamma.py igramDir
      
      e.g.  coregistSLC_DEM_gamma.py IFGRAM_PacayaT163TsxHhA_131021-131101_0011_-0007
          
            
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
    Mdate = IFGPair.split('-')[0]
    Sdate = IFGPair.split('-')[1]
    
    
    scratchDir = os.getenv('SCRATCHDIR')
    templateDir = os.getenv('TEMPLATEDIR')
    templateFile = templateDir + "/" + projectName + ".template"
    
    processDir = scratchDir + '/' + projectName + "/PROCESS"
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
    Srslc0Img = workDir + "/" + Sdate + ".rslc0"
    Srslc0Par = workDir + "/" + Sdate + ".rslc0.par"
# output multi-looked amplitude

    MampImg = workDir + "/" + Mdate + ".amp"	
    MampPar = workDir + "/" + Mdate + ".amp.par"
    SampImg = workDir + "/" + Sdate + ".amp"
    SampPar = workDir + "/" + Sdate + ".amp.par"
    
    simDir = scratchDir + '/' + projectName + "/PROCESS" + "/SIM" 
    simDir = simDir + '/sim_' + Mdate + '-' + Sdate

    rdcDEM      = simDir + '/sim_' + Mdate + '-' + Sdate + '.rdc.dem'
    
    if not os.path.isfile(rdcDEM):
        call_str= "CreateRdcDem_Gamma.py " + igramDir
        os.system(call_str)

    lt0 = workDir + "/lt0" 
    lt1 = workDir + "/lt1"
    mli0 = workDir + "/mli0" 
    diff0 = workDir + "/diff0" 
    offs0 = workDir + "/offs0"
    snr0 = workDir + "/snr0"
    offsets0 = workDir + "/offsets0"
    coffs0 = workDir + "/coffs0"
    coffsets0 = workDir + "/coffsets0"
    off = workDir + "/" + IFGPair + ".off"
    offs = workDir + "/offs"
    snr = workDir + "/snr"
    offsets = workDir + "/offsets"
    coffs = workDir + "/coffs"
    coffsets = workDir + "/coffsets"

    if os.path.isfile(diff0):
        os.remove(diff0)
    if os.path.isfile(off):
        os.remove(off)

# real processing

    call_str = "$GAMMA_BIN/multi_look " + MslcImg + " " + MslcPar + " " + MampImg + " " + MampPar + " " + rlks + " " + azlks
    os.system(call_str)

    call_str = "$GAMMA_BIN/multi_look " + SslcImg + " " + SslcPar + " " + SampImg + " " + SampPar + " " + rlks + " " + azlks
    os.system(call_str)

    
    call_str = "$GAMMA_BIN/rdc_trans " + MampPar + " " + rdcDEM + " " + SampPar + " " + lt0
    os.system(call_str)

    width_Mamp = UseGamma(MampPar, 'read', 'range_samples')
    width_Samp = UseGamma(SampPar, 'read', 'range_samples')
    line_Samp = UseGamma(SampPar, 'read', 'azimuth_lines')

    call_str = "$GAMMA_BIN/geocode " + lt0 + " " + MampImg + " " + width_Mamp + " " + mli0 + " " + width_Samp + " " + line_Samp + " 2 0"
    os.system(call_str)

    call_str = "$GAMMA_BIN/create_diff_par " + SampPar + " - " + diff0 + " 1 0"
    os.system(call_str)

    call_str = "$GAMMA_BIN/init_offsetm " + mli0 + " " + SampImg + " " + diff0 + " 1 1"
    os.system(call_str)

    call_str = "$GAMMA_BIN/offset_pwrm " + mli0 + " " + SampImg + " " + diff0 + " " + offs0 + " " + snr0 + " 256 256 " + offsets0 + " 2 16 16"
    os.system(call_str)
  
    call_str = "$GAMMA_BIN/offset_fitm " + offs0 + " " + snr0 + " " + diff0 + " " + coffs0 + " " + coffsets0 + " - 4"
    os.system(call_str)

    call_str = "$GAMMA_BIN/gc_map_fine " + lt0 + " " + width_Mamp + " " + diff0 + " " + lt1
    os.system(call_str)

    call_str = "$GAMMA_BIN/SLC_interp_lt " + SslcImg + " " + MslcPar + " " + SslcPar + " " + lt1 + " " + MampPar + " " + SampPar + " - " + Srslc0Img + " " + Srslc0Par
    os.system(call_str)


# further refinement processing for resampled SLC

    call_str = "$GAMMA_BIN/create_offset " + MslcPar + " " + Srslc0Par + " " + off + " 1 - - 0"
    os.system(call_str)

    call_str = "$GAMMA_BIN/offset_pwr " + MslcImg + " " + Srslc0Img + " " + MslcPar + " " + Srslc0Par + " " + off + " " + offs + " " + snr + " 128 128 " + offsets + " 2 32 64"
    os.system(call_str)

    call_str = "$GAMMA_BIN/offset_fit "  + offs + " " + snr + " " + off + " " + coffs + " " + coffsets + " - 3" 
    os.system(call_str)

    call_str = "$GAMMA_BIN/SLC_interp_lt " + SslcImg + " " + MslcPar + " " + SslcPar + " " + lt1 + " " + MampPar + " " + SampPar + " " + off + " " + SrslcImg + " " + SrslcPar
    os.system(call_str)

    call_str = "cp " + MslcImg + " " + MrslcImg
    os.system(call_str)

    call_str = "cp " + MslcPar + " " + MrslcPar
    os.system(call_str)

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

    os.remove(lt0)
    os.remove(lt1)
    os.remove(mli0)
    os.remove(diff0)
    os.remove(offs0)
    os.remove(snr0)
    os.remove(offsets0)
    os.remove(coffs0)
    os.remove(coffsets0)
    os.remove(off)
    os.remove(offs)
    os.remove(snr)
    os.remove(offsets)
    os.remove(coffs)
    os.remove(coffsets)
    os.remove(Srslc0Img)
    os.remove(Srslc0Par)

    print "Coregistration with DEM is done!"
 
    sys.exit(1)

if __name__ == '__main__':
    main(sys.argv[:])
