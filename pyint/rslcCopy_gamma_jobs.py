#! /usr/bin/env python
#################################################################
###  This program is part of PyINT  v2.1                      ### 
###  Copy Right (c): 2017-2019, Yunmeng Cao                   ###  
###  Author: Yunmeng Cao                                      ###                                                          
###  Contact : ymcmrs@gmail.com                               ###  
#################################################################

import numpy as np
import os
import sys  
import argparse

from pyint import _utils as ut


INTRODUCTION = '''
-------------------------------------------------------------------  
       copy SLC/RSLC from large SLC/RSLC
   
'''

EXAMPLE = '''
    Usage: 
            slcCopy_gamma_jobs.py projectName Sdate rwidth awidth --memory memory_single_job --walltime walltime_single_job
            slcCopy_gamma_jobs.py PacayaT163TsxHhA 20150601 5000 5000 --memory 5000 --walltime 00:30:00
-------------------------------------------------------------------  
'''

def cmdLineParse():
    parser = argparse.ArgumentParser(description='Copy SLC subset from a large SLC.',\
                                     formatter_class=argparse.RawTextHelpFormatter,\
                                     epilog=INTRODUCTION+'\n'+EXAMPLE)

    parser.add_argument('projectName',help='projectName for processing.')
    parser.add_argument('Date',help='Master date.')
    parser.add_argument('rwidth',help='width of range direction')
    parser.add_argument('awidth',help='width of azimith direction')
    parser.add_argument('--memory',dest = 'memory',default = '2000', help='memory to be allocated for one job, default: 5GB')
    parser.add_argument('--walltime',dest = 'walltime',default = '00:05:00', help='walltime to be allocated for one single job')
    inps = parser.parse_args()
    return inps


def main(argv):
    
    inps = cmdLineParse()     
    projectName = inps.projectName
    Date = inps.Date; rwidth = inps.rwidth; awidth = inps.awidth; memory = inps.memory; walltime = inps.walltime
    
    scratchDir = os.getenv('SCRATCHDIR')
    templateDir = os.getenv('TEMPLATEDIR')
    templateFile = templateDir + "/" + projectName + ".template"
    templateDict=ut.update_template(templateFile)
    rlks = templateDict['range_looks']
    azlks = templateDict['azimuth_looks']
    
    processDir = scratchDir + '/' + projectName + "/PROCESS"
    slcDir     = scratchDir + '/' + projectName + "/SLC"
    rslcDir    = scratchDir + '/' + projectName + '/RSLC'
    ifgDir     = scratchDir + '/' + projectName + '/ifgrams'
    
    Dslc    = rslcDir + '/' + Date + '/' + Date + '.rslc'
    DslcPar = rslcDir + '/' + Date + '/' + Date + '.rslc.par'
    
    nWidth = ut.read_gamma_par(DslcPar, 'read', 'range_samples')
    nLine =  ut.read_gamma_par(DslcPar, 'read', 'azimuth_lines')
    
    Ap_samp = np.arange(1,int(nLine),int(awidth)); Na0 = len(Ap_samp); LA_end = int(nLine) - Ap_samp[Na0-1]
    Rp_samp = np.arange(1,int(nWidth),int(rwidth)); Nr0 = len(Rp_samp); LR_end = int(nWidth) - Rp_samp[Nr0-1]
    
    if LA_end > (2/3*int(awidth)):
        Ap_samp1 = Ap_samp
    else:
        Ap_samp1 = Ap_samp[0:(Na0-1)]  # last batch with '-' means to the end
    
    if LR_end > (2/3*int(rwidth)):
        Rp_samp1 = Rp_samp
    else:
        Rp_samp1 = Rp_samp[0:(Nr0-1)]  # last batch with '-' means to the end
    
    Na = len(Ap_samp1); Nr = len(Rp_samp1); Ntotal = Na*Nr
    print('Azimuth samples: ' + str(Na))
    print('Range samples: ' + str(Nr))
    print('Total batch numbers: ' + str(Ntotal))
    
    batch_txt = scratchDir + '/' + projectName + '/RSLC/' + Date + '/Batch_copySLC'
    workDir = scratchDir + '/' + projectName + '/RSLC/' + Date 
    if os.path.isfile(batch_txt):
        os.remove(batch_txt)
    for i in range(Na):
        for j in range(Nr):
            if len(str(i)) == 1:
                i0 = '0' + str(i)
            else:
                i0 = str(i)  
            if len(str(j)) == 1:
                j0 = '0' + str(j)
            else:
                j0 = str(j)
            name0 = Date + '_' +i0 + j0
            rstart = str(Rp_samp1[j]); astart = str(Ap_samp1[i])
            if rstart == str(Rp_samp1[Nr-1]):
                rwidth0 = '-'
            else:
                rwidth0 = str(int(int(rwidth) + 200)) # extend 200 to avoid edge effect
                
            if astart == str(Ap_samp1[Na-1]):
                awidth0 = '-'
            else:
                awidth0 = str(int(int(awidth) + 200)) # extend 200 to avoid edge effect
            
            if not i==0:
                astart0 = str(int(int(astart) - 200)) # extend 200 to avoid edge effect
            else:
                astart0 = astart
            
            if not j==0:
                rstart0 = str(int(int(rstart) - 200)) # extend 200 to avoid edge effect
            else:
                rstart0 = rstart
            
            #str0 = 'SLC_copy ' + Dslc + ' ' + DslcPar + ' ' + workDir + '/' + name0 + '.rslc' + ' ' + workDir + '/' + name0 + '.rslc.par - - ' + rstart0 + ' ' + rwidth0 + ' ' + astart0 + ' ' + awidth0 + ' - -'   
            str0 = 'rslcCopy_gamma.py ' + projectName + ' ' + Date + ' ' +  rstart0 + ' ' + rwidth0 + ' ' + astart0 + ' ' + awidth0 + ' ' +  name0
            call_str = 'echo ' + str0 + ' >>' + batch_txt
            os.system(call_str)

    call_str = 'sbatch_jobs.py ' + batch_txt + ' --memory ' + inps.memory + ' --walltime ' + inps.walltime + ' --job-name ' +  Date + '_copySLC'
    os.system(call_str)
            
    print("RSLC copy done: " + Date)
    #sys.exit(1)

if __name__ == '__main__':
    main(sys.argv[:])
