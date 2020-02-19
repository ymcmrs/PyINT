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
    Samp = rslcDir  + '/' + Sdate + '/' + Sdate + '_' + rlks + 'rlks.amp'
    SampPar = rslcDir  + '/' + Sdate + '/' + Sdate + '_' + rlks + 'rlks.amp.par'
    Sampbmp = rslcDir  + '/' + Sdate + '/' + Sdate + '_' + rlks + 'rlks.amp.bmp'
    
    Mslc = slcDir  + '/' + Mdate + '/' + Mdate + '.slc'
    Mslcpar = slcDir  + '/' + Mdate + '/' + Mdate + '.slc.par'
    Mamp = slcDir  + '/' + Mdate + '/' + Mdate + '_' + rlks + 'rlks.amp'
    MampPar = slcDir  + '/' + Mdate + '/' + Mdate + '_' + rlks + 'rlks.amp.par'
    Mampbmp = slcDir  + '/' + Mdate + '/' + Mdate + '_' + rlks + 'rlks.amp.bmp'
    
    SLC1_INF_tab0 = MslcDir + '/' + Mdate + '_SLC_Tab'
    SLC2_INF_tab = SslcDir + '/' + Sdate + '_SLC_Tab'
    RSLC_tab = SslcDir + '/' + Sdate + '_RSLC_Tab'
    SLC1_INF_tab = SslcDir + '/' + Mdate + '_SLC_Tab_coreg'
    
    HGTSIM      = demDir + '/' + Mdate + '_' + rlks + 'rlks.rdc.dem'
    if not os.path.isfile(HGTSIM):
        call_str = 'generate_rdc_dem.py ' + projectName
        os.system(call_str)
    
    ############## copy master files into slave folder for parallel process ###########
    
    #if not templateDict['coreg_all_parallel'] == '1':
    #    Mslc = slcDir  + '/' + Sdate + '/' + Mdate + '.slc'
    #    Mslcpar = slcDir  + '/' + Sdate + '/' + Mdate + '.slc.par'
    #    Mamp = slcDir  + '/' + Sdate + '/' + Mdate + '_' + rlks + 'rlks.amp'
    #    MampPar = slcDir  + '/' + Sdate + '/' + Mdate + '_' + rlks + 'rlks.amp.par'
    #    HGTSIM      = slcDir  + '/' + Sdate + '/' + Mdate + '_' + rlks + 'rlks.rdc.dem'
        
    #else:
        
    #    Mslc = Mslc0
    #    Mslcpar = Mslcpar0
    #    Mamp = Mamp0
    #    MampPar = MampPar0
    #    HGTSIM  = HGTSIM0
        
        
    #Mslc = slcDir  + '/' + Sdate + '/' + Mdate + '.slc'
    #Mslcpar = slcDir  + '/' + Sdate + '/' + Mdate + '.slc.par'
    #Mamp = slcDir  + '/' + Sdate + '/' + Mdate + '_' + rlks + 'rlks.amp'
    #MampPar = slcDir  + '/' + Sdate + '/' + Mdate + '_' + rlks + 'rlks.amp.par'
    #HGTSIM      = slcDir  + '/' + Sdate + '/' + Mdate + '_' + rlks + 'rlks.rdc.dem'
    SLC1_INF_tab1 = SslcDir + '/' + Mdate + '_SLC_Tab'
    ut.copy_file(SLC1_INF_tab0,SLC1_INF_tab1) 
    ##############################################################################
    with open(SLC1_INF_tab1, "r") as f:
        lines = f.readlines()
    
    with open(SLC1_INF_tab, "w") as fw:
        lines_coreg = []
        for k0 in lines:
            k00 = k0.replace(MslcDir,SslcDir)
            lines_coreg.append(k00)
            fw.write(k00)
    
    S_IW = ut.read_txt2array(SLC1_INF_tab1)
    S_IW = S_IW.flatten()
    #M_IW = ut.read_txt2array(SLC1_INF_tab1)
    #M_IW = M_IW.flatten()TSLC = slc_dir + '/' + date + '.slc'
        #TSLCPar = slc_dir + '/' + date + '.slc.par'
    
        #
    #S_IW = ut.read_txt2array(SLC1_INF_tab)  
    #S_IW = S_IW.flatten()
        
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
    TEST = workDir + '/' + Sdate +'_' + rlks + 'rlks.amp.par'
    #TEST = workDir + '/' + Sdate +'.rslc.par'
    
    k0 = 0
    if os.path.isfile(TEST):
        if os.path.getsize(TEST) > 0:
            k0 = 1
    
    if k0==0:
        if not Mdate ==Sdate:
            call_str = 'S1_coreg_TOPS ' + SLC1_INF_tab1 + ' ' + Mdate + ' ' + SLC2_INF_tab + ' ' + Sdate + ' ' + RSLC_tab + ' ' + HGTSIM + ' ' + rlks + ' ' + azlks + ' - - 0.6 0.01 1.2 1'
            os.system(call_str)
        
            #### clean large file ####
            mslc = workDir + '/' + Mdate + '.slc'
            mrslc = workDir + '/' + Mdate + '.rslc'
            sslc = workDir + '/' + Sdate + '.slc'
            srslc = workDir + '/' + Sdate + '.rslc'
            srslcPar = workDir + '/' + Sdate + '.rslc.par'

            call_str = 'multi_look ' + srslc + ' ' + srslcPar + ' ' + Samp + ' ' + SampPar + ' ' + rlks + ' ' + azlks
            os.system(call_str)
            nWIDTH = ut.read_gamma_par(SampPar,'read', 'range_samples')
            if os.path.isfile(mslc):  os.remove(mslc)
            if os.path.isfile(mrslc): os.remove(mrslc)
            if os.path.isfile(sslc): os.remove(sslc)
        
            call_str = 'raspwr ' + Samp + ' ' + nWIDTH
            os.system(call_str)
        
            #call_str = 'rm *mli*'
            #os.system(call_str)
        
            #call_str = 'rm *IW*'
            #os.system(call_str)
        
            #call_str = 'rm *off*'
            #os.system(call_str)
        
            #call_str = 'rm *diff'
            #os.system(call_str)
        
            #call_str = 'rm *diff_par*'
            #os.system(call_str)
        
            #call_str = 'rm ' + Mdate + '.*'
            #os.system(call_str)
        
        else:
            
        #generate amp file for check image quality
            TSLC = rslcDir + '/' + Sdate + '/' + Sdate + '.rslc'
            TSLCPar = rslcDir + '/' + Sdate + '/' + Sdate + '.rslc.par'
    
            TMLI =  rslcDir + '/' + Sdate + '/' + Sdate + '_' + rlks + 'rlks.amp'
            TMLIPar = rslcDir + '/' + Sdate + '/' + Sdate +  '_' + rlks + 'rlks.amp.par'
    
            call_str = 'SLC_mosaic_S1_TOPS ' +  SLC2_INF_tab + ' ' + TSLC + ' ' + TSLCPar + ' ' + rlks + ' ' + azlks
            os.system(call_str)
   
            call_str = 'multi_look ' + TSLC + ' ' + TSLCPar + ' ' + TMLI + ' ' + TMLIPar + ' ' + rlks + ' ' + azlks
            os.system(call_str)
    
            nWidth = ut.read_gamma_par(TMLIPar, 'read','range_samples:')
            call_str = 'raspwr ' + TMLI + ' ' + nWidth + ' - - - - - - - '
            os.system(call_str)

        
    ################   clean redundant files #############
    
    #if not Mdate ==Sdate: 
        
    #    if not templateDict['diff_all_parallel'] == '1':              
    #        for i in range(len(S_IW)):
    #            if os.path.isfile(S_IW[i]):
    #                os.remove(S_IW[i])
    #        if os.path.isfile(Mslc): os.remove(Mslc)
    #        if os.path.isfile(Mslcpar): os.remove(Mslcpar)
    #        if os.path.isfile(Mamp): os.remove(Mamp)        
    #        if os.path.isfile(HGTSIM): os.remove(HGTSIM)
            
    print("Coregister TOP SLC image to the reference TOPS image is done !!")
    sys.exit(1)

if __name__ == '__main__':
    main(sys.argv[:])
