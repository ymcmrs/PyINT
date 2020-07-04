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
    
    SslcDir     = slcDir  + '/' + Sdate  
    Samp = slcDir  + '/' + Sdate + '/' + Sdate + '_' + rlks + 'rlks.amp'
    SampPar = slcDir  + '/' + Sdate + '/' + Sdate + '_' + rlks + 'rlks.amp.par'
    Sramp = rslcDir  + '/' + Sdate + '/' + Sdate + '_' + rlks + 'rlks.amp'
    SrampPar = rslcDir  + '/' + Sdate + '/' + Sdate + '_' + rlks + 'rlks.amp.par'
    
    Sslc = slcDir  + '/' + Sdate + '/' + Sdate + '.slc'
    SslcPar = slcDir  + '/' + Sdate + '/' + Sdate + '.slc.par'
    
    SrslcDir = rslcDir + "/" + Sdate

    Srslc    = SrslcDir + "/" + Sdate + ".rslc"
    SrslcPar = SrslcDir + "/" + Sdate + ".rslc.par"
    
    Srslc0    = SrslcDir + "/" + Sdate + ".rslc0"
    SrslcPar0 = SrslcDir + "/" + Sdate + ".rslc0.par"

#####################################################
## copy all of the master files into slave folder for parallel processing
    remove_file = []
    Mslc0 = slcDir  + '/' + Mdate + '/' + Mdate + '.slc'
    MslcPar0 = slcDir  + '/' + Mdate + '/' + Mdate + '.slc.par'
    #Mamp0 = slcDir  + '/' + Mdate + '/' + Mdate + '_' + rlks + 'rlks.amp'
    #MampPar0 = slcDir  + '/' + Mdate + '/' + Mdate + '_' + rlks + 'rlks.amp.par'
    HGTSIM0      = demDir + '/' + Mdate + '_' + rlks + 'rlks.rdc.dem'
    if not os.path.isfile(HGTSIM0):
        call_str = 'generate_rdc_dem.py ' + projectName
        os.system(call_str)
   
    Mslc = slcDir  + '/' + Sdate + '/' + Mdate + '.slc'
    MslcPar = slcDir  + '/' + Sdate + '/' + Mdate + '.slc.par'
    Mamp = slcDir  + '/' + Sdate + '/' + Mdate + '_' + rlks + 'rlks.amp'
    MampPar = slcDir  + '/' + Sdate + '/' + Mdate + '_' + rlks + 'rlks.amp.par'
    HGTSIM  = slcDir  + '/' + Sdate + '/'  + Mdate + '_' + rlks + 'rlks.rdc.dem'
    
    ut.copy_file(HGTSIM0,HGTSIM)
    ut.copy_file(Mslc0,Mslc)
    ut.copy_file(MslcPar0,MslcPar)
    #ut.copy_file(Mamp0,Mamp)
    #ut.copy_file(MampPar0,MampPar)
    
#######################################################    
#   define process files #
    offStd = workDir + "/" + Sdate + '_offstd'
    lt0 = workDir + "/lt0" 
    lt1 = workDir + "/lt1"
    mli0 = workDir + "/mli0" 
    diff0 = workDir + "/diff0" 
    offs0 = workDir + "/offs0"
    snr0 = workDir + "/snr0"
    offsets0 = workDir + "/offsets0"
    coffs0 = workDir + "/coffs0"
    coffsets0 = workDir + "/coffsets0"
    off = workDir + "/off"
    offs = workDir + "/offs"
    snr = workDir + "/snr"
    offsets = workDir + "/offsets"
    coffs = workDir + "/coffs"
    coffsets = workDir + "/coffsets"
##############################################

    if not os.path.isfile(MampPar):    
        call_str = 'multi_look ' + Mslc + ' ' + MslcPar + ' ' + Mamp + ' ' + MampPar + ' ' + rlks + ' ' + azlks
        os.system(call_str)
    if not os.path.isfile(SampPar):
        call_str = 'multi_look ' + Sslc + ' ' + SslcPar + ' ' + Samp + ' ' + SampPar + ' ' + rlks + ' ' + azlks
        os.system(call_str)    

    call_str = "rdc_trans " + MampPar + " " + HGTSIM + " " + SampPar + " " + lt0
    os.system(call_str)

    width_Mamp = ut.read_gamma_par(MampPar, 'read', 'range_samples')
    width_Samp = ut.read_gamma_par(SampPar, 'read', 'range_samples')
    line_Samp = ut.read_gamma_par(SampPar, 'read', 'azimuth_lines')

    call_str = "geocode " + lt0 + " " + Mamp + " " + width_Mamp + " " + mli0 + " " + width_Samp + " " + line_Samp + " 2 0"
    os.system(call_str)

    call_str = "create_diff_par " + SampPar + " - " + diff0 + " 1 0"
    os.system(call_str)

    call_str = "init_offsetm " + mli0 + " " + Samp + " " + diff0 + " 1 1"
    os.system(call_str)

    call_str = "offset_pwrm " + mli0 + " " + Samp + " " + diff0 + " " + offs0 + " " + snr0 + " 256 256 " + offsets0 + " 2 32 32"
    os.system(call_str)
  
    call_str = "offset_fitm " + offs0 + " " + snr0 + " " + diff0 + " " + coffs0 + " " + coffsets0 + " - 4"
    os.system(call_str)

    call_str = "gc_map_fine " + lt0 + " " + width_Mamp + " " + diff0 + " " + lt1
    os.system(call_str)
    
    
    call_str = "SLC_interp_lt " + Sslc + " " + MslcPar + " " + SslcPar + " " + lt1 + " " + MampPar + " " + SampPar + " - " + Srslc0 + " " + SrslcPar0
    os.system(call_str)


# further refinement processing for resampled SLC

    call_str = "create_offset " + MslcPar + " " + SrslcPar0 + " " + off + " 1 - - 0"
    os.system(call_str)

    #call_str = "offset_pwr " + MslcImg + " " + Srslc0Img + " " + MslcPar + " " + Srslc0Par + " " + off + " " + offs + " " + snr + " 128 128 " + offsets + " 2 32 64"
    #os.system(call_str)

    #call_str = "offset_fit "  + offs + " " + snr + " " + off + " " + coffs + " " + coffsets + " - 3" 
    #os.system(call_str)
    
    call_str = "offset_pwr " + Mslc + " " + Srslc0 + " " + MslcPar + " " + SrslcPar0 + " " + off + " " + offs + " " + snr + " " + templateDict['rwin4cor'] + " " + templateDict['azwin4cor'] + " " + offsets + " 2 " + templateDict['rsample4cor'] + " " + templateDict['azsample4cor']
    os.system(call_str)

    call_str = "offset_fit "  + offs + " " + snr + " " + off + " " + coffs + " " + coffsets + " - 3" 
    os.system(call_str)
    
    rfwin4cor = str(int(1/2*int(templateDict['rwin4cor'])))
    azfwin4cor = str(int(1/2*int(templateDict['azwin4cor'])))
    
    rfsample4cor = str(2*int(templateDict['rsample4cor']))
    azfsample4cor = str(2*int(templateDict['azsample4cor']))
    
    call_str = "offset_pwr " + Mslc + " " + Srslc0 + " " + MslcPar + " " + SrslcPar0 + " " + off + " " + offs + " " + snr + " " + rfwin4cor + " " + azfwin4cor + " " + offsets + " 2 " + rfsample4cor + " " + azfsample4cor
    os.system(call_str)
    
    call_str = "offset_fit "  + offs + " " + snr + " " + off + " " + coffs + " " + coffsets + " - 3 >" + offStd 
    os.system(call_str)
    
############################################     Resampling     ############################################    

    call_str = "SLC_interp_lt " + Sslc + " " + MslcPar + " " + SslcPar + " " + lt1 + " " + MampPar + " " + SampPar + " " + off + " " + Srslc + " " + SrslcPar
    os.system(call_str)

    call_str = 'multi_look ' + Srslc + ' ' + SrslcPar + ' ' + Sramp + ' ' + SrampPar + ' ' + rlks + ' ' + azlks
    os.system(call_str)

    nWidth = ut.read_gamma_par(SrampPar, 'read', 'range_samples')
    call_str = 'raspwr ' + Sramp + ' ' + nWidth 
    os.system(call_str)

    if os.path.isfile(mli0): os.remove(mli0)
    if os.path.isfile(lt0): os.remove(lt0)
    if os.path.isfile(lt1): os.remove(lt1)
    if os.path.isfile(diff0): os.remove(diff0)
    if os.path.isfile(offs0): os.remove(offs0)
    if os.path.isfile(snr0): os.remove(snr0)
    if os.path.isfile(offsets0): os.remove(offsets0)
    if os.path.isfile(coffs0): os.remove(coffs0)
    if os.path.isfile(coffsets0): os.remove(coffsets0)
    if os.path.isfile(off): os.remove(off)
    if os.path.isfile(offs): os.remove(offs)
    if os.path.isfile(snr): os.remove(snr)
    if os.path.isfile(offsets): os.remove(offsets)
    if os.path.isfile(coffs): os.remove(coffs)
    if os.path.isfile(coffsets): os.remove(coffsets)
    if os.path.isfile(Srslc0): os.remove(Srslc0)
    if os.path.isfile(SrslcPar0): os.remove(SrslcPar0)
    
    if os.path.isfile(Mslc): os.remove(Mslc)
    if os.path.isfile(MslcPar): os.remove(MslcPar)
    if os.path.isfile(Mamp): os.remove(Mamp)
    if os.path.isfile(HGTSIM): os.remove(HGTSIM)
    if os.path.isfile(MampPar): os.remove(MampPar)    

    print("Coregistration with DEM is done!")
 
    sys.exit(1)

if __name__ == '__main__':
    main(sys.argv[:])
