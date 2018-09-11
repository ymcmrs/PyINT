# PyINT
## (Python&GAMMA based interfermetry toolbox)
### Single or time-series of interferograms processing based on python and GAMMA for all of the present SAR datasets.       

### 1 Download

Download the development version (based on Python 2) using git:   
   
    cd ~/python
    git clone https://github.com/ymcmrs/PyINT
    
    
### 2 Installation

 To make pysar importable in python, by adding the path to PyINT directory to your $PYTHONPATH

For csh/tcsh user, add to your **_~/.cshrc_** file for example:   

    ############################  Python  ###############################
    if ( ! $?PYTHONPATH ) then
        setenv PYTHONPATH ""
    endif
    
    ##--------- Anaconda ---------------## 
    setenv PYTHON2DIR    ~/python/anaconda2
    setenv PATH          ${PATH}:${PYTHON2DIR}/bin
    
    ##--------- PyINT ------------------## 
    setenv PYINT_HOME    ~/python/PyINT       
    setenv PYTHONPATH    ${PYTHONPATH}:${PYINT_HOME}
    setenv PATH          ${PATH}:${PYINT_HOME}/pyint
   
### 3 Running PyINT

1). $SCRATCHDIR and $TEMPLATEDIR should be available in your system environment. $SCRATCHDIR for processing, $TEMPLATEDIR for template files to set the related processing parameters:        

      setenv SCRATCHDIR /Users/Yunmeng/Documents/SCRATCH         
      setenv TEMPLATEDIR /Users/Yunmeng/Documents/development/TEMPLATEDIR   

2). Preparing your template file, which should be saved in $TEMPLATEDIR,  for setting some basic parameters (see the template file above).The template file should be named with a prefix of your project name, like projectname.template



3). Single interferogram processing:
     
         SLC2Ifg.py 
