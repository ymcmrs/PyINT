#! /usr/bin/env python
#'''
###################################################################################
#                                                                                 #
#            Author:   Yun-Meng Cao                                               #
#            Email :   ymcmrs@gmail.com                                           #
#            Date  :   February, 2017                                             #
#                                                                                 #
#         Generating interferograms based on GAMMA                                #
#                                                                                 #
###################################################################################
#'''
import numpy as np
import os
import pysar._readfile as readfile
import sys  
import subprocess
import getopt
import time
import glob

def ras2jpg(input, strTitle):
    call_str = "convert " + input + ".ras " + input + ".jpg"
    os.system(call_str)
    call_str = "convert " + input + ".jpg -resize 250 " + input + ".thumb.jpg"
    os.system(call_str)
    call_str = "convert " + input + ".jpg -resize 500 " + input + ".bthumb.jpg"
    os.system(call_str)
    call_str = "$INT_SCR/addtitle2jpg.pl " + input + ".thumb.jpg 14 " + strTitle
    os.system(call_str)
    call_str = "$INT_SCR/addtitle2jpg.pl " + input + ".bthumb.jpg 24 " + strTitle
    os.system(call_str)

def UseGamma(inFile, task, keyword):
    if task == "read":
        f = open(inFile, "r")
        while 1:
            line = f.readline()
            if not line: break
            if line.count(keyword) == 1:
                strtemp = line.split(":")
                value = strtemp[1].strip()
                return value
        print "Keyword " + keyword + " doesn't exist in " + inFile
        f.close()
        
def geocode(inFile, outFile, UTMTORDC, nWidth, nWidthUTMDEM, nLineUTMDEM):
    if inFile.rsplit('.')[1] == 'int':
        call_str = '$GAMMA_BIN/geocode_back ' + inFile + ' ' + nWidth + ' ' + UTMTORDC + ' ' + outFile + ' ' + nWidthUTMDEM + ' ' + nLineUTMDEM + ' 0 1'
    else:
        call_str = '$GAMMA_BIN/geocode_back ' + inFile + ' ' + nWidth + ' ' + UTMTORDC + ' ' + outFile + ' ' + nWidthUTMDEM + ' ' + nLineUTMDEM + ' 0 0'
    os.system(call_str)
    

def createBlankFile(strFile):
    f = open(strFile,'w')
    for i in range (10):
        f.write('\n')
    f.close()


def usage():
    print '''
******************************************************************************************************
 
          Generateing Interferograms based on GAMMA

   usage:
   
            GenIgram_Gamma.py igramDir
      
      e.g.  GenIgram_Gamma.py IFGRAM_PacayaT163TsxHhA_131021-131101_0011_-0007
          
            
*******************************************************************************************************
    '''   
    
def main(argv):
    
    if len(sys.argv)==2:
        if argv[0] in ['-h','--help']: usage(); sys.exit(1)
        else: igramDir=sys.argv[1]        
    else:
        usage();sys.exit(1)
       
    projectName = igramDir.split('_')[1]
    IFGPair = igramDir.split(projectName+'_')[1].split('_')[0]
    Mdate = IFGPair.split('-')[0]
    Sdate = IFGPair.split('-')[1]
    
    scratchDir = os.getenv('SCRATCHDIR')
    templateDir = os.getenv('TEMPLATEDIR')
    templateFile = templateDir + "/" + projectName + ".template"
    
    processDir = scratchDir + '/' + projectName + "/PROCESS"
    slcDir     = scratchDir + '/' + projectName + "/SLC"
    workDir    = processDir + '/' + igramDir   
    
    templateContents=readfile.read_template(templateFile)
    rlks = templateContents['Range_Looks']
    azlks = templateContents['Azimuth_Looks']


# generate interferogram process

# Parameter setting for Igram

    if 'raw2slc_OrbitType'          in templateContents: orbitType = templateContents['raw2slc_OrbitType']                
    else: orbitType = 'HDR'
    if 'Igram_Flag'          in templateContents: flagIgram = templateContents['Igram_Flag']                
    else: flagIgram = 'Y'
    if 'Igram_Rlooks'          in templateContents: rLooksIgram = templateContents['Igram_Rlooks']                
    else: rLooksIgram = '4'
    if 'Igram_Alooks'          in templateContents: aLooksIgram = templateContents['Igram_Alooks']                
    else: aLooksIgram = '4'
    if 'COREG_all_Flag'          in templateContents: COREG_all_Flag = templateContents['COREG_all_Flag']                
    else: COREG_all_Flag = '0'
    
    if 'Igram_Spsflg'       in templateContents: spsflgIgram = templateContents['Igram_Spsflg']
    else: spsflgIgram = '1'
    if 'Igram_Azfflg'       in templateContents: azfflgIgram = templateContents['Igram_Azfflg']
    else: azfflgIgram = '1'
    if 'Igram_Rp1flg'       in templateContents: rp1flgIgram = templateContents['Igram_Rp1flg']
    else: rp1flgIgram = '1'
    if 'Igram_Rp2flg'       in templateContents: rp2flgIgram = templateContents['Igram_Rp2flg']
    else: rp2flgIgram = '1'
    if 'Igram_Flag_TDM' in templateContents: flagTDM = templateContents['Igram_Flag_TDM']
    else: flagTDM = 'N'
    if 'Igram_Cor_Rwin' in templateContents: rWinCor = templateContents['Igram_Cor_Rwin']
    else: rWinCor = '5'
    if 'Igram_Cor_Awin' in templateContents: aWinCor = templateContents['Igram_Cor_Awin']
    else: aWinCor = '5'
    if 'Igram_Flattening' in templateContents: flatteningIgram = templateContents['Igram_Flattening']
    else: flatteningIgram = 'orbit'
#    else: flatteningIgram = 'fft'
    if 'Igram_FilterMethod' in templateContents: strFilterMethod = templateContents['Igram_FilterMethod']
    else: strFilterMethod = 'adapt_filt'
    if 'Igram_FilterStrength' in templateContents: strFilterStrengeh = templateContents['Igram_FilterStrength']
    else: strFilterStrengeh = '0.8/4'
    fFiltLength = strFilterStrengeh.split('/')[0]
    nFiltWindow = strFilterStrengeh.split('/')[1]
    if 'Igram_FFTLength' in templateContents: nAzfft = templateContents['Igram_FFTLength']
    else: nAzfft = '512'
    if 'Igram_UnwrappedThreshold' in templateContents: unwrappedThreshold = templateContents['Igram_UnwrappedThreshold']
    else: unwrappedThreshold = '0.1'


#  Definition of file
    MrslcImg     = workDir + '/' + Mdate + '.rslc'
    MrslcPar     = workDir + '/' + Mdate + '.rslc.par'
    MampImg     = workDir + '/' + Mdate + '.amp'
    MampPar     = workDir + '/' + Mdate + '.amp.par'

    SrslcImg     = workDir + '/' + Sdate + '.rslc'
    SrslcPar     = workDir + '/' + Sdate + '.rslc.par'
    SampImg     = workDir + '/' + Sdate + '.amp'
    SampPar     = workDir + '/' + Sdate + '.amp.par'

    BLANK       = workDir + '/' + Mdate + '-' + Sdate + '.blk'
    OFF         = workDir + '/' + Mdate + '-' + Sdate + '.off'
    INT         = workDir + '/' + Mdate + '-' + Sdate + '.int'
    INTlks      = workDir + '/' + Mdate + '-' + Sdate + '_' + rlks + 'rlks.int'
    OFFlks      = workDir + '/' + Mdate + '-' + Sdate + '_' + rlks + 'rlks.off'
    FLTlks      = workDir + '/flat_' + orbitType + '_' + Mdate + '-' + Sdate + '_' + rlks + 'rlks.int'
    FLTFFTlks   = FLTlks.replace('flat_', 'flat_sim_')

    MampImglks  = workDir + '/' + Mdate + '_' + rlks + 'rlks.amp'
    MampParlks  = workDir + '/' + Mdate + '_' + rlks + 'rlks.amp.par'
    SampImglks  = workDir + '/' + Sdate + '_' + rlks + 'rlks.amp'
    SampParlks  = workDir + '/' + Sdate + '_' + rlks + 'rlks.amp.par'
    CORlks      = workDir + '/' + Mdate + '-' + Sdate + '_' + rlks + 'rlks.cor'
    CORFILTlks  = workDir + '/filt_' + Mdate + '-' + Sdate + '_' + rlks + 'rlks.cor'
    BASE        = workDir + '/' + Mdate + '-' + Sdate + '.bas'
    BASE_REF    = workDir + '/' + Mdate + '-' + Sdate + '.bas_ref'

### start generation of interferogram with coregistered master and slave in each pair


    if os.path.isfile(OFF):
        os.remove(OFF)

    call_str = '$GAMMA_BIN/create_offset '+ MrslcPar + ' ' + SrslcPar + ' ' + OFF + ' 1 - - 0'
    os.system(call_str)

    call_str = '$GAMMA_BIN/SLC_intf '+ MrslcImg + ' ' + SrslcImg + ' ' + MrslcPar + ' ' + SrslcPar + ' ' + OFF + ' ' + INT + ' 1 1 - - ' + spsflgIgram + ' ' + azfflgIgram + ' ' + rp1flgIgram + ' ' + rp2flgIgram
    os.system(call_str)

### start co-registartion of raw interferogram w.r.t. master scene  

    if COREG_all_Flag == '1':
        call_str = "Coregist_all_Gamma.py " + igramDir     ## after this step, all based on rslc
        os.system(call_str)

### continue interferometric process with re-coregistered slc parameter w.r.t. master scene

    call_str = '$GAMMA_BIN/create_offset '+ MrslcPar + ' ' + SrslcPar + ' ' + OFF + ' 1 - - 0'
    messageRsmas.log(call_str)
    os.system(call_str)    

    call_str = '$GAMMA_BIN/base_orbit '+ MrslcPar + ' ' + SrslcPar + ' ' + BASE
    messageRsmas.log(call_str)
    os.system(call_str)

    if flagTDM == 'Y':    ### shong 07/16 flag for TanDEM-X bistatic mode case to conside half length of baseline
        call_str = '$INT_SCR/halfbase.pl ' + BASE;
        os.system(call_str)

    call_str = '$GAMMA_BIN/multi_cpx '+ INT + ' ' + OFF + ' ' + INTlks + ' ' + OFFlks + ' ' + rlks + ' ' + azlks
    os.system(call_str)
########################    flatten phase remove ################################
   
    call_str = '$GAMMA_BIN/ph_slope_base '+ INTlks + ' ' + MrslcPar + ' ' + OFFlks + ' ' + BASE + ' ' + FLTlks
    os.system(call_str)
 
    call_str = '$GAMMA_BIN/multi_look '+ MrslcImg + ' ' + MrslcPar + ' ' + MampImglks + ' ' + MampParlks + ' ' + rlks + ' ' + azlks
    os.system(call_str)

    call_str = '$GAMMA_BIN/multi_look '+ SrslcImg + ' ' + SrslcPar + ' ' + SampImglks + ' ' + SampParlks + ' ' + rlks + ' ' + azlks
    os.system(call_str)

    nWidth = UseGamma(OFFlks, 'read', 'interferogram_width')

    call_str = '$GAMMA_BIN/cc_wave '+ INTlks + ' ' + MampImglks + ' ' + SampImglks + ' ' + CORlks + ' ' + nWidth + ' ' + rWinCor + ' ' + aWinCor
    os.system(call_str)

    if flatteningIgram == 'fft':
        call_str = '$GAMMA_BIN/base_est_fft ' + FLTlks + ' ' + MrslcPar + ' ' + OFFlks + ' ' + BASE_REF + ' ' + nAzfft 
        os.system(call_str)

        call_str = '$GAMMA_BIN/ph_slope_base ' + FLTlks + ' ' + MrslcPar + ' ' + OFFlks + ' ' + BASE_REF + ' ' + FLTFFTlks  
        os.system(call_str)

        FLTlks = FLTFFTlks 
        FLTFILTlks = FLTlks.replace('flat_', 'filt_')
      
        call_str = '$GAMMA_BIN/base_add ' + BASE + ' ' + BASE_REF + ' ' + BASE + '.tmp'
        os.system(call_str)
      
        os.rename(BASE+'.tmp', BASE)

    else:             
        FLTFILTlks = FLTlks.replace('flat_', 'filt_')
########################    filtering  ################################
    call_str = '$GAMMA_BIN/rasmph_pwr ' + FLTlks + ' ' + MampImglks + ' ' + nWidth + ' - - - - - 2.0 0.3 - ' 
    os.system(call_str)

    ras2jpg(FLTlks, FLTlks)

    call_str = '$GAMMA_BIN/adf ' + FLTlks + ' ' + FLTFILTlks + ' ' + CORFILTlks + ' ' + nWidth + ' 0.5'
    os.system(call_str)

    if strFilterMethod == 'adapt_filt':    
        call_str = '$GAMMA_BIN/adapt_filt ' + FLTlks + ' ' + FLTFILTlks + ' ' + nWidth + ' ' + fFiltLength + ' ' + nFiltWindow
        os.system(call_str)
        
        call_str = '$GAMMA_BIN/cc_wave '+ FLTFILTlks + ' ' + MampImglks + ' ' + SampImglks + ' ' + CORFILTlks + ' ' + nWidth + ' ' + rWinCor + ' ' + aWinCor
        os.system(call_str)
        
        
        
    call_str = '$GAMMA_BIN/rasmph_pwr ' + FLTFILTlks + ' ' + MampImglks + ' ' + nWidth + ' - - - - - 2.0 0.3 - ' 
    os.system(call_str)

    ras2jpg(FLTFILTlks, FLTFILTlks)

    print "Interferogram generation is done!"
 
    sys.exit(1)

if __name__ == '__main__':
    main(sys.argv[:])
