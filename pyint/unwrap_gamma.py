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


INTRODUCTION = '''
-------------------------------------------------------------------  
       Unwrap differential interferogram using GAMMA.
       [Only support mcf, not implement branch_cut yet]
   
'''

EXAMPLE = '''
    Usage: 
            unwrap_gamma.py projectName Mdate Sdate
            unwrap_gamma.py PacayaT163TsxHhA 20150102 20150601
-------------------------------------------------------------------  
'''

def cmdLineParse():
    parser = argparse.ArgumentParser(description='Unwrap differential interferogram using GAMMA-mcf method.',\
                                     formatter_class=argparse.RawTextHelpFormatter,\
                                     epilog=INTRODUCTION+'\n'+EXAMPLE)

    parser.add_argument('projectName',help='projectName for processing.')
    parser.add_argument('Mdate',help='Master date.')
    parser.add_argument('Sdate',help='Slave date.')
    
    inps = parser.parse_args()
    return inps


def main(argv):
    
    inps = cmdLineParse() 
    Mdate = inps.Mdate
    Sdate = inps.Sdate
    
    projectName = inps.projectName
    Sdate = inps.Sdate
    Mdate = inps.Mdate
    
    scratchDir = os.getenv('SCRATCHDIR')
    templateDir = os.getenv('TEMPLATEDIR')
    templateFile = templateDir + "/" + projectName + ".template"
    templateDict=ut.update_template(templateFile)
    rlks = templateDict['range_looks']
    azlks = templateDict['azimuth_looks']
    
    processDir = scratchDir + '/' + projectName + "/PROCESS"
    slcDir     = scratchDir + '/' + projectName + "/SLC"
    rslcDir    = scratchDir + '/' + projectName + '/RSLC'
    ifgDir     = scratchDir + '/' + projectName + '/ifgrams'
    
    Pair = Mdate + '-' + Sdate
    workDir = ifgDir + '/' + Pair
    
    ################ copy file for parallel processing ###############
    Mamp0    = rslcDir + '/' + Mdate + '/' + Mdate + '_' + rlks + 'rlks.amp'
    MampPar0 = rslcDir + '/' + Mdate + '/' + Mdate + '_' + rlks + 'rlks.amp.par'
    Samp0    = rslcDir + '/' + Sdate + '/' + Sdate + '_' + rlks + 'rlks.amp'
    SampPar0 = rslcDir + '/' + Sdate + '/' + Sdate + '_' + rlks + 'rlks.amp.par'
    
    
    Mamp    = workDir + '/' + Mdate + '_' + rlks + 'rlks.amp'
    MampPar = workDir + '/' + Mdate + '_' + rlks + 'rlks.amp.par'
    Samp    = workDir + '/' + Sdate + '_' + rlks + 'rlks.amp'
    SampPar = workDir + '/' + Sdate + '_' + rlks + 'rlks.amp.par'
    
    ut.copy_file(Mamp0,Mamp)
    ut.copy_file(Samp0,Samp)
    ut.copy_file(MampPar0,MampPar)
    ut.copy_file(SampPar0,SampPar)
    ###############################################################  

    nWidth = ut.read_gamma_par(MampPar, 'read', 'range_samples')
    nLine =  ut.read_gamma_par(MampPar, 'read', 'azimuth_lines')
    
    CORMASK = workDir + '/' + Pair + '_' +rlks + 'rlks.diff_filt.cor'
    WRAPlks = workDir + '/' + Pair + '_' +rlks + 'rlks.diff_filt'
    UNWlks = workDir + '/' + Pair + '_' +rlks + 'rlks.diff_filt.unw'
    
    CORMASKbmp = CORMASK.replace('.diff_filt.cor','.diff_filt.cor_mask.bmp')
    
    if os.path.isfile(CORMASKbmp):
        os.remove(CORMASKbmp)
            
    call_str = 'rascc_mask ' + CORMASK + ' ' + Mamp + ' ' + nWidth + ' 1 1 0 1 1 ' + templateDict['unwrapThreshold'] + ' 0.0 0.1 0.9 1. .35 1 ' + CORMASKbmp   # based on int coherence
    os.system(call_str)

    call_str = 'mcf ' + WRAPlks + ' ' + CORMASK + ' ' + CORMASKbmp + ' ' + UNWlks + ' ' + nWidth + ' ' + templateDict['mcf_triangular'] + ' - - - - ' + templateDict['unwrap_patr'] + ' ' + templateDict['unwrap_pataz']
    os.system(call_str)

    call_str = 'rasrmg ' + UNWlks + ' ' + Mamp + ' ' + nWidth + ' - - - - - - - - - - ' 
    os.system(call_str)

    os.remove(Mamp)
    os.remove(Samp)
    #os.remove(MampPar)
    #os.remove(SampPar)
    print("Uwrapping interferometric phase is done!")
    sys.exit(1)

if __name__ == '__main__':
    main(sys.argv[:])
