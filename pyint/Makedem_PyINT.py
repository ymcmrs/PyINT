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
    parser = argparse.ArgumentParser(description='Generate radar-coordinates based DEM.',\
                                     formatter_class=argparse.RawTextHelpFormatter,\
                                     epilog=INTRODUCTION+'\n'+EXAMPLE)

    parser.add_argument('projectName', help='Name of project.')
    parser.add_argument('-p', '--processor', dest='processor',choices = {'gamma','roi_pac'}, default = 'gamma', help='Interferometry processor.[default: gamma]') 
    # easy to extend to other porcessors, e.g., ISCE, SNAP
    
    inps = parser.parse_args()

    return inps


INTRODUCTION = '''
-------------------------------------------------------------------  

   Generate radar-coordinates based DEM.
   [Geo-coordinates DEM can be downloaded automatically if not provided.]
'''

EXAMPLE = """Usage:
  
  makedem_pyint.py projectName --processor gamma
  
  makedem_pyint.py PacayaT163TsxHhA 
  makedem_pyint.py PacayaT163TsxHhA --processor roi_pac
  makedem_pyint.py PacayaT163TsxHhA --processor gamma
  
------------------------------------------------------------------- 
"""
    
def main(argv):
    
    inps = cmdLineParse() 
    projectName = inps.projectName
    processor = inps.processor
    scratchDir = os.getenv('SCRATCHDIR')
    slcDir     = scratchDir + '/' + projectName + "/SLC"
    KK=os.listdir(slcDir)
    templateDir = os.getenv('TEMPLATEDIR')
    templateFile = templateDir + "/" + projectName + ".template"
    templateDict=ut.update_template(templateFile)
  
    masterDate = templateDict['masterDate']
    SLC_PAR = slcDir + '/' + masterDate + '/'+ masterDate + '.slc.par'
    
    demDir = os.getenv('DEMDIR') 
    demDir1 = demDir + '/' + projectName
    if not os.path.isdir(demDir1):
        os.mkdir(demDir1)
    
    os.chdir(demDir1)
    call_str= 'makedem.py ' + '-s ' + SLC_PAR + ' -p ' + processor + ' -o ' + projectName
    os.system(call_str)
    
    print('Generate DEM for project %s is done.' % projectName)
    sys.exit(1)
    
if __name__ == '__main__':
    main(sys.argv[:])    