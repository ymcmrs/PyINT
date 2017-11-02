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
import re
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


def usage():
    print('''
******************************************************************************************************

           Generating interferograms from SLC : InSAR, MAI, Split-specrum Interferometry

      usage:

            SLC2Ifg_Gamma.py igramDir

      e.g.  SLC2Ifg_Gamma.py IFG_PacayaT163TsxHhA_131021-131101_0011_0007
      e.g.  SLC2Ifg_Gamma.py MAI_PacayaT163TsxHhA_131021-131101_0011_0007
      e.g.  SLC2Ifg_Gamma.py RSI_PacayaT163TsxHhA_131021-131101_0011_0007
*******************************************************************************************************
    ''')

def main(argv):

    if len(sys.argv)==2:
        if argv[0] in ['-h','--help']: usage(); sys.exit(1)
        else: igramDir=sys.argv[1]
    else:
        usage();sys.exit(1)

    projectName = igramDir.split('_')[1]

    scratchDir = os.getenv('SCRATCHDIR')
    templateDir = os.getenv('TEMPLATEDIR')
    templateFile = templateDir + "/" + projectName + ".template"
    templateContents=read_template(templateFile)

    processDir = scratchDir + '/' + projectName + "/PROCESS"
    workDir    = processDir + '/' + igramDir

    if not os.path.isdir(workDir):
        call_str="mkdir "+ workDir
        os.system(call_str)


    if 'Coreg_int'          in templateContents: Coreg_int = templateContents['Coreg_int']
    else: Coreg_int = '1'

    if 'INT_Flag'          in templateContents: INT_Flag = templateContents['INT_Flag']
    else: INT_Flag = '1'

    if 'DIFF_Flag'          in templateContents: DIFF_Flag = templateContents['DIFF_Flag']
    else: DIFF_Flag = '1'

    if 'UNW_Flag'          in templateContents: UNW_Flag = templateContents['UNW_Flag']
    else: UNW_Flag = '1'

    if 'UNW_SUB_Flag'          in templateContents: UNW_SUB_Flag = templateContents['UNW_SUB_Flag']
    else: UNW_SUB_Flag = '1'

    if 'GEO_Flag'          in templateContents: GEO_Flag = templateContents['GEO_Flag']
    else: GEO_Flag = '1'

##############################################################

    if 'coregMethod'          in templateContents: coregMethod = templateContents['coregMethod']
    else: coregMethod = 'Init'
    if 'unwrapMethod'          in templateContents: unwrapMethod = templateContents['unwrapMethod']
    else: unwrapMethod = 'mcf'


    if Coreg_int == '1' :
        if coregMethod == "DEM":
            call_str = "CoregistSLC_DEM_Gamma.py " + igramDir
            os.system(call_str)
        else:
            call_str = "CoregistSLC_init_Gamma.py " + igramDir
            os.system(call_str)

    if INT_Flag == '1' :
        call_str = "GenIgram_Gamma.py " + igramDir
        os.system(call_str)

    if DIFF_Flag == '1':
        call_str = "SimPhase_Gamma.py " + igramDir
        os.system(call_str)
        call_str = "DiffPhase_Gamma.py " + igramDir
        os.system(call_str)

    call_str = "GenerateRSC_Gamma.py " + igramDir
    os.system(call_str)

    if UNW_Flag == '1':
        if unwrapMethod =="mcf":
            call_str = "UnwrapPhase_Gamma.py " + igramDir
            os.system(call_str)
        else:
            call_str = "UnwrapPhase_BranchCut_Gamma.py " + igramDir
            os.system(call_str)

    if GEO_Flag == '1':
        call_str = "Geocode_Gamma.py " + igramDir
        os.system(call_str)

    date12 = str(re.findall('\d{8}[-_]\d{8}', igramDir)[0]).replace('_','-')
    m_date, s_date = date12.split('-')
    rmCmd = 'rm %s.int %s.rslc %s.rslc flat_%s_rlks.int' % (date12, m_date, s_date, date12);   print rmCmd;  os.system(rmCmd)

    print "SLC to interferogram done!"
    return



if __name__ == '__main__':
    main(sys.argv[:])
