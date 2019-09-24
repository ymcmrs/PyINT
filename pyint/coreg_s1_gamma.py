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
    parser.add_argument('sdate', help='date of the slave S1 image. [mater date is read from template]')
    inps = parser.parse_args()
    return inps


INTRODUCTION = '''
-------------------------------------------------------------------  
   Coregister TOPS S1-SLC to a reference S1-SLC using GAMMA.
   [The reference date or master date will be read from the template file.]
'''

EXAMPLE = """Usage:
  
  coreg_s1_gamma.py projectName Sdate
  
  coreg_s1_gamma.py PacayaT163TsxHhA 20150102
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
    
    SLC1_INF_tab = MslcDir + '/' + Mdate + '_SLC_Tab'
    SLC2_INF_tab = SslcDir + '/' + Sdate + '_SLC_Tab'
    RSLC_tab = SslcDir + '/' + Sdate + '_RSLC_tab'

    HGTSIM      = demDir + '/' + Mdate + '_' + rlks + 'rlks.rdc.dem'
    if not os.path.isfile(HGTSIM):
        call_str = 'generate_rdc_dem.py ' + projectName
        os.system(call_str)
    
    #RSLC_tab = workDir + '/' + Sdate + '_RSLC_tab'
    #if os.path.isfile(RSLC_tab):
    #    os.remove(RSLC_tab)
    
    #BURST = SslcDir + '/' + Sdate + '_Burst_Tab'
    #AA = np.loadtxt(BURST)
    #if EW==SW:
    #    AA = AA.reshape([1,2])
    #
    #for kk in range(int(EW)-int(SW)+1):
    #    ii = int(int(kk) + 1)
    #    SB2=AA[ii-1,0]
    #    EB2=AA[ii-1,1]
    #    call_str = 'echo ' + workDir + '/'+ Sdate+ '_'+ str(int(SB2)) + str(int(EB2)) +'.IW'+str(int(SW)+kk)+ '.rslc' + ' ' + workDir + '/' + Sdate + '_'+ str(int(SB2)) + str(int(EB2)) +'.IW'+ str(int(SW)+kk)+ '.rslc.par' + ' ' + workDir + '/'+ Sdate+'_'+ str(int(SB2)) + str(int(EB2)) + '.IW'+str(int(SW)+kk)+ '.rslc.TOPS_par >>' + RSLC_tab
    #   os.system(call_str)
      
    os.chdir(workDir)
    
    if not Mdate ==Sdate:
        call_str = 'S1_coreg_TOPS ' + SLC1_INF_tab + ' ' + Mdate + ' ' + SLC2_INF_tab + ' ' + Sdate + ' ' + RSLC_tab + ' ' + HGTSIM + ' ' + rlks + ' ' + azlks + ' - - 0.6 0.01 1.2 1'
        os.system(call_str)
        
        #### clean large file ####
        mslc = workDir + '/' + Mdate + '.slc'
        mrslc = workDir + '/' + Mdate + '.rslc'
        sslc = workDir + '/' + Sdate + '.slc'
        srslc = workDir + '/' + Sdate + '.rslc'
        srslcPar = workDir + '/' + Sdate + '.rslc.par'
        
        samp = workDir + '/' + Sdate + '_' + rlks + 'rlks.amp'
        samppar = workDir + '/' + Sdate + '_' + rlks + 'rlks.amp'
        
        call_str = 'multi_look ' + srslc + ' ' + srslcPar + ' ' + samp + ' ' + samppar + ' ' + rlks + ' ' + azlks
        os.system(call_str)
    
        if os.path.isfile(mslc):  os.remove(mslc)
        if os.path.isfile(mrslc): os.remove(mrslc)
        if os.path.isfile(sslc): os.remove(sslc)
        
    else:
        call_str = 'cp ' + Mslc + ' ' + workDir + '/' + Mdate + '.rslc'
        os.system(call_str)
        
        call_str = 'cp ' + Mslcpar + ' ' + workDir+ '/' + Mdate + '.rslc.par'
        os.system(call_str)
        
        call_str = 'cp ' + Mamp + ' ' + workDir+ '/' + Mdate + '_' + rlks + 'rlks.amp'
        os.system(call_str)
        
        call_str = 'cp ' + MampPar + ' ' + workDir+ '/' + Mdate + '_' + rlks + 'rlks.amp.par'
        os.system(call_str)
         
    print("Generating differential S1 interferogram is done !!")
    sys.exit(1)

if __name__ == '__main__':
    main(sys.argv[:])
