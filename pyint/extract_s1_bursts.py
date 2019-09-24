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
import glob
import argparse

from pyint import _utils as ut

def common_burst(La_M,La_S):
    La_M = [float(i) for i in La_M]
    La_S = [float(i) for i in La_S]
    Min = max(min(La_M),min(La_S))
    Max = min(max(La_M),max(La_S))
    
    M_min = []
    M_max = []
    for xm in La_M:
        k0_min = float(xm) - float(Min)
        k0_max = float(xm) - float(Max)
        M_min.append(abs(k0_min))
        M_max.append(abs(k0_max))
    
    M_Index_min = M_min.index(min(M_min)) + 1
    M_Index_max = M_max.index(min(M_max)) + 1
    Mindex =[M_Index_min,M_Index_max]
    
    S_min = []
    S_max = []
    for xs in La_S:
        k0_min = float(xs) - float(Min)
        k0_max = float(xs) - float(Max)
        S_min.append(abs(k0_min))
        S_max.append(abs(k0_max))
    
    S_Index_min = S_min.index(min(S_min)) + 1 
    S_Index_max = S_max.index(min(S_max)) + 1
    Sindex =[S_Index_min,S_Index_max]

    return min(Mindex) , max(Mindex), min(Sindex),max(Sindex)

def get_common_burst(Mslc_dir,Sslc_dir,common_burst_txt):
    Mpar_list = sorted(glob.glob(Mslc_dir+'/*.IW*.burst.par'))
    Spar_list = sorted(glob.glob(Sslc_dir+'/*.IW*.burst.par'))
    if os.path.isfile(common_burst_txt):
        os.remove(common_burst_txt)
    for kk in range(3):
        MBURST = Mpar_list[kk]
        SBURST = Spar_list[kk]
        
        Mtt = Sslc_dir + '/' + os.path.basename(MBURST.replace('burst.par','tt0'))
        Stt = SBURST.replace('burst.par','tt0')
        call_str = "grep 'Burst:' " + MBURST + ' >' + Mtt
        os.system(call_str)
        
        call_str = "grep 'Burst:' " + SBURST + ' >' + Stt
        os.system(call_str)
        
        MM = ut.read_txt2array(Mtt)
        SM = ut.read_txt2array(Stt)
        La_M = MM[:,2]
        La_S = SM[:,2]
        
        PP = common_burst(La_M,La_S)
        
        print('Common bursts of swath' + str(kk+1) + ' : (master) ' + str(PP[0]) + ' ' + str(PP[1]) + ' (slave) ' + str(PP[2]) + ' ' + str(PP[3]))
        call_str = 'echo ' + str(PP[0]) + ' ' + str(PP[1]) + ' ' + str(PP[2]) + ' ' + str(PP[3]) + ' >>' +  common_burst_txt
        os.system(call_str)
                  
    return   
#########################################################################

INTRODUCTION = '''
#############################################################################
   
   Extract the common bursts for S1 TOPs based on one master image.
'''

EXAMPLE = '''
    Usage:
            extract_s1_bursts.py projectName 170115
            
    Examples:
            extract_s1_bursts.py PacayaT163TsxHhA 170115
##############################################################################
'''


def cmdLineParse():
    parser = argparse.ArgumentParser(description='Check common busrts for TOPS data.',\
                                     formatter_class=argparse.RawTextHelpFormatter,\
                                     epilog=INTRODUCTION+'\n'+EXAMPLE)

    parser.add_argument('projectName',help='Name of project.')
    parser.add_argument('Sdate',help='Slave date.')

    inps = parser.parse_args()

    return inps

################################################################################    
    
    
def main(argv):
    
    inps = cmdLineParse() 
    projectName = inps.projectName
    Sdate = inps.Sdate

    scratchDir = os.getenv('SCRATCHDIR')
    templateDir = os.getenv('TEMPLATEDIR')
    templateFile = templateDir + "/" + projectName + ".template"
    templateDict=ut.update_template(templateFile)
           
    rlks = templateDict['range_looks']
    azlks = templateDict['azimuth_looks']
    Mdate =  templateDict['masterDate']
    
    processDir = scratchDir + '/' + projectName + "/PROCESS"
    slcDir     = scratchDir + '/' + projectName + "/SLC"
    rslcDir     = scratchDir + '/' + projectName + "/RSLC"
    
    workDir0 = rslcDir + '/' + Sdate
    #if not os.path.isdir(rslcDir):
    #    os.mkdir(rslcDir)
        
    MslcDir    = slcDir + '/' + Mdate
    SslcDir    = slcDir + '/' + Sdate
    #MBurst_Par = slcDir + '/' + Mdate + '/' + 
    workDir = slcDir + '/' + Sdate
    
    BURST = workDir + '/' + Mdate + '_' + Sdate + '.common_burst_ref'
    
    MslcImg = workDir + '/'+Mdate + '.slc'
    MslcPar = workDir + '/'+Mdate + '.slc.par'    
    
    MamprlksImg = workDir + '/'+Mdate +   '_' + rlks + 'rlks' + '.amp'
    MamprlksPar = workDir + '/'+Mdate +   '_' + rlks +'rlks' + '.amp.par' 
    
    SslcImg = workDir + '/'+ Sdate + '.slc'
    SslcPar = workDir + '/'+ Sdate + '.slc.par'    
    
    SamprlksImg = workDir + '/'+ Sdate +  '_' + rlks + 'rlks' + '.amp'
    SamprlksPar = workDir + '/'+ Sdate +  '_' + rlks + 'rlks' + '.amp.par' 
    
    if not os.path.isdir(workDir):
        os.mkdir(workDir)
    
    get_common_burst(MslcDir,SslcDir,BURST)
    AA = ut.read_txt2array(BURST)
    
    SW = templateDict['start_swath']
    EW = templateDict['end_swath']             
                  
    SB = templateDict['start_burst']
    EB = templateDict['end_burst'] 
    
        
    SLC2_tab = workDir + '/' + Sdate + '_SLC_Tab0'
        

    SLC2_INF_tab = workDir + '/' + Sdate + '_SLC_Tab'
    SLC2_RSLC_tab = workDir + '/' + Sdate + '_RSLC_Tab'
    
    BURST2_tab = workDir + '/' + Sdate + '_Burst_Tab'
    
    if os.path.isfile(SLC2_tab):
        os.remove(SLC2_tab)
        
    if os.path.isfile(SLC2_INF_tab):
        os.remove(SLC2_INF_tab)
        
    if os.path.isfile(SLC2_RSLC_tab):
        os.remove(SLC2_RSLC_tab)
    
    if os.path.isfile(BURST2_tab):
        os.remove(BURST2_tab)
    
    for kk in range(int(EW)-int(SW)+1):
        
        call_str = 'echo ' + SslcDir + '/' + Sdate+'.IW'+str(int(SW)+kk) + '.slc' + ' ' + SslcDir + '/'+ Sdate + '.IW'+str(int(SW)+kk) +'.slc.par' + ' ' + SslcDir + '/'+ Sdate+'.IW'+str(int(SW)+kk) + '.slc.TOPS_par >>' + SLC2_tab
        os.system(call_str)
        
        ii = int(SW) + kk
        SB1=int(AA[ii-1,0])
        EB1=int(AA[ii-1,1])
        
        SB2=int(AA[ii-1,2])
        EB2=int(AA[ii-1,3])
        
        if not int(SB)==1:
            SB2 = SB2 + int(SB)-1
        if not int(EB)==20:
            EB2 = SB2 + int(EB) - int(SB)
        
        call_str = 'echo ' + workDir + '/'+ Sdate+ '_'+ str(int(SB2)) + str(int(EB2)) +'.IW'+str(int(SW)+kk)+ '.slc' + ' ' + workDir + '/' + Sdate + '_'+ str(int(SB2)) + str(int(EB2)) +'.IW'+ str(int(SW)+kk)+ '.slc.par' + ' ' + workDir + '/'+ Sdate+'_'+ str(int(SB2)) + str(int(EB2)) + '.IW'+str(int(SW)+kk)+ '.slc.TOPS_par >>' + SLC2_INF_tab
        os.system(call_str)
        
        call_str = 'echo ' + workDir0 + '/'+ Sdate+ '_'+ str(int(SB2)) + str(int(EB2)) +'.IW'+str(int(SW)+kk)+ '.rslc' + ' ' + workDir + '/' + Sdate + '_'+ str(int(SB2)) + str(int(EB2)) +'.IW'+ str(int(SW)+kk)+ '.rslc.par' + ' ' + workDir + '/'+ Sdate+'_'+ str(int(SB2)) + str(int(EB2)) + '.IW'+str(int(SW)+kk)+ '.rslc.TOPS_par >>' + SLC2_RSLC_tab
        os.system(call_str)
        
        call_str = 'echo ' + str(int(SB2)) + ' ' + str(int(EB2)) + ' >>' + BURST2_tab
        os.system(call_str)

    
    call_str = 'SLC_copy_S1_TOPS ' + SLC2_tab + ' ' + SLC2_INF_tab  + ' ' + BURST2_tab 
    os.system(call_str)
    
    call_str = 'SLC_mosaic_S1_TOPS ' + SLC2_INF_tab + ' ' + SslcImg + ' ' + SslcPar + ' ' + rlks + ' ' +azlks
    os.system(call_str)
    
    call_str = 'multi_look ' + SslcImg + ' ' + SslcPar + ' ' + SamprlksImg + ' ' + SamprlksPar + ' ' + rlks + ' ' + azlks
    os.system(call_str) 
    
    nWidth = ut.read_gamma_par(SamprlksPar, 'read', 'range_samples')
    call_str = 'raspwr ' + SamprlksImg + ' ' + nWidth 
    os.system(call_str)  
    
    sys.exit(1)

if __name__ == '__main__':
    main(sys.argv[:])
