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

def is_number(s):
    try:
        int(s)
        return True
    except ValueError:
        return False


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
        
def write_template(File, Str):
    f = open(File,'a')
    f.write(Str)
    f.close()

def write_run_coreg_all(projectName,master,slavelist,workdir):
    scratchDir = os.getenv('SCRATCHDIR')    
    projectDir = scratchDir + '/' + projectName   
    run_coreg_all  = projectDir + "/run_coreg_all"
    f_coreg = open(run_coreg_all,'w')
    
    for kk in range(len(slavelist)):
        str_coreg = "GenOff_Gamma.py " + projectName + ' ' + master + ' ' + slavelist[kk] + ' ' + workdir + '\n'
        f_coreg.write(str_coreg)
    f_coreg.close()
    
    
def usage():
    print '''
******************************************************************************************************
 
       Coregistration of SAR images based on cross-correlation by using GAMMA.
       Be suitable for conventional InSAR, MAI, Range Split-Spectrum InSAR.

   usage:
   
            process_tsifg projectName
      
      e.g.  process_tsifg PacayaT163TsxHhA
           
*******************************************************************************************************
    '''   
    
def main(argv):
    
    if len(sys.argv)==2:
        if argv[0] in ['-h','--help']: usage(); sys.exit(1)
        else: projectName=sys.argv[1]        
    else:
        usage();sys.exit(1)
       
    
    scratchDir = os.getenv('SCRATCHDIR')
    templateDir = os.getenv('TEMPLATEDIR')
    DEMDIR = os.getenv('DEMDIR')
    templateFile = templateDir + "/" + projectName + ".template"
    
    projectDir = scratchDir + '/' + projectName
    processDir = scratchDir + '/' + projectName + "/PROCESS"
    slcDir     = scratchDir + '/' + projectName + "/SLC"
    rslcDir    = scratchDir + '/' + projectName + "/RSLC"
 
    
    if not os.path.isdir(rslcDir):
        call_str = 'mkdir ' + rslcDir
        os.system(call_str)
       
    if not os.path.isdir(processDir):
        call_str = 'mkdir ' + processDir
        os.system(call_str)
    
    templateContents = read_template(templateFile)
    if 'memory_Ifg' in templateContents :  memory_Ifg =  templateContents['memory_Ifg']
    else: memory_Ifg = '3700'
    if 'walltime_Ifg' in templateContents :  walltime_Ifg =  templateContents['walltime_Ifg']
    else: walltime_Ifg = '1:00'
        
        
    if 'Coreg_all' in templateContents :  Coreg_all =  templateContents['Coreg_all']
    else: Coreg_all = '1'
        
    if 'Select_pairs' in templateContents :  Select_pairs =  templateContents['Select_pairs']
    else: Select_pairs = '1'

    if 'GenRdcDem_Rslc_all' in templateContents :  GenRdcDem_Rslc_all =  templateContents['GenRdcDem_Rslc_all']
    else: GenRdcDem_Rslc_all = '1'

##########################    Check DEM   ###############################################

    if 'DEM' in templateContents :  
        DEM =  templateContents['DEM']
        if not os.path.isfile(DEM):
            print 'Provided DEM is not available, a new DEM based on SRTM-1 will be generated.'
            call_str = 'Makedem_PyInt.py ' + projectName + ' gamma'
            os.system(call_str)
            
            call_str = 'echo DEM = ' + DEMDIR + '/' + projectName + '/' + projectName +'.dem >> ' + templateFile
            os.system(call_str)
    else:
        print 'DEM is not provided in the template file,  a DEM based on SRTM-1 will be generated.'
        call_str = 'Makedem_PyInt.py ' + projectName + ' gamma'
        os.system(call_str)
            
        call_str = 'echo DEM = ' + DEMDIR + '/' + projectName + '/' + projectName +'.dem >> ' + templateFile
        os.system(call_str)
 

    masterRdcDEM = scratchDir + '/' + projectName + "/PROCESS/DEM/sim_" + masterDate + "_" + rlks + "rlks.rdc.dem"
    if not os.path.isfile(masterRdcDEM):
        call_str = 'Generate_RdcDEM_Gamma.py ' + projectName + ' ' + masterDate
        os.system(call_str)
      
    
    
    if Coreg_all== '1':    
        call_str = 'COREG_ALL_Gamma.py ' + projectName
        os.system(call_str)
    
    if GenRdcDem_Rslc_all =='1':
        call_str = 'Generate_RdcDEM_Rslc_ALL.py ' + projectName
        os.system(call_str)
#################################################################################

    if Select_pairs =='1':
        call_str = 'SelectPairs_Gamma.py ' + projectName
        os.system(call_str) 
         
    IFGLIST = glob.glob(processDir+'/IFG_' +projectName + '_*') 
    
    run_slc2ifg_gamma = processDir+'/run_slc2ifg_gamma'
    if os.path.isfile(run_slc2ifg_gamma):
        os.remove(run_slc2ifg_gamma)
        
    for kk in IFGLIST:
        call_str = 'echo SLC2Ifg_Gamma.py ' + os.path.basename(kk) + ' >>' + run_slc2ifg_gamma
        os.system(call_str)
    
    
    call_str='$INT_SCR/createBatch.pl ' + run_slc2ifg_gamma + ' memory=' + memory_Ifg + ' walltime=' + walltime_Ifg
    os.system(call_str)

    print "Time series interferograms processing is done! "    
    sys.exit(1)
    
if __name__ == '__main__':
    main(sys.argv[:])



















