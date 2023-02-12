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
       copy SLC/RSLC from large SLC/RSLC
   
'''

EXAMPLE = '''
    Usage: 
            slcCopy_gamma.py projectName Sdate rstart rwidth astart awidth outname
            slcCopy_gamma.py PacayaT163TsxHhA 20150601 100 345 200 500 20150601_subset
-------------------------------------------------------------------  
'''

def cmdLineParse():
    parser = argparse.ArgumentParser(description='Copy RSLC subset from a large SLC.',\
                                     formatter_class=argparse.RawTextHelpFormatter,\
                                     epilog=INTRODUCTION+'\n'+EXAMPLE)

    parser.add_argument('projectName',help='projectName for processing.')
    parser.add_argument('Date',help='Master date.')
    parser.add_argument('rstart',help='start point of range')
    parser.add_argument('rwidth',help='width of range direction')
    parser.add_argument('astart',help='start point of azimuth')
    parser.add_argument('awidth',help='width of azimith direction')
    parser.add_argument('name',help='output name. e.g., 20150101_subset, then .slc and .slc.par will be generated')
    
    inps = parser.parse_args()
    return inps


def main(argv):
    
    inps = cmdLineParse()     
    projectName = inps.projectName
    Date = inps.Date
    rstart = inps.rstart; rwidth = inps.rwidth; astart = inps.astart; awidth = inps.awidth; name = inps.name
    
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
    
    Dslc    = rslcDir + '/' + Date + '/' + Date + '.rslc'
    DslcPar = rslcDir + '/' + Date + '/' + Date + '.rslc.par'
    
    Oslc    = rslcDir + '/' + Date + '/' + name + '.rslc'
    OslcPar = rslcDir + '/' + Date + '/' + name + '.rslc.par'
    
    Oamp    = rslcDir + '/' + Date + '/' + name + '_' + rlks + 'rlks.amp'
    OampPar = rslcDir + '/' + Date + '/' + name + '_' + rlks + 'rlks.amp.par'
    
    
    
    call_str = 'SLC_copy ' + Dslc + ' ' + DslcPar + ' ' + Oslc + ' ' + OslcPar + ' - - ' + rstart + ' ' + rwidth + ' ' + astart + ' ' + awidth + ' - -'
    os.system(call_str)
    
    call_str = 'multi_look ' + Oslc + ' ' + OslcPar + ' ' + Oamp + ' ' + OampPar + ' ' + rlks + ' ' + azlks
    os.system(call_str)
    #os.remove(MampPar)
    #os.remove(SampPar)
    print(call_str)
    print("RSLC copy done.")
    #sys.exit(1)

if __name__ == '__main__':
    main(sys.argv[:])
