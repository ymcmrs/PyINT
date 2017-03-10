#! /usr/bin/env python
#'''
###################################################################################
#                                                                                 #
#            Author:   Yun-Meng Cao                                               #
#            Email :   ymcmrs@gmail.com                                           #
#            Date  :   February, 2017                                             #
#                                                                                 #
#         Unwrap interferograms based on GAMMA                                    #
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
 
          Unwrap interferograms based on GAMMA.
       

   usage:
   
            UnwrapPhase_Gamma.py igramDir
      
      e.g.  UnwrapPhase_Gamma.py IFGRAM_PacayaT163TsxHhA_131021-131101_0011_-0007
          
            
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
 
    if 'Topo_Flag'          in templateContents: flagTopo = templateContents['Topo_Flag']           
    else: flagTopo = 'N'
#  if 'Diff_Method'          in templateContents: methodDiff = templateContents['Diff_Method']                
#  else: methodDiff = 'subphase'
    if 'Diff_Flattening'          in templateContents: flatteningDiff = templateContents['Diff_Flattening']                
    else: flatteningDiff = 'orbit'

#    if 'Igram_UnwrappedThreshold' in templateContents: unwrappedThreshold = templateContents['Igram_UnwrappedThreshold']
#    else: unwrappedThreshold = '0.6'
    if 'UnwrappedThreshold' in templateContents: UnwrappedThreshold = templateContents['UnwrappedThreshold']
    else: unwrappedThreshold = '0.6'
    if 'Unwrap_patr' in templateContents: unwrappatrDiff = templateContents['Unwrap_patr']
    else: unwrappatrDiff = '1'
    if 'Unwrap_pataz' in templateContents: unwrappatazDiff = templateContents['Unwrap_pataz']
    else: unwrappatazDiff = '1'
        
    nWidth = UseGamma(OFFlks, 'read', 'interferogram_width')
    nLine = UseGamma(OFFlks, 'read', 'interferogram_azimuth_lines')
    
    nCenterWidth = str(int(nWidth) / 2)
    nCenterLine = str(int(nLine) / 2)
    
    if 'Ref_Range' in templateContents: Ref_Range = templateContents['Ref_Range']
    else: Ref_Range = nCenterWidth
    if 'Ref_Azimuth' in templateContents: Ref_Azimuth = templateContents['Ref_Azimuth']
    else: Ref_Azimuth = nCenterLine

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
    DIFFINTFILTlks = DIFFINTlks.replace('diff_', 'diff_filt_')
  
    CORFILTlks  = workDir + '/filt_' + Mdate + '-' + Sdate + '_' + rlks + 'rlks.cor'
    CORDIFFlks = workDir+'/diff_' + Mdate + '-' + Sdate + '_' + rlks + 'rlks.cor'
    CORDIFFFILTlks = workDir+'/diff_filt_' + Mdate + '-' + Sdate + '_' + rlks + 'rlks.cor'
    
    MASKTHINlks  = CORFILTlks + 'maskt.bmp'
    MASKTHINDIFFlks  = CORDIFFFILTlks + 'maskt.bmp'
   

 ####  unwrapping differential interferogram ####
### if topo case, it calls FLTFILTlks
### else if diff case, it calls DIFFINTFILTlks

    if flagTopo == 'Y':
        if flatteningIgram == 'orbit':
            FLTFILTlks = FLTlks.replace('flat_', 'filt_')
        else :
            FLTFILTlks = FLTFFTlks.replace('flat_', 'filt_')
            WRAPlks = FLTFILTlks      
    else:
        if flatteningDiff == 'orbit':
            DIFFINTFILTlks = DIFFINTlks.replace('diff_', 'diff_filt_')    
        else:
            DIFFINTFILTlks = DIFFINTFFTlks.replace('diff_', 'diff_filt_')
    
    WRAPlks = DIFFINTFILTlks
    UWNTHINlks   = WRAPlks.replace('.int', '.unw_thinned.bmp')
    UNWINTERPlks = WRAPlks.replace('.int', '.unw_interp')
    UNWlks       = WRAPlks.replace('.int', '.unw')
 
    
#########################################################    
    
    CORFILTlksbmp = CORFILTlks + '_mask.bmp'
    
    call_str = '$GAMMA_BIN/rascc_mask ' + CORFILTlks + ' ' + MampImglks + ' ' + nWidth + ' 1 1 0 1 1 ' + unwrappedThresholdDiff + ' 0.0 0.1 0.9 1. .35 1 ' + CORFILTlksbmp   # based on int coherence
    os.system(call_str)
    
    call_str = '$GAMMA_BIN/rascc_mask_thinning ' + CORFILTlksbmp + ' ' + CORFILTlks + ' ' + nWidth + ' ' + MASKTHINlks + ' 5 0.3 0.4 0.5 0.6 0.7'
    os.system(call_str)    

###################################################   

    CORDIFFFILTlksbmp = CORDIFFFILTlks + '_mask.bmp'
    
    call_str = '$GAMMA_BIN/rascc_mask ' + CORDIFFFILTlks + ' ' + MampImglks + ' ' + nWidth + ' 1 1 0 1 1 ' + unwrappedThresholdDiff + ' 0.0 0.1 0.9 1. .35 1 ' + CORDIFFFILTlksbmp   # based on diff coherence
    os.system(call_str)
    
    call_str = '$GAMMA_BIN/rascc_mask_thinning ' + CORDIFFFILTlksbmp + ' ' + CORDIFFFILTlks + ' ' + nWidth + ' ' + MASKTHINDIFFlks + ' 5 0.3 0.4 0.5 0.6 0.7'
    os.system(call_str)
#################################################

    call_str = '$GAMMA_BIN/mcf ' + WRAPlks + ' ' + CORDIFFFILTlks + ' ' + MASKTHINDIFFlks + ' ' + UNWlks + ' ' + nWidth + ' 1 0 0 - - ' + unwrappatrDiff + ' ' + unwrappatazDiff + ' - ' + Ref_Range + ' ' + Ref_Azimuth   #choose the reference point center
    os.system(call_str)

    call_str = '$GAMMA_BIN/interp_ad ' + UNWlks + ' ' + UNWINTERPlks + ' ' + nWidth
    os.system(call_str)

    call_str = '$GAMMA_BIN/unw_model ' + WRAPlks + ' ' + UNWINTERPlks + ' ' + UNWlks + ' ' + nWidth
    os.system(call_str)

    call_str = '$GAMMA_BIN/rasrmg ' + UNWlks + ' ' + MampImglks + ' ' + nWidth + ' - - - - - - - - - - ' 
    os.system(call_str)

    ras2jpg(UNWlks, UNWlks)

    if flatteningDiff == 'quadfit':
        QUADFIT       = WRAPlks.replace('.int', '.quad_fit')

        call_str = '$GAMMA_BIN/create_diff_par ' + OFFlks + ' ' + OFFlks + ' ' + DIFFpar + ' - 0'
        os.system(call_str)

        call_str = '$GAMMA_BIN/quad_fit ' + UNWlks + ' ' + DIFFpar + ' 32 32 ' + CORFILTlks + '_mask.bmp ' + QUADFIT + ' 0'
        os.system(call_str)

        call_str = '$GAMMA_BIN/quad_sub ' + WRAPlks + ' ' + DIFFpar + ' ' + WRAPlks + '.tmp 1 0'
        os.system(call_str)

        os.rename(WRAPlks+'.tmp', WRAPlks)


    print "Uwrapping interferometric phase is done!"
 
    sys.exit(1)

if __name__ == '__main__':
    main(sys.argv[:])
