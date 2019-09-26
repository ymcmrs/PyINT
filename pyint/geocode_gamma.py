#! /usr/bin/env python
#################################################################
###  This program is part of PyINT  v2.1                      ### 
###  Copy Right (c): 2017-2019, Yunmeng Cao                   ###  
###  Author: Yunmeng Cao                                      ###                                                          
###  Contact : ymcmrs@gmail.com                               ###  
#################################################################
import os
import sys  
import argparse

from pyint import _utils as ut
        
def geocode(inFile, outFile, UTMTORDC, nWidth, nWidthUTMDEM, nLineUTMDEM, geo_interp='0'):
    
    if '.unw' in os.path.basename(inFile):
        call_str = 'geocode_back ' + inFile + ' ' + nWidth + ' ' + UTMTORDC + ' ' + outFile + ' ' + nWidthUTMDEM + ' ' + nLineUTMDEM + ' ' + geo_interp + ' 0'
    elif '.amp' in os.path.basename(inFile):
        call_str = 'geocode_back ' + inFile + ' ' + nWidth + ' ' + UTMTORDC + ' ' + outFile + ' ' + nWidthUTMDEM + ' ' + nLineUTMDEM + ' ' + geo_interp + ' 0'
    elif '.cor' in os.path.basename(inFile):
        call_str = 'geocode_back ' + inFile + ' ' + nWidth + ' ' + UTMTORDC + ' ' + outFile + ' ' + nWidthUTMDEM + ' ' + nLineUTMDEM + ' ' + geo_interp + ' 0'
    else:
        call_str = 'geocode_back ' + inFile + ' ' + nWidth + ' ' + UTMTORDC + ' ' + outFile + ' ' + nWidthUTMDEM + ' ' + nLineUTMDEM+ ' ' + geo_interp + ' 1'

    os.system(call_str)
    
    return
    
INTRODUCTION = '''
-------------------------------------------------------------------  
 Convert radar-coordinates unw-ifg and diff-ifg into geo-coordinates using GAMMA.
   
'''

EXAMPLE = '''
    Usage: 
            geocode_gamma.py projectName Mdate-Sdate
            geocode_gamma.py PacayaT163TsxHhA 20150102-20150601
-------------------------------------------------------------------  
'''

def cmdLineParse():
    parser = argparse.ArgumentParser(description='Unwrap differential interferogram using GAMMA-mcf method.',\
                                     formatter_class=argparse.RawTextHelpFormatter,\
                                     epilog=INTRODUCTION+'\n'+EXAMPLE)

    parser.add_argument('projectName',help='projectName for processing.')
    parser.add_argument('pair',help='Master-Slave, e.g., 20150101-20150106.')
    
    inps = parser.parse_args()
    return inps


def main(argv):
    
    inps = cmdLineParse() 
    projectName = inps.projectName
    Pair = inps.pair
    
    scratchDir = os.getenv('SCRATCHDIR')
    ifgDir = scratchDir + '/' + projectName + "/ifgrams"
    demDir = scratchDir + '/' + projectName + "/DEM"
    workDir = ifgDir + '/' + Pair

    templateDir = os.getenv('TEMPLATEDIR')
    templateFile = templateDir + "/" + projectName + ".template"
    templateDict=ut.update_template(templateFile)
    rlks = templateDict['range_looks']
    azlks = templateDict['azimuth_looks']
    masterDate = templateDict['masterDate']
    
    slcDir     = scratchDir + '/' + projectName + "/SLC" 
    rslcDir    = scratchDir + '/' + projectName + "/RSLC"
    demDir     = scratchDir + '/' + projectName + '/DEM'
    
    ######### copy common file for parallel processing #############
    
    Mamp0    = rslcDir + '/' + masterDate + '/' + masterDate + '_' + rlks + 'rlks.amp'
    MampPar0 = rslcDir + '/' + masterDate + '/' + masterDate + '_' + rlks + 'rlks.amp.par'
    
    Mamp     = workDir + '/' + masterDate + '_' + rlks + 'rlks.amp'
    MampPar  = workDir + '/' + masterDate + '_' + rlks + 'rlks.amp.par'
    
    ut.copy_file(Mamp0,Mamp)
    ut.copy_file(MampPar0,MampPar)
    
    #################################################################
    UNWIFG     =  workDir + '/' + Pair + '_' + rlks + 'rlks.diff_filt.unw'
    DIFFIFG    =  workDir + '/' + Pair + '_' + rlks + 'rlks.diff_filt'
    CORIFG     =  workDir + '/' + Pair + '_' + rlks + 'rlks.diff_filt.cor'
    
    GeoMamp    =  workDir + '/geo_' + masterDate + '_' + rlks + 'rlks.amp'
    GeoCOR    =  workDir + '/geo_' + masterDate + '_' + rlks + 'rlks.diff_filt.cor'
    GeoUNW     =  workDir + '/geo_' + Pair + '_' + rlks + 'rlks.diff_filt.unw'
    GeoDIFF    =  workDir + '/geo_' + Pair + '_' + rlks + 'rlks.diff_filt'
    
    UTMTORDC0 = demDir + '/' + masterDate + '_' + rlks + 'rlks.UTM_TO_RDC'
    UTMDEMpar0 = demDir + '/' + masterDate + '_' + rlks + 'rlks.utm.dem.par'
    
    UTMTORDC = workDir + '/' + masterDate + '_' + rlks + 'rlks.UTM_TO_RDC'
    UTMDEMpar = workDir + '/' + masterDate + '_' + rlks + 'rlks.utm.dem.par'
    
    ut.copy_file(UTMTORDC0,UTMTORDC)
    ut.copy_file(UTMDEMpar0,UTMDEMpar)

    nWidth = ut.read_gamma_par(MampPar, 'read', 'range_samples')
    nWidthUTMDEM = ut.read_gamma_par(UTMDEMpar, 'read', 'width')
    nLineUTMDEM = ut.read_gamma_par(UTMDEMpar, 'read', 'nlines')

    geocode(Mamp, GeoMamp, UTMTORDC, nWidth, nWidthUTMDEM, nLineUTMDEM, geo_interp = templateDict['geo_interp'])
    geocode(CORIFG, GeoCOR, UTMTORDC, nWidth, nWidthUTMDEM, nLineUTMDEM, geo_interp = templateDict['geo_interp'])
    geocode(DIFFIFG, GeoDIFF, UTMTORDC, nWidth, nWidthUTMDEM, nLineUTMDEM, geo_interp = templateDict['geo_interp'])
    geocode(UNWIFG, GeoUNW, UTMTORDC, nWidth, nWidthUTMDEM, nLineUTMDEM, geo_interp = templateDict['geo_interp'])

    call_str = 'rasmph_pwr ' + GeoDIFF + ' ' + GeoMamp + ' ' + nWidthUTMDEM + ' - - - - - - - - - ' + GeoCOR + ' - - ' 
    os.system(call_str)

    call_str = 'raspwr ' + GeoMamp + ' ' + nWidthUTMDEM + ' - - - - - - - - - - ' 
    os.system(call_str)
    
    call_str = 'rasrmg ' + GeoUNW + ' ' + GeoMamp + ' ' + nWidthUTMDEM + ' - - - - - - - - - - - '  + GeoCOR + ' - - ' 
    os.system(call_str)
    
    os.remove(Mamp)
    os.remove(MampPar)
    
    os.remove(UTMTORDC)
    os.remove(UTMDEMpar)
    
    print("Geocoding is done!") 
    sys.exit(1)

if __name__ == '__main__':
    main(sys.argv[:])
