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
        print("Keyword " + keyword + " doesn't exist in " + inFile)
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
    print('''
******************************************************************************************************

       Process time series of interferograms from downloading data or SLC images.

   usage:

            process_tsifg.py projectName

      e.g.  process_tsifg.py PacayaT163TsxHhA
            process_tsifg.py PacayaT163S1A

*******************************************************************************************************
    ''')

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

    templateContents = read_template(templateFile)

    key = 'memory_Coreg'
    if key in templateContents:
        memory_Coreg =  templateContents[key]
    else:
        memory_Coreg = '3700'
    key = 'walltime_Coreg'
    if key in templateContents:
        walltime_Coreg =  templateContents[key]
    else:
        walltime_Coreg = '1:00'

    key = 'memory_slc2ifg'
    if key in templateContents:
        memory_Ifg =  templateContents[key]
    else:
        memory_Ifg = '5000'
    key = 'walltime_slc2ifg'
    if key in templateContents:
        walltime_Ifg =  templateContents[key]
    else:
        walltime_Ifg = '4:00'

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
        call_str='process_tsifg_gamma.py ' + projectName

    os.system(call_str)

    print "Time series interferograms processing is done! "
    return

if __name__ == '__main__':
    main(sys.argv[:])
