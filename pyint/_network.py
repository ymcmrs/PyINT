############################################################
# Program is part of PyINT                                 #
# Copyright 2019 Yunmeng Cao                               #
# Contact: ymcmrs@gmail.com                                #
############################################################
# This program is modified from MintPy/select_network.py
# Copyright: 2017-2019, Yunjun Zhang
# Contact: yzhang@rsmas.miami.edu 

import os
import sys
import itertools
import h5py
import numpy as np
from scipy import sparse
from matplotlib import (colors,
                        dates as mdates,
                        pyplot as plt)
from matplotlib.tri import Triangulation
from mpl_toolkits.axes_grid1 import make_axes_locatable




##################################################################
def read_pairs_list(date12ListFile, dateList=[]):
    """Read Pairs List file like below:
    070311-070426
    070311-070611
    ...
    """
    # Read date12 list file
    date12List = sorted(list(np.loadtxt(date12ListFile, dtype=bytes).astype(str)))

    # Get dateList from date12List
    if not dateList:
        dateList = []
        for date12 in date12List:
            dates = date12.split('-')
            if not dates[0] in dateList:
                dateList.append(dates[0])
            if not dates[1] in dateList:
                dateList.append(dates[1])
        dateList.sort()
    date6List = yymmdd(dateList)

    # Get pair index
    pairs_idx = []
    for date12 in date12List:
        dates = date12.split('-')
        pair_idx = [date6List.index(dates[0]), date6List.index(dates[1])]
        pairs_idx.append(pair_idx)

    return pairs_idx

def get_date12_list(fname, dropIfgram=False):
    """Read Date12 info from input file: Pairs.list or multi-group hdf5 file
    Inputs:
        fname       - string, path/name of input multi-group hdf5 file or text file
        dropIfgram  - bool, check the "DROP_IFGRAM" attribute or not for multi-group hdf5 file
    Output:
        date12_list - list of string in YYMMDD-YYMMDD format
    Example:
        date12List = get_date12_list('ifgramStack.h5')
        date12List = get_date12_list('ifgramStack.h5', dropIfgram=True)
        date12List = get_date12_list('Pairs.list')
    """
    date12_list = []
    ext = os.path.splitext(fname)[1].lower()
    if ext == '.h5':
        k = readfile.read_attribute(fname)['FILE_TYPE']
        if k == 'ifgramStack':
            date12_list = ifgramStack(fname).get_date12_list(dropIfgram=dropIfgram)
        else:
            return None
    else:
        txtContent = np.loadtxt(fname, dtype=bytes).astype(str)
        if len(txtContent.shape) == 1:
            txtContent = txtContent.reshape(-1, 1)
        date12_list = [i for i in txtContent[:, 0]]
    date12_list = sorted(date12_list)
    return date12_list


def igram_perp_baseline_list(fname):
    """Get perpendicular baseline list from input multi_group hdf5 file"""
    print(('read perp baseline info from '+fname))
    k = readfile.read_attribute(fname)['FILE_TYPE']
    h5 = h5py.File(fname, 'r')
    epochList = sorted(h5[k].keys())
    p_baseline_list = []
    for epoch in epochList:
        p_baseline = (float(h5[k][epoch].attrs['P_BASELINE_BOTTOM_HDR']) +
                      float(h5[k][epoch].attrs['P_BASELINE_TOP_HDR']))/2
        p_baseline_list.append(p_baseline)
    h5.close()
    return p_baseline_list


def select_pairs_sbas(date_list, date12_format='YYMMDD-YYMMDD'):
    """Select All Possible Pairs/Interferograms
    Input : date_list   - list of date in YYMMDD/YYYYMMDD format
    Output: date12_list - list date12 in YYMMDD-YYMMDD format
    Reference:
        Berardino, P., G. Fornaro, R. Lanari, and E. Sansosti (2002), A new algorithm for surface deformation monitoring
        based on small baseline differential SAR interferograms, IEEE TGRS, 40(11), 2375-2383.
    """
    date8_list = sorted(yyyymmdd(date_list))
    date6_list = yymmdd(date8_list)
    date12_list = list(itertools.combinations(date6_list, 2))
    date12_list = [date12[0]+'-'+date12[1] for date12 in date12_list]
    if date12_format == 'YYYYMMDD_YYYYMMDD':
        date12_list = yyyymmdd_date12(date12_list)
    return date12_list


def select_pairs_sequential(date_list, num_connection=2, date12_format='YYMMDD-YYMMDD'):
    """Select Pairs in a Sequential way:
        For each acquisition, find its num_connection nearest acquisitions in the past time.
    Inputs:
        date_list  : list of date in YYMMDD/YYYYMMDD format
    Reference:
        Fattahi, H., and F. Amelung (2013), DEM Error Correction in InSAR Time Series, IEEE TGRS, 51(7), 4249-4259.
    """
    date8_list = sorted(yyyymmdd(date_list))
    date6_list = yymmdd(date8_list)
    date_idx_list = list(range(len(date6_list)))

    # Get pairs index list
    date12_idx_list = []
    for date_idx in date_idx_list:
        for i in range(num_connection):
            if date_idx-i-1 >= 0:
                date12_idx_list.append([date_idx-i-1, date_idx])
    date12_idx_list = [sorted(idx) for idx in sorted(date12_idx_list)]

    # Convert index into date12
    date12_list = [date6_list[idx[0]]+'-'+date6_list[idx[1]]
                   for idx in date12_idx_list]
    if date12_format == 'YYYYMMDD_YYYYMMDD':
        date12_list = yyyymmdd_date12(date12_list)
    return date12_list


def select_pairs_hierarchical(date_list, pbase_list, temp_perp_list, date12_format='YYMMDD-YYMMDD'):
    """Select Pairs in a hierarchical way using list of temporal and perpendicular baseline thresholds
        For each temporal/perpendicular combination, select all possible pairs; and then merge all combination results
        together for the final output (Zhao, 2015).
    Inputs:
        date_list  : list of date in YYMMDD/YYYYMMDD format
        pbase_list : list of float, perpendicular spatial baseline
        temp_perp_list : list of list of 2 floats, for list of temporal/perp baseline, e.g.
                         [[32.0, 800.0], [48.0, 600.0], [64.0, 200.0]]
    Examples:
        pairs = select_pairs_hierarchical(date_list, pbase_list, [[32.0, 800.0], [48.0, 600.0], [64.0, 200.0]])
    Reference:
        Zhao, W., (2015), Small deformation detected from InSAR time-series and their applications in geophysics, Doctoral
        dissertation, Univ. of Miami, Section 6.3.
    """
    # Get all date12
    date12_list_all = select_pairs_all(date_list)

    # Loop of Threshold
    print('List of temporal and perpendicular spatial baseline thresholds:')
    print(temp_perp_list)
    date12_list = []
    for temp_perp in temp_perp_list:
        tbase_max = temp_perp[0]
        pbase_max = temp_perp[1]
        date12_list_tmp = threshold_temporal_baseline(date12_list_all,
                                                      tbase_max,
                                                      keep_seasonal=False)
        date12_list_tmp = threshold_perp_baseline(date12_list_tmp,
                                                  date_list,
                                                  pbase_list,
                                                  pbase_max)
        date12_list += date12_list_tmp
    date12_list = sorted(list(set(date12_list)))
    if date12_format == 'YYYYMMDD_YYYYMMDD':
        date12_list = yyyymmdd_date12(date12_list)
    return date12_list


def select_pairs_delaunay(date_list, tbase_list, pbase_list, norm=True, date12_format='YYMMDD-YYMMDD'):
    """Select Pairs using Delaunay Triangulation based on temporal/perpendicular baselines
    Inputs:
        date_list  : list of date in YYMMDD/YYYYMMDD format
        pbase_list : list of float, perpendicular spatial baseline
        norm       : normalize temporal baseline to perpendicular baseline
    Key points
        1. Define a ratio between perpendicular and temporal baseline axis units (Pepe and Lanari, 2006, TGRS).
        2. Pairs with too large perpendicular / temporal baseline or Doppler centroid difference should be removed
           after this, using a threshold, to avoid strong decorrelations (Zebker and Villasenor, 1992, TGRS).
    Reference:
        Pepe, A., and R. Lanari (2006), On the extension of the minimum cost flow algorithm for phase unwrapping
        of multitemporal differential SAR interferograms, IEEE TGRS, 44(9), 2374-2383.
        Zebker, H. A., and J. Villasenor (1992), Decorrelation in interferometric radar echoes, IEEE TGRS, 30(5), 950-959.
    """
    # Get temporal baseline in days
    date6_list = yymmdd(date_list)
    date8_list = yyyymmdd(date_list)
    #tbase_list = date_list2tbase(date8_list)[0]

    # Normalization (Pepe and Lanari, 2006, TGRS)
    if norm:
        temp2perp_scale = (max(pbase_list)-min(pbase_list)) / (max(tbase_list)-min(tbase_list))
        tbase_list = [tbase*temp2perp_scale for tbase in tbase_list]

    # Generate Delaunay Triangulation
    date12_idx_list = Triangulation(tbase_list, pbase_list).edges.tolist()
    date12_idx_list = [sorted(idx) for idx in sorted(date12_idx_list)]

    # Convert index into date12
    date12_list = [date6_list[idx[0]]+'-'+date6_list[idx[1]]
                   for idx in date12_idx_list]
    if date12_format == 'YYYYMMDD_YYYYMMDD':
        date12_list = yyyymmdd_date12(date12_list)
    return date12_list


def select_pairs_mst(date_list, pbase_list, date12_format='YYMMDD-YYMMDD'):
    """Select Pairs using Minimum Spanning Tree technique
        Connection Cost is calculated using the baseline distance in perp and scaled temporal baseline (Pepe and Lanari,
        2006, TGRS) plane.
    Inputs:
        date_list  : list of date in YYMMDD/YYYYMMDD format
        pbase_list : list of float, perpendicular spatial baseline
    References:
        Pepe, A., and R. Lanari (2006), On the extension of the minimum cost flow algorithm for phase unwrapping
        of multitemporal differential SAR interferograms, IEEE TGRS, 44(9), 2374-2383.
        Perissin D., Wang T. (2012), Repeat-pass SAR interferometry with partially coherent targets. IEEE TGRS. 271-280
    """
    # Get temporal baseline in days
    date6_list = yymmdd(date_list)
    date8_list = yyyymmdd(date_list)
    tbase_list = date_list2tbase(date8_list)[0]
    # Normalization (Pepe and Lanari, 2006, TGRS)
    temp2perp_scale = (max(pbase_list)-min(pbase_list)) / (max(tbase_list)-min(tbase_list))
    tbase_list = [tbase*temp2perp_scale for tbase in tbase_list]

    # Get weight matrix
    ttMat1, ttMat2 = np.meshgrid(np.array(tbase_list), np.array(tbase_list))
    ppMat1, ppMat2 = np.meshgrid(np.array(pbase_list), np.array(pbase_list))
    ttMat = np.abs(ttMat1 - ttMat2)  # temporal distance matrix
    ppMat = np.abs(ppMat1 - ppMat2)  # spatial distance matrix

    # 2D distance matrix in temp/perp domain
    weightMat = np.sqrt(np.square(ttMat) + np.square(ppMat))
    weightMat = sparse.csr_matrix(weightMat)  # compress sparse row matrix

    # MST path based on weight matrix
    mstMat = sparse.csgraph.minimum_spanning_tree(weightMat)

    # Convert MST index matrix into date12 list
    [s_idx_list, m_idx_list] = [date_idx_array.tolist()
                                for date_idx_array in sparse.find(mstMat)[0:2]]
    date12_list = []
    for i in range(len(m_idx_list)):
        idx = sorted([m_idx_list[i], s_idx_list[i]])
        date12 = date6_list[idx[0]]+'-'+date6_list[idx[1]]
        date12_list.append(date12)
    if date12_format == 'YYYYMMDD_YYYYMMDD':
        date12_list = yyyymmdd_date12(date12_list)
    return date12_list


def select_pairs_star(date_list, m_date=None, pbase_list=[], date12_format='YYMMDD-YYMMDD'):
    """Select Star-like network/interferograms/pairs, it's a single master network, similar to PS approach.
    Usage:
        m_date : master date, choose it based on the following cretiria:
                 1) near the center in temporal and spatial baseline
                 2) prefer winter season than summer season for less temporal decorrelation
    Reference:
        Ferretti, A., C. Prati, and F. Rocca (2001), Permanent scatterers in SAR interferometry, IEEE TGRS, 39(1), 8-20.
    """
    date8_list = sorted(yyyymmdd(date_list))
    date6_list = yymmdd(date8_list)

    # Select master date if not existed
    if not m_date:
        m_date = select_master_date(date8_list, pbase_list)
        print(('auto select master date: '+m_date))

    # Check input master date
    m_date8 = yyyymmdd(m_date)
    if m_date8 not in date8_list:
        print('Input master date is not existed in date list!')
        print(('Input master date: '+str(m_date8)))
        print(('Input date list: '+str(date8_list)))
        m_date8 = None

    # Generate star/ps network
    m_idx = date8_list.index(m_date8)
    date12_idx_list = [sorted([m_idx, s_idx]) for s_idx in range(len(date8_list))
                       if s_idx is not m_idx]
    date12_list = [date6_list[idx[0]]+'-'+date6_list[idx[1]]
                   for idx in date12_idx_list]
    if date12_format == 'YYYYMMDD_YYYYMMDD':
        date12_list = yyyymmdd_date12(date12_list)
    return date12_list


def select_master_date(date_list, pbase_list=[]):
    """Select super master date based on input temporal and/or perpendicular baseline info.
    Return master date in YYYYMMDD format.
    """
    date8_list = yyyymmdd(date_list)
    if not pbase_list:
        # Choose date in the middle
        m_date8 = date8_list[int(len(date8_list)/2)]
    else:
        # Get temporal baseline list
        tbase_list = date_list2tbase(date8_list)[0]
        # Normalization (Pepe and Lanari, 2006, TGRS)
        temp2perp_scale = (max(pbase_list)-min(pbase_list)) / (max(tbase_list)-min(tbase_list))
        tbase_list = [tbase*temp2perp_scale for tbase in tbase_list]
        # Get distance matrix
        ttMat1, ttMat2 = np.meshgrid(np.array(tbase_list),
                                     np.array(tbase_list))
        ppMat1, ppMat2 = np.meshgrid(np.array(pbase_list),
                                     np.array(pbase_list))
        ttMat = np.abs(ttMat1 - ttMat2)  # temporal distance matrix
        ppMat = np.abs(ppMat1 - ppMat2)  # spatial distance matrix
        # 2D distance matrix in temp/perp domain
        disMat = np.sqrt(np.square(ttMat) + np.square(ppMat))

        # Choose date minimize the total distance of temp/perp baseline
        disMean = np.mean(disMat, 0)
        m_idx = np.argmin(disMean)
        m_date8 = date8_list[m_idx]
    return m_date8


def select_master_interferogram(date12_list, date_list, pbase_list, m_date=None):
    """Select reference interferogram based on input temp/perp baseline info
    If master_date is specified, select its closest slave_date, which is newer than master_date;
        otherwise, choose the closest pair among all pairs as master interferogram.
    Example:
        master_date12   = pnet.select_master_ifgram(date12_list, date_list, pbase_list)
        '080211-080326' = pnet.select_master_ifgram(date12_list, date_list, pbase_list, m_date='080211')
    """
    pbase_array = np.array(pbase_list, dtype='float64')
    # Get temporal baseline
    date8_list = yyyymmdd(date_list)
    date6_list = yymmdd(date8_list)
    tbase_array = np.array(date_list2tbase(date8_list)[0], dtype='float64')
    # Normalization (Pepe and Lanari, 2006, TGRS)
    temp2perp_scale = (max(pbase_array)-min(pbase_array)) / (max(tbase_array)-min(tbase_array))
    tbase_array *= temp2perp_scale

    # Calculate sqrt of temp/perp baseline for input pairs
    idx1 = np.array([date6_list.index(date12.split('-')[0]) for date12 in date12_list])
    idx2 = np.array([date6_list.index(date12.split('-')[1]) for date12 in date12_list])
    base_distance = np.sqrt((tbase_array[idx2] - tbase_array[idx1])**2 +
                            (pbase_array[idx2] - pbase_array[idx1])**2)

    # Get master interferogram index
    if not m_date:
        # Choose pair with shortest temp/perp baseline
        m_date12_idx = np.argmin(base_distance)
    else:
        m_date = yymmdd(m_date)
        # Choose pair contains m_date with shortest temp/perp baseline
        m_date12_idx_array = np.array([date12_list.index(date12) for date12 in date12_list
                                       if m_date+'-' in date12])
        min_base_distance = np.min(base_distance[m_date12_idx_array])
        m_date12_idx = np.where(base_distance == min_base_distance)[0][0]

    m_date12 = date12_list[m_date12_idx]
    return m_date12


##########################################################
def datenum2datetime(datenum):
    """Convert Matlab datenum into Python datetime.
    Parameters: datenum : Date in datenum format, i.e. 731763.5
    Returns:    datetime: Date in datetime.datetime format, datetime.datetime(2003, 7, 1, 12, 0)
    """
    return dt.fromordinal(int(datenum)) \
           + timedelta(days=datenum % 1) \
           - timedelta(days=366)


def decimal_year2datetime(years):
    """read date in 2002.40657084 to datetime format
    Parameters: years    : (list of) float or str for years
    Returns:    years_dt : (list of) datetime.datetime objects
    """
    def decimal_year2datetime1(x):
        x = float(x)
        year = np.floor(x).astype(int)
        yday = np.floor((x - year) * 365.25).astype(int) + 1
        x2 = '{:d}-{:d}'.format(year, yday)
        try:
            xt = dt(*time.strptime(x2, "%Y-%j")[0:5])
        except:
            raise ValueError('wrong format: ',x)
        return xt

    if isinstance(years, (float, str)):
        years_dt = decimal_year2datetime1(years)

    elif isinstance(years, list):
        years_dt = []
        for year in years:
            years_dt.append(decimal_year2datetime1(year))

    else:
        raise ValueError('unrecognized input format: {}. Only float/str/list are supported.'.format(type(years)))
    return years_dt


def yyyymmdd2years(dates):
    if isinstance(dates, str):
        d = dt(*time.strptime(dates, "%Y%m%d")[0:5])
        yy = float(d.year)+float(d.timetuple().tm_yday-1)/365.25
    elif isinstance(dates, list):
        yy = []
        for date in dates:
            d = dt(*time.strptime(date, "%Y%m%d")[0:5])
            yy.append(float(d.year)+float(d.timetuple().tm_yday-1)/365.25)
    else:
        raise ValueError('Unrecognized date format. Only string and list supported.')
    return yy


def yymmdd2yyyymmdd(date):
    if date[0] == '9':
        date = '19'+date
    else:
        date = '20'+date
    return date


def yyyymmdd(dates):
    if isinstance(dates, str):
        if len(dates) == 6:
            datesOut = yymmdd2yyyymmdd(dates)
        else:
            datesOut = dates
    elif isinstance(dates, list):
        datesOut = []
        for date in dates:
            if len(date) == 6:
                date = yymmdd2yyyymmdd(date)
            datesOut.append(date)
    else:
        # print 'Un-recognized date input!'
        return None
    return datesOut


def yymmdd(dates):
    if isinstance(dates, str):
        if len(dates) == 8:
            datesOut = dates[2:8]
        else:
            datesOut = dates
    elif isinstance(dates, list):
        datesOut = []
        for date in dates:
            if len(date) == 8:
                date = date[2:8]
            datesOut.append(date)
    else:
        # print 'Un-recognized date input!'
        return None
    return datesOut


def yyyymmdd_date12(date12_list):
    """Convert date12 into YYYYMMDD_YYYYMMDD format"""
    m_dates = yyyymmdd([i.replace('-', '_').split('_')[0] for i in date12_list])
    s_dates = yyyymmdd([i.replace('-', '_').split('_')[1] for i in date12_list])
    date12_list = ['{}-{}'.format(m, s) for m, s in zip(m_dates, s_dates)]
    return date12_list

def yymmdd_date12(date12_list):
    """Convert date12 into YYMMDD-YYMMDD format"""
    m_dates = yymmdd([i.replace('-', '_').split('_')[0] for i in date12_list])
    s_dates = yymmdd([i.replace('-', '_').split('_')[1] for i in date12_list])
    date12_list = ['{}-{}'.format(m, s) for m, s in zip(m_dates, s_dates)]
    return date12_list
