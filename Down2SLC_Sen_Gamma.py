#! /usr/bin/env python
#'''
##################################################################################
#                                                                                #
#            Author:   Yun-Meng Cao                                              #
#            Email :   ymcmrs@gmail.com                                          #
#            Date  :   March, 2017                                               #
#                                                                                #
#           Generate Sentinel SLC from the downloaded data                       #
#                                                                                #
##################################################################################
#'''
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
        f.close
        
def rm(TXT):
    call_str = 'rm ' + TXT
    os.system(call_str)        

def usage():
    print '''
******************************************************************************************************
 
                 Downloading Sentinel-1A/B data based on ssara

   usage:
   
            Down2SLC_Sen_Gamma.py ProjectName DownName 
      
      e.g.  Down2SLC_Sen_Gamma.py CotopaxiT120SenVVA S1A_IW_SLC__1SSV_20170118T232841_20170118T232911_014892_0184B8_7F54.zip
      
*******************************************************************************************************
    '''   
    
def main(argv):
    
    if len(sys.argv)==3:
        projectName = sys.argv[1]
        Date  = sys.argv[2]
    else:
        usage();sys.exit(1)
         
    scratchDir = os.getenv('SCRATCHDIR')
    templateDir = os.getenv('TEMPLATEDIR')
    
    projectDir = scratchDir + '/' + projectName 
    downDir    = scratchDir + '/' + projectName + "/DOWNLOAD"
    slcDir     = scratchDir + '/' + projectName + '/SLC'
    
    if not os.path.isdir(slcDir):
        call_str= 'mkdir ' +slcDir
        os.system(call_str)
    
    os.chdir(downDir)
    
    
    t0 = 't0_' + Date
    call_str = 'ls  >' + t0
    os.system(call_str)

    tt = 'tt_' + Date
    call_str = "grep " + Date + ' ' + t0 + '> ' + tt
    os.system(call_str)
    
    ts = 'ts_' + Date
    call_str = "grep SAFE " + tt + ' >' + ts 
    os.system(call_str)
    
    tz = 'tz_' + Date
    call_str = "grep zip " + tt + " > " + tz 
    os.system(call_str)
    
    A1= np.loadtxt(ts,dtype=np.str)
    Na1 = A1.size

    A2= np.loadtxt(tz,dtype=np.str)
    Na2 = A2.size
    
    rm(t0);rm(tt);rm(ts);rm(tz)
    
    if Na1 == 0:
        if Na2 > 0:
            if Na2 == 1:
                downName = str(A2)
            else:
                downName = str(A2[0])
            FileDir = downDir + '/' + downName
            RAWNAME = downName.split('.')[0]+'.SAFE'  
            call_str = 'unzip '+ FileDir
            os.system(call_str)
            
    else:
        if Na1 == 1:
            RAWNAME = str(A1)
        else:
            RAWNAME = str(A1[0])
    
    print RAWNAME
    RAWFILEDir = downDir + '/'+str(RAWNAME)    

     
    Date = RAWNAME[19:25]
    DateDir = slcDir + '/'+Date
    
    if not os.path.isdir(DateDir):
        call_str='mkdir '+DateDir
        os.system(call_str)
    
    measureDir = RAWFILEDir + '/measurement'
    annotatDir = RAWFILEDir + '/annotation'
    calibraDir = RAWFILEDir + '/annotation/calibration'
    
    MM = glob.glob(measureDir + '/*vv*tiff')
#     MEASURE = glob.glob(measureDir + '/*vv*tiff')
#    ANNOTAT = glob.glob(annotatDir + '/*vv*xml' )
#    CALIBRA = glob.glob(calibraDir+'/calibration*vv*') 
#    NOISE = glob.glob(calibraDir+'/noise*vv*')
    
    SLC_Tab = DateDir + '/' + Date+'_SLC_Tab'   
    TEST = DateDir + '/' + Date + '.IW1.slc'
    
    if not os.path.isfile(TEST):
        if os.path.isfile(SLC_Tab):
            os.remove(SLC_Tab)
        for kk in range(len(MM)):
            SLC    = DateDir + '/' + Date + '.IW' + str(kk+1)+'.slc'
            SLCPar = DateDir + '/' + Date + '.IW' + str(kk+1)+'.slc.par'
            TOPPar = DateDir + '/' + Date + '.IW' + str(kk+1)+'.slc.TOPS_par'
            BURST = DateDir + '/' + Date + '.IW' + str(kk+1)+'.burst.par'
        
            if os.path.isfile(BURST):
                os.remove(BURST)
            call_str = 'echo ' + SLC + ' ' + SLCPar + ' ' + TOPPar + '>>' + SLC_Tab
            os.system(call_str)
        
            MEASURE = glob.glob(measureDir + '/*iw' + str(kk+1) + '*vv*tiff')
            ANNOTAT = glob.glob(annotatDir + '/*iw' + str(kk+1) + '*vv*xml' )
            CALIBRA = glob.glob(calibraDir+'/calibration*'+ 'iw' + str(kk+1) + '*vv*') 
            NOISE = glob.glob(calibraDir+'/noise*' + 'iw' + str(kk+1) + '*vv*')
        
            #call_str = 'S1_burstloc ' + ANNOTAT[0] + '> ' +BURST
            #os.system(call_str)
            
            call_str = 'par_S1_SLC ' + MEASURE[0] + ' ' + ANNOTAT[0] + ' ' + CALIBRA[0] + ' ' + NOISE[0] + ' ' + SLCPar + ' ' + SLC + ' ' + TOPPar
            os.system(call_str)
            
            call_str = 'SLC_burst_corners ' + SLCPar + ' ' +  TOPPar + ' > ' +BURST
            os.system(call_str)
        
    TSLC = DateDir + '/' + Date + '.slc'
    TSLCPar = DateDir + '/' + Date + '.slc.par'
    
    TMLI =  DateDir + '/' + Date + '_20rlks.amp'
    TMLIPar = DateDir + '/' + Date + '_20rlks.amp.par'
    
    call_str = 'SLC_mosaic_S1_TOPS ' +  SLC_Tab + ' ' + TSLC + ' ' + TSLCPar + ' 10 2'
    os.system(call_str)
   
    call_str = 'multi_look ' + TSLC + ' ' + TSLCPar + ' ' + TMLI + ' ' + TMLIPar + ' 20 4' 
    os.system(call_str)
    
    nWidth = UseGamma(TMLIPar, 'read','range_samples:')
    call_str = 'raspwr ' + TMLI + ' ' + nWidth + ' - - - - - - - '
    os.system(call_str)
    
    ras2jpg(TMLI,TMLI)

    print "Down to SLC for %s is done! " % Date
    sys.exit(1)
    
if __name__ == '__main__':
    main(sys.argv[:])    
    
    
    
    
    
    