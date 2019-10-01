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
    parser = argparse.ArgumentParser(description='Coregister TOPS S1-SLC to a reference S1-SLC using GAMMA.',\
                                     formatter_class=argparse.RawTextHelpFormatter,\
                                     epilog=INTRODUCTION+'\n'+EXAMPLE)

    parser.add_argument('projectName', help='Name of project.')
    parser.add_argument('date', help='date of the slave S1 image. [mater date is read from template]')
    inps = parser.parse_args()
    return inps


INTRODUCTION = '''
-------------------------------------------------------------------  
   Generate multilook amplitude images for coregistered SLCs.
   
'''

EXAMPLE = """Usage:
  
  generate_multilook_amp.py projectName Date
  
  generate_multilook_amp.py PacayaT163TsxHhA 20150102
------------------------------------------------------------------- 
"""
    
def main(argv):
    
    inps = cmdLineParse() 
    projectName = inps.projectName
    Date = inps.date
    
    scratchDir = os.getenv('SCRATCHDIR')
    templateDir = os.getenv('TEMPLATEDIR')
    templateFile = templateDir + "/" + projectName + ".template"
    
    slcDir     = scratchDir + '/' + projectName + "/SLC"
    rslcDir     = scratchDir + '/' + projectName + "/RSLC"
    if not os.path.isdir(rslcDir): os.mkdir(rslcDir)
    #workDir    = processDir + '/' + igramDir   
    workDir = rslcDir + '/' + Date
    if not os.path.isdir(workDir): os.mkdir(workDir)
    
    templateDict=ut.update_template(templateFile)
    rlks = templateDict['range_looks']
    azlks = templateDict['azimuth_looks']
    Mdate = templateDict['masterDate']
    
    
    rslc = workDir + '/' + Date + '.rslc'
    rslcPar = workDir + '/' + Date + '.rslc.par'
    
    amp = workDir + '/' + Date + '_' + rlks + 'rlks.amp'
    ampPar = workDir + '/' + Date + '_' + rlks + 'rlks.amp.par'
    
    k0 = 0
    if os.path.isfile(ampPar):
        if os.path.getsize(ampPar) > 0:
            k0 =1
    
    if k0==1:
        call_str = 'multi_look ' + rslc + ' ' + rslcPar + ' ' + amp + ' ' + ampPar + ' ' + rlks + ' ' + azlks 
        os.system(call_str)
        
        nWIDTH = ut.read_gamma_par(ampPar,'read', 'range_samples')
        
        call_str = 'raspwr ' + amp + ' ' + nWIDTH
        os.system(call_str)
    
    print("Generate amplitude image for RSLC %s is done !!" % Date)
    sys.exit(1)

if __name__ == '__main__':
    main(sys.argv[:])
