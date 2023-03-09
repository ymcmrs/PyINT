#! /usr/bin/env python
# MPInSAR method for correting InSAR turbulent troposphere
# Author: Yunmeng Cao   01 Oct., 2021 

import sys
import os
import re
import subprocess
import argparse
import numpy as np
import h5py
from gigpy import elevation_models
from numpy.linalg import matrix_rank

from pykrige import OrdinaryKriging
from pykrige import variogram_models

from scipy.optimize import leastsq
from scipy.stats.stats import pearsonr

from tqdm import tqdm
from concurrent.futures import ProcessPoolExecutor, as_completed

from gigpy import _utils as ut

from pysme import variogram
###### mintPy modelu ###############################
from mintpy.utils import (ptime,
                          readfile,
                          utils as ut,
                          plot as pp)
from mintpy.multilook import multilook_data
from mintpy import subset, version
#########################################################################
def get_lat_lon(meta, box=None):
    """extract lat/lon info of all grids into 2D matrix.
    For meta dict in geo-coordinates only.
    Returned lat/lon are corresponds to the pixel center
    Parameters: meta : dict, including LENGTH, WIDTH and Y/X_FIRST/STEP
                box  : 4-tuple of int for (x0, y0, x1, y1)
    Returns:    lats : 2D np.array for latitude  in size of (length, width)
                lons : 2D np.array for longitude in size of (length, width)
    """
    length, width = int(meta['LENGTH']), int(meta['WIDTH'])
    if box is None:
        box = (0, 0, width, length)
    lat_num = box[3] - box[1]
    lon_num = box[2] - box[0]

    # generate 2D matrix for lat/lon
    lat_step = float(meta['Y_STEP'])
    lon_step = float(meta['X_STEP'])
    lat0 = float(meta['Y_FIRST']) + lat_step * (box[1])
    lon0 = float(meta['X_FIRST']) + lon_step * (box[0])
    lat1 = lat0 + lat_step * lat_num
    lon1 = lon0 + lon_step * lon_num
    lats, lons = np.mgrid[lat0:lat1:lat_num*1j,
                          lon0:lon1:lon_num*1j]

    lats = np.array(lats, dtype=np.float32)
    lons = np.array(lons, dtype=np.float32)
    return lats, lons

def remove_numb(x,y,z,numb=0):
    
    z = np.asarray(z,dtype=np.float32)
    sort_z = sorted(list(np.abs(z)))
    k0 = sort_z[len(z)-numb-1] + 0.0001
    
    fg = np.where(abs(z)<k0)
    fg = np.asarray(fg,dtype=int)
    
    x0 = x[fg]
    y0 = y[fg]
    z0 = z[fg]
    
    return x0, y0, z0

def get_dataNames(FILE):
    with h5py.File(FILE, 'r') as f:
        dataNames = []
        for k0 in f.keys():
            dataNames.append(k0)
    return dataNames

def read_hdf5(fname, datasetName=None, box=None):
    # read hdf5
    with h5py.File(fname, 'r') as f:
        data = f[datasetName][:]
        atr = dict(f.attrs)
        
    return data, atr

def read_attr(fname):
    # read hdf5
    with h5py.File(fname, 'r') as f:
        atr = dict(f.attrs)
        
    return atr

def split_lat_lon_kriging(nn, processors = 4):

    dn = round(nn/int(processors))
    
    idx = []
    for i in range(processors):
        a0 = i*dn
        b0 = (i+1)*dn
        
        if i == (processors - 1):
            b0 = nn
        
        if not a0 > b0:
            idx0 = np.arange(a0,b0)
            #print(idx0)
            idx.append(idx0)
            
    return idx

def OK_function(data0):
    OK,lat0,lon0,np = data0
    z0,s0 = OK.execute('points', lon0, lat0, n_closest_points= np, backend='loop')
    #print(s0)
    return z0,s0

def dist_weight_interp(data0):
    lat0,lon0,z0,lat1,lon1 = data0
    
    lat0 = np.asarray(lat0)
    lon0 = np.asarray(lon0)
    z0 = np.asarray(z0)
    
    if len(z0)==1:
        z0 = z0[0]
    nn = len(lat1)
    data_interp = np.zeros((nn,))
    weight_all = []
    for i in range(nn):
        dist0 = latlon2dis(lat0,lon0,lat1[i],lon1[i])
        weight0 = (1/dist0)**2
        if len(weight0) ==1:
            weight0 = weight0[0]
        weight = weight0/sum(weight0[:])
        data_interp[i] = sum(z0*weight)
        weight_all.append(weight)
    return data_interp,weight_all

def generate_para_data(lats, lons, OK, used_point_numb, split_numb):
    idx_list = split_lat_lon_kriging(len(lats),processors = split_numb)
    data_all = []
    for k in range(split_numb):
        data0 = (OK,lats[idx_list[k]],lons[idx_list[k]],used_point_numb)
        data_all.append(data0)
    return idx_list, data_all

def solve_mpinsar(raw_data, OK_function, idx_list, para_data, parallel_numb):
    
    raw_data[np.isnan(raw_data)] = 0
    zz = raw_data.copy(); zz = zz.flatten()
    zz_sigma = raw_data.copy(); zz_sigma = zz_sigma.flatten()
    future = parallel_process(para_data, OK_function, n_jobs=parallel_numb, use_kwargs=False)
    #print(future)
    #print(future[0])
    for j in range(100):
        id0 = idx_list[j]
        gg = future[j]
        #print(future[j])
        #print(gg)
        #print(gg.shape)
        zz[id0] = gg[0]
        zz_sigma[id0] = gg[1]
    
    Row,Col = raw_data.shape
    data_cor_std = zz_sigma.reshape(Row,Col)
    data_aps = zz.reshape(Row,Col)
    data_cor = raw_data - data_aps
    data_cor[raw_data==0] = 0
    
    return data_cor, data_cor_std, data_aps

def max_distance(atr):
    
    width = int(atr['WIDTH'])
    length = int(atr['LENGTH'])
    
    if 'X_FIRST' in atr:
        lon0 = float(atr['X_FIRST'])
        lat0 = float(atr['Y_FIRST'])
        lon_step = float(atr['X_STEP'])
        lat_step = float(atr['Y_STEP'])
        
        lat1 = lat0 + length*lat_step
        lon1 = lon0 + width*lon_step
        
        max_distance = latlon2dis(lat1,lon1,lat0,lon0,R=6371)
    
    else:
        pixel = float(atr['AZIMUTH_PIXEL_SIZE'])
        max_distance = math.sqrt(width**2 + length**2)
        max_distance = max_distance*pixel/1000
        
    return max_distance

def calc_distance(atr,dx,dy):
    
    if 'X_FIRST' in atr:
        lon0 = float(atr['X_FIRST'])
        lat0 = float(atr['Y_FIRST'])
        lon_step = float(atr['X_STEP'])
        lat_step = float(atr['Y_STEP'])
        
        lat1 = lat0 + dy*lat_step
        lon1 = lon0 + dx*lon_step
        
        distance = latlon2dis(lat1,lon1,lat0,lon0,R=6371)
    
    else:
        pixel = float(atr['AZIMUTH_PIXEL_SIZE'])
        distance = math.sqrt(dx**2 + dy**2)
        distance = distance*pixel/1000
    
    return distance

def write_h5(datasetDict, out_file, metadata=None, ref_file=None, compression=None):
    'lags                  1 x N '
    'semivariance          M x N '
    'sills                 M x 1 '
    'ranges                M x 1 '
    'nuggets               M x 1 '
    
    if os.path.isfile(out_file):
        print('delete exsited file: {}'.format(out_file))
        os.remove(out_file)

    print('create HDF5 file: {} with w mode'.format(out_file))
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

def parallel_process(array, function, n_jobs=16, use_kwargs=False):
    """
        A parallel version of the map function with a progress bar. 

        Args:
            array (array-like): An array to iterate over.
            function (function): A python function to apply to the elements of array
            n_jobs (int, default=16): The number of cores to use
            use_kwargs (boolean, default=False): Whether to consider the elements of array as dictionaries of 
                keyword arguments to function 
        Returns:
            [function(array[0]), function(array[1]), ...]
    """
    #We run the first few iterations serially to catch bugs
    #If we set n_jobs to 1, just run a list comprehension. This is useful for benchmarking and debugging.
    if n_jobs==1:
        return [function(**a) if use_kwargs else function(a) for a in tqdm(array[:])]
    #Assemble the workers
    with ProcessPoolExecutor(max_workers=n_jobs) as pool:
        #Pass the elements of array into function
        if use_kwargs:
            futures = [pool.submit(function, **a) for a in array[:]]
        else:
            futures = [pool.submit(function, a) for a in array[:]]
        kwargs = {
            'total': len(futures),
            'unit': 'it',
            'unit_scale': True,
            'leave': True
        }
        #Print out the progress as tasks complete
        for f in tqdm(as_completed(futures), **kwargs):
            pass
    out = []
    #Get the results from the futures. 
    for i, future in tqdm(enumerate(futures)):
        try:
            out.append(future.result())
        except Exception as e:
            out.append(e)
    return out   

def get_dataLis(date,atr):
    
    nn = len(date)
    dataList  = []
    if atr['FILE_TYPE'] == 'timeseries':
        for i in range(nn):
            d0 = 'timeseries_' + date[i].astype('U13')
            dataList.append(d0)
    elif atr['FILE_TYPE'] == 'ifgramStack':
        for i in range(nn):
            d0 = 'unwrapPhase_' + date[i,0].astype('U13') + '-' + date[i,1].astype('U13')
            dataList.append(d0)
        
    return dataList    

def cmdLineParse():
    parser = argparse.ArgumentParser(description='Interpolate high-resolution tropospheric product map.',\
                                     formatter_class=argparse.RawTextHelpFormatter,\
                                     epilog=INTRODUCTION+'\n'+EXAMPLE)

    parser.add_argument('fname', help='file name of the to be corrected file. e.g., velocity.h5, geo_velocity.h5, timeseries.h5')
    #parser.add_argument('variogramTs', help='time series of variogram file. e.g., variogramTs.h5')
    parser.add_argument('stableArea', help='mask file for stable area. e.g., mask_deform.h5')
    #parser.add_argument('--geo_file', dest='geo_file', metavar='FILE',help='name of the prefix of the output file')
    parser.add_argument('refNumb', help='number of reference pixels. e.g., 200')
    parser.add_argument('--stable-ref', dest='stable_ref', type=str, help='stable are for selecting reference points.[default: smae as stableArea]')
    parser.add_argument('--geo-file', dest='geo_file', type=str, help='geo file to provide latitude and longitutde info.')
    parser.add_argument('--ref-date', dest='ref_date', type=str, help='reference date used for time-series file.')
    parser.add_argument('--dsname','-d', dest='dsname', help='name of the dataset. e.g., unwrapPhase_20141010-20141022 timeseries-20161010')
    parser.add_argument('--step', dest='step',type=float, default = 1000.0, help='step length.')
    parser.add_argument('--max-length', dest='max_length', type=float, default = 20000, help='maximum length used for variogram modeling.[default: 2/3 of the maximum lag')
    parser.add_argument('--variogram-model', dest='variogram_model',type=str,default='spherical', help='variogram model.')   
    parser.add_argument('--removeRamp', dest='removeRamp', action='store_true', help='Removing ramp for interferograms.')
    parser.add_argument('-o','--out', dest='out_file', metavar='FILE',help='name of the prefix of the output file')
    parser.add_argument('--parallel', dest='parallelNumb', type=int, default=1, help='Enable parallel processing and Specify the number of processors.')
    parser.add_argument('--kriging-points-numb', dest='kriging_points_numb', type=int, default=15, help='Number of the closest points used for Kriging interpolation. [default: 15]')
       
    inps = parser.parse_args()

    return inps


INTRODUCTION = '''
##################################################################################
   Copy Right(c): 2021, Yunmeng Cao   @MPInSAR v1.0
   
   Reconstructing the ground displacements using MPInSAR algorithom.
'''

EXAMPLE = """Example:
  
  mpinsar.py velocity.h5 mask_deform.h5 200 --geo-file geometryRadar.h5 ---kriging-points-numb 20
  mpinsar.py timeseries.h5 mask_deform.h5 200 --geo-file geometryRadar.h5 --max-length 40 --parallel 8
  mpinsar.py ifgramStack.h5 mask_deform.h5 100 --geo-file geometryRadar.h5 --kriging-points-numb 20 --parallel 8
  mpinsar.py ifgramStack.h5 mask_deform.h5 200 --geo-file geometryRadar.h5 -d unwrapPhase_20180405-20180417 --parallel 8
  mpinsar.py geo_velocity.h5 geo_mask_deform.h5 200 --stable-ref mask_referece.h5 --max-length 40 --parallel 8
  
###################################################################################
"""

###############################################################

def main(argv):
    
    inps = cmdLineParse()
    fname = inps.fname
    dataNames = get_dataNames(fname)
     
    mask_file = inps.stableArea
    mask = read_hdf5(mask_file, datasetName='mask', box=None)[0]
    
    step = inps.step
    max_length = inps.max_length
    model = inps.variogram_model
    parallel_numb = inps.parallelNumb
    refNumb = int(inps.refNumb)
    
    atr = read_attr(fname)
    
    file_type = atr['FILE_TYPE']
    ts_files  = ['ifgramStack','timeseries']
    
    if inps.stable_ref:
        stable_ref_file = inps.stable_ref
    else:
        stable_ref_file = mask_file
    mask_ref = read_hdf5(stable_ref_file, datasetName='mask', box=None)[0]
    
    
    if file_type in ts_files:         
        if file_type =='timeseries':
            data, atr = read_hdf5(fname,datasetName='timeseries')
        else:
            data, atr = read_hdf5(fname,datasetName='unwrapPhase')
            
        date, atr = read_hdf5(fname,datasetName='date')
        dataList = get_dataLis(date,atr)
        
    if inps.dsname: 
        if file_type =='timeseries': 
            idx = dataList.index(inps.dsname)
            if inps.ref_date:
                idx_ref = dataList.index('timeseries_' + inps.ref_date)
            else:   
                idx_ref = 0
            data_calc = data[idx,:,:] - data[idx_ref,:,:]
        elif file_type =='ifgramStack':
            idx = dataList.index(inps.dsname)
            data_calc = data[idx,:,:]
        else:
            data_calc = read_hdf5(fname, datasetName=inps.dsname, box=None)[0]
        dest = inps.dsname
    else:
        if file_type in ts_files:
            data_calc = data
            if file_type =='timeseries':
                dest = 'timeseries'
            else:
                dest = 'unwrapPhase'
        else:
            datasetName = dataNames[0]
            dest = datasetName
            data_calc = read_hdf5(fname, datasetName=datasetName, box=None)[0]
    
    if inps.geo_file:
        lats = read_hdf5(inps.geo_file, datasetName='latitude', box=None)[0]
        lons = read_hdf5(inps.geo_file, datasetName='longitude', box=None)[0]
    else:
        lats,lons = get_lat_lon(atr, box = None)
    lats[np.isnan(lats)] = 0
    lons[np.isnan(lons)] = 0
    lat1 = lats[mask==1]; lon1 = lons[mask==1]
    
    lat1_ref = lats[mask_ref==1]; lon1_ref = lons[mask_ref==1]
    #print(len(lat1_ref))
    dist_matrix = np.zeros((int(refNumb),int(refNumb))) 
    while(matrix_rank(dist_matrix)<int(refNumb)):
        idx_sample, lat_sample, lon_sample = variogram.sample_data(lat1_ref, lon1_ref, mask=None, num_sample=int(refNumb))
        dist_matrix = variogram.get_distance_matrix(lat_sample, lon_sample)

    if len(data_calc.shape) == 2:
        Row,Col = data_calc.shape
        k0 = 0
        nn = 1
        if file_type in ts_files:
            OUT = inps.dsname + '_mpinsar.h5'
        else:
            OUT = fname.split('.h5')[0] + '_mpinsar.h5'        
    else:
        k0 = 1
        nn = data_calc.shape[0]
        Row,Col = data_calc.shape[1:3]
        OUT = fname.split('.h5')[0] + '_mpinsar.h5'
    
    data_cor = np.zeros((data_calc.shape),dtype='float32')
    data_aps = np.zeros((data_calc.shape),dtype='float32')
    data_std = np.zeros((data_calc.shape),dtype='float32')
    
    if k0==0:
        data1 = data_calc[mask==1]
        data1[np.isnan(data1)] = 0
        vari_para, corr= variogram.variance_modeling(data1, lat1, lon1, 3000, step, max_length, model, weight=True)
        data_sample = data1[idx_sample]
        print(vari_para)
        print(corr)
        
        OK = OrdinaryKriging(lon_sample, lat_sample, data_sample, variogram_model=model, verbose=False,enable_plotting=False)
        para = vari_para
        para[1] = para[1]/1000/6371/np.pi*180; para[2] = 0
        OK.variogram_model_parameters = para
        
        print('Start to solve MPInSAR: ' + dest)
        idx_list, para_data = generate_para_data(lats.flatten(), lons.flatten(), OK, inps.kriging_points_numb, 100)
        data_cor, data_std, data_aps = solve_mpinsar(data_calc, OK_function, idx_list, para_data, parallel_numb)
    else:
        if file_type =='timeseries':
            start = 1
        else:
            start = 0
        #print(data_calc.shape)
        #print(data_calc[3,:,:])
        for i in range(start, nn):
            
            print('Start to solve MPInSAR: ' + dataList[i] + ' ' + str(i+1) + '/' + str(nn) )
            data1 = data_calc[i,:,:]
            data1 = data1[mask==1]
            data1[np.isnan(data1)] = 0
            vari_para, corr = variogram.variance_modeling(data1, lat1, lon1, 3000, step, max_length, model, weight=True)

            data_sample = data1[idx_sample]
            
            OK = OrdinaryKriging(lon_sample, lat_sample, data_sample, variogram_model=model, verbose=False,enable_plotting=False)
            para = vari_para
            para[1] = para[1]/1000/6371/np.pi*180
            OK.variogram_model_parameters = para
            
            idx_list, para_data = generate_para_data(lats.flatten(), lons.flatten(), OK, inps.kriging_points_numb, 100)
            data_cor0, data_std0, data_aps0 = solve_mpinsar(data_calc[i,:,:], OK_function, idx_list, para_data, parallel_numb)
            data_cor[i,:,:] = data_cor0
            data_std[i,:,:] = data_std0
            data_aps[i,:,:] = data_aps0
        
    ####### Write/save data ###########
    
    dsDict = dict()
    if file_type in ts_files:  
        if k0==0:         
            dsDict['displacements'] = data_cor
            dsDict['std'] = data_std
            dsDict['aps'] = data_aps
            atr['FILE_TYPE'] = 'mpinsar'
            write_h5(dsDict, out_file = OUT, metadata=atr, ref_file=None, compression=None)
        else:
            for datasetName in dataNames:
                dsDict[datasetName] = read_hdf5(fname, datasetName = datasetName)[0]
            dsDict[dest] = data_cor
            dsDict['std'] = data_std
            dsDict['aps'] = data_aps
            write_h5(dsDict, out_file = OUT, metadata=atr, ref_file=None, compression=None)
    else:
        for datasetName in dataNames:
            dsDict[datasetName] = read_hdf5(fname, datasetName = datasetName)[0]
        dsDict[dest] = data_cor
        dsDict['std'] = data_std
        dsDict['aps'] = data_aps
        write_h5(dsDict, out_file = OUT, metadata=atr, ref_file=None, compression=None)
            
    sys.exit(1)
###############################################################

if __name__ == '__main__':
    main(sys.argv[:])
