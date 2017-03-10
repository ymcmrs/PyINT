#! /usr/bin/env python
#'''
###################################################################################
#                                                                                 #
#            Author:   Yun-Meng Cao                                               #
#            Email :   ymcmrs@gmail.com                                           #
#            Date  :   February, 2017                                             #
#                                                                                 #
#        Coregistrate all SAR or interferograms to a master one                   #
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
import re

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
 
          Coregistrate all SAR or interferograms to one master data

   usage:
   
            Coregist_all_Gamma.py igramDir
      
      e.g.  Coregist_all_Gamma.py IFGRAM_PacayaT163TsxHhA_131021-131101_0011_-0007
          
            
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
    coregCoarse = templateContents['Coreg_Coarse']
    coregThreshold = templateContents['Coreg_Threshold']
    masterDate   =  templateContents['masterDate']    
    rlks = templateContents['Range_Looks']
    azlks = templateContents['Azimuth_Looks']
      
    coregCoarse = templateContents['Coreg_Coarse']

# definition of intermediate and output file variables for slc images and parameters

    BaseslcDir = slcDir + "/" + masterDate
    BaseslcImg = BaseslcDir + '/' + masterDate + '.slc'
    BaseslcPar = BaseslcDir + '/' + masterDate + '.slc.par'

    MrslcImg  = workDir + '/' + Mdate + '.rslc'
    MrslcPar  = workDir + '/' + Mdate + '.rslc.par'
    SrslcImg  = workDir + '/' + Sdate + '.rslc'
    SrslcPar  = workDir + '/' + Sdate + '.rslc.par'
    
    MrslcImg_backup  = workDir + '/' + Mdate + '.1st.rslc'
    MrslcPar_backup  = workDir + '/' + Mdate + '.1st.rslc.par'
    SrslcImg_backup  = workDir + '/' + Sdate + '.1st.rslc'
    SrslcPar_backup  = workDir + '/' + Sdate + '.1st.rslc.par'

    MRSLCImg     = workDir + '/' + Mdate + '.RSLC'
    MRSLCPar     = workDir + '/' + Mdate + '.RSLC.par'
    SRSLCImg     = workDir + '/' + Sdate + '.RSLC'
    SRSLCPar     = workDir + '/' + Sdate + '.RSLC.par'

    Baseslc4Par = workDir + '/' + masterDate + '.SLC4.par'
    INT         = workDir + '/' + Mdate + '-' + Sdate + '.int'
    INTPar         = workDir + '/' + Mdate + '-' + Sdate + '.int.par'
    rINT         = workDir + '/' + Mdate + '-' + Sdate + '.rint'
    rINTPar         = workDir + '/' + Mdate + '-' + Sdate + '.rint.par'

    Moff = workDir +"/"+IFGPair+ "_M_master.off"
    Soff= workDir +"/"+IFGPair+ "_S_master.off"
    
    offs = workDir + "/offs"
    snr = workDir + "/snr"
    offsets = workDir + "/offsets"
    coffs = workDir + "/coffs"
    coffsets = workDir + "/coffsets"

# definition of parameter variables which may be included in the Template file

    rlks4cor = "4"
    azlks4cor = "4"
    rpos4cor = "-"
    azpos4cor = "-"
    patch4cor = "512"
    thresh4cor = "0.3"
    rwin4cor = "256"
    azwin4cor = "256"
    rfwin4cor = "128"
    azfwin4cor = "128"

    if os.path.isfile(Moff):
        os.remove(Moff)
    if os.path.isfile(Soff):
        os.remove(Soff)
#  if os.path.isfile(MrslcImgDel):
#    os.remove(MrslcImgDel)
#  if os.path.isfile(MrslcParDel):
#    os.remove(MrslcParDel)
#  if os.path.isfile(SrslcImgDel):
#    os.remove(SrslcImgDel)
#  if os.path.isfile(SrslcParDel):
#    os.remove(SrslcParDel)


### post coregistration for master image

    if Mdate != masterDate:
        off = Moff
        print "post_coregistration would start for " + Mdate
        call_str = "$GAMMA_BIN/create_offset " + BaseslcPar + " " + MrslcPar + " " + off + " 1 - - 0"
        os.system(call_str)

        print 'init offset estimation by orbit only'

        call_str = '$GAMMA_BIN/init_offset_orbit '+ BaseslcPar + ' ' + MrslcPar + ' ' + off
        os.system(call_str)

        call_str = '$GAMMA_BIN/init_offset '+ BaseslcImg + ' ' + MrslcImg + ' ' + BaseslcPar + ' ' + MrslcPar + ' ' + off + ' ' + rlks4cor + ' ' + azlks4cor + ' ' + rpos4cor + ' ' + azpos4cor
        os.system(call_str)

        call_str = "$GAMMA_BIN/offset_pwr " + BaseslcImg + " " + MrslcImg + " " + BaseslcPar + " " + MrslcPar + " " + off + " " + offs + " " + snr + " " + rwin4cor + " " + azwin4cor + " " + offsets + " 1 16 32"
        os.system(call_str)

        call_str = "$GAMMA_BIN/offset_fit " " " + offs + " " + snr + " " + off + " " + coffs + " " + coffsets + " - 3"
        os.system(call_str)

        call_str = "$GAMMA_BIN/offset_pwr " + BaseslcImg + " " + MrslcImg + " " + BaseslcPar + " " + MrslcPar + " " + off + " " + offs + " " + snr + " " + rfwin4cor + " " + azfwin4cor + " " + offsets + " 2 32 64"
        os.system(call_str)

        call_str = "$GAMMA_BIN/offset_fit " " " + offs + " " + snr + " " + off + " " + coffs + " " + coffsets + " - 4"
        os.system(call_str)

        call_str = "$GAMMA_BIN/SLC_interp " + MrslcImg + " " + BaseslcPar + " " + MrslcPar + " " + off + " " + MRSLCImg + " " + MRSLCPar
        os.system(call_str)

        if Sdate == masterDate:
            call_str = "cp " + BaseslcImg + " " + SRSLCImg
            os.system(call_str)

            call_str = "cp " + BaseslcPar + " " + SRSLCPar
            os.system(call_str)

        else:
            off= Soff
### post coregistration for slave image
 
            print "post_coregistration would start for " + Sdate

            call_str = "$GAMMA_BIN/create_offset " + BaseslcPar + " " + SrslcPar + " " + off + " 1 - - 0"
            os.system(call_str)

            print 'init offset estimation by orbit only'
   
            call_str = '$GAMMA_BIN/init_offset_orbit '+ BaseslcPar + ' ' + SrslcPar + ' ' + off
            os.system(call_str)

            call_str = '$GAMMA_BIN/init_offset '+ BaseslcImg + ' ' + SrslcImg + ' ' + BaseslcPar + ' ' + SrslcPar + ' ' + off + ' ' + rlks4cor + ' ' + azlks4cor + ' ' + rpos4cor + ' ' + azpos4cor
            os.system(call_str)
  
            call_str = "$GAMMA_BIN/offset_pwr " + BaseslcImg + " " + SrslcImg + " " + BaseslcPar + " " + SrslcPar + " " + off + " " + offs + " " + snr + " " + rwin4cor + " " + azwin4cor + " " + offsets + " 1 16 32"
            os.system(call_str)

            call_str = "$GAMMA_BIN/offset_fit " " " + offs + " " + snr + " " + off + " " + coffs + " " + coffsets + " " +  CoregThreshold + " 3"
            os.system(call_str)

            call_str = "$GAMMA_BIN/offset_pwr " + BaseslcImg + " " + SrslcImg + " " + BaseslcPar + " " + SrslcPar + " " + off + " " + offs + " " + snr + " " + rfwin4cor + " " + azfwin4cor + " " + offsets + " 2 32 64"
            os.system(call_str)

            call_str = "$GAMMA_BIN/offset_fit " " " + offs + " " + snr + " " + off + " " + coffs + " " + coffsets + " - 4"
            os.system(call_str)

            call_str = "$GAMMA_BIN/SLC_interp " + SrslcImg + " " + BaseslcPar + " " + SrslcPar + " " + off + " " + SRSLCImg + " " + SRSLCPar
            os.system(call_str)

### post coregistration for interferogram 

        fin = open(BaseslcPar,"r")
        fout = open(Baseslc4Par,"w")
        txt = fin.read()
        txtout = re.subn("SCOMPLEX","FCOMPLEX",txt)[0]
        fout.write(txtout)
        fin.close()
        fout.close()

        fin = open(MrslcPar,"r")
        fout = open(INTPar,"w")
        txt = fin.read()
        txtout = re.subn("SCOMPLEX","FCOMPLEX",txt)[0]
        fout.write(txtout)
        fin.close()
        fout.close()

        call_str = "$GAMMA_BIN/SLC_interp " + INT + " " + Baseslc4Par + " " + INTPar + " " + off + " " + rINT + " " + rINTPar
        os.system(call_str)

        os.rename(rINT, INT)

        os.remove(snr)
        os.remove(offsets)
        os.remove(offs)
        #os.remove(off)
        os.remove(coffsets)
        os.remove(coffs)

    else:

        call_str = "cp " + MrslcImg + " " + MRSLCImg
        os.system(call_str)

        call_str = "cp " + MrslcPar + " " + MRSLCPar
        os.system(call_str)
        
        call_str = "cp " + SrslcImg + " " + SRSLCImg
        os.system(call_str)

        call_str = "cp " + SrslcPar + " " + SRSLCPar
        os.system(call_str)

    os.rename(MrslcImg, MrslcImg_backup)
    os.rename(MrslcPar, MrslcPar_backup)    
    os.rename(SrslcImg, SrslcImg_backup)    
    os.rename(SrslcPar, SrslcPar_backup) 
    
    
    os.rename(MRSLCImg, MrslcImg)
    os.rename(MRSLCPar, MrslcPar)    
    os.rename(SRSLCImg, SrslcImg)    
    os.rename(SRSLCPar, SrslcPar)
    
    print "Coregistrate "+ igramDir +" to " + masterDate +" is done! "
    sys.exit(1)
    
if __name__ == '__main__':
    main(sys.argv[:])
