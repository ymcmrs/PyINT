#! /usr/bin/env python
#################################################################
###  This program is part of PyINT  v1.0                      ### 
###  Copy Right (c): 2017, Yunmeng Cao                        ###  
###  Author: Yunmeng Cao                                      ###                                                          
###  Email : ymcmrs@gmail.com                                 ###
###  Univ. : Central South University & University of Miami   ###   
#################################################################


import os
import sys
import glob
import time
import argparse

import h5py
import numpy as np

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
        
def UseGamma2(inFile, task, keyword):
    if task == "read":
        f = open(inFile, "r")
        while 1:
            line = f.readline()
            if not line: break
            if line.count(keyword) == 1:
                strtemp = line.split(":")
                value = strtemp[2].strip()
                return value
        print "Keyword " + keyword + " doesn't exist in " + inFile
        f.close()
        
def usage():
    print '''
******************************************************************************************************
 
          Generate Roi_PAC RSC file based on GAMMA par file 

   usage:
   
            GenerateRSC_Gamma.py igramDir
      
      e.g.  GenerateRSC_Gamma.py IFG_PacayaT163TsxHhA_131021-131101_0011_0007
      e.g.  GenerateRSC_Gamma.py MAI_PacayaT163TsxHhA_131021-131101_0011_0007      
      e.g.  GenerateRSC_Gamma.py RSI_PacayaT163TsxHhA_131021-131101_0011_0007          
            
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
    
    if INF=='IFG':
        Suffix=['']
    elif INF=='MAI':
        Suffix=['.F','.B']
    elif INF=='RSI':
        Suffix=['.HF','.LF']
    else:
        print "The folder name %s cannot be identified !" % igramDir
        usage();sys.exit(1)
        
    scratchDir = os.getenv('SCRATCHDIR')
    templateDir = os.getenv('TEMPLATEDIR')
    templateFile = templateDir + "/" + projectName + ".template"
    templateContents=read_template(templateFile)
    masterDate   =  templateContents['masterDate']    
    rlks = templateContents['Range_Looks']
    azlks = templateContents['Azimuth_Looks']
    
    processDir = scratchDir + '/' + projectName + "/PROCESS"
    slcDir     = scratchDir + '/' + projectName + "/SLC"
    rslcDir    = scratchDir + '/' + projectName + "/RSLC"
    MslcDir    = rslcDir + '/' + Mdate
    SslcDir    = rslcDir + '/' + Sdate
    workDir    = processDir + '/' + igramDir   
    TS_RSC     = workDir + '/' + IFGPair + '_' + rlks + 'rlks.rsc'
    OFF_STD = workDir + '/' + Mdate + '-' + Sdate + '.off_std'
    
    MRSLCPAR = workDir + '/' + Mdate + Suffix[0] + '.rslc.par'
    MCORNER = workDir + '/' + Mdate + Suffix[0] + '.corner'
    MLATLON = workDir + '/' + Mdate + Suffix[0] + '.latlon'
    SRSLCPAR = workDir + '/' + Sdate + Suffix[0] + '.rslc.par'    
    
    OFF   =  workDir + '/' + Mdate + '-' + Sdate + '_' + rlks + 'rlks' + Suffix[0] + '.off'
    if not os.path.isfile(OFF):
        call_str = 'create_offset ' + workDir+'/' + Mdate + '.rslc.par ' +  workDir+'/' + Sdate + '.rslc.par ' + OFF + ' 1 ' + rlks + ' ' + azlks + ' 0'
        os.system(call_str)
        
    BASE  =  workDir + '/' + Mdate + '-' + Sdate + Suffix[0] + '.base'
    PBASE =  workDir + '/' + Mdate + '-' + Sdate + Suffix[0] + '.base_perp'
    PBASE_TXT = workDir + '/' + Mdate + '-' + Sdate + Suffix[0] + '.base_perp_txt'
    BVH_TXT = workDir + '/' + Mdate + '-' + Sdate + Suffix[0] + '.base_vh_txt'
    
    if not os.path.isdir(rslcDir):
        call_str = 'mkdir ' + rslcDir
        os.system(call_str)

    SLC_par = MslcDir + '/' + Mdate + '_' + rlks +'rlks.amp.par' 
    SLC_par2 = SslcDir + '/' + Sdate + '_' + rlks +'rlks.amp.par'
    nWidth = UseGamma(SLC_par, 'read', 'range_samples:')
    nLine  = UseGamma(SLC_par, 'read', 'azimuth_lines:')
    
    f = open(TS_RSC,'w')
    
#    print 'FILE_LENGTH               ' + nLine
#    print 'WIDTH                     ' + nWidth
    wstr = 'PROJECT                   ' + projectName  + '\n'
    f.write(wstr)
    
    wstr = 'FILE_LENGTH               ' + nLine  + '\n'
    f.write(wstr)
    wstr = 'WIDTH                     ' + nWidth + '\n'
    f.write(wstr)
    
    freq_rd = UseGamma(SLC_par, 'read', 'radar_frequency:')
    freq_rd = freq_rd.split(' ')[0]
    wave = str((3*(10**8))/float(freq_rd))
#    print 'WAVELENGTH                ' + wave
    wstr = 'WAVELENGTH                ' + wave + '\n'
    f.write(wstr)
    
    Range_pix = UseGamma(SLC_par, 'read', 'range_pixel_spacing:')
    RP = Range_pix.split('m')[0]
    Azimuth_pix = UseGamma(SLC_par, 'read', 'azimuth_pixel_spacing:')
    AP = Azimuth_pix.split('m')[0]
    
#    print 'RANGE_PIXEL_SIZE          ' + RP
    wstr = 'RANGE_PIXEL_SIZE          ' + RP + '\n'
    f.write(wstr)
#    print 'AZIMUTH_PIXEL_SIZE        ' + AP
    wstr = 'AZIMUTH_PIXEL_SIZE        ' + AP + '\n'
    f.write(wstr)
    
    Earth_Radius = '6378135.33251539'
#    print 'EARTH_RADIUS              ' + Earth_Radius
    wstr = 'EARTH_RADIUS              ' + Earth_Radius + '\n'
    f.write(wstr)
    
    
    CentLine_UTC = UseGamma(SLC_par, 'read', 'center_time:')
    CU = CentLine_UTC.split('s')[0]
#    print 'CENTER_LINE_UTC           ' + CU
    wstr = 'CENTER_LINE_UTC           ' + CU + '\n'
    f.write(wstr)
    
    
    SAR_TO_EC = UseGamma(SLC_par, 'read', 'sar_to_earth_center:')
    SAR_TO_EC = SAR_TO_EC.split('m')[0]
    
    HEIGHT = str(float(SAR_TO_EC)-float(Earth_Radius))
    
#    print 'HEIGHT                    ' + HEIGHT
    wstr = 'HEIGHT                    ' + HEIGHT + '\n'
    f.write(wstr)
    
    
    HEADING = UseGamma(SLC_par, 'read', 'heading:')
    HEADING = HEADING.split('degrees')[0]
#    print 'HEADING                   ' + HEADING
    wstr = 'HEADING                   ' + HEADING + '\n'
    f.write(wstr)
    
    if float(HEADING) > 180.0 :
        HD = abs(float(HEADING) -360)
        if HD > 90:
            ORBIT_DIRECTION = 'descending'
        else:
            ORBIT_DIRECTION = 'ascending'
    elif float(HEADING) < (-180.0):
        HD = abs(float(HEADING) + 360)   
        if HD > 90:
            ORBIT_DIRECTION = 'descending'
        else:
            ORBIT_DIRECTION = 'ascending'
    else:
        HD = abs(float(HEADING))
        if HD > 90:
            ORBIT_DIRECTION = 'descending'
        else:
            ORBIT_DIRECTION = 'ascending' 
            
#    print 'ORBIT_DIRECTION           ' + ORBIT_DIRECTION
    wstr = 'ORBIT_DIRECTION            ' + ORBIT_DIRECTION + '\n'
    f.write(wstr)
     
            
    
    PRF =  UseGamma(SLC_par, 'read', 'prf:')
    PRF = PRF.split('Hz')[0]
#    print 'PRF                       ' + PRF   
    wstr = 'PRF                       ' + PRF + '\n'
    f.write(wstr)
    
    wstr = 'DATE                      ' + masterDate + '\n'
    f.write(wstr)
    
    Near_Range = UseGamma(SLC_par, 'read', 'near_range_slc:')
    NR = Near_Range.split('m')[0]
#    print 'STARTING_RANGE            ' + NR
    wstr = 'STARTING_RANGE             ' + NR + '\n'
    f.write(wstr)
    
    wstr = 'STARTING_RANGE1            ' + NR + '\n'
    f.write(wstr)
    
    Near_Range = UseGamma(SLC_par2, 'read', 'near_range_slc:')
    NR = Near_Range.split('m')[0]
#    print 'STARTING_RANGE            ' + NR
    wstr = 'STARTING_RANGE2            ' + NR + '\n'
    f.write(wstr)
    
    Center_Range = UseGamma(SLC_par, 'read', 'center_range_slc:')
    Far_Range = UseGamma(SLC_par, 'read', 'far_range_slc:')

    call_str = 'base_orbit ' + MRSLCPAR + ' ' + SRSLCPAR + ' ' + BASE
    os.system(call_str)
    
    call_str = 'base_perp ' + BASE + ' ' + MRSLCPAR + ' ' + OFF + ' >' + PBASE
    os.system(call_str)
    
    call_str ='cat ' + PBASE + ' | tail -n +13 | head -n 50 >' +PBASE_TXT
    os.system(call_str)
    
    BB=np.loadtxt(PBASE_TXT)
    XX = BB[:,0]
    XX = map(int,XX)
    
    BP0 = BB[:,7]
    LA0 = BB[:,5]
    XX = np.asarray(XX)
    BP0 = np.asarray(BP0)
    LA0 = np.asarray(LA0)
    
    ndx = np.where(XX==0)
    BP =BP0[ndx]
    LA = LA0[ndx]
    
    P_BASELINE_TOP_HDR = str(BP[0])
    P_BASELINE_BOTTOM_HDR = str(BP[len(BP)-1])
    
    wstr = 'P_BASELINE_TOP_HDR        ' + P_BASELINE_TOP_HDR + '\n'
    f.write(wstr)
    wstr = 'P_BASELINE_BOTTOM_HDR     ' + P_BASELINE_BOTTOM_HDR + '\n'
    f.write(wstr)       
    
    wstr = 'LOOK_REF1                 ' + str(LA[0]) + '\n'
    f.write(wstr)
    
    wstr = 'LOOK_REF2                 ' + str(LA[len(LA)-1]) + '\n'
    f.write(wstr)
    
    call_str ='SLC_corners ' + MRSLCPAR + ' > ' + MCORNER
    os.system(call_str)
    call_str = "awk 'NR==3,NR==6 {print $3,$6} ' " + MCORNER + '> ' + MLATLON
    os.system(call_str)
    LL = np.loadtxt(MLATLON)

    wstr = 'LAT_REF1                  ' + str(LL[0][0]) + '\n'
    f.write(wstr)
    wstr = 'LON_REF1                  ' + str(LL[0][1]) + '\n'
    f.write(wstr)
    
    wstr = 'LAT_REF2                  ' + str(LL[1][0]) + '\n'
    f.write(wstr)
    wstr = 'LON_REF2                  ' + str(LL[1][1]) + '\n'
    f.write(wstr)
    
    
    wstr = 'LAT_REF3                  ' + str(LL[2][0]) + '\n'
    f.write(wstr)
    wstr = 'LON_REF3                  ' + str(LL[2][1]) + '\n'
    f.write(wstr)
    
    wstr = 'LAT_REF4                  ' + str(LL[3][0]) + '\n'
    f.write(wstr)
    wstr = 'LON_REF4                  ' + str(LL[3][1]) + '\n'
    f.write(wstr)
    
    
    call_str = "awk 'NR==1,NR==2 {print $3,$4}' " + BASE + " > " + BVH_TXT
    os.system(call_str)
    BVH=np.loadtxt(BVH_TXT)
    
    H_BASELINE_TOP_HDR = str(BVH[0][0])
#    print 'H_BASELINE_TOP_HDR        ' + H_BASELINE_TOP_HDR
    wstr = 'H_BASELINE_TOP_HDR        ' + H_BASELINE_TOP_HDR + '\n'
    f.write(wstr)
    
    H_BASELINE_RATE_HDR = str(BVH[1][0])
#    print 'H_BASELINE_RATE_HDR        ' + H_BASELINE_RATE_HDR
    wstr = 'H_BASELINE_RATE_HDR        ' + H_BASELINE_RATE_HDR + '\n'
    f.write(wstr)
    
    V_BASELINE_TOP_HDR = str(BVH[0][1])
#    print 'V_BASELINE_TOP_HDR         ' + V_BASELINE_TOP_HDR
    wstr = 'V_BASELINE_TOP_HDR        ' + V_BASELINE_TOP_HDR + '\n'
    f.write(wstr)
    
    V_BASELINE_RATE_HDR = str(BVH[1][1])
#    print 'V_BASELINE_RATE_HDR        ' + V_BASELINE_RATE_HDR
    wstr = 'V_BASELINE_RATE_HDR        ' + V_BASELINE_RATE_HDR + '\n'
    f.write(wstr)
    
    #RR = UseGamma(OFF_STD,'read','final range offset poly. coeff.:')
    #cor_rg = RR.split(' ')[0]
        
    #AA = UseGamma(OFF_STD,'read','final azimuth offset poly. coeff.:')
    #cor_az = AA.split(' ')[0]
        
    #STDRR = UseGamma(OFF_STD,'read','final model fit std. dev. (samples) range:')
    #std_rg=STDRR.split(' ')[0]
    
    #std_az = UseGamma2(OFF_STD,'read','final model fit std. dev. (samples) range:')  

    #wstr = 'RANGE_OFFSET               ' + cor_az + '\n'
    #f.write(wstr)
    #wstr = 'RANGE_OFFSET_STD           ' + std_rg + '\n'
    #f.write(wstr)
    #wstr = 'AZIMUTH_OFFSET             ' + cor_az + '\n'
    #f.write(wstr)
    #wstr = 'AZIMUTH_OFFSET_STD         ' + std_az + '\n'
    #f.write(wstr)
    
    f.close()
    
    sys.exit(1)
    
    
if __name__ == '__main__':
    main(sys.argv[1:])    
    
    
    
    
    
    
