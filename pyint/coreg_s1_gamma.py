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
import glob

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
    deramp = templateDict['deramp']
    
    if 'boi' in templateDict:
        boi = templateDict['boi']
    else:
        boi = '0'
    
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
    
    #SLC1_INF_tab = MslcDir + '/' + Mdate + '_SLC_Tab'
    SLC2_INF_tab = SslcDir + '/' + Sdate + '_SLC_Tab'
    RSLC_tab = SslcDir + '/' + Sdate + '_RSLC_Tab'
    RSLC_tab2 = workDir + '/' + Sdate + '_RSLC_Tab'
    call_str = 'cp ' + RSLC_tab + ' ' + RSLC_tab2
    os.system(call_str)
    
    #SLC1_INF_tab = SslcDir + '/' + Mdate + '_SLC_Tab_coreg'
    
    HGTSIM      = demDir + '/' + Mdate + '_' + rlks + 'rlks.rdc.dem'
    if not os.path.isfile(HGTSIM):
        call_str = 'generate_rdc_dem.py ' + projectName
        os.system(call_str)
    
    srslc_fboi0 = workDir + '/' + Sdate + '_overlap.fwd.slc'; srslc_fboi = srslc_fboi0.replace('.slc','.rslc')
    srslc_fboi_par0 = workDir + '/' + Sdate + '_overlap.fwd.slc.par';  srslc_fboi_par = srslc_fboi_par0.replace('.slc','.rslc')
            
    srslc_bboi0 = workDir + '/' + Sdate + '_overlap.bwd.slc'; srslc_bboi = srslc_bboi0.replace('.slc','.rslc')
    srslc_bboi_par0 = workDir + '/' + Sdate + '_overlap.bwd.slc.par';  srslc_bboi_par = srslc_bboi_par0.replace('.slc','.rslc')
            
    samp_fboi = workDir + '/' + Sdate + '_overlap.fwd_' + rlks + 'rlks.amp'
    samp_fboi_par = workDir + '/' + Sdate + '_overlap.fwd_' + rlks + 'rlks.amp.par'
            
    samp_bboi = workDir + '/' + Sdate + '_overlap.bwd_' + rlks + 'rlks.amp'
    samp_bboi_par = workDir + '/' + Sdate + '_overlap.bwd_' + rlks + 'rlks.amp.par'  
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
    #SLC1_INF_tab1 = SslcDir + '/' + Mdate + '_SLC_Tab'
    #ut.copy_file(SLC1_INF_tab0,SLC1_INF_tab1) 
    ##############################################################################
    #with open(SLC1_INF_tab1, "r") as f:
    #    lines = f.readlines()
    
    #with open(SLC1_INF_tab, "w") as fw:
    #    lines_coreg = []
    #    for k0 in lines:
    #        k00 = k0.replace(MslcDir,SslcDir)
    #        lines_coreg.append(k00)
    #        fw.write(k00)
    
    #S_IW = ut.read_txt2array(SLC1_INF_tab1)
    #S_IW = S_IW.flatten()
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
    #TEST = workDir + '/' + Sdate +'_' + rlks + 'rlks.amp.par'
    TEST = workDir + '/' + Mdate + '_' + Sdate +'.diff.bmp'
    
    k0 = 0
    if os.path.isfile(TEST):
        if os.path.getsize(TEST) > 0:
            k0 = 1
    
    if k0==0:
        if not Mdate ==Sdate:
            
            call_str = 'cp -rf ' + MslcDir + ' ' + workDir
            os.system(call_str)
            
            MslcDir2 = workDir + '/' + Mdate
            
            SLC_list = glob.glob(MslcDir2 + '/*IW*.slc') 
            SLC_par_list = glob.glob(MslcDir2 + '/*IW*.slc.par') 
            TOP_par_list = glob.glob(MslcDir2 + '/*IW*.slc.TOPS_par') 
            
            SLC1_INF_tab = MslcDir2 + '/' + Mdate + '_SLC_Tab'
            
            if os.path.isfile(SLC1_INF_tab):
                os.remove(SLC1_INF_tab)
        
            SLC_list = sorted(SLC_list)
            SLC_par_list = sorted(SLC_par_list)
            TOP_par_list = sorted(TOP_par_list)
             
            for kk in range(len(SLC_list)):
                call_str = 'echo ' + SLC_list[kk] + ' ' + SLC_par_list[kk] + ' ' + TOP_par_list[kk] + ' >> ' + SLC1_INF_tab
                os.system(call_str)
            
            
            #call_str = 'S1_coreg_TOPS ' + SLC1_INF_tab + ' ' + Mdate + ' ' + SLC2_INF_tab + ' ' + Sdate + ' ' + RSLC_tab + ' ' + HGTSIM + ' ' + rlks + ' ' + azlks + ' - - 0.8 0.01 1.2 1'
  
            call_str = 'ScanSAR_coreg.py ' + SLC1_INF_tab + ' ' + Mdate + ' ' + SLC2_INF_tab + ' ' + Sdate + ' ' + RSLC_tab + ' ' + HGTSIM + ' ' + rlks + ' ' + azlks + ' --cc 0.8 --fraction 0.01 --ph_stdev 0.8 --num_ovr 0 --no_check '
            print(call_str)
            os.system(call_str)
        
            #### clean large file ####
            mslc = workDir + '/' + Mdate + '.slc'
            mrslc = workDir + '/' + Mdate + '.rslc'
            sslc = workDir + '/' + Sdate + '.slc'
            srslc = workDir + '/' + Sdate + '.rslc'
                        
            srslcPar = workDir + '/' + Sdate + '.rslc.par'
            
            if deramp=='1':
                call_str = 'S1_deramp_TOPS_slave ' + RSLC_tab2 + ' ' + Sdate + ' ' + SLC1_INF_tab + ' 10 2 1' 
                os.system(call_str)
                
                call_str = 'mv ' + srslc + '.deramp' + ' ' + srslc
                os.system(call_str)
 
                call_str = 'mv ' + srslc + '.deramp.par' + ' ' + srslcPar
                os.system(call_str)

            call_str = 'multi_look ' + srslc + ' ' + srslcPar + ' ' + Samp + ' ' + SampPar + ' ' + rlks + ' ' + azlks
            os.system(call_str)
            
            nWIDTH = ut.read_gamma_par(SampPar,'read', 'range_samples')
            
            if boi =='1':
                call_str = 'ScanSAR_burst_overlap ' + RSLC_tab2 + ' ' + Sdate+'_overlap' + ' ' + rlks + ' ' + azlks + ' - - ' + SLC1_INF_tab + ' - -'
                os.system(call_str)
                
                call_str = 'mv ' + srslc_fboi0 + ' ' + srslc_fboi; os.system(call_str)
                call_str = 'mv ' + srslc_fboi_par0 + ' ' + srslc_fboi_par; os.system(call_str)
                call_str = 'mv ' + srslc_bboi0 + ' ' + srslc_bboi; os.system(call_str)
                call_str = 'mv ' + srslc_bboi_par0 + ' ' + srslc_bboi_par; os.system(call_str)
                
                call_str = 'multi_look ' + srslc_fboi + ' ' + srslc_fboi_par + ' ' + samp_fboi + ' ' + samp_fboi_par + ' ' + rlks + ' ' + azlks
                os.system(call_str)
                
                call_str = 'multi_look ' + srslc_bboi + ' ' + srslc_bboi_par + ' ' + samp_bboi + ' ' + samp_bboi_par + ' ' + rlks + ' ' + azlks
                os.system(call_str)
            
                call_str = 'raspwr ' + samp_fboi + ' ' + nWIDTH
                os.system(call_str)
                
                call_str = 'raspwr ' + samp_bboi + ' ' + nWIDTH
                os.system(call_str)
            
            if os.path.isfile(mslc):  os.remove(mslc)
            if os.path.isfile(mrslc): os.remove(mrslc)
            if os.path.isfile(sslc): os.remove(sslc)
        
            call_str = 'raspwr ' + Samp + ' ' + nWIDTH
            os.system(call_str)
            
            call_str = 'rm -rf ' + MslcDir2
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
            
            if not os.path.isfile(TMLIPar):
                A1 = np.loadtxt(SLC2_INF_tab,dtype='str'); A1 = A1.flatten()
                A2 = np.loadtxt(RSLC_tab,dtype='str'); A2 = A2.flatten()
                
                nn = len(A1)
                for i in range(nn):
                    call_str = 'cp ' + A1[i] + ' ' + A2[i]
                    os.system(call_str)                   
                
                if deramp=='1':
                    call_str = 'S1_deramp_TOPS_reference ' + RSLC_tab2
                    os.system(call_str)
                
                    SLC2_INF_tab = RSLC_tab2 + '.deramp'
                else:
                    SLC2_INF_tab = RSLC_tab2
                
                call_str = 'SLC_mosaic_S1_TOPS ' +  SLC2_INF_tab + ' ' + TSLC + ' ' + TSLCPar + ' ' + rlks + ' ' + azlks
                os.system(call_str)

                call_str = 'multi_look ' + TSLC + ' ' + TSLCPar + ' ' + TMLI + ' ' + TMLIPar + ' ' + rlks + ' ' + azlks
                os.system(call_str)
    
                nWidth = ut.read_gamma_par(TMLIPar, 'read','range_samples:')
                
                if boi =='1':
                    call_str = 'ScanSAR_burst_overlap ' + RSLC_tab2 + ' ' + Sdate+'_overlap' + ' ' + rlks + ' ' + azlks + ' - - ' + SLC2_INF_tab + ' - -'
                    os.system(call_str)
                
                    call_str = 'mv ' + srslc_fboi0 + ' ' + srslc_fboi; os.system(call_str)
                    call_str = 'mv ' + srslc_fboi_par0 + ' ' + srslc_fboi_par; os.system(call_str)
                    call_str = 'mv ' + srslc_bboi0 + ' ' + srslc_bboi; os.system(call_str)
                    call_str = 'mv ' + srslc_bboi_par0 + ' ' + srslc_bboi_par; os.system(call_str)
                
                    call_str = 'multi_look ' + srslc_fboi + ' ' + srslc_fboi_par + ' ' + samp_fboi + ' ' + samp_fboi_par + ' ' + rlks + ' ' + azlks
                    os.system(call_str)
                
                    call_str = 'multi_look ' + srslc_bboi + ' ' + srslc_bboi_par + ' ' + samp_bboi + ' ' + samp_bboi_par + ' ' + rlks + ' ' + azlks
                    os.system(call_str)
            
                    call_str = 'raspwr ' + samp_fboi + ' ' + nWidth
                    os.system(call_str)
                
                    call_str = 'raspwr ' + samp_bboi + ' ' + nWidth
                    os.system(call_str)


                call_str = 'raspwr ' + TMLI + ' ' + nWidth + ' - - - - - - - '
                os.system(call_str)
    rr = glob.glob(workDir + '/*IW*.slc')
    if len(rr) > 0:  
        call_str = 'rm ' + workDir + '/*IW*.slc'
        os.system(call_str)
    uu = glob.glob(workDir + '/*IW*.rslc')
    
    if len(uu) > 0:
        call_str = 'rm ' + workDir + '/*IW*.rslc'
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
    #sys.exit(1)

if __name__ == '__main__':
    main(sys.argv[:])
