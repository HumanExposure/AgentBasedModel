
.. code:: ipython3

    # The United States Environmental Protection Agency through its Office of
    # Research and Development has developed this software. The code is made
    # publicly available to better communicate the research. All input data
    # used fora given application should be reviewed by the researcher so
    # that the model results are based on appropriate data for any given
    # application. This model is under continued development. The model and
    # data included herein do not represent and should not be construed to
    # represent any Agency determination or policy.
    #
    # This file was written by Dr. Namdi Brandon
    # ORCID: 0000-0001-7050-1538
    # March 22, 2018

This notebook is **only used for development**.

This notebook is in charge of saving data and files in a compressed
format as .zip files by doing the following:

1. save demographic data originally found in the 'data\_large' directory
   in the compressed form used by the ABMHAP in the 'data' directory

2. save the entire directory containing the ABMHAP directory in a
   compressed (.zip) format

Import

.. code:: ipython3

    import os, sys
    sys.path.append('..\\source')
    
    # ABMHAP modules
    import my_globals as mg
    
    import demography as dmg
    import chad

Save the files releated to the demographics

.. code:: ipython3

    #
    # the demographic
    #
    demo = dmg.CHILD_SCHOOL

.. code:: ipython3

    # number of characters to not include: '.zip'
    n_char = 4
    
    # chooser
    # (the outfile directory for each demographic with no .zip ending, the source directory to compress)
    chooser_fout_source = { dmg.ADULT_WORK: (chad.FNAME_ADULT_WORK[:-n_char], chad.FDIR_ADULT_WORK_LARGE),
                    dmg.ADULT_NON_WORK: (chad.FNAME_ADULT_NON_WORK[:-n_char], chad.FDIR_ADULT_NON_WORK_LARGE), 
                    dmg.CHILD_SCHOOL: (chad.FNAME_CHILD_SCHOOL[:-n_char], chad.FDIR_CHILD_SCHOOL_LARGE),
                    dmg.CHILD_YOUNG: (chad.FNAME_CHILD_YOUNG[:-n_char], chad.FDIR_CHILD_YOUNG_LARGE),
                   }
    
    # the outfile name (no .zip ending)
    fname, source_dir = chooser_fout_source[demo]
    

.. code:: ipython3

    #
    # Save (zip) a directory about the demographics
    #
    # save flag
    do_save = False
    
    # save the data
    if do_save:
        mg.save_zip(out_file=fname, source_dir=source_dir)

Save (zip) the entire directory for the ABMHAP code as a compressed file

.. code:: ipython3

    #
    # saving parameters
    #
    
    # save (zip) the entire directory that contains the ABMHAP code
    # this is the directory to be compressed
    fpath_src = os.path.dirname( os.getcwd() )
    
    # file directory
    fpath = os.getcwd()
    
    for i in range(3):
        fpath = os.path.dirname(fpath)
    
    # the file name of the save .zip file with out the .zip extension
    fname_out = fpath + '\\ABMHAP' # with no .zip

.. code:: ipython3

    #
    # save the directory
    #
    
    # save flag
    do_save_abm_dir = False
    
    if do_save_abm_dir:
        mg.save_zip(out_file=fname_out, source_dir=fpath_src)
