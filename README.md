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



Available SAR sensors:  ERS, ASAR, ALOS-1/2, Sentinal-1A/B, TSX, ...         

####If you want to make the scripts work smoothly, you should obey the following rules :              

#####1) $SCRATCHDIR and $TEMPLATEDIR should be available in your system environment. $SCRATCHDIR for processing, $TEMPLATEDIR for template files:              
      setenv SCRATCHDIR /Users/Yunmeng/Documents/SCRATCH         
      setenv TEMPLATEDIR /Users/Yunmeng/Documents/development/TEMPLATEDIR      
      ...    
            
#####2) The correct folders' format should be:        
     $SCRATCHDIR/PROJECTNAME/SLC       (SLC folder should be available!!!)     
     $SCRATCHDIR/PROJECTNAME/PROCESS/ifgramDir  
     ...     
    
      
#####3) ifgramDir should be named like:     

    IFG_PacayaT120F107AlosA_080101-090101_0111-0123   
    MAI_PacayaT120F107AlosA_080101-090101_0111-0123
    RSI_PacayaT120F107AlosA_080101-090101_0111-0123
     
     
If you set all the above OK, then these scripts shoul work for you! If you can share some advices or ideas about python, GAMMA, InSAR processing ..., I would be very grateful and very glad to communicate with you!        
   
   
Wish these scripts can help you for InSAR processing!! Enjoy it!  Any advices or problems would be very welcomed!  Do not hesitate to contact me: ymcmrs@gmail.com        
 
   
   
 March 10, 2017   Yunmeng    
