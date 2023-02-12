#! /usr/bin/env python
#################################################################
###  This program is part of PyINT  v2.1                      ### 
###  Copy Right (c): 2017-2019, Yunmeng Cao                   ###  
###  Author: Yunmeng Cao                                      ###                                                          
###  Contact : ymcmrs@gmail.com                               ###  
#################################################################
import time
import numpy as np
import os
import sys  
import argparse
import h5py

from pyint import _utils as ut
from scipy.interpolate import griddata
from scipy.interpolate import NearestNDInterpolator

#def resamp2d_near(row0,col0,z0,row1,col1):

#    xx0, yy0 = np.meshgrid((np.arange(col0) + 1), (np.arange(row0) + 1))
#    xx1, yy1 = np.meshgrid((np.arange(col1) + 1), (np.arange(row1) + 1))

#    xx00 = xx0/col0*col1; yy00 = yy0/row0*row1
#    xx = xx00.flatten(); yy = yy00.flatten(); zz = z0.flatten()
#    interp = NearestNDInterpolator(list(zip(xx, yy)), zz)
#    z1 = interp(xx1, yy1)

#    return z1

def generate_name(i,j):
    
    if len(str(int(i)))==1:
        i0 = '0' + str(int(i))
    else:
        i0 = str(int(i))
        
    if len(str(int(j)))==1:
        j0 = '0' + str(int(j))
    else:
        j0 = str(int(j))
        
    name0 = i0+j0
    return name0

def reduce_samp(xx,yy,zz,xg,yg,extend):
    
    max_x = np.max(xg)+extend; min_x = np.min(xg)-extend # e.g. extend 100
    max_y = np.max(yg)+extend; min_y = np.min(yg)-extend # e.g., extend 100
    
    xx1 = xx[((min_x<xx) & (xx<max_x) & (min_y<yy) & (yy<max_y))]
    yy1 = yy[((min_x<xx) & (xx<max_x) & (min_y<yy) & (yy<max_y))]
    zz1 = zz[((min_x<xx) & (xx<max_x) & (min_y<yy) & (yy<max_y))]
    xx1 = np.reshape(xx1,(len(xx1),))
    yy1 = np.reshape(yy1,(len(yy1),))
    zz1 = np.reshape(zz1,(len(zz1),))
    
    return xx1,yy1,zz1

def interp_split(xx,yy,zz,xg,yg,split_numb):
    row0 = len(yg); col0 =len(xg); data_total = np.zeros((row0,col0),dtype='float32')
    drow = int(row0/split_numb); dcol = int(col0/split_numb)
    
    for ki in range(split_numb):
        if ki==(split_numb-1):
            rr = np.arange(ki*drow,row0)
        else:
            rr = np.arange(ki*drow,(ki+1)*drow)
        for kj in range(split_numb):
            if kj == (split_numb-1):
                cc = np.arange(kj*dcol,col0)
            else:
                cc = np.arange(kj*dcol,(ki+1)*dcol)
            xx1,yy1,zz1 = reduce_samp(xx,yy,zz,xg,yg,100)
            xgg1,ygg1 = np.meshgrid(xg,yg)
            xgg2 = xgg1[rr[0]:(rr[len(rr)-1]+1),cc[0]:(cc[len(cc)-1]+1)]
            ygg2 = ygg1[rr[0]:(rr[len(rr)-1]+1),cc[0]:(cc[len(cc)-1]+1)]
            #points0 = np.zeros((len(xx1),2),dtype='float32'); points0[:,0]=xx1; points0[:,1] = yy1
            #points0=(xx1,yy1);print(points0.shape)
            #print(xx1.shape);print(yy1.shape);print(zz1.shape);print(xgg1.shape);print(xgg2.shape);
            data0 = griddata((xx1,yy1),zz1,(xgg2,ygg2),method='linear') 
            #data0 = griddata(points0,zz1,(xgg2,ygg2),method='linear') 
            print(data0.shape)
            data_total[rr[0]:(rr[len(rr)-1]+1),cc[0]:(cc[len(cc)-1]+1)] = data0       
            
    return data_total

def get_startSamp(nLine, nWidth, awidth, rwidth):
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
    return Ap_samp1, Rp_samp1

def subset2coord(subset, astep, rstep, nLine, nWidth, awidth, rwidth, extend):
    # default awidth = 5000 rwidth = 5000 extend = 200
    # astep: azimuth multilook numbers
    # rstep: range multilook numbers
    extend = int(extend)
    Ap_samp1, Rp_samp1 = get_startSamp(nLine, nWidth, awidth, rwidth)
    Na = len(Ap_samp1); Nr = len(Rp_samp1)
    ii = int(subset[0:2]); jj = int(subset[2:4])
    #print(ii); print(jj)                      
    rstart = str(Rp_samp1[jj]); astart = str(Ap_samp1[ii]); 
    #print(nLine);print(Ap_samp1);print(Rp_samp1)
            
    if not ii==0:
        astart0 = str(int(int(astart) - extend)) # extend 200 to avoid edge effect
    else:
        astart0 = astart
    
    if not jj==0:
        rstart0 = str(int(int(rstart) - extend)) # extend 200 to avoid edge effect
    else:
        rstart0 = rstart
    
    #print('astart')
    #print(astart);print(Ap_samp1[Na-1])
    if astart == str(Ap_samp1[Na-1]):
        awidth0 = '-'
        aend0 = str(nLine)
    else:
        awidth0 = str(int(int(awidth) + extend)) # extend 200 to avoid edge effect
        aend0 = str(int(int(astart0) + int(awidth) + extend - 1))
  
    if rstart == str(Rp_samp1[Nr-1]):
        rwidth0 = '-'
        rend0 = str(nWidth)
    else:
        rwidth0 = str(int(int(rwidth) + extend)) # extend 200 to avoid edge effect
        rend0 = str(int(int(rstart0) + int(rwidth) + extend - 1))
    
    xx0 = np.arange(int(rstart0), int(rend0), int(rstep)); Nx0 = len(xx0); xx1 = xx0[0:Nx0-1]
    yy0 = np.arange(int(astart0), int(aend0), int(astep)); Ny0 = len(yy0); yy1 = yy0[1:Ny0]
    #print(rstart0); print(rend0); print(astart0); print(aend0)
    
    rwidth_total = int(int(rend0) - int(rstart0) + 1)
    awidth_total = int(int(aend0) - int(astart0) + 1)
    if np.mod(rwidth_total,int(rstep))==0:
        xx1 = xx0
    else:
        xx1 = xx0[0:Nx0-1]
        
    if np.mod(awidth_total,int(astep))==0:
        yy1 = yy0
    else:
        yy1 =yy0[0:Ny0-1]
        
    return xx1,yy1
                                    
def read_gammadata(file0,nWidth0,nLength0):
    data0 = np.fromfile(file0,dtype='>f4',count=int(nLength0)*int(nWidth0)).reshape(int(nLength0), int(nWidth0))
    return data0

def write_h5(datasetDict, out_file, metadata=None, ref_file=None, compression=None):

    if os.path.isfile(out_file):
        print('delete exsited file: {}'.format(out_file))
        os.remove(out_file)

    print('create HDF5 file: {} with w mode'.format(out_file))
    dt = h5py.special_dtype(vlen=np.dtype('float64'))


    with h5py.File(out_file, 'w') as f:
        for dsName in datasetDict.keys():
            data = datasetDict[dsName]
            ds = f.create_dataset(dsName,
                              data=data,
                              compression=compression)

        for key, value in metadata.items():
            f.attrs[key] = str(value)
            #print(key + ': ' +  value)
    print('finished writing to {}'.format(out_file))

    return out_file

INTRODUCTION = '''
-------------------------------------------------------------------  
       Combine subset of POT results from pot_gamma_subset_jobs.py  
'''

EXAMPLE = '''
    Usage: 
            pot_gamma_subset_combine.py projectName Mdate Sdate
            pot_gamma_subset_combine.py PacayaT163TsxHhA 20150601 20150613
-------------------------------------------------------------------  
'''

def cmdLineParse():
    parser = argparse.ArgumentParser(description='Combine subset of POT results from pot_gamma_subset_jobs.py',\
                                     formatter_class=argparse.RawTextHelpFormatter,\
                                     epilog=INTRODUCTION+'\n'+EXAMPLE)

    parser.add_argument('projectName',help='projectName for processing.')
    parser.add_argument('Mdate',help='First date.')
    parser.add_argument('Sdate',help='Second date.')
    #parser.add_argument('--out',dest ='out', help='Output file name.')
    parser.add_argument('--rwidth',dest ='rwidth', default = '5000', help='Patch range size.')
    parser.add_argument('--awidth',dest ='awidth', default = '5000', help='Patch azimuth size.')
    parser.add_argument('--extend',dest ='extend', default = '200', help='Patch extend to ensure overlap regions.')
    
    inps = parser.parse_args()
    return inps


def main(argv):
    
    inps = cmdLineParse()
    start_time = time.time()
    projectName = inps.projectName
    rwidth = inps.rwidth; awidth = inps.awidth; extend = inps.extend
    
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
    Mdate = inps.Mdate; Sdate = inps.Sdate
    Pair = Mdate + '-' + Sdate
    workDir = ifgDir + '/' + Pair
    MslcPar = rslcDir + '/' + Mdate + '/' + Mdate + '.rslc.par'
    
    Samp    = rslcDir + '/' + Sdate + '/' + Sdate + '_' + rlks + 'rlks.amp'
    SampPar = rslcDir + '/' + Sdate + '/' + Sdate + '_' + rlks + 'rlks.amp.par'
    SWidth = ut.read_gamma_par(SampPar, 'read', 'range_samples')
    SLine =  ut.read_gamma_par(SampPar, 'read', 'azimuth_lines')
    SampData = read_gammadata(Samp,SWidth,SLine)
    
    nWidth = ut.read_gamma_par(MslcPar, 'read', 'range_samples'); Rp_samp_large0 = np.arange(1,int(nWidth),int(rlks))
    nLine =  ut.read_gamma_par(MslcPar, 'read', 'azimuth_lines'); Ap_samp_large0 = np.arange(1,int(nLine),int(azlks))
    Nr0 = len(Rp_samp_large0); Na0 = len(Ap_samp_large0)
    
    if np.mod(int(nWidth),int(rlks))==0:
        Rp_samp_large = Rp_samp_large0
    else:
        Rp_samp_large = Rp_samp_large0[0:Nr0-1]
        
    if np.mod(int(nLine),int(azlks))==0:
        Ap_samp_large= Ap_samp_large0
    else:
        Ap_samp_large =Ap_samp_large0[0:Na0-1]
    
    rr,aa = np.meshgrid(Rp_samp_large,Ap_samp_large)
    
    Nr = len(Rp_samp_large); Na = len(Ap_samp_large)
    print('Total samples along range and azimuth: ' + str(Nr) + ' ' + str(Na))
    
    Ap_samp1,Rp_samp1 = get_startSamp(nLine, nWidth, awidth, rwidth)
    Na = len(Ap_samp1); Nr = len(Rp_samp1)
    
    xx_total = []; yy_total = []; az_total = []; rg_total = []; cc_total = [];
    for i in range(Na):
        for j in range(Nr):
            subset0 = generate_name(i,j)
            xx0,yy0 = subset2coord(subset0, azlks, rlks, nLine, nWidth, awidth, rwidth, extend)
            #print(len(xx0)); print(len(yy0))
            [xx0,yy0] = np.meshgrid(xx0,yy0)
            az0 = workDir + '/' + Pair + '_' + subset0 + '_' + rlks + 'rlks_pot.az'
            rg0 = workDir + '/' + Pair + '_' + subset0 + '_' + rlks + 'rlks_pot.rg'
            cc0 = workDir + '/' + Pair + '_' + subset0 + '_' + rlks + 'rlks_pot.ccp'
            off0 = workDir + '/' + Pair + '_' + subset0 + '_' + rlks + 'rlks_pot.off'
            nLine0 = ut.read_gamma_par(off0, 'read', 'interferogram_azimuth_lines')
            nWidth0 =  ut.read_gamma_par(off0, 'read', 'interferogram_width')
            #print(nWidth0);print(nLine0)
            if os.path.isfile(az0):
                if os.path.getsize(az0)>0: 
                    az_data0 = read_gammadata(az0,nWidth0,nLine0)
                    rg_data0 = read_gammadata(rg0,nWidth0,nLine0)
                    cc_data0 = read_gammadata(cc0,nWidth0,nLine0)
            
                    xx_total.extend(list(xx0.flatten()));yy_total.extend(list(yy0.flatten()))
                    az_total.extend(list(az_data0.flatten()))
                    rg_total.extend(list(rg_data0.flatten()))
                    cc_total.extend(list(cc_data0.flatten()))
            else:
                data0 = np.zeros((int(nWidth0),int(nLine0)),dtype='float32')
                xx_total.extend(list(data0.flatten()));yy_total.extend(list(data0.flatten()))
                az_total.extend(list(data0.flatten()))
                rg_total.extend(list(data0.flatten()))
                cc_total.extend(list(data0.flatten()))
            
    xx_total = np.asarray(xx_total); #print(xx_total.shape)
    yy_total = np.asarray(yy_total); #print(yy_total.shape)
    az_total = np.asarray(az_total); #print(az_total.shape)
    rg_total = np.asarray(rg_total); #print(rg_total.shape)
    cc_total = np.asarray(cc_total); #print(cc_total.shape)
    
    xxa = xx_total[az_total!=0]; yya = yy_total[az_total!=0]; az_total1 = az_total[az_total!=0]
    xxr = xx_total[rg_total!=0]; yyr = yy_total[rg_total!=0]; rg_total1 = rg_total[rg_total!=0]
    xxc = xx_total[cc_total!=0]; yyc = yy_total[cc_total!=0]; cc_total1 = cc_total[cc_total!=0]
    
    #start_time = time.time()
    #az_grid_large = interp_split(xxa,yya,az_total1,Rp_samp_large,Ap_samp_large,2); print('1 finish')
    #rg_grid_large = interp_split(xx_total,yy_total,rg_total1,Rp_samp_large,Ap_samp_large,2)
    #cc_grid_large = interp_split(xx_total,yy_total,cc_total1,Rp_samp_large,Ap_samp_large,2)
    
    #start_time = time.time()
    #interp_az = NearestNDInterpolator(list(zip(xxa, yya)), az_total1)
    #az_grid_large = interp_az(rr, aa)
    #interp_rg = NearestNDInterpolator(list(zip(xxr, yyr)), rg_total1)
    #rg_grid_large = interp_rg(rr, aa)
    #interp_cc = NearestNDInterpolator(list(zip(xxc, yyc)), cc_total1)
    #cc_grid_large = interp_cc(rr, aa)
    #ut.print_process_time(start_time, time.time()) 
    
    method0 = 'nearest' # keep 0 values to make good mask
    print('Start to combine all of the sub-patches ...')
    start_time = time.time()
    az_grid_large = griddata((xxa,yya),az_total1,(rr,aa),method=method0); print('Azimuth interpolate finish')
    #ut.print_process_time(start_time, time.time()) 
    #start_time = time.time()
    rg_grid_large = griddata((xxr,yyr),rg_total1,(rr,aa),method=method0); print('Range interpolate finish')
    #ut.print_process_time(start_time, time.time()) 
    #start_time = time.time()
    cc_grid_large = griddata((xxc,yyc),cc_total1,(rr,aa),method=method0); print('CCP interpolate finish')
    ut.print_process_time(start_time, time.time())
    
    az_grid_large[SampData==0]=0
    rg_grid_large[SampData==0]=0
    cc_grid_large[SampData==0]=0
    
    row1,col1 = rr.shape
    meta = dict()
    meta['WIDTH'] = str(col1); meta['LENGTH'] = str(row1); meta['UNIT'] = 'm'
    meta['FILE_TYPE'] ='offset_tracking'; meta['DATE12'] = Pair
    
    datasetDict = dict()
    datasetDict['azimuth'] = az_grid_large
    #datasetDict['range'] = rg_grid_large
    #datasetDict['ccp'] = cc_grid_large
    #if inps.out:
    #    out_file = inps.out
    #else:
    out_file = Pair + '_pot_az.h5'
    write_h5(datasetDict, out_file, metadata=meta, ref_file=None, compression=None)
    
    datasetDict = dict()
    #datasetDict['azimuth'] = az_grid_large
    datasetDict['range'] = rg_grid_large
    #datasetDict['ccp'] = cc_grid_large
    out_file = Pair + '_pot_rg.h5'
    write_h5(datasetDict, out_file, metadata=meta, ref_file=None, compression=None)
    

    datasetDict = dict()
    #datasetDict['azimuth'] = az_grid_large
    #datasetDict['range'] = rg_grid_large
    datasetDict['coherence'] = cc_grid_large 
    #meta['FILE_TYPE'] = 'coherence'
    out_file = Pair + '_pot_cc.h5'
    write_h5(datasetDict, out_file, metadata=meta, ref_file=None, compression=None)
    print("POT calculation done: " + Pair)
    #sys.exit(1)

if __name__ == '__main__':
    main(sys.argv[:])
