#! /usr/bin/env python
#################################################################
###  This program is part of PyINT  v2.0                      ### 
###  Copy Right (c): 2019, Yunmeng Cao                        ###  
###  Author: Yunmeng Cao                                      ###                            
###  Email : ymcmrs@gmail.com                                 ###
###  Univ. : King Abdullah University of Science & Technology ###
###  Now at GNS Science, New Zealand                          ###
#################################################################
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

from pysme import variance
###### mintPy modelu ###############################
from mintpy.objects import (geometryDatasetNames,
                            geometry,
                            ifgramDatasetNames,
                            ifgramStack,
                            timeseriesKeyNames,
                            timeseries)
from mintpy.objects.gps import GPS
from mintpy.utils import (ptime,
                          readfile,
                          utils as ut,
                          plot as pp)
from mintpy.multilook import multilook_data
from mintpy import subset, version

#import matlab.engine
#######################################################
###############################################################

model_dict = {'linear': elevation_models.linear_elevation_model,
                      'onn': elevation_models.onn_elevation_model,
                      'onn_linear': elevation_models.onn_linear_elevation_model,
                      'exp': elevation_models.exp_elevation_model,
                      'exp_linear': elevation_models.exp_linear_elevation_model}



variogram_dict = {'linear': variogram_models.linear_variogram_model,
                      'power': variogram_models.power_variogram_model,
                      'gaussian': variogram_models.gaussian_variogram_model,
                      'spherical': variogram_models.spherical_variogram_model,
                      'exponential': variogram_models.exponential_variogram_model,
                      'hole-effect': variogram_models.hole_effect_variogram_model}


def function_trend(lat,lon,para):
    # mod = a*x + b*y + c*x*y
    lat = lat/180*np.pi
    lon = lon/180*np.pi  
    lon = lon*np.cos(lat) # to get isometrics coordinates
    
    a0,b0,c0,d0 = para
    data_trend = a0 + b0*lat + c0*lon +d0*lat*lon
    
    return data_trend

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

def adjust_aps_lat_lon_unavco(gps_aps_h5,epoch = 0):
    
    FILE = gps_aps_h5
    
    gps_hei = read_hdf5(FILE,datasetName='gps_height')[0]
    gps_lat = read_hdf5(FILE,datasetName='gps_lat')[0]
    gps_lon = read_hdf5(FILE,datasetName='gps_lon')[0]
    gps_nm = read_hdf5(FILE,datasetName='gps_name')[0]
    gps_nm = list(gps_nm)

    date = read_hdf5(FILE,datasetName='date')[0]
    station = read_hdf5(FILE,datasetName='station')[0]
    wzd = read_hdf5(FILE,datasetName='wzd_turb')[0]
    tzd = read_hdf5(FILE,datasetName='tzd_turb')[0]
    
    station= list(station[epoch])
    wzd= list(wzd[epoch])
    tzd= list(tzd[epoch])
    
    k0 =9999
    for i in range(len(station)):
        if station[i].decode("utf-8")=='0.0':
            if i < k0:
                k0 =i
    station = station[0:k0]
    wzd = wzd[0:k0]     
    tzd = tzd[0:k0]
    NN = len(station)
    
    hei = np.zeros((NN,))
    lat = np.zeros((NN,))
    lon = np.zeros((NN,))
    for i in range(NN):
        hei[i] = gps_hei[gps_nm.index(station[i])]
        lat[i] = gps_lat[gps_nm.index(station[i])]
        lon[i] = gps_lon[gps_nm.index(station[i])]
    tzd_turb = tzd
    wzd_turb = wzd
    
    return tzd_turb, wzd_turb, lat, lon

def adjust_aps_lat_lon_unr(gps_aps_h5,epoch = 0):
    
    FILE = gps_aps_h5
    
    gps_hei = read_hdf5(FILE,datasetName='gps_height')[0]
    gps_lat = read_hdf5(FILE,datasetName='gps_lat')[0]
    gps_lon = read_hdf5(FILE,datasetName='gps_lon')[0]
    gps_nm = read_hdf5(FILE,datasetName='gps_name')[0]
    gps_nm = list(gps_nm)

    date = read_hdf5(FILE,datasetName='date')[0]
    station = read_hdf5(FILE,datasetName='station')[0]
    tzd = read_hdf5(FILE,datasetName='tzd_turb')[0]
    
    station= list(station[epoch])
    tzd= list(tzd[epoch])
    
    k0 =9999
    for i in range(len(station)):
        if station[i].decode("utf-8")=='0.0':
            if i < k0:
                k0 =i
    station = station[0:k0]   
    tzd = tzd[0:k0]
    NN = len(station)
    
    hei = np.zeros((NN,))
    lat = np.zeros((NN,))
    lon = np.zeros((NN,))
    for i in range(NN):
        hei[i] = gps_hei[gps_nm.index(station[i])]
        lat[i] = gps_lat[gps_nm.index(station[i])]
        lon[i] = gps_lon[gps_nm.index(station[i])]
    tzd_turb = tzd
    
    return tzd_turb, lat, lon

def get_bounding_box(meta):
    """Get lat/lon range (roughly), in the same order of data file
    lat0/lon0 - starting latitude/longitude (first row/column)
    lat1/lon1 - ending latitude/longitude (last row/column)
    """
    length, width = int(meta['LENGTH']), int(meta['WIDTH'])
    if 'Y_FIRST' in meta.keys():
        # geo coordinates
        lat0 = float(meta['Y_FIRST'])
        lon0 = float(meta['X_FIRST'])
        lat_step = float(meta['Y_STEP'])
        lon_step = float(meta['X_STEP'])
        lat1 = lat0 + lat_step * (length - 1)
        lon1 = lon0 + lon_step * (width - 1)
    else:
        # radar coordinates
        lats = [float(meta['LAT_REF{}'.format(i)]) for i in [1,2,3,4]]
        lons = [float(meta['LON_REF{}'.format(i)]) for i in [1,2,3,4]]
        lat0 = np.mean(lats[0:2])
        lat1 = np.mean(lats[2:4])
        lon0 = np.mean(lons[0:3:2])
        lon1 = np.mean(lons[1:4:2])
    return lat0, lat1, lon0, lon1


#def get_lat_lon(meta):
#    """Get 2D array of lat and lon from metadata"""
#    length, width = int(meta['LENGTH']), int(meta['WIDTH'])
#    lat0, lat1, lon0, lon1 = get_bounding_box(meta)
#    lat, lon = np.mgrid[lat0:lat1:length*1j, lon0:lon1:width*1j]
#    return lat, lon


#def correct_timeseries(timeseries_file, trop_file, out_file):
#    print('\n------------------------------------------------------------------------------')
#    print('correcting delay for input time-series by calling diff.py')
#    cmd = 'diff.py {} {} -o {} --force'.format(timeseries_file,
#                                               trop_file,
#                                               out_file)
#    print(cmd)
#    status = subprocess.Popen(cmd, shell=True).wait()
#    if status is not 0:
#        raise Exception(('Error while correcting timeseries file '
#                         'using diff.py with tropospheric delay file.'))
#    return out_file


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

def latlon2dis(lat1,lon1,lat2,lon2,R=6371):
    
    lat1 = np.array(lat1)*np.pi/180.0
    lat2 = np.array(lat2)*np.pi/180.0
    dlon = (lon1-lon2)*np.pi/180.0

    # Evaluate trigonometric functions that need to be evaluated more
    # than once:
    c1 = np.cos(lat1)
    s1 = np.sin(lat1)
    c2 = np.cos(lat2)
    s2 = np.sin(lat2)
    cd = np.cos(dlon)

    # This uses the arctan version of the great-circle distance function
    # from en.wikipedia.org/wiki/Great-circle_distance for increased
    # numerical stability.
    # Formula can be obtained from [2] combining eqns. (14)-(16)
    # for spherical geometry (f=0).

    dist =  R*np.arctan2(np.sqrt((c2*np.sin(dlon))**2 + (c1*s2-s1*c2*cd)**2), s1*s2+c1*c2*cd)

    return dist

    
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
    
def cmdLineParse():
    parser = argparse.ArgumentParser(description='Interpolate high-resolution tropospheric product map.',\
                                     formatter_class=argparse.RawTextHelpFormatter,\
                                     epilog=INTRODUCTION+'\n'+EXAMPLE)

    parser.add_argument('ifgramFile', help='interferogram file. e.g., ifgramStack.h5')
    parser.add_argument('variogramTs', help='time series of variogram file. e.g., variogramTs.h5')
    parser.add_argument('stableArea', help='mask file for stable area. e.g., mask_deform.h5')
    parser.add_argument('--geo_file', dest='geo_file', metavar='FILE',help='name of the prefix of the output file')
    parser.add_argument('refNumb', help='number of reference pixels. e.g., 200')
    parser.add_argument('--max-length', dest='max_length',type=float, metavar='NUM',default=50.0,help='used bin ratio for mdeling the structure model.[default: 50km]')
    parser.add_argument('--removeRamp', dest='removeRamp', action='store_true', help='Removing ramp for interferograms.')
    parser.add_argument('-o','--out', dest='out_file', metavar='FILE',help='name of the prefix of the output file')
    parser.add_argument('--parallel', dest='parallelNumb', type=int, default=1, help='Enable parallel processing and Specify the number of processors.')
    parser.add_argument('--kriging-points-numb', dest='kriging_points_numb', type=int, default=15, help='Number of the closest points used for Kriging interpolation. [default: 15]')
       
    inps = parser.parse_args()

    return inps


INTRODUCTION = '''
##################################################################################
   Copy Right(c): 2019, Yunmeng Cao   @GigPy v1.0
   
   Reconstructing the ground displacements using MPInSAR algorithom.
'''

EXAMPLE = """Example:
  
  mpinsar_ifgram.py reconUnwrapIfgram.h5 variogramTs.h5 mask_deform.h5 200 --max-length 40
  mpinsar_ifgram.py ifgramStack.h5 variogramTs.h5 mask_deform.h5 200 --removeRamp 
  mpinsar_ifgram.py ifgramStack.h5 variogramTs.h5 mask_deform.h5 200 --parallel 8 --max-length 50
  mpinsar_ifgram.py ifgramStack.h5 variogramTs.h5 mask_deform.h5 200 --kriging-points-numb 20
  mpinsar_ifgram.py ifgramStack.h5 variogramTs.h5 mask_deform.h5 200 --removeRamp --parallel 8
  
###################################################################################
"""

###############################################################

def main(argv):
    
    inps = cmdLineParse() 
    ifgram_file = inps.ifgramFile
    vari_file = inps.variogramTs
    mask_file = inps.stableArea
    refNumb = int(inps.refNumb)
   
    max_lag = inps.max_length
    
    r0 = np.asarray(1/2*max_lag)
    range0 = r0.tolist()
    
    if inps.out_file: Out = inps.out_file
    else: Out = 'ifgramStack_mpinsar.h5'
    
    date12_list,atr = read_hdf5(ifgram_file,datasetName='date')
    m_list = date12_list[:,0]
    s_list = date12_list[:,1]
    m_list = m_list.astype('U13')
    s_list = s_list.astype('U13')
    m_list = list(m_list)
    s_list = list(s_list)
    
    date_list = read_hdf5(vari_file,datasetName='date_list')[0]
    date_list = date_list.astype('U13')
    date_list = list(date_list)

    
    variTs_data = read_hdf5(vari_file,datasetName='/semivarianceTs_weight')[0]
    paraTs_data = read_hdf5(vari_file,datasetName='/model_parameters')[0]
    
    lag = read_hdf5(vari_file,datasetName='/Lags')[0]
    
    #lat_data,lon_data = get_lat_lon(atr)

    if inps.geo_file:
        geo_file = inps.geo_file
        lat_data = read_hdf5(geo_file,datasetName='latitude')[0]
        lon_data = read_hdf5(geo_file,datasetName='longitude')[0]
    Row,Col = lat_data.shape

    lats = lat_data.flatten()
    lons = lon_data.flatten()
    
    where_are_NaNs = np.isnan(lats)
    lats[where_are_NaNs] = 0

    where_are_NaNs = np.isnan(lons)
    lons[where_are_NaNs] = 0
    
    ifgram_data = read_hdf5(ifgram_file,datasetName='unwrapPhase')[0]
    #coh_data = read_hdf5(ifgram_file,datasetName='coherence')[0]
    mask_data = read_hdf5(mask_file,datasetName='mask')[0]
    
    LL0 = lag[lag < max_lag]
    N_ifg = len(date12_list)
    
    def resi_func(m,d,y):
        variogram_function =variogram_dict['spherical'] 
        return  y - variogram_function(m,d)
    
    vari_func = variogram_dict['spherical']
    
    ifgramCor = np.zeros((N_ifg,Row,Col))
    ifgramVar = np.zeros((N_ifg,Row,Col))
    ifgramAps = np.zeros((N_ifg,Row,Col))
    SampleIdx = np.zeros((N_ifg,refNumb))
    
    #eng = matlab.engine.start_matlab()
    for i in range(N_ifg):
    #for i in range(1):
     
        ifgram_data0 = ifgram_data[i,:,:]
        ifgram_data0 = ifgram_data0.flatten()
        #coh_data0 = coh_data[i,:,:]
        
        dist_matrix = np.zeros((int(refNumb),int(refNumb))) 
        while(matrix_rank(dist_matrix)<int(refNumb)):
            idx_sample, lat_sample, lon_sample = variance.sample_data(lat_data.flatten(), lon_data.flatten(), mask_data, num_sample=int(refNumb))
            dist_matrix = variance.get_distance_matrix(lat_sample, lon_sample)
            #print(matrix_rank(dist_matrix))
    
        idm = date_list.index(m_list[i])
        ids = date_list.index(s_list[i])
         
        #S0 = variTs_data[idm,:] + variTs_data[ids,:]
        #SS0 = S0[lag < max_lag]
        #sill0 = max(SS0)
        #sill0 = sill0.tolist()

        
        #LLm = matlab.double(LL0.tolist())
        #SSm = matlab.double(SS0.tolist())
 
        #tt = eng.variogramfit(LLm,SSm,range0,sill0,[],'nugget',0.00001,'model','spherical')
        #tt = np.asarray(tt)
        #tt = tt.flatten()
        #print(tt)
            
        #sill0 = max(SS0)
        #sill0 = sill0.tolist()
            
        #p0 = [sill0, range0, 0.0001]   
        #SS01 = SS0.copy()
        #LL01 = LL0.copy()
        #tt, _ = leastsq(resi_func,p0,args = (LL01,SS01))   
        #corr, _ = pearsonr(SS01, vari_func(tt,LL01))
        #if tt[2] < 0:
        #    tt[2] =0
            
        tt = paraTs_data[i,:]; tt = tt[0:3]       
        OK = OrdinaryKriging(lons[idx_sample], lats[idx_sample], ifgram_data0[idx_sample], variogram_model='spherical', verbose=False,enable_plotting=False)
        para = tt
        para[1] = para[1]/6371/np.pi*180
        #print(para)
        OK.variogram_model_parameters = para
        
        
        Numb = inps.parallelNumb
        zz = np.zeros((len(lats),))
        zz_sigma = np.zeros((len(lats),))
        #print(len(lats))
        n_jobs = inps.parallelNumb
    
        # split dataset into multiple subdata
        split_numb = 1000
        idx_list = split_lat_lon_kriging(len(lats),processors = split_numb)
        #print(idx_list[split_numb-1])
    
        print('------------------------------------------------------------------------------')
        print('Start to correct tropospheric turbulence for interferometric pair:  ' + m_list[i] + '-' + s_list[i] + ' (' + str(int(i+1)) + '/' + str(N_ifg) + ')')
        
        np0 = inps.kriging_points_numb
        data = []
        for k in range(split_numb):
            data0 = (OK,lats[idx_list[k]],lons[idx_list[k]],np0)
            data.append(data0)
        future = parallel_process(data, OK_function, n_jobs=Numb, use_kwargs=False)
        for j in range(split_numb):
            id0 = idx_list[j]
            gg = future[j]       
            zz[id0] = gg[0]
            zz_sigma[id0] = gg[1]
        
        sigma0 = zz_sigma.reshape(Row,Col)
        aps0 = zz.reshape(Row,Col)
        ifgram0 = ifgram_data0.reshape(Row,Col) - aps0
        
        ifgramCor[i,:,:] = ifgram0
        ifgramVar[i,:,:] = sigma0
        ifgramAps[i,:,:] = aps0
        SampleIdx[i,:] = idx_sample
    
    dsDict = {}
    dsDict['unwrapPhase'] = ifgramCor
    dsDict['unwrapPhaseVari'] = ifgramVar
    dsDict['unwrapPhaseAps'] = ifgramAps
    dsDict['refRample'] = SampleIdx
    dsDict['mask'] = mask_data
    
    dropIfgram = read_hdf5(ifgram_file,datasetName='dropIfgram')[0]
    bperp = read_hdf5(ifgram_file,datasetName='bperp')[0]
    
    dsDict['dropIfgram'] = dropIfgram
    dsDict['date'] = date12_list
    dsDict['bperp'] = bperp
    write_h5(dsDict, out_file = Out, metadata=atr, ref_file=None, compression=None)
    


    
    sys.exit(1)
###############################################################

if __name__ == '__main__':
    main(sys.argv[:])
