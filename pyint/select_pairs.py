#! /usr/bin/env python
#################################################################
###  This program is part of PyINT  v2.1                      ### 
###  Copy Right (c): 2019, Yunmeng Cao                        ###  
###  Author: Yunmeng Cao                                      ###                                                          
###  Contact : ymcmrs@gmail.com                               ###  
#################################################################
# This program is modified from MintPy/select_network.py
# Copyright: 2017-2019, Yunjun Zhang
# Contact: yzhang@rsmas.miami.edu 

import os
import sys
import glob
import argparse
import datetime
import inspect
import numpy as np

from pyint import _utils as ut
from pyint import _network as nt

def get_datelist_bperplist(TS_Net):
    
    IFG_Flag=np.asarray(TS_Net[:,0])
    MDatelist=np.asarray(TS_Net[:,1])
    SDatelist=np.asarray(TS_Net[:,2])
    Berplist=np.asarray(TS_Net[:,3])
    TBaselist=np.asarray(TS_Net[:,4])
    
    date_list = []
    date_list.append(MDatelist[0])
    for k0 in SDatelist:
        date_list.append(k0)
    bperp_list = []
    bperp_list.append(0)
    for k0 in Berplist:
        bperp_list.append(float(k0))
    
    tbase_list = []
    tbase_list.append(0)
    for k0 in TBaselist:
        tbase_list.append(float(k0))
    return date_list, tbase_list, bperp_list


def prune_datelist(date_list, tbase_list, pbase_list, templateDict):
    nn = len(date_list)
    
    date_list_out = []
    for k0 in date_list:
        if (k0 not in templateDict['exclude_list']) and (float(templateDict['startDate']) < float(k0)) and (float(templateDict['endDate']) > float(k0)):
            date_list_out.append(k0)
    date_list_out = sorted(date_list_out)
    tbase_list_out = []
    pbase_list_out = []
    for k0 in date_list_out:
        tbase0 = tbase_list[date_list.index(k0)]
        pbase0 = pbase_list[date_list.index(k0)]
        tbase_list_out.append(float(tbase0))
        pbase_list_out.append(float(pbase0))
        
        tbase_list_out0 = np.asarray(tbase_list_out)
        pbase_list_out0 = np.asarray(pbase_list_out)
        
        tbase_list_out1 = tbase_list_out0 - tbase_list_out0[0]
        pbase_list_out1 = pbase_list_out0 - pbase_list_out0[0]
       
    return date_list_out, list(tbase_list_out1), list(pbase_list_out1)
   
def select_network_candidate(date_list,tbase_list,pbase_list,templateDict):
    
    method = templateDict['network_method']
    
    # Pais selection from method
    if method == 'sbas':
        date12_list = nt.select_pairs_sbas(date_list)
    elif method == 'delaunay':
        date12_list = nt.select_pairs_delaunay(date_list, pbase_list, norm = True)
    elif method == 'star':
        date12_list = nt.select_pairs_star(date_list)
    elif method == 'sequential':
        date12_list = nt.select_pairs_sequential(date_list, int(templateDict['conNumb']))
    #elif method == 'hierarchical':
    #    date12_list = nt.select_pairs_hierarchical(date_list, pbase_list, inps.tempPerpList)
    #elif method == 'mst':
    #    date12_list = nt.select_pairs_mst(date_list, pbase_list)
    else:
        raise Exception('Unrecoganized select method: '+ method)
        
    date12_list =nt.yyyymmdd_date12(date12_list)
    nn = len(date12_list)
    
    ifgram_tbase_list = []
    ifgram_pbase_list = []
    for i in range(nn):
        m0 = date12_list[i].split('-')[0]
        s0 = date12_list[i].split('-')[1]
        
        tbase0 = float(tbase_list[date_list.index(s0)]) - float(tbase_list[date_list.index(m0)])
        pbase0 = float(pbase_list[date_list.index(s0)]) - float(pbase_list[date_list.index(m0)])
        
        ifgram_tbase_list.append(tbase0)
        ifgram_pbase_list.append(pbase0)
    
    return date12_list, ifgram_tbase_list, ifgram_pbase_list


def prune_network(date12_list, ifgram_tbase_list, ifgram_pbase_list, templateDict):
    """Pruning network candidates based on temp/perp baseline"""
    date12_list0 = date12_list.copy()
    ifgram_tbase_list = [float(i) for i in ifgram_tbase_list]
    ifgram_pbase_list = [float(i) for i in ifgram_pbase_list]
    
    ifgram_tbase_list_abs = [abs(i) for i in ifgram_tbase_list]
    ifgram_pbase_list_abs = [abs(i) for i in ifgram_pbase_list]
    
    ifgram_tbase_list_abs = np.asarray(ifgram_tbase_list_abs)
    ifgram_pbase_list_abs = np.asarray(ifgram_pbase_list_abs)
    
    date12_list0 = np.asarray(date12_list0)
    ifgram_tbase_list = np.asarray(ifgram_tbase_list)
    ifgram_pbase_list = np.asarray(ifgram_pbase_list)
   
    date12_list_out = date12_list0[(ifgram_tbase_list_abs < float(templateDict['max_tb'])) & (ifgram_pbase_list_abs < float(templateDict['max_sb']))]
    ifgram_tbase_list_out = ifgram_tbase_list[(ifgram_tbase_list_abs < float(templateDict['max_tb'])) & (ifgram_pbase_list_abs < float(templateDict['max_sb']))]
    ifgram_pbase_list_out = ifgram_pbase_list[(ifgram_tbase_list_abs < float(templateDict['max_tb'])) & (ifgram_pbase_list_abs < float(templateDict['max_sb']))]

    return list(date12_list_out), list(ifgram_tbase_list_out), list(ifgram_pbase_list_out)


def write_ifgram_list(date12_list,ifgram_tbase_list,ifgram_pbase_list, out_file):
    # Output directory/filename
    # Write txt file
    f = open(out_file, 'w')
    #f.write('#Interferograms configuration generated by select_network.py\n')
    #f.write('#   Date12      Btemp(days)    Bperp(m)    sim_coherence\n')
    for i in range(len(date12_list)):
        line = '{}   {:6.0f}         {:6.1f}'.format(date12_list[i],
                                                     ifgram_tbase_list[i],
                                                     ifgram_pbase_list[i])
        f.write(line+'\n')
    f.close()
    return out_file

#---------------------------------------------------------------------------------------------------#
def cmdLineParse():
    parser = argparse.ArgumentParser(description='Select interferometric pairs for time-series InSAR process.',\
                                     formatter_class=argparse.RawTextHelpFormatter,\
                                     epilog=INTRODUCTION+'\n'+EXAMPLE)

    parser.add_argument('projectName',help='projectName for processing.')
    parser.add_argument('-o', '--outfile',dest = 'outfile',help='Output list file for network, ifgram_list.txt by default.')
    parser.add_argument('--exclude',dest='excludeDate', nargs='*', default=[],
                        help='date(s) excluded for network selection, e.g. --exclude 060713 070831')
    parser.add_argument('--start-date', dest='startDate', type=str, help='start/min date of network')
    parser.add_argument('--end-date', dest='endDate', type=str, help='end/max date of network')
    parser.add_argument('--max-sb', dest='maxSB', type=float, help='maximum spatial baseline')
    parser.add_argument('--max-tb', dest='maxTB', type=str, help='maximum temporal baseline')
    
    inps = parser.parse_args()
    return inps


INTRODUCTION = '''
-------------------------------------------------------------------  
       Select interferometric pairs based on SLC_TAB. 
       [sbas, sequential, delaunay, stars (as PS) are supported.]

'''

EXAMPLE = '''
    Usage: 
            select_pairs.py projectName 
            select_pairs.py PacayaT163TsxHhA 
-------------------------------------------------------------------  
'''

def main(argv):
    
    inps = cmdLineParse()     
    projectName = inps.projectName
    scratchDir = os.getenv('SCRATCHDIR')
    templateDir = os.getenv('TEMPLATEDIR')
    templateFile = templateDir + "/" + projectName + ".template"
    templateDict=ut.update_template(templateFile)
    
    processDir = scratchDir + '/' + projectName
    slcDir     = scratchDir + '/' + projectName + "/SLC"
    rslcDir    = scratchDir + '/' + projectName + '/RSLC'
    
    #slc_list = [os.path.basename(fname) for fname in sorted(glob.glob(slcDir + '/*'))]
    slc_list = ut.get_project_slcList(projectName)
    
    masterDate = templateDict['masterDate'] 
    
    SLCfile = []
    SLCParfile = []
    for kk in range(len(slc_list)):
        str_slc = slcDir + "/" + slc_list[kk] +"/" + slc_list[kk] + ".slc"
        str_slc_par = slcDir + "/" + slc_list[kk] +"/" + slc_list[kk] + ".slc.par"
        SLCfile.append(str_slc)
        SLCParfile.append(str_slc_par)       

    RefPar = slcDir + "/" + masterDate +"/" + masterDate + ".slc.par"
    SLC_Tab = scratchDir + '/' + projectName  + "/SLC_Tab"
    
    SLC_Tab_all = processDir + "/SLC_Tab_all"
    TS_Berp_all = processDir + "/TS_Berp_all"
    TS_Itab_all = processDir + "/TS_Itab_all"
    itab_type = '1'
    pltflg = '0'
    
    if os.path.isfile(SLC_Tab): os.remove(SLC_Tab)
    with open(SLC_Tab, 'a') as f:
        for kk in range(len(SLCfile)):
            f.write(str(SLCfile[kk])+ ' '+str(SLCParfile[kk])+'\n')

    ## Get all of the pairs using GAMMA
    call_str = "base_calc " + SLC_Tab + " " + RefPar + " " + TS_Berp_all + " " + TS_Itab_all + " " + '1 0 ' + '- - - -  >/dev/null'
    os.system(call_str)
      
    with open(TS_Berp_all, 'r') as f:
        lines = f.readlines()  
        
    TS_Net_all = ut.read_txt2array(TS_Berp_all)
    if len(lines) ==1:
        TS_Net_all = TS_Net_all.reshape(1,9)

    TS_Net = TS_Net_all[0:(len(SLCfile)-1),:]
    date_list, tbase_list, pbase_list =  get_datelist_bperplist(TS_Net)
    bl_list_txt =  scratchDir + '/' + projectName + '/bl_list.txt'
    with open(bl_list_txt, 'w') as f:
        for kk in range(len(SLCfile)):
            f.write(str(date_list[kk])+ ' '+str(pbase_list[kk])+'\n')
       
    exclude_list = []
    if 'exclude_date' in templateDict: 
        exclude_list = templateDict['exclude_date'].split(',')[:]
    if inps.excludeDate:
        exclude_list0 = inps.excludeDate
        for k0 in exclude_list0:
            exclude_list.append(k0)
    templateDict['exclude_list'] = exclude_list
    
    if inps.startDate: templateDict['startDate'] = inps.startDate
    if inps.endDate: templateDict['endDate'] = inps.endDate
    if inps.maxTB: templateDict['max_tb'] = inps.maxTB
    if inps.maxSB: templateDict['max_sb'] = inps.maxSB
        
    date_list, tbase_list, pbase_list = prune_datelist(date_list, tbase_list, pbase_list, templateDict)
    date12_list, ifgram_tbase_list, ifgram_pbase_list = select_network_candidate(date_list,tbase_list,pbase_list,templateDict)
    date12_list_final, ifgram_tbase_list_final, ifgram_pbase_list_final =  prune_network(date12_list, ifgram_tbase_list, ifgram_pbase_list, templateDict)
    
    if inps.outfile: out_file = inps.outfile
    else: out_file = scratchDir + '/' + projectName  + "/ifgram_list.txt"
        
    write_ifgram_list(date12_list_final,ifgram_tbase_list_final,ifgram_pbase_list_final, out_file)
    sys.exit(1)
    
####################################################################    
if __name__ == '__main__':
    main(sys.argv[:])    
    