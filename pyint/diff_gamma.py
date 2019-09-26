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
import getopt
import time
import glob
import argparse

from pyint import _utils as ut


INTRODUCTION = '''
-------------------------------------------------------------------  
       Generate differential interferogram image from SLC using GAMMA.
   
'''

EXAMPLE = '''
    Usage: 
            diff_gamma.py projectName Mdate Sdate
            diff_gamma.py PacayaT163TsxHhA 20150102 20150601
-------------------------------------------------------------------  
'''


def cmdLineParse():
    parser = argparse.ArgumentParser(description='Coregister all of the SLCs to the reference SAR image using GAMMA.',\
                                     formatter_class=argparse.RawTextHelpFormatter,\
                                     epilog=INTRODUCTION+'\n'+EXAMPLE)

    parser.add_argument('projectName',help='projectName for processing.')
    parser.add_argument('Mdate',help='Master date.')
    parser.add_argument('Sdate',help='Slave date.')
    
    inps = parser.parse_args()
    return inps


def main(argv):
    
    start_time = time.time()
    inps = cmdLineParse() 
    Mdate = inps.Mdate
    Sdate = inps.Sdate
    
    projectName = inps.projectName
    scratchDir = os.getenv('SCRATCHDIR')
    templateDir = os.getenv('TEMPLATEDIR')
    templateFile = templateDir + "/" + projectName + ".template"
    templateDict=ut.update_template(templateFile)
    rlks = templateDict['range_looks']
    azlks = templateDict['azimuth_looks']
    masterDate = templateDict['masterDate']
    
    projectDir = scratchDir + '/' + projectName 
    demDir    = scratchDir + '/' + projectName  + '/DEM'
    
    slcDir    = scratchDir + '/' + projectName + '/SLC'
    rslcDir   = scratchDir + '/' + projectName + '/RSLC' 
    ifgDir = projectDir + '/ifgrams'
    if not os.path.isdir(ifgDir): os.mkdir(ifgDir)
    
    Pair = Mdate + '-' + Sdate
    workDir = ifgDir + '/' + Pair
    if not os.path.isdir(workDir): os.mkdir(workDir)
    
    #######################################################################
    Mamp0     = rslcDir + '/' + Mdate + '/' + Mdate + '_' + rlks + 'rlks.amp'
    MampPar0  = rslcDir + '/' + Mdate + '/' + Mdate + '_' + rlks + 'rlks.amp.par'
    Samp0     = rslcDir + '/' + Sdate + '/' + Sdate + '_' + rlks + 'rlks.amp'
    SampPar0  = rslcDir + '/' + Sdate + '/' + Sdate + '_' + rlks + 'rlks.amp.par'
    
    Mrslc0    = rslcDir  + '/' + Mdate + '/' + Mdate + '.rslc'
    MrslcPar0 = rslcDir  + '/' + Mdate + '/' + Mdate + '.rslc.par'
    Srslc0    = rslcDir  + '/' + Sdate + '/' + Sdate + '.rslc'
    SrslcPar0 = rslcDir  + '/' + Sdate + '/' + Sdate + '.rslc.par'
    
    HGT0      = demDir + '/' + masterDate + '_' + rlks + 'rlks.rdc.dem'
    
    MasterPar0 = rslcDir  + '/' + masterDate + '/' + masterDate + '.rslc.par'
    
    ################# copy file for parallel processing ##########################
    Mamp     =   workDir + '/' + Mdate + '_' + rlks + 'rlks.amp'
    MampPar  =   workDir + '/' + Mdate + '_' + rlks + 'rlks.amp.par'
    Samp     =   workDir + '/' + Sdate + '_' + rlks + 'rlks.amp'
    SampPar  =   workDir + '/' + Sdate + '_' + rlks + 'rlks.amp.par'
    
    Mrslc    =   workDir + '/' + Mdate + '.rslc'
    MrslcPar =   workDir + '/' + Mdate + '.rslc.par'
    Srslc    =   workDir + '/' + Sdate + '.rslc'
    SrslcPar =   workDir + '/' + Sdate + '.rslc.par'
    
    HGT      =   workDir + '/' + masterDate + '_' + rlks + 'rlks.rdc.dem'
    MasterPar = workDir + '/' + masterDate + '.rslc.par'
    
    ut.copy_file(Mamp0,Mamp)
    ut.copy_file(MampPar0,MampPar)
    ut.copy_file(Samp0,Samp)
    ut.copy_file(SampPar0,SampPar)
    
    ut.copy_file(Mrslc0,Mrslc)
    ut.copy_file(MrslcPar0,MrslcPar)
    ut.copy_file(Srslc0,Srslc)
    ut.copy_file(SrslcPar0,SrslcPar)
    
    ut.copy_file(HGT0,HGT)
    ut.copy_file(MasterPar0,MasterPar)
    
    ############################################################################    
        
    OFF = workDir + '/' +  Pair +'_' + rlks + 'rlks.off'   
    call_str = 'create_offset '+ MrslcPar + ' ' + SrslcPar + ' ' + OFF + ' 1 ' + rlks + ' ' + azlks +  ' 0'
    os.system(call_str)
   
    SIM_UNW = workDir + '/' +  Pair + '.sim_unw'
    call_str = 'phase_sim_orb ' + MrslcPar + ' ' + SrslcPar + ' ' + OFF + ' ' + HGT + ' ' + SIM_UNW + ' ' + MasterPar + ' - - 1 1' 
    os.system(call_str)
    
    DIFF_IFG = workDir + '/' +  Pair + '_' + rlks + 'rlks.diff'
    call_str = 'SLC_diff_intf ' + Mrslc + ' ' + Srslc + ' ' + MrslcPar + ' ' + SrslcPar + ' ' + OFF + ' ' + SIM_UNW + ' ' + DIFF_IFG + ' ' + rlks + ' ' + azlks + ' ' + templateDict['Igram_Spsflg'] + ' ' + templateDict['Igram_Azfflg'] + ' - 1 1'
    os.system(call_str)
    
    ##### filtering process & coherence estimation ###########
    DIFFFILT = workDir + '/' +  Pair + '_' + rlks + 'rlks.diff_filt'
    COHFILT = workDir + '/' +  Pair + '_' + rlks + 'rlks.diff_filt.cor'
    
    nWIDTH = ut.read_gamma_par(OFF, 'read', 'interferogram_width')
    call_str = 'adf ' + DIFF_IFG + ' ' + DIFFFILT + ' ' + COHFILT + ' ' + nWIDTH +  ' ' + templateDict['adf_alpha'] + ' - ' + templateDict['Igram_Cor_Win']
    os.system(call_str)
    
    ################# coherence estimation #####################
    call_str = 'cc_wave ' + DIFFFILT + ' ' + Mamp + ' ' + Samp + ' ' + COHFILT + ' ' + nWIDTH + ' ' + templateDict['Igram_Cor_rwin'] + ' ' + templateDict['Igram_Cor_awin']
    os.system(call_str)
    
    
    ################ save images #####################
    call_str = 'rasmph_pwr ' +  DIFFFILT + ' ' + Mamp + ' ' + nWIDTH + ' - - - - - - - - - ' + COHFILT + ' - 0.1'
    os.system(call_str)
    
    call_str = 'rasmph_pwr ' +  DIFF_IFG + ' ' + Mamp + ' ' + nWIDTH + ' - - - - - - - - - ' + COHFILT + ' - 0.1'
    os.system(call_str)
    
    call_str = 'rascc ' + COHFILT + ' ' + Mamp + ' ' + nWIDTH
    os.system(call_str)
    
    os.remove(Mamp)
    #os.remove(MampPar)
    os.remove(Samp)
    #os.remove(SampPar)
    
    os.remove(Mrslc)
    os.remove(MrslcPar)
    os.remove(Srslc)
    os.remove(SrslcPar)
    
    os.remove(HGT)
    os.remove(MasterPar)
    
    print("Subtraction of topography and flattening phase is done!")
    ut.print_process_time(start_time, time.time())
    sys.exit(1)

if __name__ == '__main__':
    main(sys.argv[:])
