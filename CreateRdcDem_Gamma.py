#! /usr/bin/env python
#'''
###################################################################################
#                                                                                 #
#            Author:   Yun-Meng Cao                                               #
#            Email :   ymcmrs@gmail.com                                           #
#            Date  :   February, 2017                                             #
#                                                                                 #
#   Coregistration of SAR images based on cross-correlation with DEM assisstance  #
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
   
            CreateRdcDem_Gamma.py igramDir
      
      e.g.  CreateRdcDem_Gamma.py IFGRAM_PacayaT163TsxHhA_131021-131101_0011_-0007
          
            
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
    
    dem=templateContents['DEM']
    demPar = dem + ".par"
    
# simulate phase process

# Parameter setting for simPhase


    if 'raw2slc_OrbitType'          in templateContents: orbitType = templateContents['raw2slc_OrbitType']                
    else: orbitType = 'HDR'
    if 'Igram_Flattening' in templateContents: flatteningIgram = templateContents['Igram_Flattening']
    else: flatteningIgram = 'orbit'

    if 'Simphase_Flag'          in templateContents: flagSimphase = templateContents['Simphase_Flag']                
    else: flagSimphase = 'Y'
    if 'Simphase_Lat_Ovr'          in templateContents: latovrSimphase = templateContents['Simphase_Lat_Ovr']                
    else: latovrSimphase = '4'
    if 'Simphase_Lon_Ovr'          in templateContents: lonovrSimphase = templateContents['Simphase_Lon_Ovr']                
    else: lonovrSimphase = '4'

    if 'Simphase_rlks'          in templateContents: rlksSimphase = templateContents['Simphase_rlks']                
    else: rlksSimphase = '2'
    if 'Simphase_azlks'          in templateContents: azlksSimphase = templateContents['Simphase_azlks']                
    else: azlksSimphase = '2'
    if 'Simphase_rpos'          in templateContents: rposSimphase = templateContents['Simphase_rpos']                
    else: rposSimphase = '-'
    if 'Simphase_azpos'          in templateContents: azposSimphase = templateContents['Simphase_azpos']                
    else: azposSimphase = '-'
    if 'Simphase_patch'          in templateContents: patchSimphase = templateContents['Simphase_patch']                
    else: patchSimphase = '512'
    if 'Simphase_rwin'          in templateContents: rwinSimphase = templateContents['Simphase_rwin']                
    else: rwinSimphase = '512'
    if 'Simphase_azwin'          in templateContents: azwinSimphase = templateContents['Simphase_azwin']                
    else: azwinSimphase = '512'
    if 'Simphase_thresh'          in templateContents: threshSimphase = templateContents['Simphase_thresh']                
    else: threshSimphase = '7.0'

    if 'Igram_Flag_TDM' in templateContents: flagTDM = templateContents['Igram_Flag_TDM']
    else: flagTDM = 'N'

#  Definition of file

    MslcImg     = workDir + '/' + Mdate + '.slc'
    MslcPar     = workDir + '/' + Mdate + '.slc.par'
    MampImg     = workDir + '/' + Mdate + '.amp'
    MampPar     = workDir + '/' + Mdate + '.amp.par'

    SslcImg     = workDir + '/' + Sdate + '.slc'
    SslcPar     = workDir + '/' + Sdate + '.slc.par'
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

    UTMDEMpar   = simDir + '/sim_' + Mdate + '-' + Sdate + '.utm.dem.par'
    UTMDEM      = simDir + '/sim_' + Mdate + '-' + Sdate + '.utm.dem'
    UTM2RDC     = simDir + '/sim_' + Mdate + '-' + Sdate + '.utm_to_rdc'
    SIMSARUTM   = simDir + '/sim_' + Mdate + '-' + Sdate + '.sim_sar_utm'
    PIX         = simDir + '/sim_' + Mdate + '-' + Sdate + '.pix'
    LSMAP       = simDir + '/sim_' + Mdate + '-' + Sdate + '.ls_map'
    SIMSARRDC   = simDir + '/sim_' + Mdate + '-' + Sdate + '.sim_sar_rdc'
    SIMDIFFpar  = simDir + '/sim_' + Mdate + '-' + Sdate + '.diff_par'
    SIMOFFS     = simDir + '/sim_' + Mdate + '-' + Sdate + '.offs'
    SIMSNR      = simDir + '/sim_' + Mdate + '-' + Sdate + '.snr'
    SIMOFFSET   = simDir + '/sim_' + Mdate + '-' + Sdate + '.offset'
    SIMCOFF     = simDir + '/sim_' + Mdate + '-' + Sdate + '.coff'
    SIMCOFFSETS = simDir + '/sim_' + Mdate + '-' + Sdate + '.coffsets'
    UTMTORDC    = simDir + '/sim_' + Mdate + '-' + Sdate + '.UTM_TO_RDC'
    HGTSIM      = simDir + '/sim_' + Mdate + '-' + Sdate + '.rdc.dem'
    SIMUNW      = simDir + '/sim_' + Mdate + '-' + Sdate + '.sim_unw'

    GEORAWINT   = workDir + '/geo_' + igramDir.split(projectName+'_')[1] + '.raw.int'  
    GEOINT      = workDir + '/geo_' + igramDir.split(projectName+'_')[1] + '.int'
    GEOPWR      = workDir + '/geo_' + igramDir.split(projectName+'_')[1] + '.amp'
    GEOCOR      = workDir + '/geo_' + igramDir.split(projectName+'_')[1] + '.cor'

    
    if not (os.path.isdir(simDir)):
        os.makedirs(simDir)    
    createBlankFile(BLANK)


### remove DEM look up table if it existed for considering gamma overlapping

    if os.path.isfile(UTMDEM):   
        os.remove(UTMDEM)
    if os.path.isfile(UTMDEMpar):   
        os.remove(UTMDEMpar)
    if os.path.isfile(UTM2RDC):   
        os.remove(UTM2RDC)

    call_str = "$GAMMA_BIN/multi_look " + MslcImg + " " + MslcPar + " " + MampImglks + " " + MampParlks + " " + rlks + " " + azlks
    os.system(call_str)

    call_str = '$GAMMA_BIN/gc_map ' + MslcPar + ' ' + '-' + ' ' + demPar + ' ' + dem + ' ' + UTMDEMpar + ' ' + UTMDEM + ' ' + UTM2RDC + ' ' + latovrSimphase + ' ' + lonovrSimphase + ' ' + SIMSARUTM + ' - - - - ' + PIX + ' ' + LSMAP
    os.system(call_str)

    nWidthUTMDEM = UseGamma(UTMDEMpar, 'read', 'width')
    nLinePWR1 = UseGamma(MampParlks, 'read', 'azimuth_lines')
    nWidth = UseGamma(MampParlks, 'read', 'range_samples')
   
    call_str = '$GAMMA_BIN/geocode ' + UTM2RDC + ' ' + SIMSARUTM + ' ' + nWidthUTMDEM + ' ' + SIMSARRDC + ' ' + nWidth + ' ' + nLinePWR1 + ' 0 0'
    os.system(call_str)

    call_str = '$GAMMA_BIN/create_diff_par ' + MampParlks + ' ' + MampParlks + ' ' + SIMDIFFpar + ' 0 < ' + BLANK
    os.system(call_str)

    call_str = '$GAMMA_BIN/init_offsetm ' + SIMSARRDC + ' ' + MampImglks + ' ' + SIMDIFFpar + ' ' + rlksSimphase + ' ' + azlksSimphase + ' ' + rposSimphase + ' ' + azposSimphase + ' - - - ' + patchSimphase
    os.system(call_str)

    call_str = '$GAMMA_BIN/offset_pwrm ' + SIMSARRDC + ' ' + MampImglks + ' ' + SIMDIFFpar + ' ' + SIMOFFS + ' ' + SIMSNR + ' ' + rwinSimphase + ' ' + azwinSimphase + ' ' + SIMOFFSET # + ' 1 - - ' + threshSimphase 
    os.system(call_str)

    call_str = '$GAMMA_BIN/offset_fitm ' + SIMOFFS + ' ' + SIMSNR + ' ' + SIMDIFFpar + ' ' + SIMCOFF + ' ' + SIMCOFFSETS + ' 0.5'
    os.system(call_str)

    call_str = '$GAMMA_BIN/gc_map_fine ' + UTM2RDC + ' ' + nWidthUTMDEM + ' ' + SIMDIFFpar + ' ' + UTMTORDC + ' 1'
    os.system(call_str)

    call_str = '$GAMMA_BIN/geocode ' + UTMTORDC + ' ' + UTMDEM + ' ' + nWidthUTMDEM + ' ' + HGTSIM + ' ' + nWidth + ' ' + nLinePWR1 + ' 0 0 - - 1 1 1'
    os.system(call_str)



    print "Create DEM in Radar Coordinates is done!"
    sys.exit(1)

if __name__ == '__main__':
    main(sys.argv[:])