#! /usr/bin/env python
#################################################################
###  This program is part of PyINT  v2.1                      ### 
###  Copy Right (c): 2017-2022, Yunmeng Cao                   ###  
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
       Pixel offset tracking for co-registered Images. TOPs should be deramped in advance.
   
'''

EXAMPLE = '''
    Usage: 
            pot_gamma_subset.py projectName Mdate Sdate subset
            pot_gamma_subset.py PacayaT163TsxHhA 20150102 20150601 0102
-------------------------------------------------------------------  
'''


def cmdLineParse():
    parser = argparse.ArgumentParser(description='Pixel offset tracking based Azimuth/Range dispalcement estimation.',\
                                     formatter_class=argparse.RawTextHelpFormatter,\
                                     epilog=INTRODUCTION+'\n'+EXAMPLE)

    parser.add_argument('projectName',help='projectName for processing.')
    parser.add_argument('Mdate',help='Master date.')
    parser.add_argument('Sdate',help='Slave date.')
    parser.add_argument('Subset',help='Subset name, e.g., 0102')
    
    
    inps = parser.parse_args()
    return inps


def main(argv):
    
    start_time = time.time()
    inps = cmdLineParse() 
    Mdate = inps.Mdate
    Sdate = inps.Sdate
    subset = inps.Subset
    projectName = inps.projectName
    scratchDir = os.getenv('SCRATCHDIR')
    templateDir = os.getenv('TEMPLATEDIR')
    templateFile = templateDir + "/" + projectName + ".template"
    templateDict=ut.update_template(templateFile)
    rlks = templateDict['range_looks']
    azlks = templateDict['azimuth_looks']
    masterDate = templateDict['masterDate']
    
    if 'POT_rwin' in templateDict:
        POT_rwin = templateDict['POT_rwin']
    else:
        POT_rwin = '160'
    print('POT range window sise: ' + POT_rwin)
    
    if 'POT_awin' in templateDict:
        POT_awin = templateDict['POT_awin']
    else:
        POT_awin = '160'
    print('POT azimuth window sise: ' + POT_awin)
    
    if 'POT_astep' in templateDict:
        POT_astep = templateDict['POT_astep']
    else:
        POT_astep = azlks
    
    if 'POT_rstep' in templateDict:
        POT_rstep = templateDict['POT_rstep']
    else:
        POT_rstep = rlks
        
    print('POT range steps: ' + POT_rstep)
    print('POT azimuth steps: ' + POT_astep)
    
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
    Mamp     = rslcDir + '/' + Mdate + '/' + Mdate  + '_' + subset + '_' + rlks + 'rlks.amp'
    MampPar  = rslcDir + '/' + Mdate + '/' + Mdate  + '_' + subset + '_' + rlks + 'rlks.amp.par'
    Samp     = rslcDir + '/' + Sdate + '/' + Sdate  + '_' + subset + '_' + rlks + 'rlks.amp'
    SampPar  = rslcDir + '/' + Sdate + '/' + Sdate  + '_' + subset + '_' + rlks + 'rlks.amp.par'
    
    Mrslc    = rslcDir  + '/' + Mdate + '/' + Mdate + '_' + subset + '.rslc'
    MrslcPar = rslcDir  + '/' + Mdate + '/' + Mdate + '_' + subset + '.rslc.par'
    Srslc    = rslcDir  + '/' + Sdate + '/' + Sdate + '_' + subset + '.rslc'
    SrslcPar = rslcDir  + '/' + Sdate + '/' + Sdate + '_' + subset + '.rslc.par'
    
    #HGT      = demDir + '/' + masterDate + '_' + rlks + 'rlks.rdc.dem'
    #MasterPar = rslcDir  + '/' + masterDate + '/' + masterDate + '.rslc.par'
    
    ################# copy file for parallel processing ##########################
    #Mamp     =   workDir + '/' + Mdate + '_' + rlks + 'rlks.amp'
    #MampPar  =   workDir + '/' + Mdate + '_' + rlks + 'rlks.amp.par'
    #Samp     =   workDir + '/' + Sdate + '_' + rlks + 'rlks.amp'
    #SampPar  =   workDir + '/' + Sdate + '_' + rlks + 'rlks.amp.par'
    
    #if not templateDict['diff_all_parallel'] == '1':   
        
    #    Mrslc    =   workDir + '/' + Mdate + '.rslc'
    #    MrslcPar =   workDir + '/' + Mdate + '.rslc.par'
    #    Srslc    =   workDir + '/' + Sdate + '.rslc'
    #    SrslcPar =   workDir + '/' + Sdate + '.rslc.par'   
    #    ut.copy_file(Mrslc0,Mrslc)
    #    ut.copy_file(MrslcPar0,MrslcPar)
    #    ut.copy_file(Srslc0,Srslc)
    #    ut.copy_file(SrslcPar0,SrslcPar)   
        
    #else:       
        
    #    Mrslc    =   Mrslc0
    #    MrslcPar =   MrslcPar0
    #    Srslc    =   Srslc0
    #    SrslcPar =   SrslcPar0
    #    HGT = HGT0
    #    MasterPar = MasterPar0
    
    #ut.copy_file(Mamp0,Mamp)
    #ut.copy_file(MampPar0,MampPar)
    #ut.copy_file(Samp0,Samp)
    #ut.copy_file(SampPar0,SampPar)
    
    #ut.copy_file(HGT0,HGT)
    #ut.copy_file(MasterPar0,MasterPar)
    
    ############################################################################    
        
    OFF = workDir + '/' +  Pair  + '_' + subset + '_' + rlks + 'rlks_pot.off'  
    OFFS = workDir + '/' +  Pair  + '_' + subset + '_' + rlks + 'rlks_pot.offs' 
    CCP = workDir + '/' +  Pair  + '_' + subset + '_' + rlks + 'rlks_pot.ccp' 
    COFFS = workDir + '/' +  Pair  + '_' + subset + '_' + rlks + 'rlks_pot.coffs'
    COFFS_FILT = workDir + '/' +  Pair  + '_' + subset + '_' + rlks + 'rlks_pot_filt.coffs'
    POTA = workDir + '/' +  Pair  + '_' + subset + '_' + rlks + 'rlks_pot.az'
    POTR = workDir + '/' +  Pair  + '_' + subset + '_' + rlks + 'rlks_pot.rg'
    
    call_str = 'create_offset '+ MrslcPar + ' ' + SrslcPar + ' ' + OFF + ' 1 ' + rlks + ' ' + azlks +  ' 0'
    os.system(call_str)
    
    call_str = 'offset_pwr_tracking ' + Mrslc + ' ' + Srslc + ' ' + MrslcPar + ' ' + SrslcPar + ' ' + OFF + ' ' + OFFS + ' ' + CCP + ' ' + POT_rwin + ' ' + POT_awin + ' - 2 0.05 ' + POT_rstep + ' ' + POT_astep + ' - - - - - - '
    os.system(call_str)
    
    call_str = 'offset_tracking ' + OFFS + ' ' + CCP + ' ' + MrslcPar + ' ' + OFF + ' ' + COFFS + ' - 1 - 1'
    os.system(call_str)
    
    nWidth = ut.read_gamma_par(OFF, 'read', 'interferogram_width')
    
    #call_str = 'adf ' + COFFS + ' ' + COFFS_FILT + ' ' + CCP + ' ' + nWidth
    #os.system(call_str)
    
    call_str = 'cpx_to_real ' + COFFS + ' ' + POTR + ' ' + nWidth + ' 0 '
    os.system(call_str)
    
    call_str = 'cpx_to_real ' + COFFS + ' ' + POTA + ' '  + nWidth + ' 1 '
    os.system(call_str)
    
    call_str = 'rasdt_pwr ' + POTR + ' ' + Mamp + ' ' + nWidth + ' - - - - - - - BuYlRd.cm'
    os.system(call_str)
    
    call_str = 'rasdt_pwr ' + POTA + ' ' + Mamp + ' ' + nWidth + ' - - - - - - - BuYlRd.cm'
    os.system(call_str)
    
    print("Pixel offset tracking is Done!")
    ut.print_process_time(start_time, time.time())
    #sys.exit(1)

if __name__ == '__main__':
    main(sys.argv[:])
