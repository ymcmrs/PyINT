#! /usr/bin/env python
#'''
###################################################################################
#                                                                                 #
#            Author:   Yun-Meng Cao                                               #
#            Email :   ymcmrs@gmail.com                                           #
#            Date  :   February, 2017                                             #
#                                                                                 #
#         GEOCODING GAMMA FILES: INT, SLC, MLI, UNW, COR, ...                     #
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
    if inFile.rsplit('.')[len(inFile.rsplit('.'))-1] == 'int':
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
 
          Geocoding GAMMA files: slc, mli, int, unw, flt, cor...
       

   usage:
   
            Geocode_Gamma.py igramDir
      
      e.g.  Geocode_Gamma.py IFGRAM_PacayaT163TsxHhA_131021-131101_0011_-0007
          
            
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
    simDir = simDir + '/sim_' + Mdate + '-' + Sdate
    
    geoDir= scratchDir + '/' + projectName + "/PROCESS" + "/GEO"  
    if not os.path.isdir(geoDir):
        str_call="mkdir " + geoDir
        os.system(str_call)
    
    geoDir = geoDir + "/geo_" + IFGPair
    if not os.path.isdir(geoDir):
        str_call="mkdir " + geoDir
        os.system(str_call)
    
    
    ### geocode process

    if 'raw2slc_OrbitType'          in templateContents: orbitType = templateContents['raw2slc_OrbitType']                
    else: orbitType = 'HDR'
    if 'Geocode_Flag'          in templateContents: flagGeocode = templateContents['Geocode_Flag']                
    else: flagGeocode = 'Y'
    if 'Igram_Flattening' in templateContents: flatteningIgram = templateContents['Igram_Flattening']
    else: flatteningIgram = 'orbit'
    if 'Diff_Flattening'          in templateContents: flatteningDiff = templateContents['Diff_Flattening']      
    else: flatteningDiff = 'orbit'
        
    if 'Unwrap_Flattening'          in templateContents: flatteningUnwrap = templateContents['Unwrap_Flattening']      
    else: flatteningUnwrap = 'No' 
        
    if 'Topo_Flag'          in templateContents: flagTopo = templateContents['Topo_Flag']
    else: flagTopo = 'N'


#  Definition of file

    MRSLCImg     = workDir + '/' + Mdate + '.RSLC'
    MRSLCPar     = workDir + '/' + Mdate + '.RSLC.par'
    MampImg     = workDir + '/' + Mdate + '.amp'
    MampPar     = workDir + '/' + Mdate + '.amp.par'

    SRSLCImg     = workDir + '/' + Sdate + '.RSLC'
    SRSLCPar     = workDir + '/' + Sdate + '.RSLC.par'
    SampImg     = workDir + '/' + Sdate + '.amp'
    SampPar     = workDir + '/' + Sdate + '.amp.par'

    BLANK       = workDir + '/' + Mdate + '-' + Sdate + '.blk'
    OFF         = workDir + '/' + Mdate + '-' + Sdate + '.off'
    INT         = workDir + '/' + Mdate + '-' + Sdate + '.int'
    INTlks      = workDir + '/' + Mdate + '-' + Sdate + '_' + rlks + 'rlks.int'
    OFFlks      = workDir + '/' + Mdate + '-' + Sdate + '_' + rlks + 'rlks.off'
    FLTlks      = workDir + '/flat_' + orbitType + '_' + Mdate + '-' + Sdate + '_' + rlks + 'rlks.int'
    FLTFFTlks   = FLTlks.replace('flat_', 'flat_sim_')
    FLTFILTlks = FLTlks.replace('flat_', 'filt_')
    DIFFINTlks  = workDir + '/diff_' + orbitType + '_' + Mdate + '-' + Sdate + '_' + rlks + 'rlks.int'  
    DIFFINTFFTlks = DIFFINTlks.replace('diff_', 'diff_sim_')

    MampImglks  = workDir + '/' + Mdate + '_' + rlks + 'rlks.amp'
    MampParlks  = workDir + '/' + Mdate + '_' + rlks + 'rlks.amp.par'
    SampImglks  = workDir + '/' + Sdate + '_' + rlks + 'rlks.amp'
    SampParlks  = workDir + '/' + Sdate + '_' + rlks + 'rlks.amp.par'
    CORlks      = workDir + '/' + Mdate + '-' + Sdate + '_' + rlks + 'rlks.cor'
    CORFILTlks  = workDir + '/filt_' + Mdate + '-' + Sdate + '_' + rlks + 'rlks.cor'
    CORDIFFlks = workDir+'/diff_' + Mdate + '-' + Sdate + '_' + rlks + 'rlks.cor'
    CORDIFFFILTlks = workDir+'/diff_filt_' + Mdate + '-' + Sdate + '_' + rlks + 'rlks.cor'
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

    GEORAWINT   = geoDir + '/geo_' + Mdate + '-' + Sdate + '.int'  
    GEOINT      = geoDir + '/geo_' + Mdate + '-' + Sdate + '.filt.int'
    GEOPWR      = geoDir + '/geo_' + Mdate + '-' + Sdate + '.amp'
    GEOCOR      = geoDir + '/geo_' + Mdate + '-' + Sdate + '.diff.cor'
    GEODIFFRAWINT      = geoDir + '/geo_' + Mdate + '-' + Sdate + '.diff.int'
    GEODIFFINT      = geoDir + '/geo_' + Mdate + '-' + Sdate + '.diff_filt.int'
    GEOUNW      = geoDir + '/geo_' + Mdate + '-' + Sdate + '.unw'
    GEOQUADUNW  = geoDir + '/geo_' + Mdate + '-' + Sdate + '.quad_fit.unw'
    
    if flagGeocode == 'Y':
        print "Geocoding process would be started on " + workDir + "\n"

    if not (os.path.isfile(UTMDEMpar) or os.path.isfile(UTMTORDC)):
        print "Look-up table for geocoding is not found, please run phase simulation before geocode \n" 
        logger.info("Look-up table for geocoding is not found, please run phase simulation before geocode \n" )
        sys.exit(0)

    nWidth = UseGamma(OFFlks, 'read', 'interferogram_width')
    nWidthUTMDEM = UseGamma(UTMDEMpar, 'read', 'width')
    nLineUTMDEM = UseGamma(UTMDEMpar, 'read', 'nlines')

    if flatteningIgram == 'orbit':
        FLTFILTlks = FLTlks.replace('flat_', 'filt_')
    else :
        FLTFILTlks = FLTFFTlks.replace('flat_', 'filt_')

    if flatteningDiff == 'orbit':
        DIFFINTFILTlks = DIFFINTlks.replace('diff_', 'diff_filt_')    
    else:
        DIFFINTFILTlks = DIFFINTFFTlks.replace('diff_', 'diff_filt_')

    if flagTopo == 'Y':
        WRAPlks = FLTFILTlks      
    else:
        WRAPlks = DIFFINTFILTlks

    UNWlks       = WRAPlks.replace('.int', '.unw')
    QUADUNWlks   = UNWlks.replace('.unw','._quad_fit.unw')
#    if flatteningIgram == 'fft':
#      FLTlks = FLTFFTlks 

#    FLTFILTlks = FLTlks.replace('flat_', 'filt_')

    geocode(MampImglks, GEOPWR, UTMTORDC, nWidth, nWidthUTMDEM, nLineUTMDEM)
    geocode(CORDIFFFILTlks, GEOCOR, UTMTORDC, nWidth, nWidthUTMDEM, nLineUTMDEM)
    geocode(FLTlks, GEORAWINT, UTMTORDC, nWidth, nWidthUTMDEM, nLineUTMDEM)
    geocode(FLTFILTlks, GEOINT, UTMTORDC, nWidth, nWidthUTMDEM, nLineUTMDEM)

    call_str = '$GAMMA_BIN/raspwr ' + GEOPWR + ' ' + nWidthUTMDEM + ' - - - - - - - '
    os.system(call_str)

    ras2jpg(GEOPWR, GEOPWR)

    call_str = '$GAMMA_BIN/raspwr ' + GEOCOR + ' ' + nWidthUTMDEM + ' - - - - - - - ' 
    os.system(call_str)

    ras2jpg(GEOCOR, GEOCOR) 

    call_str = '$GAMMA_BIN/rasmph_pwr ' + GEORAWINT + ' ' + GEOPWR + ' ' + nWidthUTMDEM + ' - - - - - 2.0 0.3 - ' 
    os.system(call_str)

    ras2jpg(GEORAWINT, GEORAWINT)

    call_str = '$GAMMA_BIN/rasmph_pwr ' + GEOINT + ' ' + GEOPWR + ' ' + nWidthUTMDEM + ' - - - - - 2.0 0.3 - ' 
    os.system(call_str)

    ras2jpg(GEOINT, GEOINT)
 
    geocode(DIFFINTlks, GEODIFFRAWINT, UTMTORDC, nWidth, nWidthUTMDEM, nLineUTMDEM)
    geocode(DIFFINTFILTlks, GEODIFFINT, UTMTORDC, nWidth, nWidthUTMDEM, nLineUTMDEM)
    geocode(UNWlks, GEOUNW, UTMTORDC, nWidth, nWidthUTMDEM, nLineUTMDEM)

    call_str = '$GAMMA_BIN/rasmph_pwr ' + GEODIFFRAWINT + ' ' + GEOPWR + ' ' + nWidthUTMDEM + ' - - - - - 2.0 0.3 - ' 
    os.system(call_str)

    ras2jpg(GEODIFFRAWINT, GEODIFFRAWINT)

    call_str = '$GAMMA_BIN/rasmph_pwr ' + GEODIFFINT + ' ' + GEOPWR + ' ' + nWidthUTMDEM + ' - - - - - 2.0 0.3 - ' 
    os.system(call_str)

    ras2jpg(GEODIFFINT, GEODIFFINT) 

    call_str = '$GAMMA_BIN/rasrmg ' + GEOUNW + ' ' + GEOPWR + ' ' + nWidthUTMDEM + ' - - - - - - - - - - ' 
    os.system(call_str)

    ras2jpg(GEOUNW, GEOUNW) 

    
    if flatteningUnwrap == 'quadfit':
        geocode(QAUDUNWlks, GEOQUADUNW, UTMTORDC, nWidth, nWidthUTMDEM, nLineUTMDEM)
        call_str = '$GAMMA_BIN/rasrmg ' + GEOUNW + ' ' + GEOPWR + ' ' + nWidthUTMDEM + ' - - - - - - - - - - ' 
        os.system(call_str)

        ras2jpg(GEOQUADUNW, GEOQUADUNW) 
                
    
    
    
    print "Geocoding is done!"
 
    sys.exit(1)

if __name__ == '__main__':
    main(sys.argv[:])
