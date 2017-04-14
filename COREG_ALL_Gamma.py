#! /usr/bin/env python
#'''
##################################################################################
#                                                                                #
#            Author:   Yun-Meng Cao                                              #
#            Email :   ymcmrs@gmail.com                                          #
#            Date  :   March, 2017                                               #
#                                                                                #
#           Coregistrating all SAR images to one master date                     #
#              OFFSET RSLC RSLCPar will be generated                             # 
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
   
            COREG_ALL_Gamma.py projectName
      
      e.g.  COREG_ALL_Gamma.py PacayaT163TsxHhA
           
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
    if 'memory_Coreg' in templateContents :  memory_Coreg =  templateContents['memory_Coreg']
    else: memory_Coreg = '3700'
    if 'walltime_Coreg' in templateContents :  walltime_Coreg =  templateContents['walltime_Coreg']
    else: walltime_Coreg = '2:00'
    
#####################  Extract SLC Date #################################  

    ListSLC = os.listdir(slcDir)
    Datelist = []
    SLCfile = []
    SLCParfile = []
    
    print "All of the available SAR acquisition datelist is :"  
    for kk in range(len(ListSLC)):
        if ( is_number(ListSLC[kk]) and len(ListSLC[kk])==6 ):
            DD=ListSLC[kk]
            Year=int(DD[0:2])
            Month = int(DD[2:4])
            Day = int(DD[4:6])
            if  ( 0 < Year < 20 and 0 < Month < 13 and 0 < Day < 32 ):            
                Datelist.append(ListSLC[kk])
                print ListSLC[kk]
                str_slc = slcDir + "/" + ListSLC[kk] +"/" + ListSLC[kk] + ".slc"
                str_slc_par = slcDir + "/" + ListSLC[kk] +"/" + ListSLC[kk] + ".slc.par"
                SLCfile.append(str_slc)
                SLCParfile.append(str_slc_par)
    
    if 'masterDate' in templateContents : 
        masterDate = templateContents['masterDate']
        if masterDate in Datelist:
            print "masterDate: %s" % masterDate
        else:
            print "The selected masterdate %s is not in the date list!! " % masterDate
            print "The first date is chosen as the master date: %s" % str(Datelist[0])
            masterDate = Datelist[0]
            Str = 'masterDate   =   %s \n' %masterDate
            write_template(templateFile, Str)           
    else:
        print "The first date is chosen as the master date: %s" % str(Datelist[0])
        masterDate = Datelist[0]
        Str = 'masterDate   =   %s \n' %masterDate
        write_template(templateFile, Str)
        
    SLAVElist = Datelist
    del SLAVElist[Datelist.index(masterDate)]
    
    
    run_coreg_all  = projectDir + "/run_coreg_all"
    if os.path.isfile(run_coreg_all):
        os.remove(run_coreg_all)

    
    write_run_coreg_all(projectName,masterDate,SLAVElist,rslcDir)
        
    call_str='$INT_SCR/createBatch.pl ' + projectDir+'/run_coreg_all memory=' + memory_Coreg + ' walltime=' + walltime_Coreg
    os.system(call_str)

    sys.exit(1)
    
if __name__ == '__main__':
    main(sys.argv[:])



















