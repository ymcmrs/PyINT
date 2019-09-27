# PyINT
[![Language](https://img.shields.io/badge/python-3.5%2B-blue.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/license-GPL-yellow.svg)](https://github.com/ymcmrs/PyINT/blob/master/LICENSE)

### Single or time-series of interferograms processing based on python and GAMMA for all of the present SAR datasets. 

PYthon-based INterferometry Toolbox (PyINT) is an open-source package for single or time-series of interferograms processing from downloading data (or SLC) to generating differential-unwrapped interferograms by using GAMMA software. You can process in a routine way (e.g., SLC2Ifg.py or process_tsifg.py) or process step by step. There are many GAMMA-independent tools of PyINT could be useful for you no matter you use GAMMA or other interferometry softwares (e.g., ISCE, SNAP). Advantages include (but not limited to) download and update precise-orbit data automatically (support S1, ERS, ASAR), download and process 30m-SRTM dem automatically, cat multi-frames automatically, select swaths and bursts flexibly (for S1), extract the related S1 butsts for Coregistration automatically, etc. Welcome to contribute/improve PyINT.


### 1 Download

Download the development version using git:   
   
    cd ~/python
    git clone https://github.com/ymcmrs/PyINT
    
    
### 2 Installation

 1） To make pyint importable in python, by adding the path PyINT directory to your $PYTHONPATH
     For csh/tcsh user, add to your **_~/.cshrc_** file for example:   

    ############################  Python  ###############################
    if ( ! $?PYTHONPATH ) then
        setenv PYTHONPATH ""
    endif
    
    ##--------- Anaconda ---------------## 
    setenv PYTHON3DIR    ~/python/anaconda3
    setenv PATH          ${PATH}:${PYTHON3DIR}/bin
    
    ##--------- PyINT ------------------## 
    setenv PYINT_HOME    ~/python/PyINT       
    setenv PYTHONPATH    ${PYTHONPATH}:${PYINT_HOME}
    setenv PATH          ${PATH}:${PYINT_HOME}/pyint
    
 2） Install gdal, elevation module using pip or conda for DEM processing.
 
 3） Install [SSARA](https://github.com/bakerunavco/SSARA) and set account info for downloading data. [option]
 
       
### 3 Running PyINT

1). $SCRATCHDIR and $TEMPLATEDIR should be available in your system environment. $SCRATCHDIR for processing, $TEMPLATEDIR for template files to set the related processing parameters, $DEMDIR for saving DEMs:        

      setenv SCRATCHDIR /Users/Yunmeng/Documents/SCRATCH         
      setenv TEMPLATEDIR /Users/Yunmeng/Documents/development/TEMPLATEDIR
      setenv DEMDIR /Users/Yunmeng/Documents/SCRATCH/DEM

2). Preparing your template file, which should be saved in $TEMPLATEDIR,  for setting some basic parameters (see the template file above).The template file should be named with a prefix of your project name:
         
      e.g.,   MexicoCityT143F529S1D.template     [Region + Track + Frame + Satellite + Orbit]


3). Single interferogram processing:

     slc2ifg.py projectName Mdate Sdate     # start from SLC to unwrapped-differential Ifg 
     raw2ifg.py projectName Mdate Sdate     # start from raw data to unwrapped-differential Ifg 
  
     e.g. :
         slc2ifg.py HawaiiT87F526S1D 20150101 20160201
         raw2ifg.py HawaiiT87F526S1D 20150101 20160201

4). Time-series of interferograms processing.

     pyintApp.py projectName
  
     e.g. :
        pyintApp.py MexicoCityT143F529S1D   # template file MexicoCityT143F529S1D.template should be availabe in TEMPLATEDIR
        
   General work-flow: 
   
     1) download data  :  download SLCs using SSARA (please check https://github.com/bakerunavco/SSARA)
                        [You should provide Sensor, Track, Frame, or Time information in template]                     
     2) generate SLC   :  raw 2 slc (multi-frame processing is also supported)
                        [include orbit correction for S1,ASAR,ERS and burst-extraction for S1]                      
     3) generate DEM   :  reference image related geo-dem, rdc-dem, lookup table will be generated. 
                        [SRTM-1 will be downloaded and processed automatically if not provided]                       
     4) coregister SLC :  coregister SLCs to the reference SLC iamge.
                        [with assistant of DEM]  
     5) select pairs   :  select interferometric pairs for time-series processing.
                        [networks of sbas, sequential, delaunay, and stars are supported]                     
     6) interferometry :  generate unwrapped differential interferograms.
                        [include differential, unwrapping, and geocoding]
     7) load data      : loading data for time-series analysis, mintPy is supported presently.
                         
     Note: 
     
     i  ) Single interferogram processing please use slc2ifg.py or raw2ifg.py
     ii ) Multi-processor parallel processing is supported, but keep in mind GAMMA calls multi-threads already.  
     iii) You can using pyintApp.py from downloading data to generate time-series of unwrapped-differential Ifgs, 
          or you also can process step by step.

              
Note:  All of the above codes are based on the hypothesis that you have installed [GAMMA](https://www.gamma-rs.ch/). 

### 4 Citing this work

    Y.M., Cao, "PyINT: Python&GAMMA based interferometry toolbox", Remote Sensing Code Library, doi:10.21982/vd48-7p51, April, 2019. 
