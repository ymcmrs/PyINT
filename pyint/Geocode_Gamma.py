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
        print("Keyword " + keyword + " doesn't exist in " + inFile)
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
    print('''
******************************************************************************************************
 
          Geocoding GAMMA files: slc, mli, int, unw, flt, cor...
       

   usage:
   
            Geocode_Gamma.py igramDir
      
      e.g.  Geocode_Gamma.py IFG_PacayaT163TsxHhA_131021-131101_0011_0007
      e.g.  Geocode_Gamma.py MAI_PacayaT163TsxHhA_131021-131101_0011_0007
      e.g.  Geocode_Gamma.py SPI_PacayaT163TsxHhA_131021-131101_0011_0007          
            
*******************************************************************************************************
    ''')   
    
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
    workDir    = processDir + '/' + igramDir   
    demDir     = processDir + '/DEM'
    
    templateContents=read_template(templateFile)
    rlks = templateContents['Range_Looks']
    azlks = templateContents['Azimuth_Looks']
    masterDate = templateContents['masterDate']

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

    if INF=='IFG':
        Suffix=['']
    elif INF=='MAI':
        Suffix=['.F','.B']
    elif INF=='RSI':
        Suffix=['.HF','.LF']
    else:
        print("The folder name %s cannot be identified !" % igramDir)
        usage();sys.exit(1)          
    
    ### geocode process

    if 'Topo_Flag'          in templateContents: flagTopo = templateContents['Topo_Flag']
    else: flagTopo = 'N'
    if 'Igram_Flattening' in templateContents: flatteningIgram = templateContents['Igram_Flattening']
    else: flatteningIgram = 'orbit'
    if 'Diff_Flattening'          in templateContents: flatteningDiff = templateContents['Diff_Flattening']      
    else: flatteningDiff = 'orbit'     
    if 'Unwrap_Flattening'          in templateContents: flatteningUnwrap = templateContents['Unwrap_Flattening']      
    else: flatteningUnwrap = 'N'       
    
    if 'unwrapMethod'          in templateContents: unwrapMethod = templateContents['unwrapMethod']                
    else: unwrapMethod = 'mcf'

#  Definition of file
    simDir = demDir
    
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


    for i in range(len(Suffix)):          
        MrslcImg = workDir + "/" + Mdate + Suffix[i]+".rslc"
        MrslcPar = workDir + "/" + Mdate + Suffix[i]+".rslc.par"
        SrslcImg = workDir + "/" + Sdate + Suffix[i]+".rslc"
        SrslcPar = workDir + "/" + Sdate + Suffix[i]+".rslc.par"   
        
        MamprlksImg = workDir + "/" + Mdate + '_'+rlks+'rlks'+Suffix[i]+".ramp"
        MamprlksPar = workDir + "/" + Mdate + '_'+rlks+'rlks'+Suffix[i]+".ramp.par"        
        SamprlksImg = workDir + "/" + Sdate + '_'+rlks+'rlks'+Suffix[i]+".ramp"
        SamprlksPar = workDir + "/" + Sdate + '_'+rlks+'rlks'+Suffix[i]+".ramp.par"
        
        OFF         = workDir + '/' + Mdate + '-' + Sdate + Suffix[i] + '.off'
        INT         = workDir + '/' + Mdate + '-' + Sdate + Suffix[i] + '.int'
        INTlks      = workDir + '/' + Mdate + '-' + Sdate + '_' + rlks + 'rlks' + Suffix[i] + '.int'
        OFFlks      = workDir + '/' + Mdate + '-' + Sdate + '_' + rlks + 'rlks' + Suffix[i] + '.off'
        FLTlks      = workDir + '/flat_' + Mdate + '-' + Sdate + '_' + rlks + 'rlks' + Suffix[i] + '.int'
        FLTFFTlks   = FLTlks.replace('flat_', 'flat_sim_')      

        CORlks      = workDir + '/' + Mdate + '-' + Sdate + '_' + rlks + 'rlks' + Suffix[i] + '.cor'
        CORFILTlks  = workDir + '/filt_' + Mdate + '-' + Sdate + '_' + rlks + 'rlks' + Suffix[i] + '.cor'

        BASE        = workDir + '/' + Mdate + '-' + Sdate + Suffix[i] + '.base'
        BASE_REF    = workDir + '/' + Mdate + '-' + Sdate + Suffix[i] + '.base_ref'
   
        DIFFpar     = workDir + '/' + Mdate + '-' + Sdate + Suffix[i] + '.diff.par'
    
        DIFFINTlks  = workDir + '/diff_' + Mdate + '-' + Sdate + '_' + rlks + 'rlks' + Suffix[i] + '.int'  
        DIFFINTFFTlks = DIFFINTlks.replace('diff_', 'diff_sim_')

        CORDIFFlks = workDir+'/diff_' + Mdate + '-' + Sdate + '_' + rlks + 'rlks' +  Suffix[i] + '.cor'
        CORDIFFFILTlks = workDir+'/diff_filt_' + Mdate + '-' + Sdate + '_' + rlks + 'rlks' + Suffix[i] + '.cor'
        
        MASKTHINlks  = CORFILTlks + 'maskt.bmp'
        MASKTHINDIFFlks  = CORDIFFFILTlks + 'maskt.bmp'
 
        GEOINT      = geoDir + '/geo_' + Mdate + '-' + Sdate + '_'+rlks + 'rlks' + Suffix[i] +'.int'  
        GEOFILTINT  = geoDir + '/geo_' + Mdate + '-' + Sdate + '_'+rlks + 'rlks' + Suffix[i] +'.filt.int'
        GEOPWR      = geoDir + '/geo_' + Mdate + '-' + Sdate + '_'+rlks + 'rlks' + Suffix[i] +'.amp'
        GEOCOR      = geoDir + '/geo_' + Mdate + '-' + Sdate + '_'+rlks + 'rlks' + Suffix[i] +'.diff.cor'
        
        GEODIFFRAWINT   = geoDir + '/geo_' + Mdate + '-' + Sdate + '_'+rlks + 'rlks' + Suffix[i] +'.diff.int'
        GEODIFFINT      = geoDir + '/geo_' + Mdate + '-' + Sdate + '_'+rlks + 'rlks' + Suffix[i] +'.diff_filt.int'
        GEOUNW      = geoDir + '/geo_' + Mdate + '-' + Sdate + '_'+rlks + 'rlks' + Suffix[i] +'.unw'
        GEOQUADUNW  = geoDir + '/geo_' + Mdate + '-' + Sdate + '_'+rlks + 'rlks' + Suffix[i] +'.quad_fit.unw'
 
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

        if unwrapMethod == "mcf":    
            UNWlks       = WRAPlks.replace('.int', '.unw')
        else:
            UNWlks       = WRAPlks.replace('.int', '.branch.unw')
            
        QUADUNWlks   = UNWlks.replace('.unw','.quad_fit.unw')


        nWidth = UseGamma(OFFlks, 'read', 'interferogram_width')
        nWidthUTMDEM = UseGamma(UTMDEMpar, 'read', 'width')
        nLineUTMDEM = UseGamma(UTMDEMpar, 'read', 'nlines')


#    if flatteningIgram == 'fft':
#      FLTlks = FLTFFTlks 

#    FLTFILTlks = FLTlks.replace('flat_', 'filt_')

        geocode(MamprlksImg, GEOPWR, UTMTORDC, nWidth, nWidthUTMDEM, nLineUTMDEM)
        geocode(CORDIFFFILTlks, GEOCOR, UTMTORDC, nWidth, nWidthUTMDEM, nLineUTMDEM)
        geocode(FLTlks, GEOINT, UTMTORDC, nWidth, nWidthUTMDEM, nLineUTMDEM)
        geocode(FLTFILTlks, GEOFILTINT, UTMTORDC, nWidth, nWidthUTMDEM, nLineUTMDEM)

        call_str = '$GAMMA_BIN/raspwr ' + GEOPWR + ' ' + nWidthUTMDEM + ' - - - - - - - '
        os.system(call_str)

        ras2jpg(GEOPWR, GEOPWR)

        call_str = '$GAMMA_BIN/rascc ' + GEOCOR + ' ' + nWidthUTMDEM + ' - - - - - - - - - -' 
        os.system(call_str)
        ras2jpg(GEOCOR, GEOCOR) 

        call_str = '$GAMMA_BIN/rasmph_pwr ' + GEOINT + ' ' + GEOPWR + ' ' + nWidthUTMDEM + ' - - - - - 2.0 0.3 - ' 
        os.system(call_str)
        ras2jpg(GEOINT, GEOINT)

        call_str = '$GAMMA_BIN/rasmph_pwr ' + GEOFILTINT + ' ' + GEOPWR + ' ' + nWidthUTMDEM + ' - - - - - 2.0 0.3 - ' 
        os.system(call_str)
        ras2jpg(GEOFILTINT, GEOFILTINT)
 
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
   
        if flatteningUnwrap == 'Y':
            geocode(QUADUNWlks, GEOQUADUNW, UTMTORDC, nWidth, nWidthUTMDEM, nLineUTMDEM)
            call_str = '$GAMMA_BIN/rasrmg ' + GEOQUADUNW + ' ' + GEOPWR + ' ' + nWidthUTMDEM + ' - - - - - - - - - - ' 
            os.system(call_str)
            ras2jpg(GEOQUADUNW, GEOQUADUNW) 
                
    
    print("Geocoding is done!") 
    sys.exit(1)

if __name__ == '__main__':
    main(sys.argv[:])
