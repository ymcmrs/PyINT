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
import argparse

from pyint import _utils as ut

def cmdLineParse():
    parser = argparse.ArgumentParser(description='Coregister SM mode SLC to a reference SLC image using GAMMA.',\
                                     formatter_class=argparse.RawTextHelpFormatter,\
                                     epilog=INTRODUCTION+'\n'+EXAMPLE)

    parser.add_argument('projectName', help='Name of project.')
    parser.add_argument('sdate', help='date of the slave SLC image. [mater date is read from template]')
    inps = parser.parse_args()
    return inps


INTRODUCTION = '''
-------------------------------------------------------------------  
   Coregister SM mode SLC to a reference SLC image using GAMMA.
   [The reference date or master date will be read from the template file.]
'''

EXAMPLE = """Usage:
  
  coreg_gamma.py projectName Sdate
  
  coreg_gamma.py PacayaT163TsxHhA 20150102
------------------------------------------------------------------- 
"""
        
    
def main(argv):
    
    inps = cmdLineParse() 
    projectName = inps.projectName
    Sdate = inps.sdate
    
    scratchDir = os.getenv('SCRATCHDIR')
    templateDir = os.getenv('TEMPLATEDIR')
    templateFile = templateDir + "/" + projectName + ".template"
    
    slcDir     = scratchDir + '/' + projectName + "/SLC"
    rslcDir     = scratchDir + '/' + projectName + "/RSLC"
    if not os.path.isdir(rslcDir): os.mkdir(rslcDir)
    #workDir    = processDir + '/' + igramDir   
    workDir = rslcDir + '/' + Sdate
    if not os.path.isdir(workDir): os.mkdir(workDir)
    
    templateDict=ut.update_template(templateFile)
    rlks = templateDict['range_looks']
    azlks = templateDict['azimuth_looks']
    Mdate = templateDict['masterDate']
    
    demDir = scratchDir + '/' + projectName + '/DEM' 

#  Definition of file
    MslcDir     = slcDir  + '/' + Mdate
    SslcDir     = slcDir  + '/' + Sdate
    Mslc = slcDir  + '/' + Mdate + '/' + Mdate + '.slc'
    Mslcpar = slcDir  + '/' + Mdate + '/' + Mdate + '.slc.par'
    Mamp = slcDir  + '/' + Mdate + '/' + Mdate + '_' + rlks + 'rlks.amp'
    MampPar = slcDir  + '/' + Mdate + '/' + Mdate + '_' + rlks + 'rlks.amp.par'

    HGTSIM      = demDir + '/' + Mdate + '_' + rlks + 'rlks.rdc.dem'
    if not os.path.isfile(HGTSIM):
        call_str = 'generate_rdc_dem.py ' + projectName
        os.system(call_str)
    
    
# input slcs

    SslcDir = rslcDir + "/" + Sdate
    MslcDir = rslcDir + "/" + Mdate

    MslcImg = rslcDir + "/" + Mdate + ".rslc"
    MslcPar = rslcDir+ "/" + Mdate + ".rslc.par"
    SslcImg = rslcDir + "/" + Sdate + ".rslc"
    SslcPar = rslcDir + "/" + Sdate + ".rslc.par"

# output slcs

    MrslcImg = workDir + "/" + Mdate + ".rslc"
    MrslcPar = workDir + "/" + Mdate + ".rslc.par"
    SrslcImg = workDir + "/" + Sdate + ".rslc"
    SrslcPar = workDir + "/" + Sdate + ".rslc.par"
    Srslc0Img = workDir + "/" + Sdate + ".rslc0"
    Srslc0Par = workDir + "/" + Sdate + ".rslc0.par"
    
    
    
# output multi-looked amplitude

    MamprlksImg = workDir + "/" + Mdate + "_" + rlks+"rlks.amp"	
    MamprlksPar = workDir + "/" + Mdate + "_" + rlks+"rlks.amp.par"
    SamprlksImg = workDir + "/" + Sdate + "_" + rlks+"rlks.amp"
    SamprlksPar = workDir + "/" + Sdate + "_" + rlks+"rlks.amp.par"
    
    OFFSTD = workDir + "/" + Mdate + "-" + Sdate + ".off_std"
    
    simDir = scratchDir + '/' + projectName + "/PROCESS" + "/SIM" 
    simDir = simDir + '/sim_' + Mdate + '-' + Sdate

    HGTSIM      = demDir + '/sim_' + masterDate + '_'+rlks+'rlks.rdc.dem'
    if not os.path.isfile(HGTSIM):       
        call_str = 'Generate_RdcDEM_Gamma.py ' + projectName + ' ' + masterDate
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

    call_str = "multi_look " + MslcImg + " " + MslcPar + " " + MamprlksImg + " " + MamprlksPar + " " + rlks + " " + azlks
    os.system(call_str)

    call_str = "multi_look " + SslcImg + " " + SslcPar + " " + SamprlksImg + " " + SamprlksPar + " " + rlks + " " + azlks
    os.system(call_str)

    
    call_str = "rdc_trans " + MamprlksPar + " " + HGTSIM + " " + SamprlksPar + " " + lt0
    os.system(call_str)

    width_Mamp = UseGamma(MamprlksPar, 'read', 'range_samples')
    width_Samp = UseGamma(SamprlksPar, 'read', 'range_samples')
    line_Samp = UseGamma(SamprlksPar, 'read', 'azimuth_lines')

    call_str = "geocode " + lt0 + " " + MamprlksImg + " " + width_Mamp + " " + mli0 + " " + width_Samp + " " + line_Samp + " 2 0"
    os.system(call_str)

    call_str = "create_diff_par " + SamprlksPar + " - " + diff0 + " 1 0"
    os.system(call_str)

    call_str = "init_offsetm " + mli0 + " " + SamprlksImg + " " + diff0 + " 1 1"
    os.system(call_str)

    call_str = "offset_pwrm " + mli0 + " " + SamprlksImg + " " + diff0 + " " + offs0 + " " + snr0 + " 256 256 " + offsets0 + " 2 32 32"
    os.system(call_str)
  
    call_str = "offset_fitm " + offs0 + " " + snr0 + " " + diff0 + " " + coffs0 + " " + coffsets0 + " - 4"
    os.system(call_str)

    call_str = "gc_map_fine " + lt0 + " " + width_Mamp + " " + diff0 + " " + lt1
    os.system(call_str)
    
    
    call_str = "SLC_interp_lt " + SslcImg + " " + MslcPar + " " + SslcPar + " " + lt1 + " " + MamprlksPar + " " + SamprlksPar + " - " + Srslc0Img + " " + Srslc0Par
    os.system(call_str)


# further refinement processing for resampled SLC

    call_str = "create_offset " + MslcPar + " " + Srslc0Par + " " + off + " 1 - - 0"
    os.system(call_str)

    #call_str = "offset_pwr " + MslcImg + " " + Srslc0Img + " " + MslcPar + " " + Srslc0Par + " " + off + " " + offs + " " + snr + " 128 128 " + offsets + " 2 32 64"
    #os.system(call_str)

    #call_str = "offset_fit "  + offs + " " + snr + " " + off + " " + coffs + " " + coffsets + " - 3" 
    #os.system(call_str)
    
    call_str = "offset_pwr " + MslcImg + " " + Srslc0Img + " " + MslcPar + " " + Srslc0Par + " " + off + " " + offs + " " + snr + " " + rwin4cor + " " + azwin4cor + " " + offsets + " 2 " + rsample4cor + " " + azsample4cor
    os.system(call_str)

    call_str = "offset_fit "  + offs + " " + snr + " " + off + " " + coffs + " " + coffsets + " - 3" 
    os.system(call_str)
    
    call_str = "offset_pwr " + MslcImg + " " + Srslc0Img + " " + MslcPar + " " + Srslc0Par + " " + off + " " + offs + " " + snr + " " + rfwin4cor + " " + azfwin4cor + " " + offsets + " 2 " + rfsample4cor + " " + azfsample4cor
    os.system(call_str)

    
    
    call_str = "offset_fit "  + offs + " " + snr + " " + off + " " + coffs + " " + coffsets + " - 3 >" + OFFSTD 
    os.system(call_str)
    
############################################     Resampling     ############################################    
    
    
    for i in range(len(Suffix)):
        if not INF=='IFG':
            MslcImg = workDir + "/" + Mdate + Suffix[i]+".slc"
            MslcPar = workDir + "/" + Mdate + Suffix[i]+".slc.par"
            SslcImg = workDir + "/" + Sdate + Suffix[i]+".slc"
            SslcPar = workDir + "/" + Sdate + Suffix[i]+".slc.par"
        
        MrslcImg = workDir + "/" + Mdate + Suffix[i]+".rslc"
        MrslcPar = workDir + "/" + Mdate + Suffix[i]+".rslc.par"
        SrslcImg = workDir + "/" + Sdate + Suffix[i]+".rslc"
        SrslcPar = workDir + "/" + Sdate + Suffix[i]+".rslc.par"

        
######################## Resampling Slave Image ####################

        call_str = "SLC_interp_lt " + SslcImg + " " + MslcPar + " " + SslcPar + " " + lt1 + " " + MamprlksPar + " " + SamprlksPar + " " + off + " " + SrslcImg + " " + SrslcPar
        os.system(call_str)


        call_str = "cp " + MslcImg + " " + MrslcImg
        os.system(call_str)

        call_str = "cp " + MslcPar + " " + MrslcPar
        os.system(call_str)


####################  multi-looking for RSLC #########################################

        MamprlksImg = workDir + "/" + Mdate + '_'+rlks+'rlks'+Suffix[i]+".ramp"
        MamprlksPar = workDir + "/" + Mdate + '_'+rlks+'rlks'+Suffix[i]+".ramp.par"
        
        SamprlksImg = workDir + "/" + Sdate + '_'+rlks+'rlks'+Suffix[i]+".ramp"
        SamprlksPar = workDir + "/" + Sdate + '_'+rlks+'rlks'+Suffix[i]+".ramp.par"
        

        call_str = 'multi_look ' + MrslcImg + ' ' + MrslcPar + ' ' + MamprlksImg + ' ' + MamprlksPar + ' ' + rlks + ' ' + azlks
        os.system(call_str)

        call_str = 'multi_look ' + SrslcImg + ' ' + SrslcPar + ' ' + SamprlksImg + ' ' + SamprlksPar + ' ' + rlks + ' ' + azlks
        os.system(call_str)

        nWidth = UseGamma(MamprlksPar, 'read', 'range_samples')

        call_str = 'raspwr ' + MamprlksImg + ' ' + nWidth 
        os.system(call_str)  
        ras2jpg(MamprlksImg, MamprlksImg) 
        
        call_str = 'raspwr ' + SamprlksImg + ' ' + nWidth 
        os.system(call_str)
        ras2jpg(SamprlksImg, SamprlksImg)


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

    print("Coregistration with DEM is done!")
 
    sys.exit(1)

if __name__ == '__main__':
    main(sys.argv[:])
