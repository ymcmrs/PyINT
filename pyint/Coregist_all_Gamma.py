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
import sys  
import subprocess
import getopt
import time
import glob
import re

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
    print('''
******************************************************************************************************
 
          Coregistrate all SAR or interferograms to one master data

   usage:
   
            Coregist_all_Gamma.py igramDir
      
      e.g.  Coregist_all_Gamma.py IFG_PacayaT163TsxHhA_131021-131101_0011_0007
      e.g.  Coregist_all_Gamma.py MAI_PacayaT163TsxHhA_131021-131101_0011_0007      
      e.g.  Coregist_all_Gamma.py RSI_PacayaT163TsxHhA_131021-131101_0011_0007          
            
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
    rslcDir    = scratchDir + '/' + projectName + "/PROCESS/RSLC"
    workDir    = processDir + '/' + igramDir   
    
    if not os.path.isdir(rslcDir):
        call_str = 'mkdir ' + rslcDir
        os.system(call_str)
        
    templateContents=read_template(templateFile)
    masterDate   =  templateContents['masterDate']    
    rlks = templateContents['Range_Looks']
    azlks = templateContents['Azimuth_Looks']
 
    Moff = rslcDir +"/"+ masterDate + '-' + Mdate + '.off'
    Soff = rslcDir +"/"+ masterDate + '-' + Sdate + '.off'        
    
    if INF=='IFG':
        Suffix=['']
    elif INF=='MAI':
        Suffix=['.F','.B']
    elif INF=='RSI':
        Suffix=['.HF','.LF']
    else:
        print("The folder name %s cannot be identified !" % igramDir)
        usage();sys.exit(1)  
# definition of intermediate and output file variables for slc images and parameters

    BaseslcDir = slcDir + "/" + masterDate
    BaseslcImg = BaseslcDir + '/' + masterDate + '.slc'
    BaseslcPar = BaseslcDir + '/' + masterDate + '.slc.par'
    Baseslc4Par = workDir + '/' + masterDate + '.slc4.par'
    
    SslcDir = slcDir + "/" + Sdate
    MslcDir = slcDir + "/" + Mdate

    MslcImg = MslcDir + "/" + Mdate + ".slc"
    MslcPar = MslcDir + "/" + Mdate + ".slc.par"
    SslcImg = SslcDir + "/" + Sdate + ".slc"
    SslcPar = SslcDir + "/" + Sdate + ".slc.par"
 
    offs = workDir + "/offs"
    snr = workDir + "/snr"
    offsets = workDir + "/offsets"
    coffs = workDir + "/coffs"
    coffsets = workDir + "/coffsets" 
   
####################################   Start to Coregisrtate    ######################################### 

# definition of parameter variables which may be included in the Template file
    if 'Coreg_Coarse'          in templateContents: coregCoarse = templateContents['Coreg_Coarse']                
    else: coregCoarse = 'both' 
        
    if 'rlks4cor'          in templateContents: rlks4cor = templateContents['rlks4cor']                
    else: rlks4cor = '4'
    if 'azlks4cor'          in templateContents: azlks4cor = templateContents['azlks4cor']                
    else: azlks4cor = '4'  
        
    if 'rwin4cor'          in templateContents: rwin4cor = templateContents['rwin4cor']                
    else: rwin4cor = '256'  
    if 'azwin4cor'          in templateContents: azwin4cor = templateContents['azwin4cor']                
    else: azwin4cor = '256'      
    if 'rsample4cor'          in templateContents: rsample4cor = templateContents['rsample4cor']                
    else: rsample4cor = '16'  
    if 'azsample4cor'          in templateContents: azsample4cor = templateContents['azsample4cor']                
    else: azsample4cor = '32'  
        
    if ' rpos4cor'          in templateContents:  rpos4cor = templateContents[' rpos4cor']                
    else:  rpos4cor = ' - '  
    if 'azpos4cor'          in templateContents: azpos4cor = templateContents['azpos4cor']                
    else: azpos4cor = ' - '  
        

        
    if 'rfwin4cor'          in templateContents: rfwin4cor = templateContents['rfwin4cor']                
    else: rfwin4cor = str(int(int(rwin4cor)/2))
    if 'azfwin4cor'          in templateContents: azfwin4cor = templateContents['azfwin4cor']                
    else: azfwin4cor = str(int(int(azwin4cor)/2))  
    if 'rfsample4cor'          in templateContents: rfsample4cor = templateContents['rfsample4cor']                
    else: rfsample4cor = str(2*int(rsample4cor))  
    if 'azfsample4cor'          in templateContents: azfsample4cor = templateContents['azfsample4cor']                
    else: azfsample4cor = str(2*int(azsample4cor))  
        
    if 'thresh4cor'          in templateContents: thresh4cor = templateContents['thresh4cor']                
    else: thresh4cor = ' - ' 

### post coregistration for master image

    if not (Mdate == masterDate or os.path.isfile(Moff)):
        print("post_coregistration would start for " + Mdate)
        call_str = "$GAMMA_BIN/create_offset " + BaseslcPar + " " + MslcPar + " " + Moff + " 1 - - 0"
        os.system(call_str)

        if coregCoarse == 'both':
            print('init offset estimation by both orbit and ampcor')
            call_str = '$GAMMA_BIN/init_offset_orbit '+ BaseslcPar + ' ' + MslcPar + ' ' + Moff
            os.system(call_str)

            call_str = '$GAMMA_BIN/init_offset '+ BaseslcImg + ' ' + MslcImg + ' ' + BaseslcPar + ' ' + MslcPar + ' ' + Moff + ' ' + rlks4cor + ' ' + azlks4cor + ' ' + rpos4cor + ' ' + azpos4cor
            os.system(call_str)
        
            call_str = '$GAMMA_BIN/init_offset '+ BaseslcImg + ' ' + MslcImg + ' ' + BaseslcPar + ' ' + MslcPar + ' ' + Moff + ' 1 1 - - '
            os.system(call_str)
            
        elif coregCoarse == 'orbit':
            print('init offset estimation by orbit only')      
            call_str = '$GAMMA_BIN/init_offset_orbit '+ BaseslcPar + ' ' + MslcPar + ' ' + Moff
            os.system(call_str)
    
        elif coregCoarse == 'ampcor':
            print('init offset estimation by ampcor only')       
            call_str = '$GAMMA_BIN/init_offset '+ BaseslcImg + ' ' + MslcImg + ' ' + BaseslcPar + ' ' + MslcPar + ' ' + Moff + ' ' + rlks4cor + ' ' + azlks4cor + ' ' + rpos4cor + ' ' + azpos4cor
            os.system(call_str)
        
            call_str = '$GAMMA_BIN/init_offset '+ BaseslcImg + ' ' + MslcImg + ' ' + BaseslcPar + ' ' + MslcPar + ' ' + Moff + ' 1 1 - - '
            os.system(call_str)     
########## Refined Coregistration ####
        call_str = "$GAMMA_BIN/offset_pwr " + BaseslcImg + ' ' + MslcImg + ' ' + BaseslcPar + ' ' + MslcPar + " " + Moff + " " + offs + " " + snr + " " +  rwin4cor + " " + azwin4cor + " " + offsets + " 2 "+ rsample4cor + " " + azsample4cor
        os.system(call_str)
        call_str = "$GAMMA_BIN/offset_fit " " " + offs + " " + snr + " " + Moff + " " + coffs + " " + coffsets + " - 3"
        os.system(call_str)

        
        call_str = "$GAMMA_BIN/offset_pwr " + BaseslcImg + " " + MslcImg + " " + BaseslcPar + " " + MslcPar + " " + Moff + " " + offs + " " + snr + " " + rfwin4cor + " " + azfwin4cor + " " + offsets + " 2 " + rfsample4cor + " " + azfsample4cor
        os.system(call_str)
        call_str = "$GAMMA_BIN/offset_fit " " " + offs + " " + snr + " " + Moff + " " + coffs + " " + coffsets + " - 4"
        os.system(call_str)
  
        
    if not ( Sdate == masterDate or os.path.isfile(Soff)):
        print("post_coregistration would start for " + Sdate)
        call_str = "$GAMMA_BIN/create_offset " + BaseslcPar + " " + SslcPar + " " + Soff + " 1 - - 0"
        os.system(call_str)

        if coregCoarse == 'both':
            print('init offset estimation by both orbit and ampcor')
            call_str = '$GAMMA_BIN/init_offset_orbit '+ BaseslcPar + ' ' + SslcPar + ' ' + Soff
            os.system(call_str)

            call_str = '$GAMMA_BIN/init_offset '+ BaseslcImg + ' ' + SslcImg + ' ' + BaseslcPar + ' ' + SslcPar + ' ' + Soff + ' ' + rlks4cor + ' ' + azlks4cor + ' ' + rpos4cor + ' ' + azpos4cor
            os.system(call_str)
        
            call_str = '$GAMMA_BIN/init_offset '+ BaseslcImg + ' ' + SslcImg + ' ' + BaseslcPar + ' ' + SslcPar + ' ' + Soff + ' 1 1 - - '
            os.system(call_str)
            
        elif coregCoarse == 'orbit':
            print('init offset estimation by orbit only')      
            call_str = '$GAMMA_BIN/init_offset_orbit '+ BaseslcPar + ' ' + SslcPar + ' ' + Soff
            os.system(call_str)
    
        elif coregCoarse == 'ampcor':
            print('init offset estimation by ampcor only')       
            call_str = '$GAMMA_BIN/init_offset '+ BaseslcImg + ' ' + SslcImg + ' ' + BaseslcPar + ' ' + SslcPar + ' ' + Soff + ' ' + rlks4cor + ' ' + azlks4cor + ' ' + rpos4cor + ' ' + azpos4cor
            os.system(call_str)
        
            call_str = '$GAMMA_BIN/init_offset '+ BaseslcImg + ' ' + SslcImg + ' ' + BaseslcPar + ' ' + SslcPar + ' ' + Soff + ' 1 1 - - '
            os.system(call_str)     
### Refined Coregistration ##
        call_str = "$GAMMA_BIN/offset_pwr " + BaseslcImg + ' ' + SslcImg + ' ' + BaseslcPar + ' ' + SslcPar + " " + Soff + " " + offs + " " + snr + " " +  rwin4cor + " " + azwin4cor + " " + offsets + " 2 "+ rsample4cor + " " + azsample4cor
        os.system(call_str)
        call_str = "$GAMMA_BIN/offset_fit " " " + offs + " " + snr + " " + Soff + " " + coffs + " " + coffsets + " - 3"
        os.system(call_str)

        
        call_str = "$GAMMA_BIN/offset_pwr " + BaseslcImg + " " + SslcImg + " " + BaseslcPar + " " + SslcPar + " " + Soff + " " + offs + " " + snr + " " + rfwin4cor + " " + azfwin4cor + " " + offsets + " 2 " + rfsample4cor + " " + azfsample4cor
        os.system(call_str)
        call_str = "$GAMMA_BIN/offset_fit " " " + offs + " " + snr + " " + Soff + " " + coffs + " " + coffsets + " - 4"
        os.system(call_str)  
        

##############################################  Resampling #####################################################

    for i in range(len(Suffix)):
        if not INF=='IFG':
            MslcImg = workDir + "/" + Mdate + Suffix[i]+".slc"
            MslcPar = workDir + "/" + Mdate + Suffix[i]+".slc.par"
            SslcImg = workDir + "/" + Sdate + Suffix[i]+".slc"
            SslcPar = workDir + "/" + Sdate + Suffix[i]+".slc.par"
 
        INT      = workDir + '/' + Mdate + '-' + Sdate + Suffix[i] + '.int'
        INTpar   = workDir + '/' + Mdate + '-' + Sdate + Suffix[i] + '.int.par'
        
        rINT     = workDir + '/' + Mdate + '-' + Sdate + Suffix[i] + '.rint'
        rINTpar  = workDir + '/' + Mdate + '-' + Sdate + Suffix[i] + '.rint.par'
        
        MrslcImg = rslcDir + "/" + Mdate + Suffix[i]+".rslc"
        MrslcPar = rslcDir + "/" + Mdate + Suffix[i]+".rslc.par"
        SrslcImg = rslcDir + "/" + Sdate + Suffix[i]+".rslc"
        SrslcPar = rslcDir + "/" + Sdate + Suffix[i]+".rslc.par"

        MamprlksImg = rslcDir + "/" + Mdate + '_'+rlks+'rlks'+Suffix[i]+".ramp"
        MamprlksPar = rslcDir + "/" + Mdate + '_'+rlks+'rlks'+Suffix[i]+".ramp.par"
        
        SamprlksImg = rslcDir + "/" + Sdate + '_'+rlks+'rlks'+Suffix[i]+".ramp"
        SamprlksPar = rslcDir + "/" + Sdate + '_'+rlks+'rlks'+Suffix[i]+".ramp.par"

####   detect the choice for resampling #######      
        if not (Mdate == masterDate or os.path.isfile(MrslcImg)):
            call_str = "$GAMMA_BIN/SLC_interp " + MslcImg + " " + BaseslcPar + " " + MslcPar + " " + Moff + " " + MrslcImg + " " + MrslcPar
            os.system(call_str)
            
            call_str = '$GAMMA_BIN/multi_look ' + MrslcImg + ' ' + MrslcPar + ' ' + MamprlksImg + ' ' + MamprlksPar + ' ' + rlks + ' ' + azlks
            os.system(call_str)
            
        else:
            if not os.path.isfile(MrslcImg):
                call_str = 'cp ' + MslcImg + ' ' + MrslcImg
                os.system(call_str)
          
                call_str = 'cp ' + MslcPar + ' ' + MrslcPar
                os.system(call_str)   
                
                call_str = '$GAMMA_BIN/multi_look ' + MrslcImg + ' ' + MrslcPar + ' ' + MamprlksImg + ' ' + MamprlksPar + ' ' + rlks + ' ' + azlks
                os.system(call_str)               
                
                
#####################################        
        
        if not (Sdate == masterDate or os.path.isfile(SrslcImg) ):
            call_str = "$GAMMA_BIN/SLC_interp " + SslcImg + " " + BaseslcPar + " " + SslcPar + " " + Soff + " " + SrslcImg + " " + SrslcPar
            os.system(call_str)
            
            call_str = '$GAMMA_BIN/multi_look ' + SrslcImg + ' ' + SrslcPar + ' ' + SamprlksImg + ' ' + SamprlksPar + ' ' + rlks + ' ' + azlks
            os.system(call_str)
        
        else:
            if not os.path.isfile(SrslcImg):
                call_str = 'cp ' + SslcImg + ' ' + SrslcImg
                os.system(call_str)
          
                call_str = 'cp ' + SslcPar + ' ' + SrslcPar
                os.system(call_str) 
        
                call_str = '$GAMMA_BIN/multi_look ' + SrslcImg + ' ' + SrslcPar + ' ' + SamprlksImg + ' ' + SamprlksPar + ' ' + rlks + ' ' + azlks
                os.system(call_str)
        
        
###################################################################

        call_str = 'cp ' + MamprlksImg + ' ' + workDir
        os.system(call_str)
        call_str = 'cp ' + MamprlksPar + ' ' + workDir
        os.system(call_str)
        
        call_str = 'cp ' + SamprlksImg + ' ' + workDir
        os.system(call_str)
        call_str = 'cp ' + SamprlksPar + ' ' + workDir
        os.system(call_str)
        
        call_str = 'cp ' + MrslcPar + ' ' + workDir
        os.system(call_str)
        call_str = 'cp ' + SrslcPar + ' ' + workDir
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
        fout = open(INTpar,"w")
        txt = fin.read()
        txtout = re.subn("SCOMPLEX","FCOMPLEX",txt)[0]
        fout.write(txtout)
        fin.close()
        fout.close()
       
        if (masterDate != Mdate):
            call_str = "$GAMMA_BIN/SLC_interp " + INT + " " + Baseslc4Par + " " + INTpar + " " + Moff + " " + rINT + " " + rINTpar
            os.system(call_str)
            os.rename(rINT, INT)

    os.remove(snr)
    os.remove(offsets)
    os.remove(offs)
    #os.remove(off)
    os.remove(coffsets)
    os.remove(coffs)
    
    print("Coregistrate "+ igramDir +" to " + masterDate +" is done! ")
    sys.exit(1)
    
if __name__ == '__main__':
    main(sys.argv[:])
