# PyINT
[![Language](https://img.shields.io/badge/python-3.5%2B-blue.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/license-GPL-yellow.svg)](https://github.com/ymcmrs/PyINT/blob/master/LICENSE)

### Single or time-series of interferograms processing based on python and GAMMA for all of the present SAR datasets. 

PYthon-based INterferometry Toolbox (PyINT) is an open-source package for single or time-series of interferograms processing from downloading data (or SLC) to generating differential-unwrapped interferograms by using GAMMA software. You can process in a routine way (e.g., SLC2Ifg.py or process_tsifg.py) or process step by step. There are many GAMMA-independent tools of PyINT could be useful for you no matter you use GAMMA or other interferometry softwares (e.g., ISCE, SNAP). Advantages include (but not limited to) download and update precise-orbit data automatically (support S1, ERS, ASAR), download and process 30m-SRTM dem automatically, cat multi-frames automatically, select swaths and bursts flexibly (for S1), extract the related S1 butsts for Coregistration automatically, etc. Welcome to contribute/improve PyINT together. 


### 1 Download

Download the development version using git:   
   
    cd ~/python
    git clone https://github.com/ymcmrs/PyINT
    
    
### 2 Installation

 To make pyint importable in python, by adding the path PyINT directory to your $PYTHONPATH

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
   
### 3 Running PyINT

1). $SCRATCHDIR and $TEMPLATEDIR should be available in your system environment. $SCRATCHDIR for processing, $TEMPLATEDIR for template files to set the related processing parameters:        

      setenv SCRATCHDIR /Users/Yunmeng/Documents/SCRATCH         
      setenv TEMPLATEDIR /Users/Yunmeng/Documents/development/TEMPLATEDIR       

2). Preparing your template file, which should be saved in $TEMPLATEDIR,  for setting some basic parameters (see the template file above).The template file should be named with a prefix of your project name:
         
      e.g.,   MexicoCityT143F529S1D.template     [Region + Track + Frame + Satellite + Orbit]


3). Single interferogram processing:

     SLC2Ifg.py IfgramDir     ## typical name style of the ifgdir:  < IFG_PROJECTNAME_MASTER-SLAVE_PB_TB > 
 
     e.g. :
         SLC2Ifg.py IFG_MexicoCityT143F529S1D_20180506-20180518_034_048     ## general interferometry processing
         SLC2Ifg.py MAI_MexicoCityT143F529S1D_20180506-20180518_034_048     ## Multi-aperture interferometry
         SLC2Ifg.py RSI_MexicoCityT143F529S1D_20180506-20180518_034_048     ## Range-split interferometry

4). Time-series of interferograms processing.

     process_tsifg.py PROJECTNAME
  
     e.g. :
       process_tsifg.py MexicoCityT143F529S1D
       
You also can process step by step:

    step1: Download S1 data by setting "DOWNLOAD" to "1"  and input Track/Frame/Time in the template file (only for Sentinel-1).   
    step2: Check DEM, if no DEM is available, using Makedem_PyInt.py
    step3: Coregistration.   Using coreg_all.py
    step4: Selecting interferometry pairs. Using SelectPairs.py
    Step5: Generating interferograms. Using SLC2Ifg.py
    Step6: Loading data for further time-series analysis. Please check mintPy (https://github.com/ymcmrs/MintPy).
              
Note:  All of the above codes are based on the hypothesis that you have installed [GAMMA](https://www.gamma-rs.ch/). 

### 4 Citing this work

    Y.M., Cao, "PyINT: Python&GAMMA based interferometry toolbox", Remote Sensing Code Library, doi:10.21982/vd48-7p51, April, 2019. 
