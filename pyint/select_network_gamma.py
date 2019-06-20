#! /usr/bin/env python
#################################################################
###  This program is part of PyINT  v1.0                      ### 
###  Copy Right (c): 2017, Yunmeng Cao                        ###  
###  Author: Yunmeng Cao                                      ###                                                          
###  Email : ymcmrs@gmail.com                                 ###
###  Univ. : King Abdullah University of Science & Technology ###   
#################################################################

import numpy as np
import os
import sys  
import subprocess
import getopt
import time
import glob
import argparse
import matplotlib.pyplot as plt
from datetime import datetime as dt, timedelta

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

def auto_adjust_xaxis_date(ax, datevector, fontsize=12, every_year=1):
    """Adjust X axis
    Input:
        ax : matplotlib figure axes object
        datevector : list of float, date in years
                     i.e. [2007.013698630137, 2007.521917808219, 2007.6463470319634]
    Output:
        ax  - matplotlib figure axes object
        dss - datetime.datetime object, xmin
        dee - datetime.datetime object, xmax
    """
    # convert datetime.datetime format into date in years
    if isinstance(datevector[0], datetime.datetime):
        datevector = [i.year + (i.timetuple().tm_yday-1)/365.25 for i in datevector]

    # Min/Max
    ts = datevector[0]  - 0.2;  ys=int(ts);  ms=int((ts - ys) * 12.0)
    te = datevector[-1] + 0.3;  ye=int(te);  me=int((te - ye) * 12.0)
    if ms > 12:   ys = ys + 1;   ms = 1
    if me > 12:   ye = ye + 1;   me = 1
    if ms < 1:    ys = ys - 1;   ms = 12
    if me < 1:    ye = ye - 1;   me = 12
    dss = datetime.datetime(ys, ms, 1, 0, 0)
    dee = datetime.datetime(ye, me, 1, 0, 0)
    ax.set_xlim(dss, dee)

    # Label/Tick format
    ax.fmt_xdata = mdates.DateFormatter('%Y-%m-%d %H:%M:%S')
    ax.xaxis.set_major_locator(mdates.YearLocator(every_year))
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))
    ax.xaxis.set_minor_locator(mdates.MonthLocator())

    # Label font size
    ax.tick_params(labelsize=fontsize)
    # fig2.autofmt_xdate()     #adjust x overlap by rorating, may enble again
    return ax, dss, dee


def auto_adjust_yaxis(ax, dataList, fontsize=12, ymin=None, ymax=None):
    """Adjust Y axis
    Input:
        ax       : matplot figure axes object
        dataList : list of float, value in y axis
        fontsize : float, font size
        ymin     : float, lower y axis limit
        ymax     : float, upper y axis limit
    Output:
        ax
    """
    # Min/Max
    dataRange = max(dataList) - min(dataList)
    if ymin is None:
        ymin = min(dataList) - 0.1*dataRange
    if ymax is None:
        ymax = max(dataList) + 0.1*dataRange
    ax.set_ylim([ymin, ymax])
    # Tick/Label setting
    #xticklabels = plt.getp(ax, 'xticklabels')
    #yticklabels = plt.getp(ax, 'yticklabels')
    #plt.setp(yticklabels, 'color', 'k', fontsize=fontsize)
    #plt.setp(xticklabels, 'color', 'k', fontsize=fontsize)

    return ax


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

def date_list2tbase(dateList):
    """Get temporal Baseline in days with respect to the 1st date
    Input: dateList - list of string, date in YYYYMMDD or YYMMDD format
    Output:
        tbase    - list of int, temporal baseline in days
        dateDict - dict with key   - string, date in YYYYMMDD format
                             value - int, temporal baseline in days
    """
    dateList = yyyymmdd(dateList)
    dates = [dt(*time.strptime(i, "%Y%m%d")[0:5]) for i in dateList]
    tbase = [(i-dates[0]).days for i in dates]

    # Dictionary: key - date, value - temporal baseline
    dateDict = {}
    for i in range(len(dateList)):
        dateDict[dateList[i]] = tbase[i]
    return tbase, dateDict

def yyyymmdd_date12(m_dates,s_dates):
    """Convert date12 into YYYYMMDD_YYYYMMDD format"""
    #m_dates = yyyymmdd([i.replace('-', '_').split('_')[0] for i in date12_list])
    #s_dates = yyyymmdd([i.replace('-', '_').split('_')[1] for i in date12_list])
    date12_list = ['{}_{}'.format(m, s) for m, s in zip(m_dates, s_dates)]
    return date12_list

def date_list2vector(dateList):
    """Get time in datetime format: datetime.datetime(2006, 5, 26, 0, 0)
    Input: dateList - list of string, date in YYYYMMDD or YYMMDD format
    Outputs:
        dates      - list of datetime.datetime objects, i.e. datetime.datetime(2010, 10, 20, 0, 0)
        datevector - list of float, years, i.e. 2010.8020547945205
    """
    dateList = yyyymmdd(dateList)
    dates = [dt(*time.strptime(i, "%Y%m%d")[0:5]) for i in dateList]
    # date in year - float format
    datevector = [i.year + (i.timetuple().tm_yday - 1)/365.25 for i in dates]
    datevector2 = [round(i, 2) for i in datevector]
    return dates, datevector

def is_number(s):
    try:
        int(s)
        return True
    except ValueError:
        return False
    
def add_zero(s):
    if len(s)==1:
        s="000"+s
    elif len(s)==2:
        s="00"+s
    elif len(s)==3:
        s="0"+s
    return s

def yymmdd2yyyymmdd(date):
    if date[0] == '9':
        date = '19'+date
    else:
        date = '20'+date
    return date

def plot_network(mdate,sdate, dateList, pbaseList, plot_dict={}, date12List_drop=[], print_msg=True):
    """Plot Temporal-Perp baseline Network
    Inputs
        ax : matplotlib axes object
        date12List : list of string for date12 in YYYYMMDD_YYYYMMDD format
        dateList   : list of string, for date in YYYYMMDD format
        pbaseList  : list of float, perp baseline, len=number of acquisition
        plot_dict   : dictionary with the following items:
                      fontsize
                      linewidth
                      markercolor
                      markersize

                      cohList : list of float, coherence value of each interferogram, len = number of ifgrams
                      disp_min/max :  float, min/max range of the color display based on cohList
                      colormap : string, colormap name
                      coh_thres : float, coherence of where to cut the colormap for display
                      disp_title : bool, show figure title or not, default: True
                      disp_drop: bool, show dropped interferograms or not, default: True
    Output
        ax : matplotlib axes object
    """

    # Figure Setting
    if not 'fontsize'    in plot_dict.keys():  plot_dict['fontsize']    = 12
    if not 'linewidth'   in plot_dict.keys():  plot_dict['linewidth']   = 2
    if not 'markercolor' in plot_dict.keys():  plot_dict['markercolor'] = 'orange'
    if not 'markersize'  in plot_dict.keys():  plot_dict['markersize']  = 16

    # For colorful display of coherence
    if not 'cohList'     in plot_dict.keys():  plot_dict['cohList']     = None
    if not 'ylabel'      in plot_dict.keys():  plot_dict['ylabel']      = 'Perp Baseline [m]'
    if not 'cbar_label'  in plot_dict.keys():  plot_dict['cbar_label']  = 'Average Spatial Coherence'
    if not 'disp_cbar'   in plot_dict.keys():  plot_dict['disp_cbar']   = True
    if not 'disp_min'    in plot_dict.keys():  plot_dict['disp_min']    = 0.2
    if not 'disp_max'    in plot_dict.keys():  plot_dict['disp_max']    = 1.0
    if not 'colormap'    in plot_dict.keys():  plot_dict['colormap']    = 'RdBu'
    if not 'disp_title'  in plot_dict.keys():  plot_dict['disp_title']  = True
    if not 'coh_thres'   in plot_dict.keys():  plot_dict['coh_thres']   = None
    if not 'disp_drop'   in plot_dict.keys():  plot_dict['disp_drop']   = True
    if not 'disp_legend' in plot_dict.keys():  plot_dict['disp_legend'] = True
    if not 'every_year'  in plot_dict.keys():  plot_dict['every_year']  = 1
    if not 'split_cmap'  in plot_dict.keys():  plot_dict['split_cmap']  = True

    if not 'number'      in plot_dict.keys():  plot_dict['number']      = None

        
    ax = plt.gca()
        
    cohList = plot_dict['cohList']
    disp_min = plot_dict['disp_min']
    disp_max = plot_dict['disp_max']
    coh_thres = plot_dict['coh_thres']
    transparency = 0.7

    # Date Convert
    #dateList = ptime.yyyymmdd(sorted(dateList))
    dateList = yyyymmdd(sorted(dateList))
    dates, datevector = date_list2vector(dateList)
    tbaseList = date_list2tbase(dateList)[0]

    ## maxBperp and maxBtemp
    date12List = yyyymmdd_date12(mdate,sdate)
    ifgram_num = len(date12List)
    pbase12 = np.zeros(ifgram_num)
    tbase12 = np.zeros(ifgram_num)
    for i in range(ifgram_num):
        m_date, s_date = date12List[i].split('_')
        m_idx = dateList.index(m_date)
        s_idx = dateList.index(s_date)
        pbase12[i] = pbaseList[s_idx] - pbaseList[m_idx]
        tbase12[i] = tbaseList[s_idx] - tbaseList[m_idx]
    if print_msg:
        print('max perpendicular baseline: {:.2f} m'.format(np.max(np.abs(pbase12))))
        print('max temporal      baseline: {} days'.format(np.max(tbase12)))

    ## Keep/Drop - date12
    date12List_keep = sorted(list(set(date12List) - set(date12List_drop)))
    idx_date12_keep = [date12List.index(i) for i in date12List_keep]
    idx_date12_drop = [date12List.index(i) for i in date12List_drop]
    if not date12List_drop:
        plot_dict['disp_drop'] = False

    ## Keep/Drop - date
    m_dates = [i.split('_')[0] for i in date12List_keep]
    s_dates = [i.split('_')[1] for i in date12List_keep]
    dateList_keep = yyyymmdd(sorted(list(set(m_dates + s_dates))))
    dateList_drop = sorted(list(set(dateList) - set(dateList_keep)))
    idx_date_keep = [dateList.index(i) for i in dateList_keep]
    idx_date_drop = [dateList.index(i) for i in dateList_drop]

    # Ploting
    # ax=fig.add_subplot(111)
    # Colorbar when conherence is colored
    if cohList is not None:
        data_min = min(cohList)
        data_max = max(cohList)
        # Normalize
        normalization = False
        if normalization:
            cohList = [(coh-data_min) / (data_min-data_min) for coh in cohList]
            disp_min = data_min
            disp_max = data_max

        if print_msg:
            print('showing coherence')
            print(('colormap:', plot_dict['colormap']))
            print(('display range:', str([disp_min, disp_max])))
            print(('data    range:', str([data_min, data_max])))

        if plot_dict['split_cmap']:
            # Use lower/upper part of colormap to emphasis dropped interferograms
            if not coh_thres:
                # Find proper cut percentage so that all keep pairs are blue and drop pairs are red
                cohList_keep = [cohList[i] for i in idx_date12_keep]
                cohList_drop = [cohList[i] for i in idx_date12_drop]
                if cohList_drop:
                    coh_thres = max(cohList_drop)
                else:
                    coh_thres = min(cohList_keep)
            if coh_thres < disp_min:
                disp_min = 0.0
                if print_msg:
                    print('data range exceed orginal display range, set new display range to: [0.0, %f]' % (disp_max))
            c1_num = np.ceil(200.0 * (coh_thres - disp_min) / (disp_max - disp_min)).astype('int')
            coh_thres = c1_num / 200.0 * (disp_max-disp_min) + disp_min
            cmap = ColormapExt(plot_dict['colormap']).colormap
            colors1 = cmap(np.linspace(0.0, 0.3, c1_num))
            colors2 = cmap(np.linspace(0.6, 1.0, 200 - c1_num))
            cmap = LinearSegmentedColormap.from_list('truncate_RdBu', np.vstack((colors1, colors2)))
            if print_msg:
                print(('color jump at', str(coh_thres)))
        else:
            cmap = ColormapExt(plot_dict['colormap']).colormap

        if plot_dict['disp_cbar']:
            divider = make_axes_locatable(ax)
            cax = divider.append_axes("right", "3%", pad="3%")
            norm = mpl.colors.Normalize(vmin=disp_min, vmax=disp_max)
            cbar = mpl.colorbar.ColorbarBase(cax, cmap=cmap, norm=norm)
            cbar.ax.tick_params(labelsize=plot_dict['fontsize'])
            cbar.set_label(plot_dict['cbar_label'], fontsize=plot_dict['fontsize'])

        # plot low coherent ifgram first and high coherence ifgram later
        cohList_keep = [cohList[date12List.index(i)] for i in date12List_keep]
        date12List_keep = [x for _, x in sorted(zip(cohList_keep, date12List_keep))]

    # Dot - SAR Acquisition
    if idx_date_keep:
        x_list = [dates[i] for i in idx_date_keep]
        y_list = [pbaseList[i] for i in idx_date_keep]
        ax.plot(x_list, y_list, 'ko', alpha=0.7,
                ms=plot_dict['markersize'], mfc=plot_dict['markercolor'])
    if idx_date_drop:
        x_list = [dates[i] for i in idx_date_drop]
        y_list = [pbaseList[i] for i in idx_date_drop]
        ax.plot(x_list, y_list, 'ko', alpha=0.7,
                ms=plot_dict['markersize'], mfc='gray')

    ## Line - Pair/Interferogram
    # interferograms dropped
    if plot_dict['disp_drop']:
        for date12 in date12List_drop:
            date1, date2 = date12.split('_')
            idx1 = dateList.index(date1)
            idx2 = dateList.index(date2)
            x = np.array([dates[idx1], dates[idx2]])
            y = np.array([pbaseList[idx1], pbaseList[idx2]])
            if cohList is not None:
                coh = cohList[date12List.index(date12)]
                coh_idx = (coh - disp_min) / (disp_max - disp_min)
                ax.plot(x, y, '--', lw=plot_dict['linewidth'],
                        alpha=transparency, c=cmap(coh_idx))
            else:
                ax.plot(x, y, '--', lw=plot_dict['linewidth'],
                        alpha=transparency, c='k')

    # interferograms kept
    for date12 in date12List_keep:
        date1, date2 = date12.split('_')
        idx1 = dateList.index(date1)
        idx2 = dateList.index(date2)
        x = np.array([dates[idx1], dates[idx2]])
        y = np.array([pbaseList[idx1], pbaseList[idx2]])
        if cohList is not None:
            coh = cohList[date12List.index(date12)]
            coh_idx = (coh - disp_min) / (disp_max - disp_min)
            ax.plot(x, y, '-', lw=plot_dict['linewidth'],
                    alpha=transparency, c=cmap(coh_idx))
        else:
            ax.plot(x, y, '-', lw=plot_dict['linewidth'],
                    alpha=transparency, c='k')

    if plot_dict['disp_title']:
        ax.set_title('Interferogram Network', fontsize=plot_dict['fontsize'])

    # axis format
    ax = auto_adjust_xaxis_date(ax, datevector, fontsize=plot_dict['fontsize'],
                                every_year=plot_dict['every_year'])[0]
    ax = auto_adjust_yaxis(ax, pbaseList, fontsize=plot_dict['fontsize'])
    ax.set_xlabel('Time [years]', fontsize=plot_dict['fontsize'])
    ax.set_ylabel(plot_dict['ylabel'], fontsize=plot_dict['fontsize'])
    ax.tick_params(which='both', direction='in', labelsize=plot_dict['fontsize'],
                   bottom=True, top=True, left=True, right=True)

    if plot_dict['number'] is not None:
        ax.annotate(plot_dict['number'], xy=(0.03, 0.92), color='k',
                    xycoords='axes fraction', fontsize=plot_dict['fontsize'])

    # Legend
    if plot_dict['disp_drop'] and plot_dict['disp_legend']:
        solid_line = mlines.Line2D([], [], color='k', ls='solid',  label='Ifg used')
        dash_line  = mlines.Line2D([], [], color='k', ls='dashed', label='Ifg dropped')
        ax.legend(handles=[solid_line, dash_line])

    return ax

#########################################################################

INTRODUCTION = '''
##############################################################################################
   Copy Right(c): 2017, Yunmeng Cao   @PyINT v1.0   
   
              Select and Display network of a specific project based on the selection of the pairs
'''

EXAMPLE = '''
    Usage:
              select_network_gamma.py ProjectName
      
    Example:  select_network_gamma.py PacayaT163TsxHhA
              select_network_gamma.py PacayaT163TsxHhA --display  

###################################################################################################
'''


def cmdLineParse():
    parser = argparse.ArgumentParser(description='Correct orbit data for all of the Sentinel-1 data.',\
                                     formatter_class=argparse.RawTextHelpFormatter,\
                                     epilog=INTRODUCTION+'\n'+EXAMPLE)

    parser.add_argument('projectName',help='Name of the projection.')
    parser.add_argument('--disp', dest='disp_network', action='store_true',
                     help='show the figure of the network')
    
    inps = parser.parse_args()
    return inps

################################################################################    


def main(argv):
    
    inps = cmdLineParse()
    projectName = inps.projectName
        
    scratchDir = os.getenv('SCRATCHDIR')
    templateDir = os.getenv('TEMPLATEDIR')
    templateFile = templateDir + "/" + projectName + ".template"
    templateContents=read_template(templateFile)
    processDir = scratchDir + '/' + projectName + "/PROCESS"
    slcDir     = scratchDir + '/' + projectName + "/SLC"
    
    if not os.path.isdir(processDir):
        call_str = 'mkdir ' + processDir
        os.system(call_str)
        
# define files    
    
    SLC_Tab = processDir + "/SLC_Tab"
    TS_Berp = processDir + "/TS_Berp"
    TS_Itab = processDir + "/TS_Itab"
    itab_type = '1'
    pltflg = '0'
    
    if 'Max_Spacial_Baseline'  in templateContents: MaxSB=templateContents['Max_Spacial_Baseline']
    else:
        print("Max_Spacial_Baseline is not found in template!! ")
        print("500m is chosen as the threshold for spatial baseline!")
        MaxSB = '100'
        
    if 'Max_Temporal_Baseline'  in templateContents: MaxTB=templateContents['Max_Temporal_Baseline']
    else:
        print("Max_Temporal_Baseline is not found in template!! ")
        print("500 days is chosen as the threshold for temporal baseline!")
        MaxTB = '100'
    
    
#  extract available SAR images slc and slc_par    
    ListSLC = os.listdir(slcDir)
    Datelist = []
    SLCfile = []
    SLCParfile = []
    

    for kk in range(len(ListSLC)):
        if ( is_number(ListSLC[kk]) and len(ListSLC[kk])==6 ):    #  if SAR date number is 8, 6 should change to 8.
            DD=ListSLC[kk]
            Year=int(DD[0:2])
            Month = int(DD[2:4])
            Day = int(DD[4:6])           
            Datelist.append(ListSLC[kk])
    
    list(map(int,Datelist))                
    Datelist.sort()
    list(map(str,Datelist))
    
    print("All of the available SAR acquisition datelist is :")      
    for kk in range(len(Datelist)):
        print(Datelist[kk])
        str_slc = slcDir + "/" + Datelist[kk] +"/" + Datelist[kk] + ".slc"
        str_slc_par = slcDir + "/" + Datelist[kk] +"/" + Datelist[kk] + ".slc.par"
        SLCfile.append(str_slc)
        SLCParfile.append(str_slc_par)       
    
    if 'masterDate'          in templateContents:
        masterDate0 = templateContents['masterDate']
        if masterDate0 in Datelist:
            masterDate = masterDate0
            print("masterDate : " + masterDate0)
        else:
            masterDate=Datelist[0]
            print("The selected masterDate is not included in above datelist !!")
            print("The first date [ %s ] is chosen as the master date! " % Datelist[0]) 
            
    else:  
        masterDate=Datelist[0]
        print("masterDate is not found in template!!! ")
        print("The first date [ %s ] is chosen as the master date! " % Datelist[0]) 

    RefPar=slcDir + "/" + masterDate +"/" + masterDate + ".slc.par"
       
    File= open(SLC_Tab,'w')
    
    for kk in range(len(SLCfile)):
        File.write(str(SLCfile[kk])+ ' '+str(SLCParfile[kk])+'\n')
        
    File.close()
     
    call_str = "base_calc " + SLC_Tab + " " + RefPar + " " + TS_Berp + " " + TS_Itab + " " + '1 0 ' + '- ' + MaxSB + ' - ' + MaxTB
    os.system(call_str)

    TS_Net=np.loadtxt(TS_Berp)
    
#    print TS_Net[:,0]
#    print TS_Net[:,1]
    IFG_Flag=TS_Net[:,0]
    MDatelist=TS_Net[:,1]
    SDatelist=TS_Net[:,2]
    Berplist=TS_Net[:,3]
    TBaselist=TS_Net[:,4]
    
    MDatelist = np.array(MDatelist,dtype=int)
    SDatelist = np.array(SDatelist,dtype=int)
    plot_network(MDatelist,SDatelist, Datelist, Berplist, plot_dict={}, date12List_drop=[], print_msg=True)
    
###############################    Add or Remove Date  #############################    

    
    print("Selection of interferometric pairs is done! ")
    sys.exit(1)
    
if __name__ == '__main__':
    main(sys.argv[:])

    
