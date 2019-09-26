#! /usr/bin/env python
#################################################################
###  This program is part of PyINT  v2.1                      ###
###  Purpose: loading PyINT products for mintPy               ###
###  Copy Right (c): 2019, Yunmeng Cao                        ###  
###  Author  : Yunmeng Cao                                    ###                                                          
###  Contact : ymcmrs@gmail.com                               ###  
#################################################################

import numpy as np
import os
import sys  
import subprocess
import time
import argparse
import glob

from pyint import _utils as ut

def write_template(str0,templateFile):
    with open(templateFile, 'a') as f:
        f.write(str0 + '\n')
    return

def cmdLineParse():
    parser = argparse.ArgumentParser(description='Loading pyint products for mintPy time-series analysis.',\
                                     formatter_class=argparse.RawTextHelpFormatter,\
                                     epilog=INTRODUCTION+'\n'+EXAMPLE)

    parser.add_argument('projectName', help='name of the project.')  
    #parser.add_argument('--data-type', dest='dataType', type=str, default='big_endian',choices={'big_endian', 'little_endian'},help='data type, big endian or little endian. [default: big_endian]')
    inps = parser.parse_args()

    return inps


INTRODUCTION = '''
-----------------------------------------------------------------
   Loading pyint products for mintPy time-series analysis.
   
'''

EXAMPLE = """Usage:
  
        load_mintpy.py projectName
-----------------------------------------------------------------
"""

def main(argv):
    
    inps = cmdLineParse()
    projectName = inps.projectName
    scratchDir = os.getenv('SCRATCHDIR')
    projectDir = scratchDir + '/' + projectName 
    demDir    = scratchDir + '/' + projectName  + '/DEM'
    rslcDir   = scratchDir + '/' + projectName + '/RSLC' 
     
    ifgDir = projectDir + '/ifgrams'
    unwFile = projectDir + '/ifgrams/*/2*rlks.diff_filt.unw'  # considering geocode unw file
    corFile = projectDir + '/ifgrams/*/2*rlks.diff_filt.cor'
    #print(unwFile)
    templateDir = os.getenv('TEMPLATEDIR')
    templateFile = templateDir + "/" + projectName + ".template"
    templateDict=ut.update_template(templateFile)
    
    rlks = templateDict['range_looks']
    azlks = templateDict['azimuth_looks']
    masterDate =  templateDict['masterDate']
    MampPar = rslcDir + '/' + masterDate + '/' + masterDate + '_' + rlks + 'rlks.amp.par'
    date_list = ut.get_project_slcList(projectName)
    date_list = sorted(date_list)
    slc_par_list = [rslcDir + '/' + date0 + '/' + date0 + '.rlsc.par' for date0 in date_list ]
    ifgdir_list = glob.glob(ifgDir + '/*')
    for k0 in ifgdir_list:
        pair0 = os.path.basename(k0)
        m0 = pair0.split('-')[0]
        s0 = pair0.split('-')[1]
        
        workDir = k0
        mamppar0 = rslcDir + '/' + m0 + '/' + m0 + '_' + rlks + 'rlks.amp.par'
        samppar0 = rslcDir + '/' + s0 + '/' + s0 + '_' + rlks + 'rlks.amp.par'        
        mrslcpar0 = rslcDir + '/' + m0 + '/' + m0 + '.rslc.par'
        srslcpar0 = rslcDir + '/' + s0 + '/' + s0 + '.rslc.par'
        
        mamppar = workDir + '/' + m0 + '_' + rlks + 'rlks.amp.par'
        samppar = workDir + '/' + s0 + '_' + rlks + 'rlks.amp.par'        
        mrslcpar = workDir + '/' + m0 + '.rslc.par'
        srslcpar = workDir + '/' + s0 + '.rslc.par'
        
        ut.copy_file(mamppar0, mamppar)
        ut.copy_file(samppar0, samppar)
        ut.copy_file(mrslcpar0,mrslcpar)
        ut.copy_file(srslcpar0,srslcpar)
     
    #unw_list = glob.glob(ifgDir + '/*/*rlks.diff_filt.unw')
    #cor_list = glob.glob(ifgDir + '/*/*rlks.diff_filt.cor')
    
    dem_geo  = glob.glob(demDir + '/*rlks.utm.dem')[0]
    geo_par  = glob.glob(demDir + '/*rlks.utm.dem.par')[0]  
    
    dem_rdc  = glob.glob(demDir + '/*_' + rlks + 'rlks.rdc.dem')[0]
    rdc_par  = glob.glob(demDir + '/*_' + rlks + 'rlks.diff_par')[0]       # diff_par
    lt       = glob.glob(demDir + '/*_' + rlks + 'rlks.UTM_TO_RDC')[0] 
    
    strPro = 'mintpy.load.processor      = gamma'
    strUNW = "mintpy.load.unwFile        = " + unwFile
    strCOR = 'mintpy.load.corFile        = ' + corFile
    strCon = 'mintpy.load.connCompFile   = auto'
    strInt = 'mintpy.load.intFile        = auto'
    strIon = 'mintpy.load.ionoFile       = auto'
    
    strDem = 'mintpy.load.demFile        = ' + dem_rdc
    strDemGeo = 'mintpy.load.demFile        = ' + dem_geo
    strLtY = 'mintpy.load.lookupYFile    = ' + lt
    strLtX = 'mintpy.load.lookupXFile    = ' + lt
    strInc = 'mintpy.load.incAngleFile   = auto'
    strAza = 'mintpy.load.azAngleFile    = auto'
    strSha = 'mintpy.load.shadowMaskFile = auto'
    strWat = 'mintpy.load.waterMaskFile  = auto'
    strBrp = 'mintpy.load.bperpFile      = auto'
    
    templateFile0 =  projectDir + '/mintpy.template' 
    
    if 'mintpy.load.processor' not in templateDict: write_template(strPro,templateFile0)
    if 'mintpy.load.unwFile' not in templateDict: write_template(strUNW,templateFile0)
    if 'mintpy.load.corFile' not in templateDict: write_template(strCOR,templateFile0)
    if 'mintpy.load.connCompFile' not in templateDict: write_template(strCon,templateFile0)
    if 'mintpy.load.intFile' not in templateDict: write_template(strInt,templateFile0)
    if 'mintpy.load.ionoFile' not in templateDict: write_template(strIon,templateFile0)
        
    if 'mintpy.load.demFile' not in templateDict: write_template(strDem,templateFile0)
    if 'mintpy.load.lookupYFile' not in templateDict: write_template(strLtY,templateFile0)
    if 'mintpy.load.lookupXFile' not in templateDict: write_template(strLtX,templateFile0)
    if 'mintpy.load.incAngleFile' not in templateDict: write_template(strInc,templateFile0)
    if 'mintpy.load.azAngleFile' not in templateDict: write_template(strAza,templateFile0)
    if 'mintpy.load.shadowMaskFile' not in templateDict: write_template(strSha,templateFile0)
    if 'mintpy.load.waterMaskFile' not in templateDict: write_template(strWat,templateFile0)
    if 'mintpy.load.bperpFile' not in templateDict: write_template(strBrp,templateFile0)
    
    os.chdir(projectDir)
    call_str = 'load_data.py -t ' + templateFile0
    os.system(call_str)
    
    os.chdir(projectDir)
    write_template(strDemGeo,templateFile0)
    call_str = 'load_data.py -t ' + templateFile0
    os.system(call_str)
    
    sys.exit(1)
    
if __name__ == '__main__':
    main(sys.argv[:])    
    