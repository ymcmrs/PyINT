#! /usr/bin/env python
#'''
###################################################################################
#                                                                                 #
#            Author:   Yun-Meng Cao                                               #
#            Email :   ymcmrs@gmail.com                                           #
#            Date  :   February, 2017                                             #
#                                                                                 #
#         Generating differential interferograms based on GAMMA                   #
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
 
       Coregistration of SAR images based on cross-correlation by using GAMMA.
       With or without DEM assisstance can be chosen.

   usage:
   
            diffPhase_gamma.py igramDir
      
      e.g.  diffPhase_gamma.py IFGRAM_PacayaT163TsxHhA_131021-131101_0011_-0007
          
            
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

# subtract simulated interferometric phase process

# Parameter setting for diffPhase
    simDir = scratchDir + '/' + projectName + "/PROCESS" + "/SIM" 
    if not os.path.isdir(simDir):
        call_str='mkdir ' + simDir  
  
    simDir = simDir + '/sim_' + Mdate + '-' + Sdate
    if not os.path.isdir(simDir):
        call_str='mkdir ' + simDir  
    

    if 'raw2slc_OrbitType'          in templateContents: orbitType = templateContents['raw2slc_OrbitType']                
    else: orbitType = 'HDR'
    if 'Igram_Flattening' in templateContents: flatteningIgram = templateContents['Igram_Flattening']
    else: flatteningIgram = 'orbit'
   
    if 'Igram_Cor_Rwin' in templateContents: rWinCor = templateContents['Igram_Cor_Rwin']
    else: rWinCor = '5'
    if 'Igram_Cor_Awin' in templateContents: aWinCor = templateContents['Igram_Cor_Awin']
    else: aWinCor = '5'
        
    if 'Diff_Flag'          in templateContents: flagDiff = templateContents['Diff_Flag']                
    else: flagDiff = 'Y'
    if 'Diff_Method'          in templateContents: methodDiff = templateContents['Diff_Method']                
    else: methodDiff = 'subphase'
    if 'Diff_Flattening'          in templateContents: flatteningDiff = templateContents['Diff_Flattening']                
    else: flatteningDiff = 'orbit'
    if 'Diff_FilterMethod' in templateContents: strFilterMethod = templateContents['Diff_FilterMethod']
    else: strFilterMethod = "adpt_filt"
    strFilterMethodDiff = strFilterMethod
    
    if 'Diff_FilterStrength' in templateContents: 
        strFilterStrengeh = templateContents['Diff_FilterStrength']
        fFiltLengthDiff = strFilterStrengeh.split('/')[0]
        nFiltWindowDiff = strFilterStrengeh.split('/')[1]
    else:
        fFiltLengthDiff = '-'
        nFiltWindowDiff='-'
    if 'Diff_FFTLength' in templateContents: nAzfftDiff = templateContents['Diff_FFTLength']
    else: nAzfftDiff = '512'
    if 'Diff_UnwrappedThreshold' in templateContents: unwrappedThresholdDiff = templateContents['Diff_UnwrappedThreshold']
    else: unwrappedThresholdDiff = '0.1'
    if 'Diff_Unwrap_patr' in templateContents: unwrappatrDiff = templateContents['Diff_Unwrap_patr']
    else: unwrappatrDiff = '1'
    if 'Diff_Unwrap_pataz' in templateContents: unwrappatazDiff = templateContents['Diff_Unwrap_pataz']
    else: unwrappatazDiff = '1'


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
    BASE        = workDir + '/' + Mdate + '-' + Sdate + '.bas'
    BASE_REF    = workDir + '/' + Mdate + '-' + Sdate + '.bas_ref'

    HGTSIM      = simDir + '/sim_' + Mdate + '-' + Sdate + '.hgt_sim'
    SIMUNW      = simDir + '/sim_' + Mdate + '-' + Sdate + '.sim_unw'

    DIFFpar     = workDir + '/' + Mdate + '-' + Sdate + '.diff.par'
    GCP         = workDir + '/' + Mdate + '-' + Sdate + '.gcp'
    DIFFINTlks  = workDir + '/diff_' + orbitType + '_' + Mdate + '-' + Sdate + '_' + rlks + 'rlks.int'  
    DIFFINTFFTlks = DIFFINTlks.replace('diff_', 'diff_sim_')
    CORFILTlks  = workDir + '/filt_' + Mdate + '-' + Sdate + '_' + rlks + 'rlks.cor'
    CORFILTlksonly =workDir+ '/filt_' + Mdate + '-' + Sdate + '_' + rlks + 'rlks.cor'
    CORDIFFlks = workDir+'/diff_' + Mdate + '-' + Sdate + '_' + rlks + 'rlks.cor'
    CORDIFFFILTlks = workDir+'/diff_filt_' + Mdate + '-' + Sdate + '_' + rlks + 'rlks.cor'
    
    
    DIFFMASKTHINlks  = CORFILTlks + 'maskt.bmp'
    DIFFMASKTHINlksonly = CORFILTlksonly + 'maskt.bmp'

    if flagDiff == 'Y':
        print "Differential interferogram generation would be started on " + workDir + "\n"

    if not (os.path.isdir(workDir)):
        print "Interferogram working directory is not found on " + workDir + "\n"

    createBlankFile(BLANK)
    nWidth = UseGamma(OFFlks, 'read', 'interferogram_width')

    if not (os.path.isfile(HGTSIM) or os.path.isfile(SIMUNW)):
        print "Simulated height information is not found, please run phase simulation before diff \n" 
        sys.exit(0)
    
    call_str = '$GAMMA_BIN/create_diff_par ' + OFFlks + ' ' + OFFlks + ' ' + DIFFpar + ' 0 0 '
    os.system(call_str)        
    
    call_str = '$GAMMA_BIN/extract_gcp ' + HGTSIM + ' ' + OFFlks + ' ' + GCP
    os.system(call_str)   

    if methodDiff == 'subphase':

        call_str = '$GAMMA_BIN/sub_phase ' + INTlks + ' ' + SIMUNW + ' ' + DIFFpar + ' ' + DIFFINTlks + ' 1'
        os.system(call_str)   

        if not flatteningDiff == 'orbit':
            call_str = '$GAMMA_BIN/base_est_fft ' + DIFFINTlks + ' ' + MrslcPar + ' ' + OFFlks + ' ' + BASE_REF + ' ' + nAzfftDiff 
            os.system(call_str)   

            call_str = '$GAMMA_BIN/ph_slope_base ' + DIFFINTlks + ' ' + MrslcPar + ' ' + OFFlks + ' ' + BASE_REF + ' ' + DIFFINTFFTlks 
            os.system(call_str)

            DIFFINTlks = DIFFINTFFTlks
            call_str = '$GAMMA_BIN/base_add ' + BASE + ' ' + BASE_REF + ' ' + BASE + '.tmp'
            os.system(call_str)

            os.rename(BASE+'.tmp', BASE)

        DIFFINTlksbmp = DIFFINTlks + '.bmp'
        call_str = '$GAMMA_BIN/rasmph_pwr ' + DIFFINTlks + ' ' + MampImglks + ' ' + nWidth + ' - - - - - 2.0 0.3 - ' + DIFFINTlksbmp
        os.system(call_str)

        ras2jpg(DIFFINTlks, DIFFINTlks)

        DIFFINTFILTlks = DIFFINTlks.replace('diff_', 'diff_filt_')
        
        
        call_str = '$GAMMA_BIN/adf ' + DIFFINTlks + ' ' + DIFFINTFILTlks + ' ' + CORFILTlks + ' ' + nWidth + ' 0.5'
        os.system(call_str)
      
        if strFilterMethodDiff == 'adapt_filt':
            call_str = '$GAMMA_BIN/adapt_filt ' + DIFFINTFILTlks + ' ' + DIFFINTFILTlks + ' ' + nWidth + ' ' + fFiltLengthDiff + ' ' + nFiltWindowDiff
            os.system(call_str)
        
################ calculate coherence based on differential interferogram ####################################

        call_str = '$GAMMA_BIN/cc_wave '+ DIFFINTlks + ' ' + MampImglks + ' ' + SampImglks + ' ' + CORDIFFlks + ' ' + nWidth + ' ' + rWinCor + ' ' + aWinCor
        os.system(call_str)

        call_str = '$GAMMA_BIN/cc_wave '+ DIFFINTFILTlks + ' ' + MampImglks + ' ' + SampImglks + ' ' + CORDIFFFILTlks + ' ' + nWidth + ' ' + rWinCor + ' ' + aWinCor
        os.system(call_str)
        
##############################################################################################################        
        call_str = '$GAMMA_BIN/rasmph_pwr ' + DIFFINTFILTlks + ' ' + MampImglks + ' ' + nWidth + ' - - - - - 2.0 0.3 - ' 
        os.system(call_str)
        ras2jpg(DIFFINTFILTlks, DIFFINTFILTlks)
        sys.exit(1)

    elif methodDiff == 'lsfit':
        print call_str
        
    print "Subtraction of Simulated interfergram phase is done"
    sys.exit(1)

if __name__ == '__main__':
    main(sys.argv[:])
