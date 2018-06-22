# PyINT
## (Python&GAMMA based interfermetry toolbox)
### Time series interferometry processing based on python and GAMMA for all of the present SAR datasets.       

### 1 Download

Download the development version (based on Python 2) using git:   
   
    cd ~/python
    git clone https://github.com/ymcmrs/PyINT
    
    
### 2 Installation

 To make pysar importable in python, by adding the path to PySAR directory to your $PYTHONPATH

For csh/tcsh user, add to your **_~/.cshrc_** file for example:   

    ############################  Python  ###############################
    if ( ! $?PYTHONPATH ) then
        setenv PYTHONPATH ""
    endif
    
    ##--------- Anaconda ---------------## 
    setenv PYTHON2DIR    ~/python/anaconda2
    setenv PATH          ${PATH}:${PYTHON2DIR}/bin
    
    ##--------- PySAR ------------------## 
    setenv PYINT_HOME    ~/python/PyINT       
    setenv PYTHONPATH    ${PYTHONPATH}:${PYINT_HOME}
    setenv PATH          ${PATH}:${PYINT_HOME}/pyint
   
### 3 Running PyInt

1. $SCRATCHDIR and $TEMPLATEDIR should be available in your system environment. $SCRATCHDIR for processing, $TEMPLATEDIR for template files:        

      setenv SCRATCHDIR /Users/Yunmeng/Documents/SCRATCH         
      setenv TEMPLATEDIR /Users/Yunmeng/Documents/development/TEMPLATEDIR   

2. Preparing your template file, which should be saved in $TEMPLATEDIR,  for setting some basic parameters (see the template file above).The template file should be named with a prefix of your project name, like projectname.template


3. 1) Running for conventional SAR datasets (like ENVISAT, ALOS-1, Radarsat-1, TerreSAR-x):

      process_tsifg.py projectName
      
   2) Running for TOPS SAR datasets (like Sentinel-1A/B):
      
      process_tsifg_sen.py projectName

    Of course, you also can process step by step: 
    
       step1: Check DEM, if no DEM is available, using Makedem_PyINT.py
       step2: Coregistration.   Using COREG_ALL_GAMMA.py   or COREG_ALL_Sen_GAMMA.py
       step3: Selecting interferometry pairs. Using SelectPairs_Gamma.py    (Generate_IfgDir.py for available ifg_list file)
       Step4: Generating interferograms. Using SLC2Ifg_Gamma.py  or SLC2Ifg_Sen_Gamma.py
       Step5: Loading data for further time-series processing (PYSAR).  Using Load_data_gamma.py 
   
   
Wish these scripts can help you for InSAR processing!! Enjoy it!  Any advices or problems would be very welcomed!  Do not hesitate to contact me: ymcmrs@gmail.com        
 
   
   
 March 10, 2017   Yunmeng    
 updated June 22, 2018    Miami  
