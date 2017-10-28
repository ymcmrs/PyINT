#! /usr/bin/env python
#################################################################
###  This program is part of PyINT  v1.0                      ### 
###  Copy Right (c): 2017, Yunmeng Cao                        ###  
###  Author: Yunmeng Cao                                      ###                                                          
###  Email : ymcmrs@gmail.com                                 ###
###  Univ. : Central South University & University of Miami   ###   
#################################################################

import numpy as np
import os
import sys  
import subprocess
import getopt
import time
import glob

def check_variable_name(path):
    s=path.split("/")[0]
    if len(s)>0 and s[0]=="$":
        p0=os.getenv(s[1:])
        path=path.replace(path.split("/")[0],p0)
    return path

def read_template(File, delimiter='='):
    '''Reads the template file into a python dictionary structure.
    Input : string, full path to the template file
    Output: dictionary, pysar template content
    Example:
        tmpl = read_template(KyushuT424F610_640AlosA.template)
        tmpl = read_template(R1_54014_ST5_L0_F898.000.pi, ':')
    '''
    template_dict = {}
    for line in open(File):
        line = line.strip()
        c = [i.strip() for i in line.split(delimiter, 1)]  #split on the 1st occurrence of delimiter
        if len(c) < 2 or line.startswith('%') or line.startswith('#'):
            next #ignore commented lines or those without variables
        else:
            atrName  = c[0]
            atrValue = str.replace(c[1],'\n','').split("#")[0].strip()
            atrValue = check_variable_name(atrValue)
            template_dict[atrName] = atrValue
    return template_dict


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
    if ( inFile.rsplit('.')[1] == 'int' or inFile.rsplit('.')[1] == 'diff' ):
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
      
      e.g.  Geocode_Gamma.py IFG_PacayaT163TsxHhA_131021-131101_0011_0007
      e.g.  Geocode_Gamma.py MAI_PacayaT163TsxHhA_131021-131101_0011_0007
      e.g.  Geocode_Gamma.py SPI_PacayaT163TsxHhA_131021-131101_0011_0007          
            
*******************************************************************************************************
    '''   
    
def main(argv):
    
    if len(sys.argv)==2:
        if argv[0] in ['-h','--help']: usage(); sys.exit(1)
        else: igramDir=sys.argv[1]        
    else:
        usage();sys.exit(1)
    
    INF = igramDir.split('_')[0]
    projectName = igramDir.split('_')[1]
    IFGPair = igramDir.split(projectName+'_')[1].split('_')[0]
    Mdate = IFGPair.split('-')[0]
    Sdate = IFGPair.split('-')[1]
    
    scratchDir = os.getenv('SCRATCHDIR')
    templateDir = os.getenv('TEMPLATEDIR')
    templateFile = templateDir + "/" + projectName + ".template"
    
    processDir = scratchDir + '/' + projectName + "/PROCESS"
    slcDir     = scratchDir + '/' + projectName + "/SLC"
    rslcDir     = scratchDir + '/' + projectName + "/RSLC"
    workDir    = processDir + '/' + igramDir   
    demDir     = processDir + '/DEM'
    simDir     = demDir
    MslcDir = rslcDir + '/' + Mdate
    SslcDir = rslcDir + '/' + Sdate
    
    templateContents=read_template(templateFile)
    if 'Resamp_All'          in templateContents: Resamp_All = templateContents['Resamp_All']                
    else: Resamp_All = '1'
    
    rlks = templateContents['Range_Looks']
    azlks = templateContents['Azimuth_Looks']
    masterDate = templateContents['masterDate']
    masterDir = rslcDir + '/' + masterDate
    
    
    if not Resamp_All=='1':
        masterDate = Mdate
    
    UTMDEMpar   = simDir + '/sim_' + masterDate + '_'+rlks +'rlks.utm.dem.par'
    UTMDEM      = simDir + '/sim_' + masterDate + '_'+rlks +'rlks.utm.dem'
    UTM2RDC     = simDir + '/sim_' + masterDate + '_'+rlks +'rlks.utm_to_rdc'
    SIMSARUTM   = simDir + '/sim_' + masterDate + '_'+rlks +'rlks.sim_sar_utm'
    PIX         = simDir + '/sim_' + masterDate + '_'+rlks +'rlks.pix'
    LSMAP       = simDir + '/sim_' + masterDate + '_'+rlks +'rlks.ls_map'
    SIMSARRDC   = simDir + '/sim_' + masterDate + '_'+rlks +'rlks.sim_sar_rdc'
    SIMDIFFpar  = simDir + '/sim_' + masterDate + '_'+rlks +'rlks.diff_par'
    SIMOFFS     = simDir + '/sim_' + masterDate + '_'+rlks +'rlks.offs'
    SIMSNR      = simDir + '/sim_' + masterDate + '_'+rlks +'rlks.snr'
    SIMOFFSET   = simDir + '/sim_' + masterDate + '_'+rlks +'rlks.offset'
    SIMCOFF     = simDir + '/sim_' + masterDate + '_'+rlks +'rlks.coff'
    SIMCOFFSETS = simDir + '/sim_' + masterDate + '_'+rlks +'rlks.coffsets'
    UTMTORDC    = simDir + '/sim_' + masterDate + '_'+rlks +'rlks.UTM_TO_RDC'
    HGTSIM      = simDir + '/sim_' + masterDate + '_'+rlks +'rlks.rdc.dem'
    SIMUNW      = simDir + '/sim_' + masterDate + '_'+rlks +'rlks.sim_unw'
    
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

    if 'Topo_Flag'          in templateContents: flagTopo = templateContents['Topo_Flag']
    else: flagTopo = 'N'
    if 'Igram_Flattening' in templateContents: flatteningIgram = templateContents['Igram_Flattening']
    else: flatteningIgram = 'orbit'
    if 'Diff_Flattening'          in templateContents: flatteningDiff = templateContents['Diff_Flattening']      
    else: flatteningDiff = 'orbit'     
    if 'Unwrap_Flattening'          in templateContents: flatteningUnwrap = templateContents['Unwrap_Flattening']      
    else: flatteningUnwrap = 'N'       
   
        
    MamprlksImg = MslcDir  + '/' + Mdate + '_' + rlks + 'rlks.amp'
    MamprlksPar = MslcDir  + '/' + Mdate + '_' + rlks + 'rlks.amp.par'
    
    MrslcPar = workDir  + '/' + Mdate + '.rslc.par'
    MrslcImg = workDir  + '/' + Mdate + '.rslc'
    SrslcPar = workDir  + '/' + Sdate + '.rslc.par'
    SrslcImg = workDir  + '/' + Sdate + '.rslc'
    
    
    if Resamp_All=='1':
        MamprlksImg = masterDir  + '/' + masterDate + '_' + rlks + 'rlks.amp'
        MamprlksPar = masterDir  + '/' + masterDate + '_' + rlks + 'rlks.amp.par'
        MrslcPar = MslcDir  + '/' + Mdate + '.rslc.par'
        MrslcImg = MslcDir  + '/' + Mdate + '.rslc'
        SrslcPar = SslcDir  + '/' + Sdate + '.rslc.par'
        SrslcImg = SslcDir  + '/' + Sdate + '.rslc'
  
    
#  Definition of file
    UNWlks = workDir + '/diff_filt_' + Mdate + '-' + Sdate + '_' + rlks + 'rlks.unw'
    CORDIFFFILTlks = workDir + '/diff_filt_' + Mdate + '-' + Sdate + '_' + rlks + 'rlks.cor'    
    DIFFINTFILTlks = workDir + '/diff_filt_' + Mdate + '-' + Sdate + '_' + rlks + 'rlks.int'
    QUADUNWlks = UNWlks.replace('.unw','.quad_fit.unw')
    OFFlks = workDir + '/' + Mdate + '-' + Sdate + '_' + rlks + 'rlks.off'
    
    GEOPWR      = geoDir + '/geo_' + os.path.basename(MamprlksImg)
    GEOCOR      = geoDir + '/geo_' + Mdate + '-' + Sdate + '_'+rlks + 'rlks.diff_filt.cor' 
    GEODIFFINT  = geoDir + '/geo_' + Mdate + '-' + Sdate + '_'+rlks + 'rlks.diff_filt.int'
    GEOUNW      = geoDir + '/geo_' + Mdate + '-' + Sdate + '_'+rlks + 'rlks.unw'
    GEOQUADUNW  = geoDir + '/geo_' + Mdate + '-' + Sdate + '_'+rlks + 'rlks.quad_fit.unw'

    if os.path.isfile(OFFlks):
        os.remove(OFFlks)
        
    call_str = 'create_offset ' +  MrslcPar + ' ' +   SrslcPar + ' ' + OFFlks + ' 1 ' + rlks + ' ' + azlks + ' 0'
    os.system(call_str)

    nWidth = UseGamma(OFFlks, 'read', 'interferogram_width')
    nWidthUTMDEM = UseGamma(UTMDEMpar, 'read', 'width')
    nLineUTMDEM = UseGamma(UTMDEMpar, 'read', 'nlines')


#    if flatteningIgram == 'fft':
#      FLTlks = FLTFFTlks 

#    FLTFILTlks = FLTlks.replace('flat_', 'filt_')

    geocode(MamprlksImg, GEOPWR, UTMTORDC, nWidth, nWidthUTMDEM, nLineUTMDEM)
    geocode(CORDIFFFILTlks, GEOCOR, UTMTORDC, nWidth, nWidthUTMDEM, nLineUTMDEM)
        #geocode(FLTlks, GEOINT, UTMTORDC, nWidth, nWidthUTMDEM, nLineUTMDEM)
        #geocode(FLTFILTlks, GEOFILTINT, UTMTORDC, nWidth, nWidthUTMDEM, nLineUTMDEM)

    call_str = '$GAMMA_BIN/raspwr ' + GEOPWR + ' ' + nWidthUTMDEM + ' - - - - - - - '
    os.system(call_str)

    ras2jpg(GEOPWR, GEOPWR)

    call_str = '$GAMMA_BIN/rascc ' + GEOCOR + ' ' + nWidthUTMDEM + ' - - - - - - - - - -' 
    os.system(call_str)
    ras2jpg(GEOCOR, GEOCOR) 

    geocode(DIFFINTFILTlks, GEODIFFINT, UTMTORDC, nWidth, nWidthUTMDEM, nLineUTMDEM)
    geocode(UNWlks, GEOUNW, UTMTORDC, nWidth, nWidthUTMDEM, nLineUTMDEM)

    call_str = '$GAMMA_BIN/rasmph_pwr ' + GEODIFFINT + ' ' + GEOPWR + ' ' + nWidthUTMDEM + ' - - - - - 2.0 0.3 - ' 
    os.system(call_str)
    ras2jpg(GEODIFFINT, GEODIFFINT) 

    call_str = '$GAMMA_BIN/rasrmg ' + GEOUNW + ' ' + GEOPWR + ' ' + nWidthUTMDEM + ' - - - - - - - - - - ' 
    os.system(call_str)
    ras2jpg(GEOUNW, GEOUNW) 
   
    if flatteningUnwrap == 'Y':
        geocode(QUADUNWlks, GEOQUADUNW, UTMTORDC, nWidth, nWidthUTMDEM, nLineUTMDEM)
        call_str = '$GAMMA_BIN/rasrmg ' + GEOQUADUNW + ' ' + GEOPWR + ' ' + nWidthUTMDEM + ' - - - - - - - - - - ' 
        os.system(call_str)
        ras2jpg(GEOQUADUNW, GEOQUADUNW) 
                
    
    print "Geocoding is done!" 
    sys.exit(1)

if __name__ == '__main__':
    main(sys.argv[:])
