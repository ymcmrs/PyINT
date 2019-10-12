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
import getopt
import time
import glob
import argparse

from pyint import _utils as ut


INTRODUCTION = '''
-------------------------------------------------------------------  
 Calculate the ionospheric phases in an interferogram based on RSI
   
'''

EXAMPLE = '''
    Usage: 
            ionosphere_gamma.py projectName Mdate Sdate
            ionosphere_gamma.py PacayaT163TsxHhA 20150102 20150601
-------------------------------------------------------------------  
'''


def cmdLineParse():
    parser = argparse.ArgumentParser(description='Calculate the ionospheric phases in an interferogram based on RSI.',\
                                     formatter_class=argparse.RawTextHelpFormatter,\
                                     epilog=INTRODUCTION+'\n'+EXAMPLE)

    parser.add_argument('projectName',help='projectName for processing.')
    parser.add_argument('Mdate',help='Master date.')
    parser.add_argument('Sdate',help='Slave date.')
    
    inps = parser.parse_args()
    return inps


def main(argv):
    
    start_time = time.time()
    inps = cmdLineParse() 
    Mdate = inps.Mdate
    Sdate = inps.Sdate
    
    projectName = inps.projectName
    scratchDir = os.getenv('SCRATCHDIR')
    templateDir = os.getenv('TEMPLATEDIR')
    templateFile = templateDir + "/" + projectName + ".template"
    templateDict=ut.update_template(templateFile)
    rlks = templateDict['range_looks']
    azlks = templateDict['azimuth_looks']
    masterDate = templateDict['masterDate']
    
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
    Mamp0     = rslcDir + '/' + Mdate + '/' + Mdate + '_' + rlks + 'rlks.amp'
    MampPar0  = rslcDir + '/' + Mdate + '/' + Mdate + '_' + rlks + 'rlks.amp.par'
    Samp0     = rslcDir + '/' + Sdate + '/' + Sdate + '_' + rlks + 'rlks.amp'
    SampPar0  = rslcDir + '/' + Sdate + '/' + Sdate + '_' + rlks + 'rlks.amp.par'
    
    Mrslc0    = rslcDir  + '/' + Mdate + '/' + Mdate + '.rslc'
    MrslcPar0 = rslcDir  + '/' + Mdate + '/' + Mdate + '.rslc.par'
    Srslc0    = rslcDir  + '/' + Sdate + '/' + Sdate + '.rslc'
    SrslcPar0 = rslcDir  + '/' + Sdate + '/' + Sdate + '.rslc.par'
    
    HGT0      = demDir + '/' + masterDate + '_' + rlks + 'rlks.rdc.dem'
    
    MasterPar0 = rslcDir  + '/' + masterDate + '/' + masterDate + '.rslc.par'
    
    ################# copy file for parallel processing ##########################
    Mamp     =   workDir + '/' + Mdate + '_' + rlks + 'rlks.amp'
    MampPar  =   workDir + '/' + Mdate + '_' + rlks + 'rlks.amp.par'
    Samp     =   workDir + '/' + Sdate + '_' + rlks + 'rlks.amp'
    SampPar  =   workDir + '/' + Sdate + '_' + rlks + 'rlks.amp.par'
    
    Mrslc    =   workDir + '/' + Mdate + '.rslc'
    MrslcPar =   workDir + '/' + Mdate + '.rslc.par'
    Srslc    =   workDir + '/' + Sdate + '.rslc'
    SrslcPar =   workDir + '/' + Sdate + '.rslc.par'
    
    HGT      =   workDir + '/' + masterDate + '_' + rlks + 'rlks.rdc.dem'
    MasterPar = workDir + '/' + masterDate + '.rslc.par'
    
    if not os.path.isfile(Mamp):ut.copy_file(Mamp0,Mamp)    
    if not os.path.isfile(MampPar):ut.copy_file(MampPar0,MampPar)
    if not os.path.isfile(Samp):ut.copy_file(Samp0,Samp)
    if not os.path.isfile(SampPar):ut.copy_file(SampPar0,SampPar)
    
    if not os.path.isfile(Mrslc): ut.copy_file(Mrslc0,Mrslc)
    if not os.path.isfile(MrslcPar): ut.copy_file(MrslcPar0,MrslcPar)
    if not os.path.isfile(Srslc):ut.copy_file(Srslc0,Srslc)
    if not os.path.isfile(SrslcPar):ut.copy_file(SrslcPar0,SrslcPar)
    
    if not os.path.isfile(HGT):ut.copy_file(HGT0,HGT)
    if not os.path.isfile(MasterPar):ut.copy_file(MasterPar0,MasterPar)
    
    
    nWidth = ut.read_gamma_par(MampPar, 'read', 'range_samples')
    nLine =  ut.read_gamma_par(MampPar, 'read', 'azimuth_lines')
    
    ###################### Output files #################################   
    ionoDir = workDir + '/ionosphere'
    if not os.path.isdir(ionoDir):
        os.mkdir(ionoDir)
    
    workDir = ionoDir
    Mrslc_low    =   ionoDir + '/' + Mdate + '.low.rslc'
    MrslcPar_low =   ionoDir + '/' + Mdate + '.low.rslc.par'
    Mrslc_high    =   ionoDir + '/' + Mdate + '.high.rslc'
    MrslcPar_high =   ionoDir + '/' + Mdate + '.high.rslc.par'
    
    Srslc_low    =   ionoDir + '/' + Sdate + '.low.rslc'
    SrslcPar_low =   ionoDir + '/' + Sdate + '.low.rslc.par'
    Srslc_high    =   ionoDir + '/' + Sdate + '.high.rslc'
    SrslcPar_high =   ionoDir + '/' + Sdate + '.high.rslc.par'
#########################################################
    
    call_str = 'bpf_ssi ' + Mrslc + ' ' + MrslcPar + ' ' + Mrslc_low + ' ' + MrslcPar_low + ' ' + Mrslc_high + ' ' + MrslcPar_high
    os.system(call_str)
    
    call_str = 'bpf_ssi ' + Srslc + ' ' + SrslcPar + ' ' + Srslc_low + ' ' + SrslcPar_low + ' ' + Srslc_high + ' ' + MrslcPar_high
    os.system(call_str)
    
 ################## interferometry #####################   

    off_low = workDir + '/' +  Pair +'_' + rlks + 'rlks.low.off'   
    call_str = 'create_offset '+ MrslcPar_low + ' ' + SrslcPar_low + ' ' + off_low + ' 1 ' + rlks + ' ' + azlks +  ' 0'
    os.system(call_str)
   
    sim_low_unw = workDir + '/' +  Pair + '.low.sim_unw'
    call_str = 'phase_sim_orb ' + MrslcPar_low + ' ' + SrslcPar_low + ' ' + off_low + ' ' + HGT + ' ' + sim_low_unw + ' ' + MasterPar + ' - - 1 1' 
    os.system(call_str)
    
    diff_low = workDir + '/' +  Pair + '_' + rlks + 'rlks.low.diff'
    call_str = 'SLC_diff_intf ' + Mrslc_low + ' ' + Srslc_low + ' ' + MrslcPar_low + ' ' + SrslcPar_low + ' ' + off_low + ' ' + sim_low_unw + ' ' + diff_low + ' ' + rlks + ' ' + azlks + ' ' + ' 1 0 0.25'
    os.system(call_str)
   

    off_low = workDir + '/' +  Pair +'_' + rlks + 'rlks.high.off'   
    call_str = 'create_offset '+ MrslcPar_high + ' ' + SrslcPar_high + ' ' + off_high + ' 1 ' + rlks + ' ' + azlks +  ' 0'
    os.system(call_str)
   
    sim_high_unw = workDir + '/' +  Pair + '.high.sim_unw'
    call_str = 'phase_sim_orb ' + MrslcPar_high + ' ' + SrslcPar_high + ' ' + off_high + ' ' + HGT + ' ' + sim_high_unw + ' ' + MasterPar + ' - - 1 1' 
    os.system(call_str)
    
    diff_high = workDir + '/' +  Pair + '_' + rlks + 'rlks.high.diff'
    call_str = 'SLC_diff_intf ' + Mrslc_high + ' ' + Srslc_high + ' ' + MrslcPar_high + ' ' + SrslcPar_high + ' ' + off_high + ' ' + sim_high_unw + ' ' + diff_high + ' ' + rlks + ' ' + azlks + ' ' + ' 1 0 0.25'
    os.system(call_str)

  ######################################################
    hl_diff = workDir + '/' +  Pair + '_' + rlks + 'rlks.hl.diff'
    hl_diff_cc = workDir + '/' +  Pair + '_' + rlks + 'rlks.hl.diff.cc'
    hl_diff_mask = workDir + '/' +  Pair + '_' + rlks + 'rlks.hl.diff.cc_mask.bmp'
    
    hl_diff1 = workDir + '/' +  Pair + '_' + rlks + 'rlks.hl.diff1'
    hl_diff2 = workDir + '/' +  Pair + '_' + rlks + 'rlks.hl.diff2'
    hl_diff3 = workDir + '/' +  Pair + '_' + rlks + 'rlks.hl.diff3'
    hl_diff4 = workDir + '/' +  Pair + '_' + rlks + 'rlks.hl.diff4'
    
    hl_diff4_phase = workDir + '/' +  Pair + '_' + rlks + 'rlks.hl.diff4_phase'
    
    hl_diff_jpg = workDir + '/' +  Pair + '_' + rlks + 'rlks.hl.diff.jpg'
    
    diff_low_phase = workDir + '/' +  Pair + '_' + rlks + 'rlks.low.diff_phase'
    call_str = 'cpx_to_real ' + diff_low_phase + ' ' + nWidth + ' 4'
    os.system(call_str)
    
    call_str = 'subtract_phase ' + diff_high + ' ' + diff_low_phase + ' ' + hl_diff + ' ' + nWidth + ' 1'
    os.system(call_str)
    
    call_str = 'rasmph_pwr ' + Mamp + ' ' + hl_diff + ' ' + nWidth
    #call_str = 'vismph_pwr.py ' + hl_diff + ' ' + Mamp + ' ' + nWidth + ' -f 1.0 ' + ' -z 1000 ' + ' -p ' + hl_diff_jpg
    os.system(call_str)
    
   #### filter
   
    call_str = 'adf ' + hl_diff + ' ' + hl_diff1 + ' ' + hl_diff_cc + ' ' + nWidth + ' 0.2 512 7 128'
    os.system(call_str)
    
    call_str = 'adf ' + hl_diff1 + ' ' + hl_diff2 + ' ' + hl_diff_cc + ' ' + nWidth + ' 0.3 256 7 64'
    os.system(call_str)
    
    call_str = 'adf ' + hl_diff2 + ' ' + hl_diff3 + ' ' + hl_diff_cc + ' ' + nWidth + ' 0.3 128 7 64'
    os.system(call_str)
    
    call_str = 'adf ' + hl_diff3 + ' ' + hl_diff4 + ' ' + hl_diff_cc + ' ' + nWidth + ' 0.3 128 7 16'
    os.system(call_str)
    
    # unwrawp
    call_str = 'cpx_to_real ' + hl_diff4 + ' ' + hl_diff4_phase + ' ' + nWidth + ' 4'
    os.system(call_str)
    
    # shift to zero
    # mask very low coherence
    
    call_str = 'cc_ad ' + hl_diff + ' ' + Mamp + ' ' + Samp + ' - - ' + hl_diff_cc + ' ' + nWidth + ' 3 9'
    os.system(call_str)
    
    call_str = 'rascc_mask ' +  hl_diff_cc + ' ' + Mamp + ' ' + nWidth + ' 1 1 0 1 1 0.15 0.0 0.1 0.9 1.0 0.35 1 ' + hl_diff_mask
    os.system(call_str)
    
    nWidth_half = str(float(nWidth)/2)
    image_report = workDir + '/' +  Pair + '.image_stat.report'
    
    call_str = 'image_stat ' + hl_diff4_phase + ' ' + nWidth + ' ' + nWidth_half + ' 200 200 ' + image_report
    os.system(call_str)
    
    mean_phase = ut.read_gamma_par(image_report, 'read', 'mean')
    std_phase = ut.read_gamma_par(image_report, 'read', 'stdev')
    
    
    hl_diff_phase_shift = workDir + '/' +  Pair + '_' + rlks + 'rlks.hl.diff.ph_shift'
    hl_diff_shifted = workDir + '/' +  Pair + '_' + rlks + 'rlks.hl.diff4.shifted'
    hl_diff_shifted_phase = workDir + '/' +  Pair + '_' + rlks + 'rlks.hl.diff4.shifted.phase'
    call_str = 'lin_comb 1 ' + hl_diff4_phase + ' ' + mean_phase + ' 0.0 ' +  hl_diff_phase_shift + ' ' + nWidth + ' 1 ' + nLine
    os.system(call_str)
    
    call_str = 'subtract_phase ' + hl_diff4_phase + ' ' + hl_diff_phase_shift + ' ' + hl_diff_shifted + ' ' + nWidth + '  1'
    os.system(call_str)
    
    call_str = 'cpx_to_real ' + hl_diff_shifted + ' ' + hl_diff_shifted_phase + ' ' + nWidth + ' 4'
    os.system(call_str)
    
    call_str = 'lin_comb 1 ' +  hl_diff_shifted_phase + ' ' + mean_phase + ' 1.0 ' + hl_diff4_phase + ' ' + nWidth + ' 1 ' + nLine
    os.system(call_str)
    
    ############# determine trend considering cc_mask using unwrapping with multi_cpx before unwrapping ###
    
    diff_par = workDir + '/' + Pair + 'ddiff.par'
    call_str = 'create_diff_par ' + MampPar + ' - ' + diff_par + ' 1 0'
    os.system(call_str)
    
    ddiff_phase_trend = workDir + '/' +  Pair + '_' + rlks + 'rlks.hl.diff4_phase.trend'
    call_str = 'quad_fit ' + hl_diff4_phase + ' ' + diff_par + ' 5 5 ' + hl_diff_mask + ' - 3 ' + ddiff_phase_trend
    os.system(call_str)
    
    #call_str = 'vistd_pwr.py ' + ddiff_phase_trend + ' ' + Mamp + ' ' + nWidth + ' -c 12.6 -z 1000 -f 1.0 -m rmg -p ' + ddiff_phase_trend + '.jpg'
    #os.system(call_str)
    
    hl_diff_detrend = hl_diff+ '.detrend'
    call_str = 'subtract_phase ' + hl_diff + ' ' + ddiff_phase_trend  + ' ' + hl_diff_detrend + ' ' + nWidth + ' 1.'
    os.system(call_str)
    
    #call_str = 'vismph_pwr.py ' + hl_diff_detrend + ' ' + Mamp + ' ' + nWidth + ' -f 1.0 -z 1000 -p ' +  hl_diff_detrend+'.jpg'
    #os.system(call_str)
    
    
    call_str = 'adf ' + hl_diff_detrend + ' ' + hl_diff1 + ' ' + hl_diff+'.smcc' + ' ' + nWidth + ' 0.2 512 7 128'
    os.system(call_str)
    
    call_str = 'adf ' + hl_diff1 + ' ' + hl_diff2 + ' ' + hl_diff+'.smcc' + ' ' + nWidth + ' 0.3 256 7 64'
    os.system(call_str)
    
    call_str = 'adf ' + hl_diff2 + ' ' + hl_diff3 + ' ' + hl_diff+'.smcc' + ' ' + nWidth + ' 0.3 128 7 64'
    os.system(call_str)
    
    hl_diff4_detrend = hl_diff4+ '.detrend'
    hl_diff_cc = hl_diff+'.sm4.cc'
    call_str = 'adf ' + hl_diff3 + ' ' + hl_diff4_detrend + ' ' + hl_diff_cc + ' ' + nWidth + ' 0.3 128 7 16'
    os.system(call_str)
    
    off1 = workDir + '/' +  Pair + '.off1'
    call_str = 'create_offset ' + MampPar + ' ' + MampPar + ' ' + off1 + ' 1 1 1 0'
    os.system(call_str)
    
    hl_diff4_mask = hl_diff+'.sm4.cc_mask.bmp'
    call_str = 'rascc_mask ' + hl_diff_cc + ' ' + Mamp + ' ' + nWidth + ' 1 1 0 1 1 0.95 0.0 0.1 0.1 0.9 1.0 0.35 1 ' + hl_diff4_mask 
    os.system(call_str)
    
    call_str = 'mask_class ' + hl_diff_mask + ' ' + hl_diff4_detrend + ' ' + hl_diff4_detrend + '.masked.tmp ' + ' 1 1 1 1 0 0.0 0.0'
    os.system(call_str)
    
    call_str = 'mask_class ' + hl_diff4_mask + ' ' + hl_diff4_detrend + '.masked.tmp ' + ' ' + hl_diff4_detrend + '.masked' +  + ' 1 1 1 1 0 0.0 0.0'
    os.system(call_str)
    
    
    ddiff5 = workDir + '/' +  Pair + '_' + rlks + 'rlks.hl.diff5'
    off5 = workDir + '/' +  Pair + '.off5'
    call_str = 'multi_cpx ' + hl_diff4_detrend + '.masked' +  ' ' + off1 + ddiff5 + ' ' + off5 + ' 5 5'
    os.system(call_str)
    
    call_str = 'multi_real ' + Mamp + ' ' + off1 + ' ' + Mamp + '.5' + off5 + ' 5 5'
    os.system(call_str)
    
    call_str = 'multi_real ' + hl_diff_cc + ' ' + off1 + ' ' + hl_diff_cc + '.5' + off5 + ' 5 5'
    os.system(call_str)
    
    nWidth5 = ut.read_gamma_par(off5,'read','interferogram_width')
    
    ddiff5_phase_tmp = ddiff5 + '.phase.tmp'
    ddiff5_phase_interp = ddiff5 + '.phase.interp'
    call_str = 'cpx_to_real ' + ddiff5 + ' ' + ddiff5_phase_tmp + ' ' + nWidth5 + ' 4'
    os.system(call_str)
    
    call_str = 'fill_gaps ' + ddiff5_phase_tmp + ' ' + nWidth5 + ' ' + ddiff5_phase_interp + ' 0 4 - 1 100 4 400'
    os.system(call_str)
    
    
    #### remove outliers
    ddiff5_fspf = ddiff5_phase_interp + '.fspf'
    call_str = 'fspf ' + ddiff5_phase_interp + ' ' + ddiff5_fspf + ' ' + nWidth5 + ' 2 64 3'
    os.system(call_str)
    
    ddiff5_phase_interp_outliers = ddiff5_phase_interp + '.outliers'
    call_str = 'lin_comb 2 ' + ddiff5_phase_interp + ' ' + ddiff5_fspf + ' 100 1.0 -1.0 ' + ddiff5_phase_interp_outliers + ' ' + nWidth5
    os.system(call_str)
    
    hl_diff_cc5 = hl_diff_cc + '.5'
    hl_diff5_mask = ddiff5 + '.mask.bmp'
    call_str = 'single_class_mapping 2 ' +  ddiff5_phase_interp_outliers + ' 99.95 100.05 ' + hl_diff_cc5 + ' 0.15 1.0 ' + hl_diff5_mask + ' ' + nWidth5
    os.system(call_str)
    
    ddiff5_phase_tmp1 = ddiff5_phase_tmp + '1'
    call_str = 'mask_class ' + hl_diff5_mask + ' ' + ddiff5_phase_tmp + ' ' + ddiff5_phase_tmp1 + ' 0 1 1 1 0 0.0 0.0'
    os.system(call_str)
    
    call_str = 'fill_gaps ' + ddiff5_phase_tmp1 + ' ' + ddiff5_phase_interp + ' 0 4 - 1 100 4 400'
    os.system(call_str)
    
    ddiff_detrend_interp_phase = hl_diff + '.detrend' + '.interp.phase'
    call_str = 'multi_real ' + ddiff5_phase_interp + ' ' + off5 + ' ' +  ddiff_detrend_interp_phase + ' ' + off1 + ' -5 -5'
    os.system(call_str)
    
    call_str = 'fspf ' + ddiff_detrend_interp_phase + ' ' + ddiff_detrend_interp_phase + '.fspf' + ' ' + nWidth + ' 2 8 3'
    os.system(call_str)
    
    #call_str = ' visdt_pwr.py ' +  ddiff_detrend_interp_phase + '.fspf' + ' ' + Mamp + ' ' + nWidth + ' -c 1.6 -z 1000 -f 1.0 -m rmg -p ' + ddiff_detrend_interp_phase + '.fspf.jpg'
    #os.system(call_str)
    
    
    ###### add the solutions
    
    ddiff_phase_fspf =  hl_diff + ' .phase.fspf'
    call_str = 'lin_comb 2 ' + ddiff_phase_trend + ' ' + ddiff_detrend_interp_phase + '.fspf' + ' 0.0 1.0 1.0 ' + ddiff_phase_fspf + ' ' + nWidth + ' 1 ' + nLine
    os.system(call_str)
    
    #call_str ='visdt_pwr.py ' + ddiff_phase_fspf + ' ' + Mamp + ' ' + nWidth + ' -c 1.6 -z 1000 -f 1.0 -m rmg -p ' + ddiff_phase_fspf + '.jpg'
    #os.system(call_str)
    
    
    ###################### determin scaling factor using bpf_ssi
    
    bpf_ssi_out = workDir + '/bpf_ssi.out'
    call_str = 'bpf_ssi ' + Mrslc + ' ' + MrslcPar + ' - - - - 0.6666 > ' + bpf_ssi_out
    os.system(call_str)
    
    a0 = ut.read_gamma_par(bpf_ssi_out,'read','a')
    b0 = ut.read_gamma_par(bpf_ssi_out,'read','b')
    x0 = ut.read_gamma_par(bpf_ssi_out,'read','x')
    y0 = ut.read_gamma_par(bpf_ssi_out,'read','y')
    z0 = ut.read_gamma_par(bpf_ssi_out,'read','z')
    zz0 = str(float(z0)*2)
    
    ddiff_phase_fspf_scaled = ddiff_phase_fspf + '.scaled'
    call_str = 'lin_comb 1 ' + ddiff_phase_fspf + ' 0.0 ' + zz0 + ' ' + ddiff_phase_fspf_scaled + ' ' + nWidth
    os.system(call_str)
    
    call_str = 'rasrmg ' + ddiff_phase_fspf_scaled + ' ' + Mamp + ' ' + nWidth
    #call_str = 'vismph_pwr.py ' + hl_diff + ' ' + Mamp + ' ' + nWidth + ' -f 1.0 ' + ' -z 1000 ' + ' -p ' + hl_diff_jpg
    os.system(call_str)
    
    #call_str ='visdt_pwr.py ' + ddiff_phase_fspf_scaled + ' ' + Mamp + ' ' + nWidth + ' -c 1.6 -z 1000 -f 1.0 -m rmg -p ' + ddiff_phase_fspf_scaled + '.jpg'
    #os.system(call_str)
    
    # 2_phi_iono            =  phi0 + zz * ddiff_phase_fspf
    # 2_phi_non-dispersive  =  phi0 - zz * ddiff_phase_fspf
    
    #call_str = ' subtract_phase ' + 
    
    
    print("Estimating the scaled ionospheric phases is done!")
    ut.print_process_time(start_time, time.time())
    sys.exit(1)

if __name__ == '__main__':
    main(sys.argv[:])
